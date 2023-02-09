from unittest.mock import ANY
from pathlib import Path

import pytest
from IPython.display import Image


from ploomber_engine import execute_notebook
from conftest import _make_nb, _read_nb


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


def test_execute_notebook_with_parameters(tmp_empty):
    nb_in = _make_nb(["x + y"])

    nb = execute_notebook(nb_in, "out.ipynb", parameters=dict(x=21, y=21))
    nb_source = _read_nb("nb.ipynb")
    nb_from_file = _read_nb("out.ipynb")

    assert nb.cells[1]["outputs"][0]["data"] == {"text/plain": "42"}
    assert not nb_source.cells[0]["outputs"]
    assert nb_from_file.cells[1]["outputs"][0]["data"] == {"text/plain": "42"}


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

    execute_notebook(nb_in, "out.ipynb", log_output=True, progress_bar=False)

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


@pytest.mark.parametrize(
    "cells",
    [
        ["1+1"],
        ["1+1", ("markdown", "# hello")],
    ],
)
def test_execute_notebook_profile_runtime(cells, tmp_empty):
    nb_in = _make_nb(cells)

    execute_notebook(nb_in, "out.ipynb", profile_runtime=True)

    assert Path("out-runtime.png")
    assert Image(filename="out-runtime.png")


@pytest.mark.parametrize(
    "cells",
    [["1+1"], ["1+1", ("markdown", "# hello")]],
)
def test_execute_notebook_profile_memory(cells, tmp_empty):
    nb_in = _make_nb(cells)

    execute_notebook(nb_in, "out.ipynb", profile_memory=True)

    assert Path("out-memory-usage.png")
    assert Image(filename="out-memory-usage.png")


def test_progress_bar(tmp_empty, capsys):
    nb = _make_nb(["1 + 1"], path=None)

    execute_notebook(nb, output_path=None)

    captured = capsys.readouterr()
    assert "Executing cell: 1" in captured.err


def test_stores_partially_executed_notebook(tmp_empty):
    nb = _make_nb(["1 + 1", "1 / 0"], path=None)

    with pytest.raises(ZeroDivisionError):
        execute_notebook(nb, output_path="output.ipynb")

    out = _read_nb("output.ipynb")

    assert out.cells[0]["outputs"][0]["data"] == {"text/plain": "2"}
    assert out.cells[1]["outputs"][0] == {
        "ename": "ZeroDivisionError",
        "evalue": "division by zero",
        "output_type": "error",
        "traceback": ANY,
    }


@pytest.mark.parametrize(
    "out, dump",
    [
        ["out.ipynb", "out.dump"],
        ["path/to/out.ipynb", "path/to/out.dump"],
    ],
)
def test_execute_notebook_debug_later(tmp_empty, out, dump):
    nb_in = _make_nb(["x = 1", "y = 0", "x / y"])

    with pytest.raises(ZeroDivisionError):
        execute_notebook(nb_in, out, debug_later=True)

    assert Path(dump).is_file()


def test_execute_notebook_remove_tagged_cells(tmp_empty):
    nb_in = _make_nb(
        [
            ("code", "1/0", dict(tags=["remove"])),
            ("code", "1 + 1"),
        ]
    )

    out = execute_notebook(nb_in, "out.ipynb", remove_tagged_cells="remove")

    assert [c.source for c in out.cells] == ["1 + 1"]
