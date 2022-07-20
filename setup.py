import re
import ast
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/ploomber_engine/__init__.py', 'rb') as f:
    VERSION = str(
        ast.literal_eval(
            _version_re.search(f.read().decode('utf-8')).group(1)))

REQUIRES = [
    'papermill',
    'ipykernel',
]

DEV = [
    'pytest',
    'flake8',
    'invoke',
]

setup(
    name='ploomber-engine',
    version=VERSION,
    description=None,
    license=None,
    author=None,
    author_email=None,
    url=None,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    classifiers=[],
    keywords=[],
    install_requires=REQUIRES,
    extras_require={
        'dev': DEV,
    },
    entry_points={
        "papermill.engine":
        ["ploomber-engine=ploomber_engine.engine:PloomberClientEngine"],
    },
)
