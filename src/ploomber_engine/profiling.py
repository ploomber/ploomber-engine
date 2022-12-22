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


class PloomberMemoryProfilerClient(PloomberClient):

    @requires(['psutil'], name='PloomberMemoryProfilerClient')
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


@telemetry.log_call("ploomber-engine-memory-profile")
def memory_profile(path, output):
    import matplotlib.pyplot as plt

    path = Path(path)
    target = path.with_name(path.stem + "-memory-usage.png")

    client = PloomberMemoryProfilerClient.from_path(path)

    click.echo("Running notebook...")
    nb = client.execute()
    nbformat.write(nb, output)
    click.echo(f"Finished execution. Stored executed notebook at {output!s}")

    mem = [cell.metadata["ploomber"]["memory_usage"] for cell in nb.cells]
    fig, ax = plt.subplots()

    ax.plot(range(1, len(mem) + 1), mem, marker="o")
    ax.grid()
    ax.set_title("Memory usage")
    ax.set_xlabel("Cell index")
    ax.set_ylabel("Memory used (MB) upon finishing cell")
    fig.savefig(target)

    click.echo(f"Plot stored at {target!s}")
