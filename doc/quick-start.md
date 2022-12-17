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

# Quick Start

[ploomber-engine](https://github.com/ploomber/ploomber-engine) is a toolbox for executing notebooks.

It provides enhanced capabilities such as debugging, profiling and experiment tracking.

## Installation

```bash
pip install -U ploomber-engine
```

or

```bash
conda install ploomber-engine -c conda-forge
```
## Example

Execute a crashing notebook and start a debugging session:

```bash
# get sample notebook
curl -O https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/debuglater.ipynb

# run notebook
papermill debuglater.ipynb tmp.ipynb --engine debuglater

# start debugging session
dltr jupyter.dump
```
