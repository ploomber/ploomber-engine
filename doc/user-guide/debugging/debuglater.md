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

# Debug later

ploomber-engine uses our [debuglater](https://github.com/ploomber/debuglater) package to serialize the error traceback so you can start a debugging session after your notebook crashes.

So, for example, if you're running notebooks in production or remote servers, you can debug after they crash. Likewise, you can use the generated file to debug on a different machine (assuming the environment is the same) without having access to the source code.

![debuglater gif](https://camo.githubusercontent.com/3463b13da6c719e35b986288c5bb7dcbc6fe26cc4172d66f7a2cc2d47970bc01/68747470733a2f2f706c6f6f6d6265722e696f2f696d616765732f646f632f706c6f6f6d6265722d656e67696e652d64656d6f2f64656275676c617465722e676966)

```{note}
You can download this tutorial in Jupyter notebook format by clicking on the icon in the upper right corner.
```

+++

## Example

Install requirements:

```{code-cell} ipython3
%pip install ploomber-engine --quiet
```

Download [sample notebook](https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/debuglater.ipynb):

```{code-cell} ipython3
%%sh
curl https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/debuglater.ipynb --output debuglater-demo.ipynb
```

Run the notebook with `--engine debuglater` option (note that this notebook crashes on purpose):

```{code-cell} ipython3
:tags: [raises-exception, hide-output]

%%sh
papermill debuglater-demo.ipynb tmp.ipynb --engine debuglater
```

The above command generates a `jupyter.dump` file which is the serialized traceback:

```{code-cell} ipython3
%%sh
ls *.dump
```

We can use the `dltr` command (from our [debuglater](https://github.com/ploomber/debuglater) package) to start a debugging session:

```sh
dltr jupyter.dump
```
