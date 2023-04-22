import pytest
import nbformat
from pathlib import Path
from ploomber_engine.ipython import PloomberClient


def print_memory():
    """helper to get free and used memory"""
    import psutil

    print(
        "free",
        psutil._common.bytes2human(psutil.virtual_memory().free),
        "used",
        psutil._common.bytes2human(psutil.virtual_memory().used),
    )


@pytest.fixture
def path_notebook(tmpdir):
    nb = nbformat.v4.new_notebook()
    cells = [
        "array = [1 for i in range(10**8)]",
        "array1 = array",
        "arrays = [array,array1]",
    ]
    nb.cells = [nbformat.v4.new_code_cell(cell) for cell in cells]

    path_notebook = Path(tmpdir).joinpath("noteboook.ipynb")
    nbformat.write(nb, path_notebook)
    return path_notebook


def test_if_memory_leak_within_notebook(path_notebook):
    for _ in range(3):
        print_memory()

        client = PloomberClient.from_path(path_notebook)
        namespace = client.get_namespace()
        del client
        del namespace
    print_memory()
