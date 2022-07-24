from unittest.mock import ANY
import nbformat
from ploomber_engine.ipython import PloomberShell, PloomberClient


def test_captures_display_data():
    shell = PloomberShell()

    code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
"""

    shell.run_cell(code)

    output = shell._get_output()

    assert output == [
        {
            'output_type': 'execute_result',
            'metadata': {},
            'data': {
                'text/plain': ANY,
            },
            'execution_count': None
        },
        {
            'output_type': 'display_data',
            'metadata': {},
            'data': {
                'text/plain': ANY,
                'image/png': ANY
            }
        },
    ]


def test_client_captures_display_data():
    nb = nbformat.v4.new_notebook()
    cell = nbformat.v4.new_code_cell(source="""
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
""")
    nb.cells.append(cell)

    client = PloomberClient(nb)

    result = client.execute_cell(cell,
                                 cell_index=0,
                                 execution_count=0,
                                 store_history=False)

    assert len(result) == 2


def test_client_captures_all_outputs():
    nb = nbformat.v4.new_notebook()
    cell = nbformat.v4.new_code_cell(source="""
import matplotlib.pyplot as plt
print('hello')
plt.plot([1, 2, 3])
'bye'
""")
    nb.cells.append(cell)

    client = PloomberClient(nb)

    result = client.execute_cell(cell,
                                 cell_index=0,
                                 execution_count=0,
                                 store_history=False)

    assert len(result) == 3


def test_client_captures_tracebacks():
    nb = nbformat.v4.new_notebook()
    cell = nbformat.v4.new_code_cell(source="""
raise ValueError('something went wrong')
""")
    nb.cells.append(cell)

    client = PloomberClient(nb)

    result = client.execute_cell(cell,
                                 cell_index=0,
                                 execution_count=0,
                                 store_history=False)

    assert len(result) == 1
    assert 'something went wrong' in result[0]['text']


def test_client_execute(tmp_assets):
    nb = nbformat.read(tmp_assets / 'different-outputs.ipynb',
                       as_version=nbformat.NO_CONVERT)
    client = PloomberClient(nb)
    nb_out = client.execute()

    # this will complain if the notebook is not well formatted
    nbformat.write(nb_out, 'out.ipynb', version=nbformat.NO_CONVERT)

    assert nb_out.cells[0]['outputs'] == [{
        'output_type': 'execute_result',
        'metadata': {},
        'data': {
            'text/plain': '3'
        },
        'execution_count': None
    }]

    assert nb_out.cells[1]['outputs'] == [{
        'output_type': 'execute_result',
        'metadata': {},
        'data': {
            'text/plain': 'None'
        },
        'execution_count': None
    }, {
        'output_type': 'stream',
        'name': 'stdout',
        'text': 'stuff\n'
    }]

    assert nb_out.cells[2]['outputs'] == [{
        'output_type': 'execute_result',
        'metadata': {},
        'data': {
            'text/plain': '2'
        },
        'execution_count': None
    }, {
        'output_type': 'stream',
        'name': 'stdout',
        'text': 'a\nb\n'
    }]

    assert nb_out.cells[3]['outputs'] == [{
        'output_type': 'execute_result',
        'metadata': {},
        'data': {
            'text/plain': ANY,
        },
        'execution_count': None
    }, {
        'output_type': 'display_data',
        'metadata': {},
        'data': {
            'text/plain': ANY,
            'image/png': ANY,
        }
    }]


def test_client_gets_clean_shell():
    nb1 = nbformat.v4.new_notebook()
    nb1.cells.append(nbformat.v4.new_code_cell(source='some_variable = 1'))
    PloomberClient(nb1).execute()

    nb2 = nbformat.v4.new_notebook()
    nb2.cells.append(nbformat.v4.new_code_cell(source='print(some_variable)'))
    PloomberClient(nb2).execute()

    assert ("name 'some_variable' is not defined"
            in nb2.cells[0].outputs[0]['text'])


def test_output_to_sys_stderr():
    nb = nbformat.v4.new_notebook()
    cell = nbformat.v4.new_code_cell(source="""
import sys
print('error', file=sys.stderr)
""")
    nb.cells.append(cell)

    out = PloomberClient(nb).execute()

    assert out.cells[0]['outputs'] == [{
        'output_type': 'execute_result',
        'metadata': {},
        'data': {
            'text/plain': 'None'
        },
        'execution_count': None
    }, {
        'output_type': 'stream',
        'name': 'stderr',
        'text': 'error\n'
    }]
