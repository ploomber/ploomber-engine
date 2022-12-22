from pathlib import Path
from unittest.mock import Mock

import pytest
import papermill as pm
import nbformat


@pytest.mark.parametrize(
    "engine",
    [
        "debug",
        "debuglater",
        "profiling",
        "embedded",
    ],
)
def test_sample_notebook(tmp_assets, engine):
    pm.execute_notebook("sample.ipynb", "out.ipynb", engine_name=engine)


def test_crashing_notebook(tmp_assets, monkeypatch, capsys):
    mock = Mock(side_effect=['print(f"x is {x}")', "quit"])

    with monkeypatch.context() as m:
        m.setattr("builtins.input", mock)

        with pytest.raises(SystemExit):
            pm.execute_notebook("crash.ipynb", "out.ipynb", engine_name="debug")

    out, _ = capsys.readouterr()

    assert "x is 1\n" in out


def test_managed_client(tmp_empty):
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(source="1 + 1"))
    Path("nb.ipynb").write_text(nbformat.v4.writes(nb))

    pm.execute_notebook(
        "nb.ipynb",
        "out.ipynb",
        # the embedded engine uses the managed client
        engine_name="embedded",
        kernel_name="python3",
    )

    out = nbformat.v4.reads(Path("out.ipynb").read_text())

    assert out.cells[0]["outputs"] == [
        {
            "data": {"text/plain": "2"},
            "execution_count": 1,
            "metadata": {},
            "output_type": "execute_result",
        }
    ]
