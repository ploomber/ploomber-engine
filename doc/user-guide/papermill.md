# Integration with `papermill`

`ploomber-engine` was developed to address some of [papermill's](https://github.com/nteract/papermill) limitations. However, given that papermill is widely used, you can use some of `ploomber-engine`'s feature from the `papermill` command-line interface via custom engines.

## Installation

Install both packages:

```sh
pip install ploomber-engine papermill ipykernel
```

## Debugging

If your notebook crashes mid-execution, papermill will provide you with the crashed `.ipynb` file. However, in many cases this isn't enough and you might want to use a debugger like [`pdb`](https://docs.python.org/3/library/pdb.html) for interactive debugging, you can use the `debuglater` engine to do so.


```sh
papermill input.ipynb output.ipynb --engine debuglater
```

Upon crashing, a `jupyter.dump` file is stored. You can start a debugging session with:


```sh
dltr jupyter.dump
```

## Profiling

Since papermill runs your code spins up a new process to execute your code, monitoring the `papermill` process won't yield useful information. You can run your notebook in the same process using our embedded engine:

```sh
papermill input.ipynb output.ipynb --engine embedded
```

You can monitor usage with tools such as `htop`, or the [memory-profiler](https://github.com/pythonprofilers/memory_profiler) package.

