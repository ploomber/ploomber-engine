from pathlib import Path
from datetime import datetime

import nbformat
import click
from ploomber_core.dependencies import requires

from ploomber_engine.ipython import PloomberClient
from ploomber_engine._util import recursive_update
from ploomber_engine._telemetry import telemetry

try:
    import psutil
except ModuleNotFoundError:
    psutil = None


try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


class PloomberMemoryProfilerClient(PloomberClient):
    @requires(["psutil"], name="PloomberMemoryProfilerClient")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def hook_cell_pre(self, cell):
        metadata = {"ploomber": {"timestamp_start": datetime.now().timestamp()}}
        recursive_update(cell.metadata, metadata)

    def hook_cell_post(self, cell):
        # get memory usage in megabytes
        mem = psutil.Process().memory_full_info().uss / 1048576

        metadata = {
            "ploomber": {
                "timestamp_end": datetime.now().timestamp(),
                "memory_usage": mem,
            }
        }
        recursive_update(cell.metadata, metadata)


@telemetry.log_call("memory-profile")
def memory_profile(path, output):
    path = Path(path)
    target = path.with_name(path.stem + "-memory-usage.png")

    client = PloomberMemoryProfilerClient.from_path(path)

    click.echo("Running notebook...")
    nb = client.execute()
    nbformat.write(nb, output)
    click.echo(f"Finished execution. Stored executed notebook at {output!s}")

    ax = plot_memory_usage(nb)
    ax.figure.savefig(target)

    click.echo(f"Plot stored at {target!s}")


@requires(["matplotlib"])
def plot_memory_usage(nb):
    """
    Plot cell memory usage. Notebook must contain "memory_usage" under the
    "ploomber" key in the metadata

    Notes
    -----
    .. versionadded:: 0.0.18
    """
    code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
    mem = [cell.metadata["ploomber"]["memory_usage"] for cell in code_cells]
    _, ax = plt.subplots()

    ax.plot(range(1, len(mem) + 1), mem, marker="o")
    ax.grid()
    ax.set_title("Memory usage")
    ax.set_xlabel("Cell index")
    ax.set_ylabel("Memory used (MB) upon finishing cell")
    return ax


# runtime profiling


def _compute_runtime(cell):
    start = cell.metadata.ploomber.timestamp_start
    end = cell.metadata.ploomber.timestamp_end
    return end - start


@requires(["matplotlib"])
def plot_cell_runtime(nb):
    """
    Plot cell runtime

    Notes
    -----
    .. versionadded:: 0.0.18
    """
    code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
    cell_runtime = [_compute_runtime(c) for c in code_cells]
    cell_indexes = list(range(1, len(cell_runtime) + 1))

    _, ax = plt.subplots()
    ax.plot(cell_indexes, cell_runtime, marker="o")
    ax.set_xticks(cell_indexes)
    ax.set_title("Cell runtime")
    ax.set_xlabel("Cell index")
    ax.set_ylabel("Runtime (seconds)")
    ax.grid()
    ax.figure.tight_layout()

    return ax


def get_profiling_data(nb):
    """
    Collect profiling data from the notebook and return as a dictionary

    Parameters
    ----------
    nb : NotebookNode
        Notebook to collect profiling data from

    Returns
    -------
    dict: dictionary with the following keys:
        cell: list of cell indexes
        runtime: list of cell runtimes
        memory: list of cell memory usage
    """
    code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
    return dict(
        cell=list(range(1, len(code_cells) + 1)),
        runtime=[_compute_runtime(c) for c in code_cells],
        memory=[c.metadata["ploomber"].get("memory_usage", "NA") for c in code_cells],
    )
