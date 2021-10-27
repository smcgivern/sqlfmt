from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from sqlfmt.cli import sqlfmt as sqlfmt_main
from tests.util import copy_test_data_to_tmp, discover_test_files


@pytest.fixture(
    params=[
        list(discover_test_files(["preformatted"])),
        ["preformatted"],
    ]
)
def preformatted_target(request: Any, tmp_path: Path) -> Path:
    """
    Copies the parameterized list of files/directories from the test/data
    directory into a temp directory (provided by pytest fixture tmp_path),
    and then returns the path to the temp directory.
    """
    test_dir = copy_test_data_to_tmp(request.param, tmp_path)
    return test_dir


@pytest.mark.parametrize(
    "options",
    [
        "",
        "--line-length 88",
        "-l 88",
        "--output update",
        "-o update",
        "--output check",
        "-o check",
        pytest.param("--output diff", marks=pytest.mark.xfail),
        pytest.param("-o diff", marks=pytest.mark.xfail),
    ],
)
def test_end_to_end(
    sqlfmt_runner: CliRunner, preformatted_target: Path, options: str
) -> None:

    args = f"{preformatted_target} {options}"
    result = sqlfmt_runner.invoke(sqlfmt_main, args=args)

    assert result
    assert "4 files" in result.stderr
    if "check" in options or "diff" in options:
        assert "passed formatting check" in result.stderr
    else:
        assert "left unchanged" in result.stderr

    assert result.exit_code == 0