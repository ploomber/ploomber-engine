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

# Testing existing outputs

```{note}
This is an experimental feature, please share your feedback on [Slack!](https://ploomber.io/community/). This feature requires ploomber-engine `0.0.16` or higher
```


With `ploomber-engine` , you can re-run your notebooks and ensure that their outputs still match.

## Example (test passes)

Let's create a simple notebook that prints a few numbers:

```{code-cell} ipython3
import nbformat

nb = nbformat.v4.new_notebook()

cells = [
    "print(1)",
    "print(2)",
]

nb.cells = [nbformat.v4.new_code_cell(cell) for cell in cells]
nbformat.write(nb, "notebook.ipynb")
```

Let's run the notebook, and re-write the original file:

```{code-cell} ipython3
from ploomber_engine.ipython import PloomberClient


client = PloomberClient.from_path("notebook.ipynb")
out = client.execute()
nbformat.write(out, "notebook.ipynb")
```

Run the function to test the notebook (it won't raise any errors since the notebook will produce the same outputs):

```{code-cell} ipython3
from ploomber_engine.testing import test_notebook
```

```{code-cell} ipython3
test_notebook("notebook.ipynb")
```

## Test failure: output mismatch

Let's load the notebook and modify the source code, but keep the outputs the same:

```{code-cell} ipython3
nb = nbformat.read("notebook.ipynb", as_version=nbformat.NO_CONVERT)

# this was previously: print(1)
nb.cells[0].source = "print(100)"

# store the notebook
nbformat.write(nb, "notebook.ipynb")
```

```{code-cell} ipython3
:tags: ["raises-exception"]
test_notebook("notebook.ipynb")
```

## Test failure: different num of outputs

`test_notebook` also checks that the number of outputs for each cell match.


Let's modify the notebook so the first cell produces two outputs:

```{code-cell} ipython3
nb = nbformat.read("notebook.ipynb", as_version=nbformat.NO_CONVERT)

nb.cells[0].source = "print(100); 200"

# store the notebook
nbformat.write(nb, "notebook.ipynb")
```

```{code-cell} ipython3
:tags: ["raises-exception"]
test_notebook("notebook.ipynb")
```

## Limitations

Currently, plots are ignored since they'll produce different data even if the plots look the same.
