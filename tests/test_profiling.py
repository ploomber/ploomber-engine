from unittest.mock import Mock
from pathlib import Path

import nbformat
import pytest
from matplotlib.testing.decorators import image_comparison

from ploomber_engine import profiling


@pytest.fixture
def cells():
    sleep = "time.sleep(2)"
    cells = [
        "import numpy as np; import time",  # i=1
        sleep,  # i=2
        "x = np.ones(131072, dtype='float64')",  # i=3
        sleep,  # i=4
        "y = np.ones(131072*10, dtype='float64')",  # i=5
        sleep,  # i=6
    ]
    return cells


@pytest.fixture
def nb(cells):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(cell) for cell in cells]
    return nb


@pytest.fixture
def nb_metadata(cells):
    cells_with_metadata = []
    memory_usage = [107.65, 41.84, 44.79, 37.29, 47.39, 48.15]
    timestamp_start = [
        1674998730.886695,
        1674998730.888831,
        1674998732.901863,
        1674998732.907168,
        1674998734.917144,
        1674998734.923841,
    ]
    timestamp_end = [
        1674998730.888669,
        1674998732.900239,
        1674998732.906827,
        1674998734.915482,
        1674998734.923498,
        1674998736.933173,
    ]
    for ind, cell in enumerate(cells):
        cells_with_metadata.append(
            nbformat.v4.new_code_cell(
                cell,
                metadata={
                    "ploomber": {
                        "memory_usage": memory_usage[ind],
                        "timestamp_start": timestamp_start[ind],
                        "timestamp_end": timestamp_end[ind],
                    }
                },
            )
        )
    nb.cells = cells_with_metadata
    return nb


def test_profiling(nb, monkeypatch):
    class FakeMem:
        def __init__(self, value):
            self._value = value

        @property
        def uss(self):
            return self._value

    mock_psutil = Mock()
    mock_psutil.Process().memory_full_info.side_effect = [
        FakeMem(v) for v in [0, 0, 1048576, 1048576, 10 * 1048576, 10 * 1048576]
    ]

    monkeypatch.setattr(profiling, "psutil", mock_psutil)

    client = profiling.PloomberMemoryProfilerClient(nb)

    nb = client.execute()
    mem = [cell.metadata["ploomber"]["memory_usage"] for cell in nb.cells]

    assert mem == [0.0, 0.0, 1.0, 1.0, 10.0, 10.0]


def test_memory_profile(nb, tmp_empty):
    nbformat.write(nb, "notebook.ipynb")

    profiling.memory_profile("notebook.ipynb", "output.ipynb")

    assert Path("output.ipynb").is_file()
    assert Path("notebook-memory-usage.png").is_file()


@image_comparison(
    baseline_images=["plot_memory_usage"], extensions=["png"], remove_text=False
)
def test_plot_memory_usage(nb_metadata, tmp_empty):
    profiling.plot_memory_usage(nb_metadata)


@image_comparison(
    baseline_images=["plot_cell_runtime"], extensions=["png"], remove_text=False
)
def test_plot_cell_runtime(nb_metadata, tmp_empty):
    profiling.plot_cell_runtime(nb_metadata)
