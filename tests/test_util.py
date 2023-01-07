from conftest import _make_nb

import pytest
from ploomber_engine._util import parametrize_notebook


@pytest.mark.parametrize(
    "nb, params_idx",
    [
        [_make_nb(["1 + 1"]), 0],
        [_make_nb([("code", "1 + 1", {"tags": ["parameters"]})]), 1],
        [_make_nb(["21 + 21", ("code", "1 + 1", {"tags": ["parameters"]})]), 2],
        [_make_nb(["# parameters\n1 + 2"]), 1],
        [_make_nb(["1 + 1", "# parameters\n1 + 2"]), 2],
        [_make_nb(["#PARAMETERS\n1 + 2"]), 1],
        [_make_nb(["1 + 1", "#PARAMETERS\n1 + 2"]), 2],
    ],
)
def test_parametrize_notebook(tmp_empty, nb, params_idx):
    params = dict(x=1, y=2)
    out = parametrize_notebook(nb, params)
    assert out.cells[params_idx].source == "# Injected parameters\nx = 1\ny = 2\n"
