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

# Notebook profiling (CPU, GPU, RAM)

Papermill executes the notebook in an independent process. We built an engine that runs a notebook in the same process, which enables resource monitoring.

![profiling](https://ploomber.io/images/doc/ploomber-engine-demo/profiling.gif)

[See the profiling demo here.](./profiling.ipynb)


