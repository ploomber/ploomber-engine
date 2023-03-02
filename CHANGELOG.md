# CHANGELOG

## 0.0.23 (2023-03-01)

* [Feature] Save profiling data (memory/time per cell) using `--save-profiling-data=` in the CLI or `save_profiling_data` in the Python API
* [Feature] Adds `cwd` to allow users to specify the working directory when executing notebooks ([#53](https://github.com/ploomber/ploomber-engine/issues/53))

## 0.0.22 (2023-02-10)

* [Feature] Adds `namespace` to `PloomberClient.get_namespce` to pass objects before execution

## 0.0.21 (2023-02-10)

* [Feature] `parameters` in `track_execution` is optional ([#41](https://github.com/ploomber/ploomber-engine/issues/41))
* [Feature] Remove cells before execution using `--remove-tagged-cells` in the CLI or `remove_tagged_cells` in the Python API ([#37](https://github.com/ploomber/ploomber-engine/issues/37))
* [Fix] Support for Python 3.7 deprecated.

## 0.0.20 (2023-01-29)

* [Fix] `setup.py` fix due to change in setuptools 67.0.0

## 0.0.19 (2023-01-11)

* Adds notebook parametrization to the CLI (`-p/--parameters`) and Python API (`parameters`)
* Integrates debug later to the CLI `--debug-later` and Python API (`debug_later`)
* Adds progress bar when executing notebooks
* Partially execute notebook stored (`.ipynb` file) even when notebook execution fails

## 0.0.18 (2023-01-04)

* Adds `ploomber-engine` CLI with a papermill-like API
* Adds `ploomber_engine.execute_notebook` function with a papermill-like API
* Adds `display_stdout` to `PloomberClient.from_path`
* Updates docs to use `ploomber_engine.execute_notebook`
* Fixes error in profiling functions that broke execution of notebooks with Markdown cells
* Makes plotting functions part of the public API

## 0.0.17 (2022-12-22)

* Makes papermill an optional dependency

## 0.0.16 (2022-12-21)

* Adds `ploomber_engine.testing.test_notebook` to test notebooks against existing outputs

## 0.0.15 (2022-12-21)

* Fixes inline matplotlib after using PloomberClient

## 0.0.14 (2022-12-20)

* Adds `memory_profiler`
* `PloomberClient` records cell timestamps
* Docs refactoring
* Adds notebook running and notebook testing sections to docs

## 0.0.13 (2022-12-15)

* Clean release after CI broke

## 0.0.12 (2022-12-15)

* Releasing telemetry on top of tracking and import of `ploomber_engine.tracking`

## 0.0.11 (2022-11-15)

* Adds `ploomber_engine.tracking` module for experiment tracking

## 0.0.10 (2022-08-23)

* Changes telemetry key

## 0.0.9 (2022-08-22)

* Fixes error when notebook called methods in `sys.stdout`

## 0.0.8 (2022-08-20)

* Correctly clearing up `PloomberShell` to prevent interfering with IPython terminal singleton

## 0.0.7 (2022-08-20)

* Removes `nbclient>0.6.1` requirements (it's only applicable when using the `debug` engine)

## 0.0.6 (2022-08-13)

* Adds (optional) anonymous telemetry

## 0.0.5 (2022-08-11)

* Renames `profiling` engine to `embedded` (keeping `profiling` as alias for backwards compatibility)
* Adds execution count to cell outputs
* Adds `PloomberManagedClient` so papermill can keep track of status and progress
* Catching exceptions
* Fixes output display order

## 0.0.4 (2022-08-02)

* `debuglater` engine accepts `path_to_dump` argument
* `PloomberClient` adds current path to `sys.path` while executing ([#4](https://github.com/ploomber/ploomber-engine/issues/4))
* `DebugEngine` adds a `%pdb on` cell at the top before execution

## 0.0.3 (2022-07-24)

* Correctly identifying `stderr` stream (displayed with red background in the notebook file)
* Capturing HTML outputs
* Adds execution count to cells
* Ignoring non-code cells from execution
* Catching exception when enabling matplotlib failed upon shell initialization (due to matplotlib not installed in the env)
* Fixes an error that displayed empty messages from the shell

## 0.0.2 (2022-07-22)

* Renames `ploomber-engine` to `debug`
* Adds `debuglater` engine
* Adds (experimental) `profiling` engine

## 0.0.1 (2022-07-20)

* First release
