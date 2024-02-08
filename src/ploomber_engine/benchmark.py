"""
A module to benchmark notebooks in a directory.
"""

from pathlib import Path

import click

from ploomber_engine import execute_notebook
from ploomber_engine.profiling import _compute_runtime


class CellResult:
    """Represents the result of executing a cell."""

    def __init__(self, index, source, runtime, path):
        self.index = index
        self.source = source
        self.runtime = runtime
        self.path = path

    @classmethod
    def from_cell(cls, index, cell, path):
        return cls(
            index=index,
            source="".join(cell.source),
            runtime=_compute_runtime(cell),
            path=path,
        )

    def to_dict(self):
        return dict(
            index=self.index,
            source=self.source,
            runtime=self.runtime,
            path=self.path,
        )


class NotebookResult:
    """Represents the result of executing a notebook."""

    def __init__(self, path, nb=None, exc=None) -> None:
        self.path = path
        self.nb = nb
        self.exc = exc

        if nb:
            self._cell_results = [
                CellResult.from_cell(index=index, cell=cell, path=path)
                for index, cell in enumerate(nb.cells)
                if cell.cell_type == "code"
            ]
        else:
            self._cell_results = []

        self._total_runtime = sum(r.runtime for r in self._cell_results)
        self._n_code_cells = len(self._cell_results)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r})"

    def cell_results_to_dict(self):
        return [r.to_dict() for r in self._cell_results]

    def to_dict(self):
        return dict(
            path=self.path,
            exc=self.exc,
            total_runtime=self._total_runtime,
            n_code_cells=self._n_code_cells,
        )


def benchmark_notebooks_in_directory(path_to_notebooks):
    """Benchmark notebooks in a directory.

    Parameters
    ----------
    path_to_notebooks
        Path to a directory containing notebooks
    """
    import pandas as pd

    results = []
    notebooks = [nb for nb in Path(path_to_notebooks).glob("*.ipynb")]

    for path in notebooks:
        try:
            click.echo(f"Executed {path}")
            nb = execute_notebook(path, output_path=None)
            res = NotebookResult(path=path, nb=nb)
        except Exception as e:
            click.echo(f"Failed to execute {path}")
            res = NotebookResult(path=path, exc=e)

        results.append(res)

    data_notebooks = pd.DataFrame.from_records([r.to_dict() for r in results])
    nested = [r.cell_results_to_dict() for r in results]
    data_cells = pd.DataFrame.from_records([r for r in nested for r in r])

    return data_notebooks, data_cells


@click.command()
@click.argument("path_to_notebooks", type=click.Path(exists=True))
def cli(path_to_notebooks):
    """Benchmark notebooks in a directory."""
    data_notebooks, data_cells = benchmark_notebooks_in_directory(path_to_notebooks)
    data_notebooks.to_csv("notebooks.csv", index=False)
    data_cells.to_csv("cells.csv", index=False)
    click.echo("Notebooks runtime saved to notebooks.csv")
    click.echo("Cells runtime saved to cells.csv")


if __name__ == "__main__":
    cli()
