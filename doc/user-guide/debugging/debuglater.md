---
jupytext:
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
html_meta:
  "description lang=en": "How to use the debuglater package."
  "keywords": "python,jupyter,notebooks,ploomber"
  "property=og:locale": "en_US"
---

# Debug later

```{versionadded} 0.0.19

```

ploomber-engine uses our [debuglater](https://github.com/ploomber/debuglater) package to serialize the error traceback so you can start a debugging session after your notebook crashes.

So, for example, if you're running notebooks in production or remote servers, you can debug after they crash. Likewise, you can use the generated file to debug on a different machine (assuming the environment is the same) without having access to the source code.

+++

## Example

Install requirements:

```{code-cell} ipython3
%pip install ploomber-engine --quiet
```

Download [sample notebook](https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/debuglater.ipynb):

```{code-cell} ipython3
%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/debuglater.ipynb --output debuglater-demo.ipynb
```

Run the notebook with `debug_later=True` option (note that this notebook crashes on purpose):

```{code-cell} ipython3
:tags: [raises-exception, hide-output]

from ploomber_engine import execute_notebook

execute_notebook("debuglater-demo.ipynb", "output.ipynb", debug_later=True)
```

```{admonition} Command-line equivalent
:class: dropdown

`ploomber-engine nb.ipynb output.ipynb --debug-later`
```

The above command generated an `output.dump` file which is the serialized traceback:

```{code-cell} ipython3
%%sh
ls *.dump
```

We can use the `dltr` command (from our [debuglater](https://github.com/ploomber/debuglater) package) to start a debugging session:

```sh
dltr output.dump
```

```{tip}
By default, only built-in data structures are serialized, for other types, only their string representation is stored. If you want to serialize every data type: `pip install 'debuglater[all]'`
```
