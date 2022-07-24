# CHANGELOG
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