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

# Profiling

With ploomber-engine and [memory-profiler](https://github.com/pythonprofilers/memory_profiler) you can profile Jupyter notebook's memory usage. Unlike papermill, which isn't capable of doing it.

![profiling](https://ploomber.io/images/doc/ploomber-engine-demo/profiling.gif)


```{note}
You can download this tutorial in Jupyter notebook format by clicking on the icon in the upper right corner.
```

+++

## Profiling memory usage

+++

Install requirements:

```{code-cell} ipython3
%pip install ploomber-engine memory-profiler --quiet
```

Download sample notebook:

```{code-cell} ipython3
%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/profiling.ipynb --output profiling-demo.ipynb
```

Run the notebook with the `--engine profiling` argument and prepend the command with `mprof run` to monitor memory usage:

```{code-cell} ipython3
%%sh
mprof run papermill profiling-demo.ipynb tmp.ipynb --engine profiling
```

Use the `mprof` command (part of the `memory-profiler` package) to generate a plot:

```{code-cell} ipython3
%%sh
mprof plot --output profiling.png
```

Display the plot:

```{code-cell} ipython3
from IPython.display import Image

Image('profiling.png')
```

## Using papermill (profiling doesn't work)

As a counter-example, we'll run the same notebook using papermill and show that profiling doesn't work, since papermill spins up a second process to run the notebook.

Download sample notebook:

```{code-cell} ipython3
%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/profiling.ipynb --output profiling-demo.ipynb
```

Run the notebook with papermill and prepend the command with `mprof run` to monitor memory usage:

```{code-cell} ipython3
%%sh
mprof run papermill profiling-demo.ipynb tmp.ipynb
```

Use the `mprof` command (part of the `memory-profiler` package) to generate a plot:

```{code-cell} ipython3
%%sh
mprof plot --output papermill.png
```

Display the plot:

```{code-cell} ipython3
from IPython.display import Image

Image('papermill.png')
```

We can see that memory usage remains constant, we cannot profile memory with papermill.
