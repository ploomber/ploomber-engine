"""
Command-line interface tests
"""
from unittest.mock import Mock, call

import pytest
from click.testing import CliRunner

from ploomber_engine import cli
from ploomber_engine import execute_notebook
from conftest import _make_nb


@pytest.mark.parametrize(
    "cli_args, call_expected",
    [
        [
            ["nb.ipynb", "out.ipynb", "--no-progress-bar"],
            call(
                "nb.ipynb",
                "out.ipynb",
                log_output=False,
                profile_memory=False,
                profile_runtime=False,
                progress_bar=False,
                parameters=None,
                debug_later=False,
            ),
        ],
        [
            ["nb.ipynb", "out.ipynb", "--log-output", "--no-progress-bar"],
            call(
                "nb.ipynb",
                "out.ipynb",
                log_output=True,
                profile_memory=False,
                profile_runtime=False,
                progress_bar=False,
                parameters=None,
                debug_later=False,
            ),
        ],
        [
            ["nb.ipynb", "out.ipynb", "--profile-memory", "--no-progress-bar"],
            call(
                "nb.ipynb",
                "out.ipynb",
                log_output=False,
                profile_memory=True,
                profile_runtime=False,
                progress_bar=False,
                parameters=None,
                debug_later=False,
            ),
        ],
        [
            ["nb.ipynb", "out.ipynb", "--profile-runtime", "--no-progress-bar"],
            call(
                "nb.ipynb",
                "out.ipynb",
                log_output=False,
                profile_memory=False,
                profile_runtime=True,
                progress_bar=False,
                parameters=None,
                debug_later=False,
            ),
        ],
        [
            ["nb.ipynb", "out.ipynb", "--no-progress-bar", "-p", "key", "value"],
            call(
                "nb.ipynb",
                "out.ipynb",
                log_output=False,
                profile_memory=False,
                profile_runtime=False,
                progress_bar=False,
                parameters=dict(key="value"),
                debug_later=False,
            ),
        ],
        [
            ["nb.ipynb", "out.ipynb", "--no-progress-bar", "-p", "key", "1"],
            call(
                "nb.ipynb",
                "out.ipynb",
                log_output=False,
                profile_memory=False,
                profile_runtime=False,
                progress_bar=False,
                parameters=dict(key=1),
                debug_later=False,
            ),
        ],
        [
            ["nb.ipynb", "out.ipynb", "--no-progress-bar", "-p", "key", "1.0"],
            call(
                "nb.ipynb",
                "out.ipynb",
                log_output=False,
                profile_memory=False,
                profile_runtime=False,
                progress_bar=False,
                parameters=dict(key=1.0),
                debug_later=False,
            ),
        ],
        [
            ["nb.ipynb", "out.ipynb", "--no-progress-bar", "-p", "key", "{'a': 1}"],
            call(
                "nb.ipynb",
                "out.ipynb",
                log_output=False,
                profile_memory=False,
                profile_runtime=False,
                progress_bar=False,
                parameters=dict(key=dict(a=1)),
                debug_later=False,
            ),
        ],
        [
            ["nb.ipynb", "out.ipynb", "--no-progress-bar", "--debug-later"],
            call(
                "nb.ipynb",
                "out.ipynb",
                log_output=False,
                profile_memory=False,
                profile_runtime=False,
                progress_bar=False,
                parameters=None,
                debug_later=True,
            ),
        ],
    ],
)
def test_cli(tmp_empty, monkeypatch, cli_args, call_expected):
    mock = Mock(wraps=execute_notebook)
    monkeypatch.setattr(cli, "execute_notebook", mock)

    _make_nb(["1 + 1"])

    runner = CliRunner()
    result = runner.invoke(cli.cli, cli_args)

    assert result.exit_code == 0
    assert result.output == ""
    assert mock.call_args_list == [call_expected]


def test_cli_input_doesnt_exist(tmp_empty):
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["input.ipynb"])

    assert result.exit_code == 2
    assert (
        "Error: Invalid value for 'INPUT_PATH': Path 'input.ipynb' does not exist.\n"
    ) in result.output


def test_cli_missing_output_arg(tmp_empty):
    _make_nb(["1 + 1"])

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["nb.ipynb"])

    assert result.exit_code == 2
    assert "Error: Missing argument 'OUTPUT_PATH'.\n" in result.output


def test_cli_progress_bar(tmp_empty):
    _make_nb(["1 + 1"])

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["nb.ipynb", "output.ipynb"])

    assert result.exit_code == 0
    assert "Executing cell: 1" in result.output


@pytest.mark.parametrize(
    "params, expected",
    [
        [tuple(), None],
        [(("key", "value"),), {"key": "value"}],
        [(("key", "value"), ("key", "value")), {"key": "value"}],
        [
            (("key", "value"), ("key_another", "value_another")),
            {"key": "value", "key_another": "value_another"},
        ],
        [(("key", "1"),), {"key": 1}],
        [(("key", "1.1"),), {"key": 1.1}],
        [(("key", "[1, 2, 3]"),), {"key": [1, 2, 3]}],
        [(("key", "{'a': 1}"),), {"key": {"a": 1}}],
    ],
)
def test_parse_cli_notebook_parameters(params, expected):
    assert cli._parse_cli_notebook_parameters(params) == expected
