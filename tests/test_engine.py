from unittest.mock import Mock

import pytest
import papermill as pm


@pytest.mark.parametrize('engine', [
    'debug',
    'debuglater',
    'profiling',
])
def test_sample_notebook(tmp_assets, engine):
    pm.execute_notebook('sample.ipynb', 'out.ipynb', engine_name=engine)


def test_crashing_notebook(tmp_assets, monkeypatch, capsys):
    mock = Mock(side_effect=['print(f"x is {x}")', 'quit'])

    with monkeypatch.context() as m:
        m.setattr('builtins.input', mock)

        with pytest.raises(SystemExit):
            pm.execute_notebook('crash.ipynb',
                                'out.ipynb',
                                engine_name='debug')

    out, _ = capsys.readouterr()

    assert "x is 1\n" in out
