import re
import subprocess
from typing import List

from click.testing import CliRunner

from sqlfmt.cli import sqlfmt as sqlfmt_main


def run_cli_command(commands: List[str]) -> subprocess.CompletedProcess:
    process = subprocess.run(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
    )
    return process


def test_click_cli_runner_is_equivalent_to_py_subprocess(
    sqlfmt_runner: CliRunner,
) -> None:

    builtin_results = run_cli_command(["sqlfmt"])
    click_results = sqlfmt_runner.invoke(sqlfmt_main)

    assert builtin_results.returncode == click_results.exit_code
    assert builtin_results.stdout == click_results.stdout
    assert builtin_results.stderr == click_results.stderr


def test_help_command(sqlfmt_runner: CliRunner) -> None:
    # Sally installs sqlfmt; not knowing where to start, she types "sqlfmt --help" into
    # her command line, and sees that it displays the version and a help menu
    help_option = "--help"
    help_results = sqlfmt_runner.invoke(sqlfmt_main, args=help_option)
    assert help_results.exit_code == 0
    assert help_results.stdout.startswith("Usage: sqlfmt")


def test_version_command(sqlfmt_runner: CliRunner) -> None:
    version_option = "--version"
    results = sqlfmt_runner.invoke(sqlfmt_main, args=version_option)
    assert results.exit_code == 0
    assert results.stdout.startswith("sqlfmt, version ")

    semver_pattern = r"\d+\.\d+.\d+"
    match = re.search(semver_pattern, results.stdout)
    assert match, "Semantic version number not in output"
