---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Cell runtime

```{important}
Cell runtime profiling requires ploomber-engine `0.0.14` or higher
```

Install requirements:

```{code-cell} ipython3
%pip install ploomber-engine matplotlib --quiet
```

Let's create a simple notebook that calls `time.sleep`:

```{code-cell} ipython3
import nbformat

nb = nbformat.v4.new_notebook()
cells = [
    "import time",
    "time.sleep(1)",
    "time.sleep(2)",
    "time.sleep(1)",
    "time.sleep(0.5)",
]
nb.cells = [nbformat.v4.new_code_cell(cell) for cell in cells]
nbformat.write(nb, "notebook.ipynb")
```

Run the notebook with `PloomberClient`:

```{code-cell} ipython3
from ploomber_engine.ipython import PloomberClient
```

```{code-cell} ipython3
client = PloomberClient.from_path("notebook.ipynb")
out = client.execute()
```

Utility function to compute the runtime from each cell:

```{code-cell} ipython3
def compute_runtime(cell):
    start = cell.metadata.ploomber.timestamp_start
    end = cell.metadata.ploomber.timestamp_end
    return end - start
```

Compute runtime for each cell:

```{code-cell} ipython3
cell_runtime = [compute_runtime(c) for c in out.cells]
cell_indexes = list(range(1, len(cell_runtime) + 1))
```

Plot the results:

```{code-cell} ipython3
import matplotlib.pyplot as plt
```

```{code-cell} ipython3
ax = plt.gca()
ax.plot(cell_indexes, cell_runtime, marker="o")
ax.set_xticks(cell_indexes)
ax.set_title("Cell runtime")
ax.set_xlabel("Cell index")
ax.set_ylabel("Runtime (seconds)")
ax.grid()
```
