import pytest
import nbformat
from pathlib import Path
from ploomber_engine.ipython import PloomberClient
import copy


def get_current_memory_usage():
    """helper to get free and used expressed in GB"""
    import psutil

    memory_usage = psutil.virtual_memory().used

    memory_usage = float(psutil._common.bytes2human(memory_usage)[:-1])

    return memory_usage


@pytest.mark.memory
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


def copy_shell(exit_method):
    def new_exit(self, exc_type, exc_value, traceback):
        self.user_ns_copy = self._shell.user_ns.keys()
        self.user_ns_before_deletion = copy.deepcopy(tuple(self.user_ns_copy))
        exit_method(self, exc_type, exc_value, traceback)
        self.user_ns_after_deletion = copy.deepcopy(tuple(self.user_ns_copy))

    return new_exit


def test_if_memory_leak_within_notebook(path_notebook):
    """
    epsilon is an amount of memory that is negligeable with respect
    to the data declared on the test,
    """
    mem_usage_start = get_current_memory_usage()

    # memory_usages.append(get_current_memory_usage())
    client = PloomberClient.from_path(path_notebook)

    PloomberClient.__exit__ = copy_shell(PloomberClient.__exit__)

    new_variables = dict(a=[1 for _ in range(10**7)], b=[1 for _ in range(10**7)])
    # injecting new variables in namespace
    namespace = client.get_namespace(namespace=new_variables)
    # executing notebook with execute method

    nb_node = client.execute()

    mem_usage_before_deletion = get_current_memory_usage()

    deleted_objets = set(client.user_ns_before_deletion).difference(
        set(client.user_ns_after_deletion)
    )

    assert deleted_objets == {"array1", "array", "arrays"}

    del nb_node
    del namespace
    del client
    del new_variables

    mem_usage_end = get_current_memory_usage()

    # mem_rate_consumption represents the rate of memory consumtion after the
    # beginning until the deletion of  the created variables within the test
    # (which should be negligeable in case of absence of memory leak) , and
    # the memory usage from the beginning of the test until the
    # creation of all the (memory heavy) variables.
    mem_rate_consumption = (mem_usage_end - mem_usage_start) / (
        mem_usage_before_deletion - mem_usage_start
    )
    print(mem_rate_consumption)
