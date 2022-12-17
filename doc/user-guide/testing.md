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

# Testing notebooks

## Testing output variables

ploomber-engine allows you to test output cells from your notebooks.

Install dependencies:

```{code-cell} ipython3
%pip install ploomber-engine --quiet
```

Download sample notebook:

```{code-cell} ipython3
%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/examples/nb.ipynb --output testing-demo.ipynb
```

Run the notebook and get the output variables:

```{code-cell} ipython3
from ploomber_engine.ipython import PloomberClient

client = PloomberClient.from_path("testing-demo.ipynb")
namespace = client.get_namespace()
namespace
```

Now we can check if the variables in the notebook have the values we expected:

```{code-cell} ipython3
assert namespace['a'] == 42
assert namespace['b'] == 200
```

```{code-cell} ipython3
namespace['df']
```

## Testing functions/classes

ploomber-engine allows you to extract function or class definitions to write unit tests.

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
add = definitions['add']
multiply = definitions['multiply']
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

## `pytest` integration

You can use ploomber-engine to test your notebooks with [pytest](https://docs.pytest.org/en/7.2.x/), here's a full example:

```python
# test_notebook.py

from pathlib import Path

import pytest
from ploomber_engine.ipython import PloomberClient


@pytest.fixture
def ns():
    client = PloomberClient.from_path(Path(__file__).parent / 'nb.ipynb')
    return client.get_namespace()


def test_add(ns):
    add = ns['add']
    assert add(1, 2) == 3


def test_multiply(ns):
    multiply = ns['multiply']
    assert multiply(2, 2) == 4


def test_notebook_results(ns):
    assert ns['a'] == 42
    assert ns['b'] == 200
```

To run your tests, execute:

```sh
pytest
```

```{code-cell} ipython3

```
