from pathlib import Path

import pytest
from ploomber_engine.ipython import PloomberClient


@pytest.fixture
def ns():
    client = PloomberClient.from_path(Path(__file__).parent / 'nb.ipynb')
    return client.get_namespace()


def test_add(ns):
    add = ns['add']
    assert add(1, 2) == 3


def test_multiply(ns):
    multiply = ns['multiply']
    assert multiply(2, 2) == 4


def test_notebook_results(ns):
    assert ns['a'] == 42
    assert ns['b'] == 200
