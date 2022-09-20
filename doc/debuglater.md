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

# Debug later

This engine uses our [debuglater](https://github.com/ploomber/debuglater) package to serialize the error traceback so you can start a debugging session whenever possible.

So, for example, if you're running notebooks in production or remote servers, you can debug them upon crashing. Likewise, you can use the generated file to debug on a different machine (assuming the environment is the same) without having access to the source code.

![debuglater gif](https://camo.githubusercontent.com/3463b13da6c719e35b986288c5bb7dcbc6fe26cc4172d66f7a2cc2d47970bc01/68747470733a2f2f706c6f6f6d6265722e696f2f696d616765732f646f632f706c6f6f6d6265722d656e67696e652d64656d6f2f64656275676c617465722e676966)


## Debug later example

The following section includes instruuctions to run an example.

```sh
# install package (this installs papermill as well)
pip install ploomber-engine

# get sample notebook
curl -O https://raw.githubusercontent.com/ploomber/ploomber-engine/main/tests/assets/debuglater.ipynb
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