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



def test_if_memory_leak_within_notebook(path_notebook):
    """
    epsilon is an amount of memory that is negligeable with respect
    to the data declared on the test,
    """
    mem_usage_start = get_current_memory_usage()

    # memory_usages.append(get_current_memory_usage())
    client = PloomberClient.from_path(path_notebook)


    new_variables = dict(a=[1 for _ in range(10**7)], b=[1 for _ in range(10**7)])
    # injecting new variables in namespace
    namespace = client.get_namespace(
        namespace=new_variables
    )
    # executing notebook with execute method

    nb_node = client.execute()

    mem_usage_before_deletion = get_current_memory_usage()

    del nb_node
    del namespace
    del client
    del new_variables

    mem_usage_end = get_current_memory_usage()


    # mem_rate_consumption represents the rate of memory consumtion after the beginning of the test
    # until the deletion of  the created variables within the test (which should be negligeable in case 
    # of absence of memory leak) , and the memory usage from the beginning of the test until the 
    # creation of all the (memory heavy) variables.
    mem_rate_consumption = (mem_usage_end-mem_usage_start)/(mem_usage_before_deletion-mem_usage_start)
    print(mem_rate_consumption)

    
