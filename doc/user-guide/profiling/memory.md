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

# Memory usage

With ploomber-engine you can profile Jupyter notebook's memory usage. Unlike papermill, which isn't capable of doing it.

```{note}
You can download this tutorial in Jupyter notebook format by clicking on the icon in the upper right corner.
```

```{important}
Memory profiling requires ploomber-engine `0.0.14` or higher
```

Install requirements:

```{code-cell} ipython3
%pip install ploomber-engine psutil matplotlib --quiet
```

Import the `memory_profile` function:

```{code-cell} ipython3
from ploomber_engine.profiling import memory_profile
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

Let's run the profiling function (which also runs the notebook):

```{code-cell} ipython3
memory_profile("notebook.ipynb", "output.ipynb")
```

Display the plot:

```{code-cell} ipython3
from IPython.display import Image

Image(filename="notebook-memory-usage.png")
```

We can see that after running cells 1-2, there isn't any important increment in memory usage. However, when finishing execution of cell 3, we see a bump of 1MB, since we allocated the array there. Cell 4 doesn't increase memory usage, since it only contains a call to `time.sleep`, but cell 5 has a 10MB bump since we allocated the second (larger) array.

If you want to look at the executed notebook, it's available at `output.ipynb`.
