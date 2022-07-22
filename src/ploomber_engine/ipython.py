import sys
import contextlib
from io import StringIO
import nbformat

from IPython.core.interactiveshell import InteractiveShell
from IPython.core.displaypub import DisplayPublisher
from IPython.core.displayhook import DisplayHook


def _make_stream_output(out):
    return nbformat.v4.new_output(output_type='stream', text=str(out))


class CustomDisplayHook(DisplayHook):
    """
    Hook when receiving plain text messages. For example, when the last line
    in the cell has a string/number or anything that doesn't have a rich
    representation
    """

    def __call__(self, result=None):
        out = nbformat.v4.new_output(output_type='execute_result',
                                     data={'text/plain': str(result)})
        self.shell._current_output.append(out)


class CustomDisplayPublisher(DisplayPublisher):
    """
    Hook then receiving display data messages. For example, when the cell
    creates a matplotlib plot or anything that has a rich representation
    (not plain text)
    """

    def publish(self, data, metadata=None, **kwargs):
        out = nbformat.v4.new_output(output_type='display_data', data=data)
        self.shell._current_output.append(out)


class PloomberShell(InteractiveShell):
    """
    A subclass of IPython's InteractiveShell to gather all the output
    produced by a code cell
    """

    def __init__(self):
        super().__init__(display_pub_class=CustomDisplayPublisher,
                         displayhook_class=CustomDisplayHook)
        InteractiveShell._instance = self
        self.enable_matplotlib('inline')
        # all channels send the output here
        self._current_output = []

    # this is an abstract method in InteractiveShell
    def enable_gui(self, gui=None):
        pass

    # to execute cells, call run_cell

    # custom methods

    def _get_output(self):
        current_output = self._current_output.copy()
        self._current_output.clear()
        return current_output

    def enable_matplotlib(self, gui=None):
        # if we don't put this, we'll lose some display_data messages. found
        # about this trick via fastai/execnb
        from matplotlib_inline.backend_inline import configure_inline_support
        configure_inline_support.current_backend = 'unset'
        return super().enable_matplotlib(gui)


class PloomberClient():
    """
    Partially implements nbclient.client's interface and uses PloomberShell
    to execute cells.
    """

    def __init__(self, nb):
        self._nb = nb
        self._shell = PloomberShell()

    def execute_cell(self, cell, cell_index, execution_count, store_history):
        # results are published in different places. Here we grab all of them
        # and return them

        with patch_sys_std_out_err() as (stdout_stream, stderr_stream):
            _ = self._shell.run_cell(cell['source'])
            stdout = stdout_stream.getvalue()
            stderr = stderr_stream.getvalue()

        output = self._shell._get_output()

        if stdout:
            output.append(_make_stream_output(stdout))

        if stderr:
            output.append(_make_stream_output(stderr))

        # add outputs to the cell object
        cell.outputs = output

        return output

    def execute(self):
        for index, cell in enumerate(self._nb.cells):
            self.execute_cell(cell,
                              cell_index=index,
                              execution_count=index,
                              store_history=False)

        return self._nb


@contextlib.contextmanager
def patch_sys_std_out_err():
    """
    """
    # keep a reference to the system ones
    stdout, stderr = sys.stdout, sys.stderr

    # patch them
    stdout_stream, stderr_stream = StringIO(), StringIO()
    sys.stdout, sys.stderr = stdout_stream, stderr_stream

    try:
        yield stdout_stream, stderr_stream
    finally:
        # revert
        sys.stdout, sys.stderr = stdout, stderr
