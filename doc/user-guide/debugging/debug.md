---
jupytext:
  cell_metadata_filter: -all
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
myst:
  html_meta:
    "description lang=en": "How to debug ploomber-engine notebooks"
    "keywords": "python,jupyter,notebooks,ploomber"
    "property=og:locale": "en_US"
---

# Debug

ploomber-engine allows you to start a debugging session right after your notebook crashes.

![debug](https://ploomber.io/images/doc/ploomber-engine-demo/debug.gif)

## Example

Install requirements:

```{code-cell} ipython3
%pip install ploomber-engine papermill ipykernel --quiet
```

Download [sample notebook](https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/crash.ipynb):

```{code-cell} ipython3
%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/crash.ipynb --output debug-demo.ipynb
```

Run the notebook with the `--engine debug` option to enable debugging. Upon crashing, a debugging session will start:

```sh
papermill crash.ipynb tmp.ipynb --engine debug
```

```{note}
Currently, the `debug` engine is only available via `papermill`, in a future release, it'll be possible to use it without it.
```

Sample debugging session:

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
