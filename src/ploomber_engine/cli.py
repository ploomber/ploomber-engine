"""
Command-line interface
"""
import ast
import click

from ploomber_engine import execute_notebook


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
@click.option(
    "--log-output",
    is_flag=True,
    default=False,
    help="Display notebook's stdout",
)
@click.option(
    "--profile-runtime",
    is_flag=True,
    default=False,
    help="Profile cell's runtime",
)
@click.option(
    "--profile-memory",
    is_flag=True,
    default=False,
    help="Profile cell's memory usage",
)
@click.option(
    "--progress-bar/--no-progress-bar", default=True, help="Display a progress bar"
)
@click.option("--parameters", "-p", nargs=2, multiple=True)
@click.option(
    "--debug-later",
    is_flag=True,
    default=False,
    help="Serialize traceback for later debugging",
)
def cli(
    input_path,
    output_path,
    log_output,
    profile_runtime,
    profile_memory,
    progress_bar,
    parameters,
    debug_later,
):
    """
    Execute my-notebook.ipynb, store results in output.ipynb:

    $ ploomber-engine my-notebook.ipynb output.ipynb

    Pass parameters:

    $ ploomber-engine my-notebook.ipynb output.ipynb -p key value -p x 42

    Display print statements:

    $ ploomber-engine my-notebook.ipynb output.ipynb --log-output

    Store a plot with cell's runtime:

    $ ploomber-engine my-notebook.ipynb output.ipynb --profile-runtime

    Store a plot with cell's memory usage:

    $ ploomber-engine my-notebook.ipynb output.ipynb --profile-memory
    """
    execute_notebook(
        input_path,
        output_path,
        log_output=log_output,
        profile_memory=profile_memory,
        profile_runtime=profile_runtime,
        progress_bar=progress_bar,
        parameters=_parse_cli_notebook_parameters(parameters),
        debug_later=debug_later,
        verbose=True,
    )


def _safe_literal_eval(val):
    try:
        return ast.literal_eval(val)
    except Exception:
        return val


def _parse_cli_notebook_parameters(parameters):
    if not parameters:
        return None

    return {k: _safe_literal_eval(v) for k, v in parameters}
