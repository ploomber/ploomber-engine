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

# Running notebooks

```{versionadded} 0.0.18
`execute_notebook` was introduced in `0.0.18`. If using an older version, check out [`PloomberClient` docs](../api/api.html#ploomberclient)
```

`ploomber-engine` allows you to run Jupyter notebooks programmatically. It is a drop-in replacement for `papermill.execute_notebook` with enhanced support for debugging, profiling, experiment tracking and more!

## Example

Install dependencies:

```{code-cell} ipython3
%pip install ploomber-engine --quiet
```

Download sample notebook:

```{code-cell} ipython3
%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/examples/display.ipynb --output running-demo.ipynb
```

Run the notebook and store the executed version:

```{admonition} Command-line equivalent
:class: dropdown

`ploomber-engine nb.ipynb output.ipynb`
```

```{code-cell} ipython3
from ploomber_engine import execute_notebook

nb = execute_notebook("running-demo.ipynb",
                      output_path="output.ipynb")
```

The function returns a notebook object (same contents as stored in `output_path`):

```{code-cell} ipython3
type(nb)
```

Skip storing the output notebook:

```{code-cell} ipython3
_ = execute_notebook("running-demo.ipynb",
                     output_path=None)
```

## Logging `print` statements

If your notebook contains `print` statements and want to see them in the current session:

```{admonition} Command-line equivalent
:class: dropdown

`ploomber-engine nb.ipynb output.ipynb --log-output`
```

```{code-cell} ipython3
_ = execute_notebook("running-demo.ipynb",
                     output_path="output.ipynb",
                     log_output=True)
```
