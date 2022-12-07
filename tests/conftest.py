import sys
from functools import wraps
import os
import tempfile
from pathlib import Path
import shutil

import pytest
from unittest.mock import Mock

from ploomber_core.telemetry import telemetry

MOCK_API_KEY = 'phc_P1dsjk20bijsabdaib2eu'


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


@pytest.fixture
def no_sys_modules_cache():
    """
    Removes modules from sys.modules that didn't exist before the test
    """
    mods = set(sys.modules)

    yield

    current = set(sys.modules)

    to_remove = current - mods

    for a_module in to_remove:
        del sys.modules[a_module]


@pytest.fixture
def tmp_empty(tmp_path):
    """
    Create temporary path using pytest native fixture,
    them move it, yield, and restore the original path
    """
    old = os.getcwd()
    os.chdir(str(tmp_path))
    yield str(Path(tmp_path).resolve())
    os.chdir(old)


@pytest.fixture
def mock_telemetry(monkeypatch):
    telemetry.Telemetry('ploomber', '0.14.0', MOCK_API_KEY)

    mock = Mock()
    mock_dt = Mock()
    mock_dt.now.side_effect = [1, 2]

    monkeypatch.setattr(telemetry.Telemetry, 'log_api', mock)
    monkeypatch.setattr(telemetry.datetime, 'datetime', mock_dt)
    monkeypatch.setattr(telemetry.sys, 'argv', ['/path/to/bin', 'arg'])

    yield mock
