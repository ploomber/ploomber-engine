import pytest
from copy import copy
from unittest.mock import ANY
import nbformat
from ploomber_engine.ipython import PloomberShell, PloomberClient
from ploomber_engine import ipython


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


def test_reports_exceptions():
    nb = nbformat.v4.new_notebook()
    nb.cells.append(
        nbformat.v4.new_code_cell(source="""
def crash():
    raise ValueError("something went wrong")

crash()
"""))

    with pytest.raises(ValueError) as excinfo:
        PloomberClient(nb).execute()

    assert str(excinfo.value) == 'something went wrong'
    assert 'something went wrong' in nb.cells[0].outputs[0]['text']


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

    assert nb_out.cells[1]['outputs'] == [
        {
            'output_type': 'stream',
            'name': 'stdout',
            'text': 'stuff\n'
        },
    ]

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

    with pytest.raises(NameError):
        PloomberClient(nb2).execute()


def test_output_to_sys_stderr():
    nb = nbformat.v4.new_notebook()
    cell = nbformat.v4.new_code_cell(source="""
import sys
print('error', file=sys.stderr)
""")
    nb.cells.append(cell)

    out = PloomberClient(nb).execute()

    assert out.cells[0]['outputs'] == [
        {
            'output_type': 'stream',
            'name': 'stderr',
            'text': 'error\n'
        },
    ]


def test_displays_html_repr():
    nb = nbformat.v4.new_notebook()
    cell = nbformat.v4.new_code_cell(source="""
import pandas as pd
pd.DataFrame({'x': [1, 2, 3]})
""")
    nb.cells.append(cell)

    out = PloomberClient(nb).execute()

    assert out.cells[0]['outputs'] == [{
        'output_type': 'execute_result',
        'metadata': {},
        'data': {
            'text/plain': '   x\n0  1\n1  2\n2  3',
            'text/html': ANY,
        },
        'execution_count': None
    }]


def test_matplotlib_is_optional(monkeypatch):
    # raise ModuleNotFoundError when importing matplotlib
    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == 'matplotlib':
            raise ModuleNotFoundError
        else:
            return __import__(name,
                              globals=globals,
                              locals=locals,
                              fromlist=fromlist,
                              level=level)

    builtins = copy(ipython.__builtins__)
    builtins['__import__'] = mock_import

    # path builtins in ipython modfule
    monkeypatch.setattr(ipython, '__builtins__', builtins)

    # should not raise ModuleNotFoundError
    assert PloomberShell()


def test_adds_execution_count():
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell())
    nb.cells.append(nbformat.v4.new_code_cell())
    out = PloomberClient(nb).execute()

    assert [c['execution_count'] for c in out.cells] == [1, 2]


def test_keeps_same_std_out_err_order_as_jupyter():
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell())
    nb.cells.append(nbformat.v4.new_code_cell())
    out = PloomberClient(nb).execute()

    assert [c['execution_count'] for c in out.cells] == [1, 2]


def test_ignores_non_code_cells():
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_markdown_cell('this is markdown'))
    nb.cells.append(nbformat.v4.new_code_cell('1 + 1'))
    out = PloomberClient(nb).execute()

    assert out.cells[1] == {
        'id':
        ANY,
        'cell_type':
        'code',
        'metadata': {},
        'execution_count':
        1,
        'source':
        '1 + 1',
        'outputs': [{
            'output_type': 'execute_result',
            'metadata': {},
            'data': {
                'text/plain': '2'
            },
            'execution_count': None
        }]
    }


@pytest.mark.parametrize('source, expected', [
    [
        "from IPython.display import HTML; HTML('<br>some html</br>')",
        {
            'output_type': 'execute_result',
            'metadata': {},
            'data': {
                'text/plain': '<IPython.core.display.HTML object>',
                'text/html': '<br>some html</br>'
            },
            'execution_count': None
        },
    ],
    [
        "from IPython.display import Markdown; Markdown('# some md')",
        {
            'output_type': 'execute_result',
            'metadata': {},
            'data': {
                'text/plain': '<IPython.core.display.Markdown object>',
                'text/markdown': '# some md'
            },
            'execution_count': None
        },
    ],
    [
        "from IPython.display import JSON; JSON(dict(a=1))",
        {
            'output_type': 'execute_result',
            'metadata': {
                'application/json': {
                    'expanded': False,
                    'root': 'root'
                }
            },
            'data': {
                'text/plain': '<IPython.core.display.JSON object>',
                'application/json': {
                    'a': 1
                }
            },
            'execution_count': None
        },
    ],
    [
        "from IPython.display import Javascript; Javascript('let x = 1')",
        {
            'output_type': 'execute_result',
            'metadata': {},
            'data': {
                'text/plain': '<IPython.core.display.Javascript object>',
                'application/javascript': 'let x = 1'
            },
            'execution_count': None
        },
    ],
    [
        "from IPython.display import Latex; Latex('$ x = 1$')",
        {
            'output_type': 'execute_result',
            'metadata': {},
            'data': {
                'text/plain': '<IPython.core.display.Latex object>',
                'text/latex': '$ x = 1$'
            },
            'execution_count': None
        },
    ],
],
                         ids=[
                             'html',
                             'md',
                             'json',
                             'js',
                             'latex',
                         ])
def test_display_formats(source, expected):
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(source=source))
    out = PloomberClient(nb).execute()

    assert out.cells[0]['outputs'][0] == expected
