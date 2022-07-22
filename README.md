# ploomber-engine

[Papermill](https://github.com/nteract/papermill) does not support debugging notebooks when they crash. For example, if you enable debugging mode (using `%pdb on`) and the notebook crashes, you'll see this:

> IPython.core.error.StdinNotImplementedError: raw_input was called, but this frontend does not support input requests.

`ploomber-engine` adds debugging capabilities to Papermill by adding custom execution engines.

## Debug later

The `debuglater` engine serializes the error traceback so you can start a debugging session whenever possible. So, for example, if you're running notebooks in production or remote servers, you can debug them upon crashing. Likewise, you can use the generated file to debug on a different machine (assuming the environment is the same) without having access to the source code.

### Debug later example

```sh
# install package (this installs papermill as well)
pip install ploomber-engine

# get sample notebook
curl -O https://raw.githubusercontent.com/ploomber/ploomber-engine/ipython/tests/assets/debuglater.ipynb
```

Run the notebook with `--engine debuglater`

```sh tags=['raises-exception']
papermill debuglater.ipynb tmp.ipynb --engine debuglater
```

Start debugging session (using `debuglater` CLI)

<!-- #region -->
```
dltr jupyter.dump
```
<!-- #endregion -->

## Debug now

This engine will automatically start a debugging session upon notebook crash.
### Debug now example

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

## [Experimental] Notebook profiling (CPU, GPU, RAM)

Papermill executes the notebook in an independent process. Consequently,
resources like CPU/GPU usage or RAM cannot be monitored. We have an
experimental engine that runs a notebook in the same process.

[See the profiling demo here.](doc/profiling.ipynb)


If you give it a try, please share your feedback: [join our community](https://ploomber.io/community) and send us a message.
## Support

For support, feature requests, and product updates: [join our community](https://ploomber.io/community) or follow us on [Twitter](https://twitter.com/ploomber)/[LinkedIn](https://www.linkedin.com/company/ploomber/).