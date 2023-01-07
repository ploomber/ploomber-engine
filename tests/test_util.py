from conftest import _make_nb_obj

import pytest
from ploomber_engine._util import parametrize_notebook, add_debuglater_cells


@pytest.mark.parametrize(
    "nb, params_idx, cells_total",
    [
        [_make_nb_obj(["1 + 1"]), 0, 2],
        [_make_nb_obj([("code", "1 + 1", {"tags": ["parameters"]})]), 1, 2],
        [_make_nb_obj(["21 + 21", ("code", "1 + 1", {"tags": ["parameters"]})]), 2, 3],
        [_make_nb_obj(["# parameters\n1 + 2"]), 1, 2],
        [_make_nb_obj(["1 + 1", "# parameters\n1 + 2"]), 2, 3],
        [_make_nb_obj(["#PARAMETERS\n1 + 2"]), 1, 2],
        [_make_nb_obj(["1 + 1", "#PARAMETERS\n1 + 2"]), 2, 3],
    ],
)
def test_parametrize_notebook(tmp_empty, nb, params_idx, cells_total):
    params = dict(x=1, y=2)
    out = parametrize_notebook(nb, params)
    assert out.cells[params_idx].source == "# Injected parameters\nx = 1\ny = 2\n"
    assert out.cells[params_idx].metadata.tags == ["injected-parameters"]
    assert len(out.cells) == cells_total


@pytest.mark.parametrize(
    "nb, params_idx, cells_total",
    [
        [
            _make_nb_obj(
                [
                    ("code", "1 + 1", {"tags": ["parameters"]}),
                    ("code", "x = 10\ny = 10", {"tags": ["injected-parameters"]}),
                ]
            ),
            1,
            2,
        ],
        [
            _make_nb_obj(
                [
                    ("code", "1 + 1", {"tags": ["parameters"]}),
                    "1 + 2",
                    "1 + 2",
                    ("code", "x = 10\ny = 10", {"tags": ["injected-parameters"]}),
                ]
            ),
            3,
            4,
        ],
    ],
)
def test_parametrize_notebook_with_existing_parameters(
    tmp_empty, nb, params_idx, cells_total
):
    params = dict(x=1, y=2)
    out = parametrize_notebook(nb, params)
    assert out.cells[params_idx].source == "# Injected parameters\nx = 1\ny = 2\n"
    assert len(out.cells) == cells_total


def test_parametrized_notebook_with_comment_and_tag(tmp_empty):
    nb = _make_nb_obj(
        [
            ("code", "x = 0\ny = 0", {"tags": ["parameters"]}),
            "#PARAMETERS\nx = 10\ny = 20",
        ]
    )

    params = dict(x=1, y=2)
    out = parametrize_notebook(nb, params)
    assert out.cells[2].source == "# Injected parameters\nx = 1\ny = 2\n"
    assert len(out.cells) == 3


@pytest.mark.parametrize(
    "nb, idx, cells_total",
    [
        [_make_nb_obj(["1 + 1", "21 + 21"]), 0, 3],
        [_make_nb_obj([]), 0, 1],
        [
            _make_nb_obj(
                [("code", "1 + 1", {"tags": ["injected-debuglater"]}), "2 + 2"]
            ),
            0,
            2,
        ],
        [
            _make_nb_obj(
                ["1 + 2", ("code", "1 + 1", {"tags": ["injected-debuglater"]}), "2 + 2"]
            ),
            1,
            3,
        ],
    ],
    ids=[
        "simple",
        "empty",
        "existing-cell",
        "existing-cell-middle",
    ],
)
def test_add_debuglater_cells(nb, idx, cells_total):
    add_debuglater_cells(nb)

    assert "from debuglater import patch_ipython\n" in nb.cells[idx].source
    assert "\npatch_ipython()\n" in nb.cells[idx].source
    assert nb.cells[idx].metadata.tags == ["injected-debuglater"]
    assert len(nb.cells) == cells_total
