import re
import ast
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages
from setuptools import setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("src/ploomber_engine/__init__.py", "rb") as f:
    VERSION = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

REQUIRES = [
    "ploomber-core>=0.0.4",
    "papermill",
    "ipykernel",
    "debuglater",
    "nbclient",
    "ipython",
    "parso",
    "nbformat",
    "click",
]

DEV = [
    "pkgmt",
    "pytest",
    "flake8",
    "invoke",
    "twine",
    # for testing PloomberShell
    "matplotlib",
    "pandas",
    # for testing the profiling engine
    "numpy",
    # for testing the track module
    "sklearn-evaluation",
    "jupytext",
]

setup(
    name="ploomber-engine",
    version=VERSION,
    description=None,
    license=None,
    author=None,
    author_email=None,
    url=None,
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    classifiers=[],
    keywords=[],
    install_requires=REQUIRES,
    extras_require={"dev": DEV},
    entry_points={
        "papermill.engine": [
            "debug=ploomber_engine.engine:DebugEngine",
            "debuglater=ploomber_engine.engine:DebugLaterEngine",
            "embedded=ploomber_engine.engine:ProfilingEngine",
            # we keep this here for backwards compatibility
            "profiling=ploomber_engine.engine:ProfilingEngine",
        ],
    },
)
