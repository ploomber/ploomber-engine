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

# Unit testing

`ploomber-engine` allows you to extract function or class definitions to write unit tests.

## Example

Install dependencies:

```{code-cell} ipython3
%pip install ploomber-engine --quiet
```

Download sample notebook:

```{code-cell} ipython3
%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/examples/nb.ipynb --output testing-demo.ipynb
```

Extract the definitions from the notebook (this won't run the notebook):

```{code-cell} ipython3
from ploomber_engine.ipython import PloomberClient

client = PloomberClient.from_path("testing-demo.ipynb")
definitions = client.get_definitions()
definitions
```

Get the `add` and `multiply` function defined in the notebook:

```{code-cell} ipython3
add = definitions["add"]
multiply = definitions["multiply"]
```

Test the functions:

```{code-cell} ipython3
assert add(1, 41) == 42
assert add(50, 50) == 100
```

```{code-cell} ipython3
assert multiply(2, 21) == 42
assert multiply(0, 10) == 0
```

```{note}
[testbook](https://github.com/nteract/testbook) is another library that helps writing unit tests for Jupyter notebooks. However, testbook has a big limitation since it needs to serialize objects defined in a notebook, which makes debugging tests a lot more difficult. With `ploomber-engine` this isn't the case.
```
