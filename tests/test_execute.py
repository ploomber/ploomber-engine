from pathlib import Path

import nbformat
import pytest
from IPython.display import Image

from ploomber_engine import execute_notebook


@pytest.fixture
def nb():
    pass


def _make_cell(cell):
    if isinstance(cell, str):
        return nbformat.v4.new_code_cell(cell)
    elif cell[0] == "markdown":
        return nbformat.v4.new_markdown_cell(cell[1])
    else:
        raise ValueError(f"Unexpected value: {cell}")


def _make_nb(cells, path="nb.ipynb"):
    nb = nbformat.v4.new_notebook()
    nb.cells = [_make_cell(cell) for cell in cells]

    if path:
        nbformat.write(nb, path)

    return nb


def _read_nb(path):
    return nbformat.read(path, as_version=nbformat.NO_CONVERT)


@pytest.mark.parametrize("input_", ["nb.ipynb", Path("nb.ipynb")])
def test_execute_notebook_from_path(tmp_empty, input_):
    _make_nb(["1+1"])

    nb = execute_notebook(input_, "out.ipynb")
    nb_source = _read_nb(input_)
    nb_from_file = _read_nb("out.ipynb")

    assert nb.cells[0]["outputs"][0]["data"] == {"text/plain": "2"}
    assert not nb_source.cells[0]["outputs"]
    assert nb_from_file.cells[0]["outputs"][0]["data"] == {"text/plain": "2"}


def test_execute_notebook_from_object(tmp_empty):
    nb_in = _make_nb(["1+1"])

    nb = execute_notebook(nb_in, "out.ipynb")
    nb_source = _read_nb("nb.ipynb")
    nb_from_file = _read_nb("out.ipynb")

    assert nb.cells[0]["outputs"][0]["data"] == {"text/plain": "2"}
    assert not nb_source.cells[0]["outputs"]
    assert nb_from_file.cells[0]["outputs"][0]["data"] == {"text/plain": "2"}


def test_execute_notebook_no_output_path(tmp_empty):
    _make_nb(["1+1"])

    nb_out = execute_notebook("nb.ipynb", output_path=None)
    nb_source = _read_nb("nb.ipynb")

    assert nb_out.cells[0]["outputs"][0]["data"] == {"text/plain": "2"}
    assert not nb_source.cells[0]["outputs"]
    assert not Path("out.ipynb").is_file()


def test_execute_notebook_with_errors(tmp_empty):
    nb_in = _make_nb(["1+1", "1/0"])

    with pytest.raises(ZeroDivisionError):
        execute_notebook(nb_in, "out.ipynb")


@pytest.mark.xfail(reason="not implemented")
def test_execute_notebook_with_errors_saves_partiall_executed_notebook(tmp_empty):
    nb_in = _make_nb(["1+1", "1/0"])

    with pytest.raises(ZeroDivisionError):
        execute_notebook(nb_in, "out.ipynb")

    nb_from_file = _read_nb("out.ipynb")
    assert nb_from_file.cells[0]["outputs"][0]["data"] == {"text/plain": "2"}
    # TODO: check that papermill-like cells are added at the top and above the failing
    # cell


@pytest.mark.xfail(reason="not implemented")
def test_execute_notebook_with_params(tmp_empty):
    nb_in = _make_nb(["x+y"])

    nb = execute_notebook(nb_in, "out.ipynb", parameters=dict(x=21, y=21))
    nb_source = _read_nb("nb.ipynb")
    nb_from_file = _read_nb("out.ipynb")

    assert nb.cells[0]["outputs"][0]["data"] == {"text/plain": "42"}
    assert not nb_source.cells[0]["outputs"]
    assert nb_from_file.cells[0]["outputs"][0]["data"] == {"text/plain": "42"}


def test_execute_notebook_inline(tmp_empty):
    _make_nb(["1+1"])

    nb = execute_notebook("nb.ipynb", "nb.ipynb")
    nb_out = _read_nb("nb.ipynb")

    assert nb.cells[0]["outputs"][0]["data"] == {"text/plain": "2"}
    assert nb_out.cells[0]["outputs"][0]["data"] == {"text/plain": "2"}


def test_execute_notebook_log_stdout(tmp_empty, capsys):
    nb_in = _make_nb(
        ["import sys", "print('hello')", "print('world', file=sys.stderr)"]
    )

    execute_notebook(nb_in, "out.ipynb", log_output=True)

    captured = capsys.readouterr()
    assert captured.out == "hello\n"
    assert captured.err == ""


@pytest.mark.xfail(reason="not implemented")
def test_execute_notebook_log_stderr(tmp_empty, capsys):
    nb_in = _make_nb(["import sys", "print('hello', file=sys.stderr)"])

    execute_notebook(nb_in, "out.ipynb", log_output=True)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "hello\n"


# TODO: we should check the contents of the plot
# check sklearn-evaluation plot tests for examples
@pytest.mark.parametrize(
    "cells",
    [
        ["1+1"],
        ["1+1", ("markdown", "# hello")]
    ],
)
def test_execute_notebook_profile_runtime(cells, tmp_empty):
    nb_in = _make_nb(cells)

    execute_notebook(nb_in, "out.ipynb", profile_runtime=True)

    assert Path("out-runtime.png")
    assert Image(filename="out-runtime.png")


# TODO: we should check the contents of the plot
# check sklearn-evaluation plot tests for examples
@pytest.mark.parametrize(
    "cells",
    [
        ["1+1"],
        ["1+1", ("markdown", "# hello")]
    ],
)
def test_execute_notebook_profile_memory(cells, tmp_empty):
    nb_in = _make_nb(cells)

    execute_notebook(nb_in, "out.ipynb", profile_memory=True)

    assert Path("out-memory-usage.png")
    assert Image(filename="out-memory-usage.png")
