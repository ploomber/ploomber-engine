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
    assert captured.out == "\nhello\n"
    assert captured.err == "world\n"


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

    custom_path = str(Path(tmp_empty + "/new_dir/custom.png"))
    execute_notebook(nb_in, "out.ipynb", profile_runtime=custom_path)
    assert Path(custom_path).is_file()


@pytest.mark.parametrize(
    "profile_memory,profile_runtime,err_check",
    [
        ["bogus", "time1.png", r"Invalid .* path must end with .png"],
        ["mem1", True, r"Invalid .* path must end with .png"],
        ["mem1", 2, r"Invalid .* provide either a boolean or a string"],
    ],
)
def test_invalid_profile_plot_args(
    tmp_empty, profile_memory, profile_runtime, err_check
):
    nb_in = _make_nb(["1 + 1"])
    execute_kwgs = dict(
        input_path=nb_in,
        output_path="out.ipynb",
        profile_memory=profile_memory,
        profile_runtime=profile_runtime,
    )
    with pytest.raises(ValueError, match=err_check):
        execute_notebook(**execute_kwgs)


@pytest.mark.parametrize(
    "profile_memory,profile_runtime",
    [
        ["mem.png", "time.png"],
        ["mem2.png", True],
        [True, False],
        [True, True],
    ],
)
def test_valid_profile_plot_args(tmp_empty, profile_memory, profile_runtime):
    nb_in = _make_nb(["1 + 1"])
    label = "out"
    execute_kwgs = dict(
        input_path=nb_in,
        output_path=f"{label}.ipynb",
        profile_memory=profile_memory,
        profile_runtime=profile_runtime,
    )

    execute_notebook(**execute_kwgs)
    if profile_memory:
        fname = (
            profile_memory
            if isinstance(profile_memory, str)
            else f"{label}-memory-usage.png"
        )
        assert Path(fname).exists()
    if profile_runtime:
        fname = (
            profile_runtime
            if isinstance(profile_runtime, str)
            else f"{label}-runtime.png"
        )
        assert Path(fname).exists()


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

    assert out.cells[1]["outputs"][0]["data"] == {"text/plain": "2"}
    assert out.cells[3]["outputs"][0] == {
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


@pytest.mark.parametrize(
    "save_profiling_data_value, save_profiling_output",
    [(True, "out-profiling-data.csv"), ("test.csv", "test.csv")],
)
def test_execute_notebook_save_profiling_data(
    tmp_empty, save_profiling_data_value, save_profiling_output
):
    nb_in = _make_nb(["1 + 1"])
    with pytest.warns(UserWarning, match="save_profiling_data=True requires"):
        # save_profiling_data requires profile_runtime and/or profile_memory
        execute_notebook(
            nb_in, "out.ipynb", save_profiling_data=save_profiling_data_value
        )

    execute_notebook(
        nb_in,
        "out.ipynb",
        save_profiling_data=save_profiling_data_value,
        profile_runtime=True,
    )
    outfile = save_profiling_output
    assert Path(outfile).is_file()
    with open(outfile, "r") as f:
        read_lines = f.readlines()
        lines = []
        # In case of Windows there are
        # extra '\n' characters, so skipping those
        for line in read_lines:
            if line.strip():
                lines.append(line)
        assert len(lines) == 2, "File should have 2 lines"
        data = lines[1].strip().split(",")
        assert len(data) == 3, "File should have 3 columns"
        assert data[2] == "NA", "memory should be NA (since not profiled)"

    execute_notebook(
        nb_in,
        "out.ipynb",
        save_profiling_data=save_profiling_data_value,
        profile_runtime=True,
        profile_memory=True,
    )
    outfile = save_profiling_output
    with open(outfile, "r") as f:
        read_lines = f.readlines()
        lines = []
        # In case of Windows there are
        # extra '\n' characters, so skipping those
        for line in read_lines:
            if line.strip():
                lines.append(line)
        assert len(lines) == 2, "File should have 2 lines"
        data = lines[1].strip().split(",")
        assert len(data) == 3, "File should have 3 columns"
        assert data[2] != "NA", "memory is profiled and should not be NA"


@pytest.mark.parametrize(
    "saved_path, exception_msg, exception_type",
    [
        (
            "abc",
            "Invalid save_profiling_data(.*), path must end with .csv",
            ValueError,
        ),
        (
            "./abc",
            "Invalid save_profiling_data(.*), path must end with .csv",
            ValueError,
        ),
        (
            "./abc.py",
            "Invalid save_profiling_data(.*), path must end with .csv",
            ValueError,
        ),
        (
            "./abc.txt",
            "Invalid save_profiling_data(.*), path must end with .csv",
            ValueError,
        ),
        (
            "./abc.png",
            "Invalid save_profiling_data(.*), path must end with .csv",
            ValueError,
        ),
        (
            "./abc",
            "Invalid save_profiling_data(.*), path must end with .csv",
            ValueError,
        ),
        (
            float(123.0),
            "Invalid save_profiling_data(.*). "
            "Please provide either a boolean or a string",
            ValueError,
        ),
        (
            {"test": "test123"},
            "Invalid save_profiling_data(.*). "
            "Please provide either a boolean or a string",
            ValueError,
        ),
        (
            set(["test", "test123"]),
            "Invalid save_profiling_data(.*). "
            "Please provide either a boolean or a string",
            ValueError,
        ),
    ],
)
def test_execute_notebook_invalid_save_profiling_data(
    saved_path, exception_msg, exception_type
):
    nb_in = _make_nb(["1 + 1"])
    with pytest.raises(exception_type, match=exception_msg):
        execute_notebook(
            nb_in,
            "out.ipynb",
            save_profiling_data=saved_path,
            profile_runtime=True,
        )


# seems like we have some shared state, we're getting a plot even though the
# code is only printing the current working directory, the problem is in the line:
# self._shell._get_output()
# this happens if we remove the pip install "matplotlib<3.7" "numpy<1.24.2" from ci.yml
def test_execute_notebook_different_cwd(tmp_empty):
    # setup
    run_dir = Path("run_dir")
    run_dir.mkdir()
    nb_in = _make_nb(["import os; print(os.getcwd())"])
    nb_fname = f"{run_dir}/out.ipynb"

    # test using nb_node
    cell = execute_notebook(nb_in, nb_fname, cwd=run_dir).cells[-1]
    cell_cwd = cell["outputs"][-1]["text"].strip()
    assert cell_cwd == str(run_dir.absolute())

    # test using path to nb
    cell = execute_notebook(nb_fname, nb_fname, cwd=run_dir).cells[-1]
    cell_cwd = cell["outputs"][-1]["text"].strip()
    assert cell_cwd == str(run_dir.absolute())
