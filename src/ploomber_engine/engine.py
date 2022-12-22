import warnings

import nbformat

from papermill.engines import Engine
from papermill.utils import merge_kwargs, remove_args
from papermill.log import logger
from papermill.clientwrap import PapermillNotebookClient

from ploomber_engine.papermill import PapermillPloomberNotebookClient
from ploomber_engine.ipython import PloomberManagedClient
from ploomber_engine._telemetry import telemetry


class DebugEngine(Engine):
    """An engine that starts a debugging session once the notebook fails"""

    @classmethod
    @telemetry.log_call("debug-execute-managed-nb")
    def execute_managed_notebook(
        cls,
        nb_man,
        kernel_name,
        log_output=False,
        stdout_file=None,
        stderr_file=None,
        start_timeout=60,
        execution_timeout=None,
        **kwargs,
    ):
        # Exclude parameters that named differently downstream
        safe_kwargs = remove_args(["timeout", "startup_timeout"], **kwargs)

        # Nicely handle preprocessor arguments prioritizing values set by
        # engine
        final_kwargs = merge_kwargs(
            safe_kwargs,
            timeout=execution_timeout if execution_timeout else kwargs.get("timeout"),
            startup_timeout=start_timeout,
            kernel_name=kernel_name,
            log=logger,
            log_output=log_output,
            stdout_file=stdout_file,
            stderr_file=stderr_file,
        )

        cell = nbformat.versions[nb_man.nb["nbformat"]].new_code_cell(
            source="%pdb on", metadata=dict(tags=[], papermill=dict())
        )
        nb_man.nb.cells.insert(0, cell)

        #  use our Papermill client
        return PapermillPloomberNotebookClient(nb_man, **final_kwargs).execute()


class DebugLaterEngine(Engine):
    """An engine that stores the traceback object for later debugging"""

    @classmethod
    @telemetry.log_call("debuglater-execute-managed-nb")
    def execute_managed_notebook(
        cls,
        nb_man,
        kernel_name,
        log_output=False,
        stdout_file=None,
        stderr_file=None,
        start_timeout=60,
        execution_timeout=None,
        **kwargs,
    ):
        # Exclude parameters that named differently downstream
        safe_kwargs = remove_args(["timeout", "startup_timeout"], **kwargs)

        # Nicely handle preprocessor arguments prioritizing values set by
        # engine
        final_kwargs = merge_kwargs(
            safe_kwargs,
            timeout=execution_timeout if execution_timeout else kwargs.get("timeout"),
            startup_timeout=start_timeout,
            kernel_name=kernel_name,
            log=logger,
            log_output=log_output,
            stdout_file=stdout_file,
            stderr_file=stderr_file,
        )

        path_to_dump = kwargs.get("path_to_dump")

        if path_to_dump is None:
            warnings.warn(
                "Did not pass path_to_dump to "
                "DebugLaterEngine.execute_managed_notebook, "
                "the default value will be used"
            )
            source = """
from debuglater import patch_ipython
patch_ipython()
"""
        else:
            source = f"""
from debuglater import patch_ipython
patch_ipython({path_to_dump!r})
"""

        cell = nbformat.versions[nb_man.nb["nbformat"]].new_code_cell(
            source=source, metadata=dict(tags=[], papermill=dict())
        )
        nb_man.nb.cells.insert(0, cell)

        return PapermillNotebookClient(nb_man, **final_kwargs).execute()


class ProfilingEngine(Engine):
    """
    An engine that runs the notebook in the current process and can be used
    for resource usage profiling
    """

    @classmethod
    @telemetry.log_call("embedded-execute-managed-nb")
    def execute_managed_notebook(
        cls,
        nb_man,
        kernel_name,
        log_output=False,
        stdout_file=None,
        stderr_file=None,
        start_timeout=60,
        execution_timeout=None,
        **kwargs,
    ):

        return PloomberManagedClient(nb_man).execute()
