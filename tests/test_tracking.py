from pathlib import Path
from unittest.mock import ANY, Mock

import pytest

from ploomber_engine.tracking.tracking import _parse_cli_parameters, extract_name
from ploomber_engine.tracking import track_execution
from sklearn_evaluation import SQLiteTracker
from ploomber_engine import _telemetry


@pytest.mark.parametrize(
    "params, expected",
    [
        ["a=1,b=2", dict(a=1, b=2)],
        ["  a=1,  b=2  ", dict(a=1, b=2)],
        ["number=1.1,another=2.2", dict(number=1.1, another=2.2)],
        ["s=something,b=2", dict(s="something", b=2)],
        ["s=a.b.c", dict(s="a.b.c")],
    ],
    ids=[
        "simple",
        "whitespace",
        "floats",
        "string",
        "dotted-path",
    ],
)
def test_parse_cli_parameters(params, expected):
    assert _parse_cli_parameters(params) == expected


variables_wo_extra_parameters = """
x = 1
x

y = 2
y

sum_ = x + y
sum_
"""

variables = """
x = 1
x

y = 2
y

sum_ = x + y + a + b
sum_
"""

calls_wo_extra_parameters = """
def x():
    return 1

def y():
    return 2

def sum_(args):
    return sum(args)

x()

y()

sum_(args=[x(), y()])
"""

calls = """
def x():
    return 1

def y():
    return 2

def sum_(args):
    return sum(args)

x()

y()

sum_(args=[x(), y(), a, b])
"""

imports_wo_extra_parameters = """
import functions

functions.x()

functions.y()

functions.sum_(args=[functions.x(), functions.y()])
"""

imports = """
import functions

functions.x()

functions.y()

functions.sum_(args=[functions.x(), functions.y(), a, b])
"""


@pytest.mark.parametrize(
    "script",
    [
        variables,
        calls,
        imports,
    ],
    ids=[
        "variables",
        "calls",
        "imports",
    ],
)
def test_track(tmp_empty, script):
    Path("functions.py").write_text(
        """
def x():
    return 1

def y():
    return 2

def sum_(args):
    return sum(args)
"""
    )

    Path("script.py").write_text(script)

    track_execution(
        filename="script.py", parameters=dict(a=1, b=2), database="exps.db", quiet=True
    )

    tracker = SQLiteTracker("exps.db")

    result = tracker.query(
        """
SELECT
    uuid,
    json_extract(parameters, '$.a') as a,
    json_extract(parameters, '$.b') as b,
    json_extract(parameters, '$.sum_') as sum_,
    json_extract(parameters, '$.x') as x,
    json_extract(parameters, '$.y') as y
    FROM experiments
""",
        as_frame=False,
    )

    assert result.rows == [(ANY, 1, 2, 6, 1, 2)]


@pytest.mark.parametrize(
    "script",
    [
        variables_wo_extra_parameters,
        calls_wo_extra_parameters,
        imports_wo_extra_parameters,
    ],
    ids=[
        "variables",
        "calls",
        "imports",
    ],
)
def test_track_wo_parameter(tmp_empty, script):
    Path("functions.py").write_text(
        """
def x():
    return 1

def y():
    return 2

def sum_(args):
    return sum(args)
"""
    )

    Path("script.py").write_text(script)

    track_execution(filename="script.py", database="exps.db", quiet=True)

    tracker = SQLiteTracker("exps.db")

    result = tracker.query(
        """
SELECT
    uuid,
    json_extract(parameters, '$.sum_') as sum_,
    json_extract(parameters, '$.x') as x,
    json_extract(parameters, '$.y') as y
    FROM experiments
""",
        as_frame=False,
    )

    assert result.rows == [(ANY, 3, 1, 2)]


@pytest.mark.parametrize(
    "source, expected",
    [
        [
            """
x = 1
x
""",
            "x",
        ],
        [
            """
x()
""",
            "x",
        ],
        [
            """
x(y, z)
""",
            "x",
        ],
        [
            """
x(y=y, z=z)
""",
            "x",
        ],
        [
            """
x(y, z=z)
""",
            "x",
        ],
        [
            """
x([1, 2, 3], z=package.funion(dict(x=1, y=2)))
""",
            "x",
        ],
        [
            """
package.x([1, 2, 3], z=package.funion(dict(x=1, y=2)))
""",
            "x",
        ],
        [
            """
nested.package.x([1, 2, 3], z=package.funion(dict(x=1, y=2)))
""",
            "x",
        ],
        pytest.param(
            """
mapping['x']
""",
            "x",
            marks=pytest.mark.xfail(reason="not implemented"),
        ),
        pytest.param(
            """
mapping['another']['x']
""",
            "x",
            marks=pytest.mark.xfail(reason="not implemented"),
        ),
        pytest.param(
            """
something.mapping['another']['x']
""",
            "x",
            marks=pytest.mark.xfail(reason="not implemented"),
        ),
    ],
    ids=[
        "variable-simple",
        "function-call-simple",
        "function-call-args",
        "function-call-kwargs",
        "function-call-mixed",
        "function-call-complex",
        "function-call-package",
        "function-call-nested-package",
        "getitem",
        "getitem-nested",
        "getitem-nested-and-attribtue",
    ],
)
def test_extract_name(source, expected):
    assert extract_name(source) == expected


def test_tracking_import_telemetry(tmp_empty, monkeypatch):
    Path("functions.py").write_text("""x = 1""")
    mock = Mock()
    monkeypatch.setattr(_telemetry.telemetry, "log_api", mock)

    track_execution(
        filename="functions.py",
        parameters=dict(a=1, b=2),
        database="exps.db",
        quiet=True,
    )

    assert mock.call_count == 2
