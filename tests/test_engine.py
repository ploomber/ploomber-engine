import papermill as pm


def test_sample_notebook(tmp_assets):
    pm.execute_notebook('sample.ipynb',
                        'out.ipynb',
                        engine_name='ploomber-engine')


def test_crashing_notebook(tmp_assets):
    pm.execute_notebook('crash.ipynb',
                        'out.ipynb',
                        engine_name='ploomber-engine')
