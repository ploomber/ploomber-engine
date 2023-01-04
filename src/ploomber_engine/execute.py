"""
Abstractions for running notebooks with papermill-like interface
"""
from pathlib import Path

import nbformat

from ploomber_engine.ipython import PloomberClient
from ploomber_engine import profiling


def execute_notebook(
    input_path,
    output_path,
    *,
    log_output=False,
    profile_runtime=False,
    profile_memory=False
):
    """Executes a notebook. Drop-in replacement for
    ``papermill.execute_notebook`` with enhanced capabilities.

    Parameters
    ----------
    input_path : str or Path or nbformat.NotebookNode
        Path to input notebook or NotebookNode object of notebook

    output_path : str or Path or None
        Path to save executed notebook. If None, no file will be saved

    log_output : bool, optional, default=False
        Flag for whether or not to write notebook output to stdout

    profile_runtime : bool, optional, default=False
        If True, profile cell's runtime (stores plot in a ``.png``
        file in the same folder as ``output_path``)

    profile_memory : bool, optional, default=False
        If True, profile cell's memory usage (stores plot in a ``.png``
        file in the same folder as ``output_path``)


    Returns
    -------
    nb : NotebookNode
        Executed notebook object

    Notes
    -----
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

    """
    path_like_input = isinstance(input_path, (str, Path))

    if profile_memory:
        INIT_FUNCTION = (
            profiling.PloomberMemoryProfilerClient.from_path
            if path_like_input
            else profiling.PloomberMemoryProfilerClient
        )
    else:
        INIT_FUNCTION = PloomberClient.from_path if path_like_input else PloomberClient

    client = INIT_FUNCTION(input_path, display_stdout=log_output)

    out = client.execute()

    if profile_runtime:
        ax = profiling.plot_cell_runtime(out)
        output_path = Path(output_path)
        output_path_runtime = output_path.with_name(output_path.stem + "-runtime.png")
        ax.figure.savefig(output_path_runtime)

    if profile_memory:
        ax = profiling.plot_memory_usage(out)
        output_path = Path(output_path)
        output_path_memory = output_path.with_name(
            output_path.stem + "-memory-usage.png"
        )
        ax.figure.savefig(output_path_memory)

    if output_path:
        nbformat.write(out, output_path)

    return out
