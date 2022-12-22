"""
This module contains our customizatiosn to nbclient and papermill.
"""
__version__ = "0.0.17"

import typing as t

# NOTE: fully initialize papermill here to prevent circular import
try:
    import papermill  # noqa
except ModuleNotFoundError:
    # optional dependency, so do not throw an error if missing
    pass

from jupyter_client import KernelManager
from nbformat import NotebookNode


# NOTE: adapted from nbclient.client
# NOTE: do we need this? I don't think is documented, so we should remove it
def execute(
    nb: NotebookNode,
    cwd: t.Optional[str] = None,
    km: t.Optional[KernelManager] = None,
    **kwargs: t.Any,
) -> NotebookNode:
    """Execute a notebook's code, updating outputs within the notebook object.
    This is a convenient wrapper around NotebookClient. It returns the
    modified notebook object.

    Parameters
    ----------
    nb : NotebookNode
      The notebook object to be executed
    cwd : str, optional
      If supplied, the kernel will run in this directory
    km : AsyncKernelManager, optional
      If supplied, the specified kernel manager will be used for code
      execution.
    kwargs :
      Any other options for NotebookClient, e.g. timeout, kernel_name
    """
    from ploomber_engine.client import PloomberNotebookClient

    resources = {}
    if cwd is not None:
        resources["metadata"] = {"path": cwd}
    return PloomberNotebookClient(nb=nb, resources=resources, km=km, **kwargs).execute()
