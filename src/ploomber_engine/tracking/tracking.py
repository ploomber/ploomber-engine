# FUTURE
# TODO: clean up traceback
# TODO: partially track things if things fail. this might lead to some
# confusion. so we should add a flag to indicate if the experiment was
# successful or not

import ast
import uuid

import click
import parso

import nbformat
from ploomber_engine._translator import translate_parameters
from IPython.core.interactiveshell import InteractiveShell

from ploomber_engine.ipython import PloomberClient, add_to_sys_path
from ploomber_engine.tracking.io import _process_content_data
from ploomber_engine._telemetry import telemetry
from ploomber_engine._util import find_cell_with_parameters_comment

try:
    import jupytext
except ModuleNotFoundError:
    jupytext = None

try:
    import sklearn_evaluation
except ModuleNotFoundError:
    sklearn_evaluation = None


# add support for extracting name from getitem operations
def extract_name(source):
    mod = parso.parse(source.splitlines()[-1])
    names = dict(mod.get_used_names())

    if len(names) == 1:
        return list(names)[0]
    else:
        try:
            return _get_function_name(mod)
        except Exception:
            return None


def _get_function_name(mod):
    leaf = mod.get_first_leaf()
    children = leaf.parent.children

    if len(children) == 2:
        # simple case: function()
        _, call = children
    else:
        # mod.name case: metrics.acuracy_score()
        call = children[-1]
        leaf = children[-2].children[1]

    left = call.children[0].value
    right = call.children[-1].value

    if left == "(" and right == ")":
        return leaf.value


def _safe_literal_eval(source):
    try:
        return ast.literal_eval(source)
    except (SyntaxError, ValueError):
        return source.strip()


class PloomberLogger(PloomberClient):
    def _execute(self, tracker, uuid_, parameters):
        execution_count = 1

        # make sure that the current working directory is in the sys.path
        # in case the user has local modules
        with add_to_sys_path(self._cwd):
            for index, cell in enumerate(self._nb.cells):
                if cell.cell_type == "code":
                    self.execute_cell(
                        cell,
                        cell_index=index,
                        execution_count=execution_count,
                        store_history=False,
                    )
                    execution_count += 1

                    if cell["outputs"]:
                        out = _process_content_data(
                            cell["outputs"][-1], counter=None, idx=None
                        )

                        if out:
                            name = extract_name(cell.source)

                            if name:
                                if out[0] == "text/plain":
                                    val = _safe_literal_eval(out[1])
                                else:
                                    val = out[1]

                                parameters[name] = val

        tracker.upsert(uuid_, parameters)

    def execute(self, tracker, uuid_, parameters):
        """Execute the notebook"""
        # FIXME: this logic is duplicated.
        # it's also on PloomberClient.execute
        original = InteractiveShell._instance

        with self:
            self._execute(tracker, uuid_, parameters)

        if original is not None:
            # restore original instance
            InteractiveShell._instance = original

            # restore inline matplotlib
            try:
                from matplotlib_inline.backend_inline import configure_inline_support
            except ModuleNotFoundError:
                pass
            else:
                configure_inline_support(original, "inline")
                original.run_line_magic("matplotlib", "inline")


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option("-d", "--database", default="experiments.db")
@click.option("-p", "--parameters")
@click.option("-q", "--quiet", is_flag=True)
def _cli(filename, database, parameters, quiet):
    return track_execution(
        filename,
        parameters=_parse_cli_parameters(parameters),
        database=database,
        quiet=quiet,
    )


def _parse_param(value):
    exp = parso.parse(value).children[0]

    if exp.type == "name":
        return exp.value
    elif hasattr(exp, "value"):
        return ast.literal_eval(exp.value)
    else:
        return exp.get_code()


def _parse_cli_parameters(parameters):
    if parameters is None:
        return {}

    pairs = [pair.strip().split("=") for pair in parameters.split(",")]
    return {k: _parse_param(v) for k, v in pairs}


@telemetry.log_call("track-execution")
def track_execution(filename, parameters=None, database="experiments.db", quiet=False):
    """
    Execute a script or notebook and write outputs to a SQLite database
    """
    if jupytext is None:
        raise click.ClickException("Missing jupytext: pip install jupytext")

    if sklearn_evaluation is None:
        raise click.ClickException(
            "Missing sklearn-evaluation: pip install sklearn-evaluation"
        )
    parameters = parameters or dict()
    nb = jupytext.read(filename)
    _, idx = find_cell_with_parameters_comment(nb)

    if idx is None:
        click.echo("Could not find block with the # parameters comment")
        idx_injected_params = 0
    else:
        idx_injected_params = idx + 1

    if not quiet:
        click.echo(f"Parameters: {parameters}")

    params = translate_parameters(parameters, comment="User parameters")

    params_cell = nbformat.v4.new_code_cell(source=params)
    nb.cells.insert(idx_injected_params, params_cell)

    logger = PloomberLogger(nb, display_stdout=not quiet)

    if not quiet:
        click.echo("Running...")

    tracker = sklearn_evaluation.SQLiteTracker(database)
    uuid_ = str(uuid.uuid4())[:8]
    tracker.insert(uuid_, parameters)
    logger.execute(tracker=tracker, uuid_=uuid_, parameters=parameters)
