from unittest.mock import Mock

import pytest
import papermill as pm


def test_sample_notebook(tmp_assets):
    pm.execute_notebook('sample.ipynb', 'out.ipynb', engine_name='debug')


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


# def test_profiling_engine(tmp_assets):
#     pm.execute_notebook('different-outputs.ipynb', 'pm.ipynb')
#     pm.execute_notebook('different-outputs.ipynb',
#                         'profiling.ipynb',
#                         engine_name='profiling')

#     from IPython import embed
#     embed()
