# CHANGELOG

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
