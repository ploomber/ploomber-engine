import re
import ast
from glob import glob
from os.path import basename, splitext
import fnmatch

from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_py import build_py as build_py_orig

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("src/ploomber_engine/__init__.py", "rb") as f:
    VERSION = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

REQUIRES = [
    "ploomber-core>=0.2",
    "debuglater>=1.4.4",
    # used for our debug now feature (PloomberNotebookClient)
    "nbclient",
    # used in PloomberClient
    "ipython",
    # used in the experiment tracker
    "parso",
    # used in several places for manipulating notebook objects
    "nbformat",
    # for the CLI
    "click",
    # for loading package version without importing the root __init__.py
    'importlib-metadata;python_version<"3.8"',
    # for progress bar
    "tqdm",
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
    # optional dependency for memory profiling
    "psutil",
]


exclude = ["*.conftest"]


# this is the only way I found for excluding single  .py files in wheels
# (https://stackoverflow.com/a/50592100/709975). MANIFEST.in only applies to source
# distributions. Some more info:
# https://github.com/pypa/packaging.python.org/issues/306
# https://github.com/pypa/setuptools/issues/511
class build_py(build_py_orig):
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)

        return [
            (pkg, mod, file)
            for (pkg, mod, file) in modules
            if not any(
                fnmatch.fnmatchcase(pkg + "." + mod, pat=pattern) for pattern in exclude
            )
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
    cmdclass={"build_py": build_py},
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    classifiers=[],
    keywords=[],
    install_requires=REQUIRES,
    extras_require={
        "dev": DEV,
    },
    entry_points={
        "papermill.engine": [
            "debug=ploomber_engine.engine:DebugEngine",
            "debuglater=ploomber_engine.engine:DebugLaterEngine",
            "embedded=ploomber_engine.engine:ProfilingEngine",
            # we keep this here for backwards compatibility
            "profiling=ploomber_engine.engine:ProfilingEngine",
        ],
        "console_scripts": ["ploomber-engine=ploomber_engine.cli:cli"],
    },
)
