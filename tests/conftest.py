from functools import wraps
import os
import tempfile
from pathlib import Path
import shutil

import pytest


def _path_to_tests():
    return Path(__file__).resolve().parent.parent / 'tests'


def fixture_tmp_dir(source, **kwargs):
    """
    A lot of our fixtures are copying a few files into a temporary location,
    making that location the current working directory and deleting after
    the test is done. This decorator allows us to build such fixture
    """

    # NOTE: I tried not making this a decorator and just do:
    # some_fixture = factory('some/path')
    # but didn't work
    def decorator(function):

        @wraps(function)
        def wrapper():
            old = os.getcwd()
            tmp_dir = tempfile.mkdtemp()
            tmp = Path(tmp_dir, 'content')
            # we have to add extra folder content/, otherwise copytree
            # complains
            shutil.copytree(str(source), str(tmp))
            os.chdir(str(tmp))
            yield tmp

            os.chdir(old)
            shutil.rmtree(tmp_dir)

        return pytest.fixture(wrapper, **kwargs)

    return decorator


@fixture_tmp_dir(_path_to_tests() / 'assets')
def tmp_assets():
    pass
