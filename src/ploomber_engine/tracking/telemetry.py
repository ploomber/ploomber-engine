from ploomber_core.telemetry.telemetry import Telemetry

try:
    from importlib.metadata import version
except ModuleNotFoundError:
    from importlib_metadata import version

telemetry = Telemetry(
    api_key="phc_P9SpSeypyPwxrMdFn2edOOEooQioF2axppyEeDwtMSP",
    package_name="ploomber-engine",
    version=version("ploomber_engine"),
)
