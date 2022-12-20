from unittest.mock import Mock
from pathlib import Path

import nbformat
import pytest

from ploomber_engine.profiling import PloomberProfilingClient, memory_profile
from ploomber_engine import profiling


@pytest.fixture
def nb():
    nb = nbformat.v4.new_notebook()
    sleep = "time.sleep(2)"
    cells = [
        "import numpy as np; import time",  # i=1
        sleep,  # i=2
        "x = np.ones(131072, dtype='float64')",  # i=3
        sleep,  # i=4
        "y = np.ones(131072*10, dtype='float64')",  # i=5
        sleep,  # i=6
    ]

    nb.cells = [nbformat.v4.new_code_cell(cell) for cell in cells]

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

    client = PloomberProfilingClient(nb)

    nb = client.execute()
    mem = [cell.metadata["ploomber"]["memory_usage"] for cell in nb.cells]

    assert mem == [0.0, 0.0, 1.0, 1.0, 10.0, 10.0]


def test_memory_profile(nb, tmp_empty):
    nbformat.write(nb, "notebook.ipynb")

    memory_profile("notebook.ipynb", "output.ipynb")

    assert Path("output.ipynb").is_file()
    assert Path("notebook-memory-usage.png").is_file()
