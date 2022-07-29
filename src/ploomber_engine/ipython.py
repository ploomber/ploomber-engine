import os
import sys
import contextlib
from io import StringIO
import nbformat

from IPython.core.interactiveshell import InteractiveShell
from IPython.core.displaypub import DisplayPublisher
from IPython.core.displayhook import DisplayHook


def _make_stream_output(out, name):
    return nbformat.v4.new_output(output_type='stream',
                                  text=str(out),
                                  name=name)


class CustomDisplayHook(DisplayHook):
    """
    Hook when receiving text messages (plain text, HTML, etc)
    """

    def __call__(self, result=None):
        if result is not None:
            data, metadata = self.shell.display_formatter.format(result)
            out = nbformat.v4.new_output(output_type='execute_result',
                                         data=data,
                                         metadata=metadata)
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

        try:
            self.enable_matplotlib('inline')
        except ModuleNotFoundError:
            pass

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
            result = self._shell.run_cell(cell['source'])
            stdout = stdout_stream.getvalue()
            stderr = stderr_stream.getvalue()

        output = self._shell._get_output()

        if stdout:
            output.append(_make_stream_output(stdout, name='stdout'))

        if stderr:
            output.append(_make_stream_output(stderr, name='stderr'))

        # add outputs to the cell object
        cell.outputs = output
        cell.execution_count = execution_count

        if not result.success:
            result.raise_error()

        return output

    def execute(self):
        execution_count = 1

        # make sure that the current working directory is in the sys.path
        # in case the user has local modules
        with add_to_sys_path('.'):
            for index, cell in enumerate(self._nb.cells):
                if cell.cell_type == 'code':
                    self.execute_cell(cell,
                                      cell_index=index,
                                      execution_count=execution_count,
                                      store_history=False)
                    execution_count += 1

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


@contextlib.contextmanager
def add_to_sys_path(path, chdir=False):
    """
    Add directory to sys.path, optionally making it the working directory
    temporarily
    """
    cwd_old = os.getcwd()

    if path is not None:
        path = os.path.abspath(path)
        sys.path.insert(0, path)

        if chdir:
            os.chdir(path)

    try:
        yield
    finally:
        if path is not None:
            sys.path.remove(path)
            os.chdir(cwd_old)
