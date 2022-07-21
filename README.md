<!-- #region -->
# ploomber-engine

A custom papermill engine to enable debugging. 🐞

[Papermill](https://github.com/nteract/papermill) does not support debugging notebooks when they crash. For example, if you enable debugging mode (using `%pdb on`) and the notebook crashes, you'll see this:

> IPython.core.error.StdinNotImplementedError: raw_input was called, but this frontend does not support input requests.

This custom engine enables debugging:

```sh
papermill crash.ipynb tmp.ipynb --engine ploomber-engine
```

Once the notebook crashes, it'll start the debugging session:

```pytb
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
<!-- #endregion -->

## Example

```sh
pip install ploomber-engine

# get the example notebook
curl -O https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/crash.ipynb
```

<!-- #region -->
Run the notebook with the custom engine:

```sh
papermill crash.ipynb tmp.ipynb --engine ploomber-engine
```
<!-- #endregion -->
