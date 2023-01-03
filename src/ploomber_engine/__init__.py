__version__ = "0.0.18dev"

import typing as t

# NOTE: fully initialize papermill here to prevent circular import
try:
    import papermill  # noqa
except ModuleNotFoundError:
    # optional dependency, so do not throw an error if missing
    pass
