import pytest
import nbformat

from ploomber_engine.ipython import PloomberClient

# add a leading underscore so pytest doesn't think it's a test
from ploomber_engine.testing import (
    test_notebook as _test_notebook,
    NotebookTestException,
)


def make_and_execute_nb(cells):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(cell) for cell in cells]

    client = PloomberClient(nb)
    out = client.execute()

    nbformat.write(out, "nb.ipynb")


def edit_nb(cells):
    nb = nbformat.read("nb.ipynb", as_version=nbformat.NO_CONVERT)

    for idx, source in cells:
        cell = nb.cells[idx]
        cell["source"] = source
        nb.cells[idx] = cell

    nbformat.write(nb, "nb.ipynb")


def test_no_outputs(tmp_empty):
    make_and_execute_nb(["x = 1", "y = 2"])

    _test_notebook("nb.ipynb")


def test_ok_simple(tmp_empty):
    make_and_execute_nb(["print(1)", "print(2)"])

    _test_notebook("nb.ipynb")


def test_ok_multiple_outputs(tmp_empty):
    make_and_execute_nb(["print(1); 2", "print(2); 3"])

    _test_notebook("nb.ipynb")


def test_fail_different_output(tmp_empty):
    make_and_execute_nb(["print(1)", "print(2)"])

    edit_nb([(1, "print(100)")])

    with pytest.raises(NotebookTestException) as excinfo:
        _test_notebook("nb.ipynb")

    assert str(excinfo.value) == "Error in cell 2: Expected output (2), actual (100)"


def test_fail_different_number_of_outputs(tmp_empty):
    make_and_execute_nb(["print(1)", "print(2)"])

    edit_nb([(0, "print(1); 2")])

    with pytest.raises(NotebookTestException) as excinfo:
        _test_notebook("nb.ipynb")

    assert (
        str(excinfo.value)
        == "Error in cell 1: Expected number of cell outputs (1), actual (2)"
    )


def test_ignores_image(tmp_empty):
    make_and_execute_nb(["import matplotlib.pyplot as plt; plt.plot([1, 2, 3])"])
    _test_notebook("nb.ipynb")
