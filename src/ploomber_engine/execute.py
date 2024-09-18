"""
Abstractions for running notebooks with papermill-like interface
"""

import warnings
from pathlib import Path
import csv

import click
import nbformat

from ploomber_engine.ipython import PloomberClient
from ploomber_engine import profiling
from ploomber_engine import _util


def execute_notebook(
    input_path,
    output_path,
    *,
    parameters=None,
    log_output=False,
    profile_runtime=False,
    profile_memory=False,
    progress_bar=True,
    debug_later=False,
    verbose=False,
    remove_tagged_cells=None,
    cwd=".",
    save_profiling_data=False,
):
    """Executes a notebook. Drop-in replacement for
    ``papermill.execute_notebook`` with enhanced capabilities.

    Parameters
    ----------
    input_path : str or Path or nbformat.NotebookNode
        Path to input notebook or NotebookNode object of notebook

    output_path : str or Path or None
        Path to save executed notebook. If None, no file will be saved

    parameters : dict, optional, default=None
        Arbitrary keyword arguments to pass to the notebook parameters

    log_output : bool, optional, default=False
        Flag for whether or not to write notebook output to stdout

    profile_runtime : bool or Path, default=False
        If True, profile cell's runtime (stores plot in a ``.png``
        file in the same folder as ``output_path``).
        If Path, profiles and stores the plot to the given Path.

    profile_memory : bool or Path, default=False
        If True, profile cell's memory usage (stores plot in a ``.png``
        file in the same folder as ``output_path``).
        If Path, profiles and stores the plot to the given Path.

    progress_bar : bool, default=True
        Display a progress bar.

    debug_later : bool, default=False
        Serialize Python traceback for later debugging. The ``.dump`` file is stored
        next to the output notebook.

    verbose : bool, default=False
        If True, prints information messages

    remove_tagged_cells : str or list, default=None
        Cells with any of the passed tag(s) will be removed from the notebook before
        execution.

    cwd : str or Path, default='.'
        Working directory to use when executing the notebook

    save_profiling_data : bool or Path, default=False
        If True, saves profiling data generated from profile_memory and profile_runtime
        (stores a ``.csv`` file in the same folder as ``output_path``).
        If Path, saves profiling data to the given Path

    Returns
    -------
    nb : NotebookNode
        Executed notebook object

    Notes
    -----
    .. versionchanged:: 0.0.31
        Allow paths to be passed to ``profile_runtime``, ``profile_memory``
        arguments.

    .. versionchanged:: 0.0.23
        Added ``cwd`` argument.
        Added ``save_profiling_data`` argument.

    .. versionchanged:: 0.0.21
        Added ``remove_tagged_cells`` arguments.

    .. versionchanged:: 0.0.19
        Added ``parameters``, ``progress_bar``, ``debug_later``, and ``verbose``
        arguments.

    .. versionadded:: 0.0.18

    Examples
    --------
    Execute a notebook:

    >>> from ploomber_engine import execute_notebook
    >>> out = execute_notebook("nb.ipynb", "out.ipynb")

    Display any printed messages:

    >>> from ploomber_engine import execute_notebook
    >>> out = execute_notebook("nb.ipynb", "out.ipynb", log_output=True)

    Store a plot with cell's runtime:

    >>> from ploomber_engine import execute_notebook
    >>> out = execute_notebook("nb.ipynb", "out.ipynb", profile_runtime=True)

    Store a plot with cell's memory usage:

    >>> from ploomber_engine import execute_notebook
    >>> out = execute_notebook("nb.ipynb", "out.ipynb", profile_memory=True)

    Store a plot with cell's memory usage at a custom path:

    >>> from ploomber_engine import execute_notebook
    >>> out = execute_notebook("nb.ipynb", "out.ipynb", profile_memory='memory.png')


    Remove cells with the tag "remove" before execution:

    >>> from ploomber_engine import execute_notebook
    >>> out = execute_notebook("nb.ipynb", "out.ipynb", remove_tagged_cells="remove")

    Remove cells with any of the passed tags before execution:

    >>> from ploomber_engine import execute_notebook
    >>> out = execute_notebook("nb.ipynb", "out.ipynb",
    ...                        remove_tagged_cells=["remove", "also-remove"])
    """
    path_like_input = isinstance(input_path, (str, Path))
    if save_profiling_data and not (profile_runtime or profile_memory):
        warnings.warn(
            "save_profiling_data=True requires "
            "profile_runtime=True or profile_memory=True",
            UserWarning,
        )

    if profile_memory:
        INIT_FUNCTION = (
            profiling.PloomberMemoryProfilerClient.from_path
            if path_like_input
            else profiling.PloomberMemoryProfilerClient
        )
    else:
        INIT_FUNCTION = PloomberClient.from_path if path_like_input else PloomberClient

    if debug_later:
        debug_later_ = _util.sibling_with_suffix(output_path, ".dump")
    else:
        debug_later_ = debug_later

    client = INIT_FUNCTION(
        input_path,
        display_stdout=log_output,
        progress_bar=progress_bar,
        debug_later=debug_later_,
        remove_tagged_cells=remove_tagged_cells,
        cwd=cwd,
    )

    try:
        out = client.execute(parameters=parameters)
    except Exception:
        if output_path:
            nbformat.write(client._nb, output_path)

        if verbose and output_path:
            click.secho(
                "An error happened while executing the notebook. "
                f"Partially executed notebook stored at {output_path}",
                fg="red",
            )

        if debug_later and verbose:
            click.secho(
                f"Storing serialized traceback at: {debug_later_}. "
                f"To start debugging, run: dltr {debug_later_}",
                fg="yellow",
            )

        raise

    if profile_runtime:
        profile_runtime, output_path_runtime = _parse_bool_or_path(
            arg_key="profile_runtime",
            arg_value=profile_runtime,
            default_path=_util.sibling_with_suffix(output_path, "-runtime.png"),
        )
        ax = profiling.plot_cell_runtime(out)
        ax.figure.savefig(output_path_runtime)

        if verbose:
            click.secho(
                f"Cell runtime plot stored at: {output_path_runtime}", fg="green"
            )

    if profile_memory:
        profile_memory, output_path_memory = _parse_bool_or_path(
            arg_key="profile_memory",
            arg_value=profile_memory,
            default_path=_util.sibling_with_suffix(output_path, "-memory-usage.png"),
        )
        ax = profiling.plot_memory_usage(out)
        ax.figure.savefig(output_path_memory)

        if verbose:
            click.secho(
                f"Cell memory profile plot stored at: {output_path_memory}", fg="green"
            )

    if save_profiling_data:
        save_profiling_data, output_path_profiling_data = _parse_bool_or_path(
            arg_key="save_profiling_data",
            arg_value=save_profiling_data,
            default_path=_util.sibling_with_suffix(output_path, "-profiling-data.csv"),
        )
        data = profiling.get_profiling_data(out)
        with open(output_path_profiling_data, "w") as f:
            writer = csv.writer(f)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))

    if output_path:
        nbformat.write(out, output_path)
    return out


def _parse_bool_or_path(arg_key, arg_value, default_path):
    """Parse a boolean or a path argument (arg_val).
    If a boolean is passed, return the bool and the default path.
    If a string is passed, return True and the string as the path.
    """

    if isinstance(arg_value, str):
        expected_file_extension = Path(default_path).suffix
        if not arg_value.endswith(expected_file_extension):
            raise ValueError(
                f"Invalid {arg_key}:{arg_value}, "
                f"path must end with {expected_file_extension}"
            )
        parsed_bool = True
        parsed_path = arg_value

    elif isinstance(arg_value, bool):
        parsed_bool = arg_value
        parsed_path = default_path

    else:
        raise ValueError(
            f"Invalid {arg_key} type ({type(arg_value)}). "
            f"Please provide either a boolean or a string"
        )

    # make sure the path's parent directory exists
    parsed_path = Path(parsed_path)
    parsed_path.parent.mkdir(parents=True, exist_ok=True)

    return parsed_bool, parsed_path
