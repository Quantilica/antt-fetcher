"""Tests for antt-fetcher Typer plugin."""

from typer.testing import CliRunner

from antt_fetcher.plugin import app


def test_cli_list() -> None:
    """Test quantilica antt list."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "rodovias" in result.output


def test_cli_convert_help() -> None:
    """Test quantilica antt convert --help."""
    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "--lake" in result.output
