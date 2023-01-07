# Integration with `papermill`

`ploomber-engine` was developed to address some of [papermill's](https://github.com/nteract/papermill) limitations. However, given that papermill is widely used, you can use some of `ploomber-engine`'s feature from the `papermill` command-line interface via custom engines.

## Installation

Install both packages:

```sh
pip install ploomber-engine papermill ipykernel
```

## Debugging

If your notebook crashes mid-execution, papermill will provide you with the crashed `.ipynb` file. However, in many cases this isn't enough and you might want to use a debugger like [`pdb`](https://docs.python.org/3/library/pdb.html) for interactive debugging, you can use the `debuglater` engine to do so.

![debuglater gif](https://camo.githubusercontent.com/3463b13da6c719e35b986288c5bb7dcbc6fe26cc4172d66f7a2cc2d47970bc01/68747470733a2f2f706c6f6f6d6265722e696f2f696d616765732f646f632f706c6f6f6d6265722d656e67696e652d64656d6f2f64656275676c617465722e676966)


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

