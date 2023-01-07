import os
from pathlib import Path

import nbformat
import pytest


@pytest.fixture
def tmp_empty(tmp_path):
    """
    Create temporary path using pytest native fixture,
    them move it, yield, and restore the original path
    """
    old = os.getcwd()
    os.chdir(str(tmp_path))
    yield str(Path(tmp_path).resolve())
    os.chdir(old)


@pytest.fixture(autouse=True)
def doctests_fixture(tmp_empty):
    """
    Create temporary path using pytest native fixture,
    them move it, yield, and restore the original path
    """
    nb = nbformat.v4.new_notebook()
    cell = nbformat.v4.new_code_cell("1+1")
    nb.cells = [cell]
    nbformat.write(nb, "nb.ipynb")
