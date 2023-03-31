---
jupytext:
  notebook_metadata_filter: myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
myst:
  html_meta:
    "description lang=en": "A quick-start guide for ploomber-engine, a toolbox for  executing jupyter notebooks"
    "keywords": "python,jupyter,notebooks,ploomber"
    "property=og:locale": "en_US"
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

## Run notebook

```{tip}
There is a command-line interface available. Run: `ploomber-engine --help` to learn more.
```

Let's download a [sample notebook.](https://github.com/ploomber/ploomber-engine/blob/main/examples/display.ipynb)

```{code-cell} ipython3
%%bash
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/examples/display.ipynb --output nb.ipynb
```

```{code-cell} ipython3
:tags: [hide-output]

from ploomber_engine import execute_notebook

_ = execute_notebook("nb.ipynb", "output.ipynb", parameters=dict(x=1, y=2))
```

## Log print statements

```{code-cell} ipython3
_ = execute_notebook("nb.ipynb", "output.ipynb", log_output=True, progress_bar=False)
```

## Plot cell's runtime

```{note}
Runtime profiling requires extra dependencies: `pip install matplotlib`
```

```{code-cell} ipython3
_ = execute_notebook(
    "nb.ipynb", "output.ipynb", profile_runtime=True, progress_bar=False
)
```

```{code-cell} ipython3
ls output-*
```

## Plot cell's memory usage

```{note}
Memory profiling requires extra dependencies: `pip install matplotlib psutil`
```

```{code-cell} ipython3
_ = execute_notebook(
    "nb.ipynb", "output.ipynb", profile_memory=True, progress_bar=False
)
```

```{code-cell} ipython3
ls output-*
```
