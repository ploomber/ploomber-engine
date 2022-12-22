import sys

from nbclient.exceptions import CellExecutionError, CellTimeoutError
from papermill.clientwrap import PapermillNotebookClient


from ploomber_engine.client import PloomberNotebookClient


class PapermillPloomberNotebookClient(PapermillNotebookClient, PloomberNotebookClient):
    """A papermill client that uses our custom notebook client"""

    # NOTE: adapted from papermill's source code
    def papermill_execute_cells(self):
        """
        This function replaces cell execution with it's own wrapper.
        We are doing this for the following reasons:
        1. Notebooks will stop executing when they encounter a failure but not
           raise a `CellException`. This allows us to save the notebook with
           the traceback even though a `CellExecutionError` was encountered.
        2. We want to write the notebook as cells are executed. We inject our
           logic for that here.
        3. We want to include timing and execution status information with the
           metadata of each cell.
        """
        # Execute each cell and update the output in real time.
        for index, cell in enumerate(self.nb.cells):
            try:
                self.nb_man.cell_start(cell, index)
                self.execute_cell(cell, index)
            except CellExecutionError as ex:
                self.nb_man.cell_exception(
                    self.nb.cells[index], cell_index=index, exception=ex
                )
                break
            except CellTimeoutError as e:
                # this will exit execution gracefully upon debugging, but
                # it will also cause the notebook to abort execution after
                # an "input" cell
                print(e)
                sys.exit(1)
            finally:
                self.nb_man.cell_complete(self.nb.cells[index], cell_index=index)
