from ploomber_engine.execute import execute_notebook

__version__ = "0.0.23"


# NOTE: fully initialize papermill here to prevent circular import
try:
    import papermill  # noqa
except ModuleNotFoundError:
    # optional dependency, so do not throw an error if missing
    pass


__all__ = ["execute_notebook"]
