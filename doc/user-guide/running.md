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

ploomber-engine allows you to run Jupyter notebooks programmatically.

Install dependencies:

```{code-cell} ipython3
%pip install ploomber-engine --quiet
```

Download sample notebook:

```{code-cell} ipython3
%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/examples/display.ipynb --output running-demo.ipynb
```

Import and initialize the notebook client:

```{code-cell} ipython3
from ploomber_engine.ipython import PloomberClient

client = PloomberClient.from_path("running-demo.ipynb")
```

Execute the notebook:

```{code-cell} ipython3
out = client.execute()
```

Store the notebook:

```{code-cell} ipython3
import nbformat

nbformat.write(out, "output-demo.ipynb")
```
