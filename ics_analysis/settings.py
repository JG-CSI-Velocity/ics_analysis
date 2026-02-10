"""Configuration system using Pydantic BaseModel + yaml.safe_load."""

import logging
import re
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator, model_validator

from ics_analysis.exceptions import ConfigError

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("config.yaml")

DEFAULT_BALANCE_BINS = [float("-inf"), 0, 1000, 5000, 10000, 25000, 50000, 100000, float("inf")]
DEFAULT_BALANCE_LABELS = [
    "$0 or Less",
    "$0-$1K",
    "$1K-$5K",
    "$5K-$10K",
    "$10K-$25K",
    "$25K-$50K",
    "$50K-$100K",
    "$100K+",
]

DEFAULT_AGE_BINS = [0, 30, 90, 180, 365, 730, 1825, 3650, float("inf")]
DEFAULT_AGE_LABELS = [
    "0-1 month",
    "1-3 months",
    "3-6 months",
    "6-12 months",
    "1-2 years",
    "2-5 years",
    "5-10 years",
    "10+ years",
]

BRAND_COLORS = ["#1B365D", "#4A90D9", "#7BC67E", "#F5A623", "#D0021B", "#8B572A"]


class BalanceTierConfig(BaseModel):
    """Balance tier bin configuration."""

    bins: list[float] = DEFAULT_BALANCE_BINS.copy()
    labels: list[str] = DEFAULT_BALANCE_LABELS.copy()


class AgeRangeConfig(BaseModel):
    """Account age range bin configuration."""

    bins: list[float] = DEFAULT_AGE_BINS.copy()
    labels: list[str] = DEFAULT_AGE_LABELS.copy()


class ChartConfig(BaseModel):
    """Chart rendering settings."""

    theme: str = "plotly_white"
    colors: list[str] = BRAND_COLORS.copy()
    width: int = 900
    height: int = 500
    scale: int = 3


class OutputConfig(BaseModel):
    """Which output formats to generate."""

    excel: bool = True
    powerpoint: bool = True
    html_charts: bool = False


class Settings(BaseModel):
    """Main application configuration."""

    data_file: Path
    client_id: str | None = None
    client_name: str | None = None
    output_dir: Path = Path("output/")
    cohort_start: str = "2025-01"
    ics_not_in_dump: int = 0
    balance_tiers: BalanceTierConfig = BalanceTierConfig()
    age_ranges: AgeRangeConfig = AgeRangeConfig()
    outputs: OutputConfig = OutputConfig()
    charts: ChartConfig = ChartConfig()
    pptx_template: Path | None = None
    last_12_months: list[str] = []

    @field_validator("data_file")
    @classmethod
    def validate_data_file(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(
                f"Data file not found: {v}\n"
                "Please check the path in config.yaml or pass the correct path."
            )
        suffix = v.suffix.lower()
        if suffix not in (".csv", ".xlsx", ".xls"):
            raise ValueError(
                f"Unsupported file type: {suffix}\nSupported formats: .csv, .xlsx, .xls"
            )
        return v

    @model_validator(mode="after")
    def derive_client_fields(self):
        if self.client_id is None:
            match = re.match(r"^(\d+)", self.data_file.stem)
            if match:
                self.client_id = match.group(1)
            else:
                self.client_id = "unknown"
                logger.warning(
                    "Could not extract client ID from filename '%s'. Set client_id in config.yaml.",
                    self.data_file.name,
                )
        if self.client_name is None:
            self.client_name = f"Client {self.client_id}"
        return self

    @classmethod
    def from_yaml(cls, config_path: Path = DEFAULT_CONFIG_PATH, **cli_overrides) -> "Settings":
        """Load settings from YAML file with CLI overrides.

        Priority: CLI args > config.yaml > defaults.
        """
        raw: dict = {}
        if config_path.exists():
            with open(config_path) as f:
                raw = yaml.safe_load(f) or {}
            logger.info("Loaded config from %s", config_path)

        for key, value in cli_overrides.items():
            if value is not None:
                raw[key] = str(value) if isinstance(value, Path) else value

        try:
            return cls(**raw)
        except Exception as e:
            raise ConfigError(
                f"Configuration error: {e}\n\n"
                "Fix your config.yaml or pass the correct options on the command line.\n"
                "Example: python -m ics_analysis data/your_file.xlsx"
            ) from e

    @classmethod
    def from_args(cls, data_file: Path, **kwargs) -> "Settings":
        """Create settings directly from arguments (no YAML needed)."""
        try:
            return cls(data_file=data_file, **kwargs)
        except Exception as e:
            raise ConfigError(f"Configuration error: {e}") from e
