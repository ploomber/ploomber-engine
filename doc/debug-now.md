---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Debug now

This engine will automatically start a debugging session upon notebook crash.

![debug](https://ploomber.io/images/doc/ploomber-engine-demo/debug.gif)

## Debug now example

The following section includes instruuctions to run an example.

```sh
# install package (this installs papermill as well)
pip install ploomber-engine

# get the example notebook
curl -O https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/crash.ipynb
```

Run the notebook with the custom engine:

```sh tags=['raises-exception']
papermill crash.ipynb tmp.ipynb --engine debug
```


Once the notebook crashes, it'll start the debugging session:

```
Input Notebook:  crash.ipynb
Output Notebook: tmp.ipynb
---------------------------------------------------------------------------
ZeroDivisionError                         Traceback (most recent call last)
Input In [2], in <cell line: 3>()
      1 x = 1
      2 y = 0
----> 3 x/y

ZeroDivisionError: division by zero
> /var/folders/3h/_lvh_w_x5g30rrjzb_xnn2j80000gq/T/ipykernel_64532/3136424576.py(3)<cell line: 3>()
      1 x = 1
      2 y = 0
----> 3 x/y

ipdb>
```