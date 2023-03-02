---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Cell runtime

```{versionadded} 0.0.18
[`execute_notebook`](../../api/api.html#execute-notebook)
```

Install requirements:

```{code-cell} ipython3
%pip install ploomber-engine matplotlib --quiet
```

## Example

Let's create a sample notebook with a few calls to `time.sleep`:

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

Let's execute the notebook with `profile_runtime=True`

```{admonition} Command-line equivalent
:class: dropdown

`ploomber-engine notebook.ipynb output.ipynb --profile-runtime`
```

```{code-cell} ipython3
from ploomber_engine import execute_notebook

_ = execute_notebook("notebook.ipynb", "output", profile_runtime=True)
```

## Customize plot

You might customize the plot by calling the `plot_cell_runtime` function and passing the output notebook, the returned object is a `matplotlib.Axes`.

```{code-cell} ipython3
from ploomber_engine.profiling import plot_cell_runtime

nb = execute_notebook("notebook.ipynb", "output.ipynb")
```

```{code-cell} ipython3
ax = plot_cell_runtime(nb)
_ = ax.set_title("My custom title")
```

## Saving profiling data

You can save the profiling data by setting `save_profiling_data=True`.

```{code-cell} ipython3
%%capture
_ = execute_notebook(
    "notebook.ipynb", "output.ipynb",
    profile_runtime=True, save_profiling_data=True
)
```

```{code-cell} ipython3
import pandas as pd
pd.read_csv("output-profiling-data.csv")
```

Note: you must set `profile_memory=True` to get non-NA data 
saved for the memory usage.
