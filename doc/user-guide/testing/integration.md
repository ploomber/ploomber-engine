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

# Integration testing

`ploomber-engine` allows you to test output cells from your notebooks.

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

Run the notebook and get the output variables:

```{code-cell} ipython3
from ploomber_engine.ipython import PloomberClient

client = PloomberClient.from_path("testing-demo.ipynb")
namespace = client.get_namespace()
namespace
```

Now we can check if the variables in the notebook have the values we expected:

```{code-cell} ipython3
assert namespace["a"] == 42
assert namespace["b"] == 200
```
