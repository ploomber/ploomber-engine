try:
    from importlib.metadata import version
except ModuleNotFoundError:
    from importlib_metadata import version


from ploomber_core.telemetry.telemetry import Telemetry


telemetry = Telemetry(
    api_key="phc_P9SpSeypyPwxrMdFn2edOOEooQioF2axppyEeDwtMSP",
    package_name="ploomber-engine",
    version=version("ploomber-engine"),
)
