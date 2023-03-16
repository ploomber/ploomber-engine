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

# Memory usage


```{versionadded} 0.0.18
`execute_notebook`
```

With ploomber-engine you can profile Jupyter notebook's memory usage. Unlike papermill, which isn't capable of doing it.

Install requirements:

```{code-cell} ipython3
%pip install ploomber-engine psutil matplotlib --quiet
```

## Example

Import the `execute_notebook` function:

```{code-cell} ipython3
from ploomber_engine import execute_notebook
```

We'll now programmatically create a sample notebook and stored it in `notebook.ipynb`. Note that it creates a 1MB numpy array on cell 3 and one 10MB numpy array on cell 5.

```{code-cell} ipython3
import nbformat

nb = nbformat.v4.new_notebook()
sleep = "time.sleep(0.5)"
cells = [
    # cell 1
    "import numpy as np; import time",
    # cell 2
    sleep,
    # cell 3
    "x = np.ones(131072, dtype='float64')",
    # cell 4
    sleep,
    # cell 5
    "y = np.ones(131072*10, dtype='float64')",
    # cell 6
    sleep,
]

nb.cells = [nbformat.v4.new_code_cell(cell) for cell in cells]

nbformat.write(nb, "notebook.ipynb")
```

Let's execute the notebook with `profile_memory=True`

```{admonition} Command-line equivalent
:class: dropdown

`ploomber-engine notebook.ipynb output.ipynb --profile-memory`
```

```{code-cell} ipython3
_ = execute_notebook("notebook.ipynb", "output.ipynb", profile_memory=True)
```

We can see that after running cells 1-2, there isn't any important increment in memory usage. However, when finishing execution of cell 3, we see a bump of 1MB, since we allocated the array there. Cell 4 doesn't increase memory usage, since it only contains a call to `time.sleep`, but cell 5 has a 10MB bump since we allocated the second (larger) array.

If you want to look at the executed notebook, it's available at `output.ipynb`.

+++

## Customizing the plot

You might customize the plot by calling the `plot_memory_usage` function and passing the output notebook, the returned object is a `matplotlib.Axes`.

```{code-cell} ipython3
%%capture

from ploomber_engine.profiling import plot_memory_usage

nb = execute_notebook("notebook.ipynb", "output.ipynb", profile_memory=True)
```

```{code-cell} ipython3
ax = plot_memory_usage(nb)
_ = ax.set_title("My custom title")
```

## Saving profiling data

You can save the profiling data by setting `save_profiling_data=True`.

```{code-cell} ipython3
%%capture
_ = execute_notebook(
    "notebook.ipynb", "output.ipynb",
    profile_memory=True, save_profiling_data=True
)
```

```{code-cell} ipython3
import pandas as pd
pd.read_csv("output-profiling-data.csv")
```
