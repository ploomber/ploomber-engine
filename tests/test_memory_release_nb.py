import pytest
import nbformat
from pathlib import Path
from ploomber_engine.ipython import PloomberClient


def get_current_memory_usage(and_print=True):
    """helper to get free and used expressed in GB"""
    import psutil

    memory_usage = {
        "free": psutil.virtual_memory().free,
        "used": psutil.virtual_memory().used,
    }

    memory_usage = {
        key: float(psutil._common.bytes2human(val)[:-1])
        for key, val in memory_usage.items()
    }

    if and_print:
        for key, val in memory_usage.items():
            print(key, val)
    return memory_usage


@pytest.fixture
def path_notebook(tmpdir):
    nb = nbformat.v4.new_notebook()
    cells = [
        "array = [1 for i in range(10**7)]",
        "array1 = array",
        "arrays = [array,array1]",
    ]
    nb.cells = [nbformat.v4.new_code_cell(cell) for cell in cells]

    path_notebook = Path(tmpdir).joinpath("noteboook.ipynb")
    nbformat.write(nb, path_notebook)
    return path_notebook


@pytest.mark.parametrize(
    "epsilon,",
    [
        0.01,
    ],
)
def test_if_memory_leak_within_notebook(path_notebook, epsilon):
    """
    epsilon is an amount of memory that is negligeable with respect
    to the data declared on the test,
    """
    memory_usage_start = get_current_memory_usage()

    for _ in range(2):
        # memory_usages.append(get_current_memory_usage())
        memory_usage_begining_loop = get_current_memory_usage()
        client = PloomberClient.from_path(path_notebook)

        # injecting new variables in namespace
        namespace = client.get_namespace(
            namespace=dict(a=[1 for _ in range(10**7)], b=[1 for _ in range(10**7)])
        )
        memory_usage_with_namespace_in_mem = get_current_memory_usage()

        # executing notebook with execute method

        nb_node = client.execute()

        del nb_node
        memory_usage_after_exec_method = get_current_memory_usage()

        del namespace
        del client

    memory_usage_after_namespace_deletion = get_current_memory_usage()

    assert (
        memory_usage_after_namespace_deletion["free"] - memory_usage_start["free"]
    ) < epsilon
