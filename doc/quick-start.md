---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
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

# Quick Start

[ploomber-engine](https://github.com/ploomber/ploomber-engine) is a toolbox for executing notebooks.

It provides enhanced capabilities such as debugging, profiling and experiment tracking.

## Installation

```bash
pip install -U ploomber-engine
```

or

```bash
conda install ploomber-engine -c conda-forge
```
## Example

Here's a quick example showing how to run a notebook.

First, let's create notebook object (Note: you can also load them from .ipynb files):

```{code-cell} python
from ploomber_engine.ipython import PloomberClient
import nbformat

nb = nbformat.v4.new_notebook()
cell = nbformat.v4.new_code_cell("1+1")
nb.cells = [cell]
nb
```

Start client and execute the notebook:

```{code-cell} python
client = PloomberClient(nb)
out = client.execute()
```

```{code-cell} python
out
```

Inspect outputs:

```{code-cell} python
out.cells[0]['outputs'][0]['data']
```

Store the notebook:

```python
nbformat.write(out, "output.ipynb")
```
