"""Tests for cli.py -- Typer CLI entry point."""

from typer.testing import CliRunner

from ics_analysis.cli import app

runner = CliRunner()


class TestCLI:
    def test_help_flag(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ICS" in result.stdout

    def test_missing_data_file(self):
        result = runner.invoke(app, ["nonexistent.csv"])
        assert result.exit_code == 1

    def test_runs_with_sample_data(self, sample_settings, tmp_path):
        result = runner.invoke(
            app,
            [
                str(sample_settings.data_file),
                "--output",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0

    def test_verbose_flag(self, sample_settings, tmp_path):
        result = runner.invoke(
            app,
            [
                str(sample_settings.data_file),
                "--output",
                str(tmp_path),
                "--verbose",
            ],
        )
        assert result.exit_code == 0

    def test_client_id_override(self, sample_settings, tmp_path):
        result = runner.invoke(
            app,
            [
                str(sample_settings.data_file),
                "--output",
                str(tmp_path),
                "--client-id",
                "9999",
                "--client-name",
                "Test Client",
            ],
        )
        assert result.exit_code == 0
