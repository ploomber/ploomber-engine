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
---

## Passing outputs between notebooks

```{versionadded} 0.0.22
```

+++

Let's create two simple notebooks:

The first notebook has:

```python
x = 1
```

While the second notebook contains:

```python
x = 0

y = x + 1
```

For this example, we'll genearate the notebooks programmatically, but you can use existing `.ipynb` files.

```{code-cell} ipython3
from pathlib import Path
import nbformat

first = nbformat.v4.new_notebook()
first.cells = [nbformat.v4.new_code_cell("x = 1")]
Path("first.ipynb").write_text(nbformat.v4.writes(first), encoding="utf-8")

second = nbformat.v4.new_notebook()
second.cells = [nbformat.v4.new_code_cell("x = 0", metadata=dict(tags=["defaults"])),
                nbformat.v4.new_code_cell("y = x + 1")]
Path("second.ipynb").write_text(nbformat.v4.writes(second), encoding="utf-8")
```

Now, we'll execute the first notebook and extract the outputs:

```{code-cell} ipython3
from ploomber_engine.ipython import PloomberClient

client_first = PloomberClient.from_path("first.ipynb")
ns_first = client_first.get_namespace()
ns_first
```

Execute the second notebook:

```{code-cell} ipython3
client_second = PloomberClient.from_path("second.ipynb")
ns_second = client_second.get_namespace()
ns_second
```

We see that the second notebook is using `x=0`, the defeault value. Now, let's use the `namespace` argument so it uses the outputs from the first notebook:

```{code-cell} ipython3
client_second = PloomberClient(second, remove_tagged_cells="defaults")
ns_second = client_second.get_namespace(namespace=ns_first)
ns_second
```
