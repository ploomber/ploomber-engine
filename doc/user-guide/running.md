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
---

# Running notebooks

````{versionadded} 0.0.18
```{eval-rst}
``execute_notebook`` was introduced in ``0.0.18``. If using an older version, check out ``PloomberClient`` docs :ref:`../../api/api.html#execute-notebook`
```
````

`ploomber-engine` allows you to run Jupyter notebooks programmatically. It is a drop-in replacement for `papermill.execute_notebook` with enhanced support for debugging, profiling, experiment tracking and more!

## Example

Install dependencies:

```{code-cell} ipython3
:tags: [hide-output]

%pip install ploomber-engine --quiet
```

Download sample notebook:

```{code-cell} ipython3
:tags: [hide-output]

%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/examples/display.ipynb \
    --output running-demo.ipynb
```

Run the notebook and store the executed version:

```{admonition} Command-line equivalent
:class: dropdown

`ploomber-engine nb.ipynb output.ipynb`
```

```{code-cell} ipython3
:tags: [hide-output]

from ploomber_engine import execute_notebook

nb = execute_notebook("running-demo.ipynb", output_path="output.ipynb")
```

The function returns a notebook object (same contents as stored in `output_path`):

```{code-cell} ipython3
type(nb)
```

Skip storing the output notebook:

```{code-cell} ipython3
:tags: [hide-output]

_ = execute_notebook("running-demo.ipynb", output_path=None)
```

## Logging `print` statements

If your notebook contains `print` statements and want to see them in the current session:

```{admonition} Command-line equivalent
:class: dropdown

`ploomber-engine nb.ipynb output.ipynb --log-output`
```

```{code-cell} ipython3
_ = execute_notebook(
    "running-demo.ipynb",
    output_path="output.ipynb",
    log_output=True,
    progress_bar=False,
)
```

## Parametrizing notebooks

```{versionadded} 0.0.19
```

You can parametrize notebooks and switch their values at runtime. By default values, are injected in the first cell. However, if you want to provide default values, you may add a cell like this:

```python
# parameters
x = 1
y = 2
```

If you do so, the passed parameters will be injected in a cell below to replace the default values. If you prefer, you can tag the cell with default values as `"parameters"` (*à la* papermill) instead of adding the `# parameters` comment.

Let's download a sample notebook that prints `x + y`:

```{code-cell} ipython3
:tags: [hide-output]

%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/examples/sum.ipynb \
    --output sum-demo.ipynb
```

If we don't pass parameters, it uses the default values:

```{code-cell} ipython3
_ = execute_notebook(
    "sum-demo.ipynb", output_path=None, log_output=True, progress_bar=False
)
```

Passing `parameters` overrides the defaults:


```{admonition} Command-line equivalent
:class: dropdown

`ploomber-engine nb.ipynb output.ipynb -p x 21 -p y 21`
```

```{code-cell} ipython3
_ = execute_notebook(
    "sum-demo.ipynb",
    output_path=None,
    log_output=True,
    parameters=dict(x=21, y=21),
    progress_bar=False,
)
```

## Removing cells

```{versionadded} 0.0.21
```

```{admonition} Command-line equivalent
:class: dropdown

`ploomber-engine nb.ipynb output.ipynb --remove-tagged-cells remove`
```

If there are cells you want to remove before execution, tag them and use `remove_tagged_cells`. [This sample notebook](https://github.com/ploomber/ploomber-engine/blob/main/examples/remove.ipynb) contains one cell that will fail, if executed; however, the cell contains the tag `"remove"`, so let's remove it before execution:

```{code-cell} ipython3
:tags: [hide-output]

%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/examples/remove.ipynb \
    --output running-remove.ipynb
```

```{code-cell} ipython3
:tags: [hide-output]

_ = execute_notebook(
    "running-remove.ipynb",
    output_path=None,
    remove_tagged_cells="remove",
)
```

You may also pass multiple tags to `remove_tagged_cells` in a list:
`["remove", "also-remove"]`.
