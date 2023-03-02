import os
import sys
import contextlib
from io import StringIO
import itertools
from datetime import datetime
from pathlib import Path

import parso
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.displaypub import DisplayPublisher
from IPython.core.displayhook import DisplayHook
from IPython import get_ipython

# NOTE: we're not using tqdm.auto (which renders better-looking bars in Jupyter)
# because it is incompatible with PloomberShell due to the CustomDisplayHook and
# CustomDisplayPublisher. That's also the reason why we are not using the "rich"
# package, since it doesn't have a way to turn off Jupyter integration
from tqdm import tqdm

from ploomber_engine._util import (
    recursive_update,
    parametrize_notebook,
    add_debuglater_cells,
)


def is_notebook():
    return type(get_ipython()).__name__ == "ZMQInteractiveShell"


_IS_NOTEBOOK = is_notebook()


def _make_stream_output(out, name):
    return nbformat.v4.new_output(output_type="stream", text=str(out), name=name)


def _process_stdout(out, result):
    if not result.success:
        exception = out[-2]
        # ignore newlines
        out = out[:-2:2]

        cells = []

        if out:
            cells.append(
                nbformat.v4.new_output(
                    output_type="stream", text="\n".join(out), name="stdout"
                )
            )

        cells.append(
            nbformat.v4.new_output(
                "error",
                ename=type(result.error_in_exec).__name__,
                evalue=str(result.error_in_exec),
                traceback=exception.splitlines(),
            )
        )
        return cells

    else:
        return [
            nbformat.v4.new_output(
                output_type="stream", text="".join(out), name="stdout"
            )
        ]


class CustomDisplayHook(DisplayHook):
    """
    Hook when receiving text messages (plain text, HTML, etc)
    """

    def __call__(self, result=None):
        if result is not None:
            data, metadata = self.shell.display_formatter.format(result)
            out = nbformat.v4.new_output(
                output_type="execute_result", data=data, metadata=metadata
            )
            self.shell._current_output.append(out)


class CustomDisplayPublisher(DisplayPublisher):
    """
    Hook then receiving display data messages. For example, when the cell
    creates a matplotlib plot or anything that has a rich representation
    (not plain text)
    """

    def publish(self, data, metadata=None, **kwargs):
        out = nbformat.v4.new_output(output_type="display_data", data=data)
        self.shell._current_output.append(out)


class PloomberShell(InteractiveShell):
    """
    A subclass of IPython's InteractiveShell to gather all the output
    produced by a code cell

    Notes
    -----
    This is intended to be used as a singleton, so either call
    `.clear_instance()` when you're done or use it as a context manager
    """

    def __init__(self):
        super().__init__(
            display_pub_class=CustomDisplayPublisher,
            displayhook_class=CustomDisplayHook,
        )
        # no assigning this produces some weird behavior when calling
        # .clear_instance()
        InteractiveShell._instance = self
        PloomberShell._instance = self

        try:
            self.enable_matplotlib("inline")
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

        configure_inline_support.current_backend = "unset"
        return super().enable_matplotlib(gui)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.clear_instance()


def _remove_cells_with_tags(nb, tags):
    if not tags:
        return nb

    if isinstance(tags, str):
        tags = {tags}

    cells_ = []

    for cell in nb.cells:
        if not (set(tags) & set(cell.metadata.get("tags", set()))):
            cells_.append(cell)

    nb.cells = cells_

    return nb


class PloomberClient:
    """PloomberClient executes Jupyter notebooks

    Parameters
    ----------
    nb
        Notebook object

    display_output : bool, default=False
        If True, it prints the same output the notebook prints.

    progress_bar : bool, default=True
        Display a progress bar.

    debug_later : bool or str, default=False
        Serialize Python traceback for later debugging. If True, it stores
        the traceback at ``jupyter.dump``, if a string, it stores the traceback
        there.

    remove_tagged_cells : str or list, default=None
        Cells with any of the passed tag(s) will be removed from the notebook before
        execution.

    cwd : str or Path, default='.'
        Working directory to use when executing the notebook

    Notes
    -----
    .. versionchanged:: 0.0.23
        Added ``cwd`` argument.

    .. versionchanged:: 0.0.21
        Added ``remove_tagged_cells`` arguments.


    .. versionchanged:: 0.0.19
        Added ``progress_bar`` and ``debug_later`` arguments.

    Examples
    --------

    Execute notebook:

    >>> from ploomber_engine.ipython import PloomberClient
    >>> import nbformat
    >>> nb = nbformat.v4.new_notebook()
    >>> cell = nbformat.v4.new_code_cell("1+1")
    >>> nb.cells = [cell]
    >>> client = PloomberClient(nb)
    >>> out = client.execute()
    >>> out.cells[0]['outputs'][0]['data']
    {'text/plain': '2'}

    Remove cells tagged "remove" before execution:

    >>> from ploomber_engine.ipython import PloomberClient
    >>> import nbformat
    >>> nb = nbformat.v4.new_notebook()
    >>> nb.cells = [nbformat.v4.new_code_cell("1+1"),
    ...             nbformat.v4.new_code_cell("1/0",
    ...             metadata=dict(tags=["remove"]))]
    >>> client = PloomberClient(nb, remove_tagged_cells="remove")
    >>> out = client.execute()
    >>> out.cells[0]['outputs'][0]['data']
    {'text/plain': '2'}


    Remove cells tagged with any of the passed tags before execution:

    >>> from ploomber_engine.ipython import PloomberClient
    >>> import nbformat
    >>> nb = nbformat.v4.new_notebook()
    >>> nb.cells = [nbformat.v4.new_code_cell("1+1"),
    ...             nbformat.v4.new_code_cell("1/0",
    ...             metadata=dict(tags=["remove"])),
    ...             nbformat.v4.new_code_cell("2/0",
    ...             metadata=dict(tags=["also-remove"]))
    ...             ]
    >>> client = PloomberClient(nb, remove_tagged_cells=["remove", "also-remove"])
    >>> out = client.execute()
    >>> out.cells[0]['outputs'][0]['data']
    {'text/plain': '2'}
    """

    def __init__(
        self,
        nb,
        display_stdout=False,
        progress_bar=True,
        debug_later=False,
        remove_tagged_cells=None,
        cwd=".",
    ):
        self._nb = _remove_cells_with_tags(nb, remove_tagged_cells)
        self._shell = None
        self._display_stdout = display_stdout
        self._debug_later = debug_later
        self._cwd = cwd

        # NOTE: this env var is only used internally so the doctests don't show
        # the progress bar
        var = os.environ.get("_PLOOMBER_ENGINE_PROGRESS_BAR")

        if var is not None:
            self._progress_bar = var == "true"
        else:
            self._progress_bar = progress_bar

    @classmethod
    def from_path(
        cls,
        path,
        display_stdout=False,
        progress_bar=True,
        debug_later=False,
        remove_tagged_cells=None,
        cwd=".",
    ):
        """Initialize client from a path to a notebook

        Parameters
        ----------
        path : str
            Path to the ``.ipynb`` file

        display_output : bool, default=False
            If True, it prints the same output the notebook prints.

        progress_bar : bool, default=True
            Display a progress bar.

        debug_later : bool or str, default=False
            Serialize Python traceback for later debugging. If True, it stores
            the traceback at ``jupyter.dump``, if a string, it stores the traceback
            there.

        remove_tagged_cells : str or list, default=None
            Cells with any of the passed tag(s) will be removed from the notebook before
            execution.

        cwd : str or Path, default='.'
            Working directory to use when executing the notebook

        Notes
        -----
        .. versionchanged:: 0.0.23
            Added ``cwd`` argument.

        .. versionchanged:: 0.0.21
            Added ``remove_tagged_cells`` arguments.

        .. versionchanged:: 0.0.19
            Added ``progress_bar`` and ``debug_later`` arguments.

        .. versionchanged:: 0.0.18
            Added ``display_stdout`` argument.

        Examples
        --------
        >>> from ploomber_engine.ipython import PloomberClient
        >>> client = PloomberClient.from_path("nb.ipynb")
        >>> out = client.execute()

        """
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        return cls(
            nb,
            display_stdout=display_stdout,
            progress_bar=progress_bar,
            debug_later=debug_later,
            remove_tagged_cells=remove_tagged_cells,
        )

    def execute_cell(self, cell, cell_index, execution_count, store_history):
        if self._shell is None:
            raise RuntimeError("A shell has not been initialized")

        # results are published in different places. Here we grab all of them
        # and return them
        with patch_sys_std_out_err() as (stdout_stream, stderr_stream):
            self.hook_cell_pre(cell)
            result = self._shell.run_cell(cell["source"])
            self.hook_cell_post(cell)
            stdout = stdout_stream.get_separated_values()
            stderr = stderr_stream.getvalue()

        output = []

        if stdout:
            if self._display_stdout:
                print("".join([line.strip() for line in stdout]))

            output.extend(_process_stdout(stdout, result=result))

        if stderr:
            output.append(_make_stream_output(stderr, name="stderr"))

        # order is important, this should be the last one to match
        # what jupyter does
        out = self._shell._get_output()

        # NOTE: is there any situation where we receive more than one?
        for current in out:
            if current["output_type"] == "execute_result":
                current["execution_count"] = execution_count

        output = output + out

        # add outputs to the cell object
        cell.outputs = output
        cell.execution_count = execution_count

        if not result.success:
            result.raise_error()

        return output

    def execute(self, parameters=None):
        """Execute the notebook

        Returns
        -------
        nb
            Notebook object

        Notes
        -----
        .. versionchanged:: 0.0.19
            Added ``parameters`` argument
        """
        original = InteractiveShell._instance

        if parameters is not None:
            parametrize_notebook(self._nb, parameters=parameters)

        if self._debug_later:
            add_debuglater_cells(
                self._nb,
                path_to_dump=self._debug_later
                if isinstance(self._debug_later, (str, Path))
                else None,
            )

        with self:
            self._execute()

        if original is not None:
            # restore original instance
            InteractiveShell._instance = original

            # restore inline matplotlib
            try:
                from matplotlib_inline.backend_inline import configure_inline_support
            except ModuleNotFoundError:
                pass
            else:
                configure_inline_support(original, "inline")
                original.run_line_magic("matplotlib", "inline")

        return self._nb

    def get_namespace(self, namespace=None):
        """Run the notebook and return all the output variables

        Parameters
        ----------
        namespace: dict, default=None
            The initial namespace. It can be used to set initial values prior to
            execution.

        Examples
        --------
        Execute notebook and get the output variables:

        >>> from ploomber_engine.ipython import PloomberClient
        >>> import nbformat
        >>> nb = nbformat.v4.new_notebook()
        >>> first = nbformat.v4.new_code_cell("x = 1")
        >>> second = nbformat.v4.new_code_cell("y = 41")
        >>> third = nbformat.v4.new_code_cell("z = x + y")
        >>> nb.cells = [first, second, third]
        >>> client = PloomberClient(nb)
        >>> ns = client.get_namespace()
        >>> ns["x"]
        1
        >>> ns["y"]
        41
        >>> ns["z"]
        42

        Notes
        -----
        .. versionchanged:: 0.0.22
            Added ``namespace`` arguments.
        """
        with self:
            existing = set(self._shell.user_ns)

            namespace = namespace or {}
            self._shell.user_ns.update(namespace)

            self._execute()
            namespace = {
                k: v for k, v in self._shell.user_ns.items() if k not in existing
            }

        return namespace

    def get_definitions(self):
        """
        Returns class and function definitions without running the notebook

        Examples
        --------
        >>> from ploomber_engine.ipython import PloomberClient
        >>> import nbformat
        >>> nb = nbformat.v4.new_notebook()
        >>> first = nbformat.v4.new_code_cell("def add(x, y): return x + y")
        >>> second = nbformat.v4.new_code_cell("def multiply(x, y): return x * y")
        >>> nb.cells = [first, second]
        >>> client = PloomberClient(nb)
        >>> defs = client.get_definitions()
        >>> add = defs["add"]
        >>> add(1, 41)
        42
        >>> multiply = defs["multiply"]
        >>> multiply(2, 21)
        42
        """
        source = "\n".join([c.source for c in self._nb.cells if c.cell_type == "code"])
        module = parso.parse(source)

        defs = [
            def_.get_code()
            for def_ in itertools.chain(module.iter_classdefs(), module.iter_funcdefs())
        ]

        defs_source = "\n".join(defs)

        with self:
            existing = set(self._shell.user_ns)
            self._shell.run_cell(defs_source)
            defs = {k: v for k, v in self._shell.user_ns.items() if k not in existing}

        return defs

    def _execute(self):
        """
        Internal method to execute a notebook, assumes the shell has been
        initialized
        """
        execution_count = 1

        # the progress bar will not resize if running on a notebook, so we fix its size
        kwargs = dict(ncols=80) if _IS_NOTEBOOK else dict()
        iterator = (
            self._nb.cells if not self._progress_bar else tqdm(self._nb.cells, **kwargs)
        )

        # make sure that the current working directory is in the sys.path
        # in case the user has local modules
        with add_to_sys_path(self._cwd):
            for index, cell in enumerate(iterator):
                if cell.cell_type == "code":
                    if self._progress_bar:
                        iterator.set_description(f"Executing cell: {execution_count}")

                    self.execute_cell(
                        cell,
                        cell_index=index,
                        execution_count=execution_count,
                        store_history=False,
                    )
                    execution_count += 1

        return self._nb

    def __enter__(self):
        """Initialize shell"""
        if self._shell is None:
            self._shell = PloomberShell()
            return self
        else:
            raise RuntimeError("A shell is already active")

    def __exit__(self, exc_type, exc_value, traceback):
        """Clear shell"""
        self._shell.clear_instance()
        self._shell = None

    def hook_cell_pre(self, cell):
        metadata = {"ploomber": {"timestamp_start": datetime.now().timestamp()}}
        recursive_update(cell.metadata, metadata)

    def hook_cell_post(self, cell):
        metadata = {"ploomber": {"timestamp_end": datetime.now().timestamp()}}
        recursive_update(cell.metadata, metadata)


class PloomberManagedClient(PloomberClient):
    def __init__(self, nb_man):
        super().__init__(nb_man.nb)
        self._nb_man = nb_man

    def _execute(self):
        execution_count = 1

        # make sure that the current working directory is in the sys.path
        # in case the user has local modules
        with add_to_sys_path(self._cwd):
            for index, cell in enumerate(self._nb.cells):
                if cell.cell_type == "code":
                    try:
                        self._nb_man.cell_start(cell, index)
                        self.execute_cell(
                            cell,
                            cell_index=index,
                            execution_count=execution_count,
                            store_history=False,
                        )
                    except Exception as ex:
                        self._nb_man.cell_exception(
                            self._nb.cells[index], cell_index=index, exception=ex
                        )
                        break
                    finally:
                        self._nb_man.cell_complete(
                            self._nb.cells[index], cell_index=index
                        )
                        execution_count += 1

        return self._nb


class IO(StringIO):
    def __init__(self, initial_value="", newline="\n"):
        super().__init__(initial_value=initial_value, newline=newline)
        self._values = []

    def write(self, s):
        self._values.append(s)
        super().write(s)

    def get_separated_values(self):
        return self._values[:]


@contextlib.contextmanager
def patch_sys_std_out_err():
    """Path sys.{stout, sterr} to capture output"""
    # keep a reference to the system ones
    stdout, stderr = sys.stdout, sys.stderr

    # patch them
    stdout_stream, stderr_stream = IO(), StringIO()
    sys.stdout, sys.stderr = stdout_stream, stderr_stream

    try:
        yield stdout_stream, stderr_stream
    finally:
        # revert
        sys.stdout, sys.stderr = stdout, stderr


@contextlib.contextmanager
def add_to_sys_path(path, chdir=True):
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
