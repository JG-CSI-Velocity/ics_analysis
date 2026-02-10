"""Tests for settings.py -- Pydantic configuration."""

from pathlib import Path

import pytest
import yaml

from ics_analysis.exceptions import ConfigError
from ics_analysis.settings import (
    BRAND_COLORS,
    ChartConfig,
    OutputConfig,
    Settings,
)


class TestSettings:
    def test_from_args_with_valid_file(self, tmp_path):
        data_file = tmp_path / "test.csv"
        data_file.write_text("col1,col2\n1,2\n")

        s = Settings.from_args(data_file=data_file)
        assert s.data_file == data_file
        assert s.client_id == "unknown"

    def test_from_args_extracts_client_id(self, tmp_path):
        data_file = tmp_path / "1453-test.xlsx"
        data_file.write_bytes(b"")  # Dummy file

        # Bypass file validation for this test
        s = Settings.model_construct(
            data_file=data_file,
            client_id=None,
            client_name=None,
            output_dir=Path("output/"),
            cohort_start="2025-01",
            ics_not_in_dump=0,
        )
        s = s.model_validate(s)
        assert s.client_id == "1453"
        assert s.client_name == "Client 1453"

    def test_from_args_invalid_file_raises(self, tmp_path):
        data_file = tmp_path / "nonexistent.csv"

        with pytest.raises(ConfigError):
            Settings.from_args(data_file=data_file)

    def test_from_args_unsupported_type_raises(self, tmp_path):
        data_file = tmp_path / "test.json"
        data_file.write_text("{}")

        with pytest.raises(ConfigError):
            Settings.from_args(data_file=data_file)

    def test_from_yaml_with_overrides(self, tmp_path):
        data_file = tmp_path / "test.csv"
        data_file.write_text("col1,col2\n1,2\n")

        config_path = tmp_path / "config.yaml"
        config_path.write_text(yaml.dump({"data_file": str(data_file), "client_id": "1234"}))

        s = Settings.from_yaml(config_path=config_path, client_name="Override CU")
        assert s.client_id == "1234"
        assert s.client_name == "Override CU"

    def test_from_yaml_missing_config_uses_defaults(self, tmp_path):
        data_file = tmp_path / "test.csv"
        data_file.write_text("col1,col2\n1,2\n")

        config_path = tmp_path / "nonexistent.yaml"
        s = Settings.from_yaml(config_path=config_path, data_file=str(data_file))
        assert s.output_dir == Path("output/")

    def test_defaults(self, tmp_path):
        data_file = tmp_path / "test.csv"
        data_file.write_text("col1,col2\n1,2\n")

        s = Settings.from_args(data_file=data_file)
        assert s.cohort_start == "2025-01"
        assert s.ics_not_in_dump == 0
        assert s.outputs.excel is True
        assert s.outputs.powerpoint is True
        assert s.charts.theme == "plotly_white"
        assert s.charts.colors == BRAND_COLORS
        assert s.charts.scale == 3
        assert s.last_12_months == []


class TestChartConfig:
    def test_defaults(self):
        c = ChartConfig()
        assert c.width == 900
        assert c.height == 500
        assert c.scale == 3


class TestOutputConfig:
    def test_defaults(self):
        o = OutputConfig()
        assert o.excel is True
        assert o.powerpoint is True
        assert o.html_charts is False
