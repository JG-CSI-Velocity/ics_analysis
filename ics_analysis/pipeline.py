"""Pipeline orchestrator shared by CLI and Jupyter/REPL."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd
import plotly.graph_objects as go

from ics_analysis.analyses import run_all_analyses
from ics_analysis.analyses.base import AnalysisResult
from ics_analysis.charts import create_charts
from ics_analysis.data_loader import load_data
from ics_analysis.settings import Settings
from ics_analysis.utils import get_ics_accounts, get_ics_stat_o, get_ics_stat_o_debit

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Container for all pipeline outputs."""

    settings: Settings
    df: pd.DataFrame
    analyses: list[AnalysisResult] = field(default_factory=list)
    charts: dict[str, go.Figure] = field(default_factory=dict)


def run_pipeline(
    settings: Settings,
    on_progress: Callable[[int, int, str], None] | None = None,
) -> PipelineResult:
    """Execute the full analysis pipeline: load -> filter -> analyze -> chart.

    Args:
        settings: Application configuration.
        on_progress: Optional callback(step, total, message) for UI progress.
    """
    # Step 1: Load data
    if on_progress:
        on_progress(0, 4, "Loading data...")
    df = load_data(settings)

    # Step 2: Build pre-filtered DataFrames
    if on_progress:
        on_progress(1, 4, "Filtering data...")
    ics_all = get_ics_accounts(df)
    ics_stat_o = get_ics_stat_o(df)
    ics_stat_o_debit = get_ics_stat_o_debit(df)
    logger.info(
        "Filters: %d ICS total, %d stat O, %d stat O + debit",
        len(ics_all),
        len(ics_stat_o),
        len(ics_stat_o_debit),
    )

    # Step 3: Run analyses
    if on_progress:
        on_progress(2, 4, "Running analyses...")
    analyses = run_all_analyses(
        df,
        ics_all,
        ics_stat_o,
        ics_stat_o_debit,
        settings,
        on_progress=None,
    )
    successful = [a for a in analyses if a.error is None]
    failed = [a for a in analyses if a.error is not None]
    if failed:
        for a in failed:
            logger.warning("Skipped: %s (%s)", a.name, a.error)
    logger.info("%d/%d analyses completed", len(successful), len(analyses))

    # Step 4: Build charts
    if on_progress:
        on_progress(3, 4, "Building charts...")
    charts: dict[str, go.Figure] = {}
    try:
        charts = create_charts(analyses, settings)
        logger.info("Built %d charts", len(charts))
    except Exception as e:
        logger.error("Chart generation failed: %s", e, exc_info=True)

    return PipelineResult(
        settings=settings,
        df=df,
        analyses=analyses,
        charts=charts,
    )


def export_outputs(result: PipelineResult) -> list[Path]:
    """Export pipeline results to configured output formats.

    Returns list of generated file paths.
    """
    settings = result.settings
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []
    date_str = datetime.now().strftime("%Y%m%d")
    client_id = settings.client_id or "unknown"

    if settings.outputs.excel:
        try:
            from ics_analysis.exports.excel import write_excel_report

            path = settings.output_dir / f"{client_id}_ICS_Report_{date_str}.xlsx"
            write_excel_report(
                settings,
                result.df,
                result.analyses,
                charts=result.charts,
                output_path=path,
            )
            generated.append(path)
        except Exception as e:
            logger.error("Excel report failed: %s", e, exc_info=True)

    if settings.outputs.powerpoint:
        try:
            from ics_analysis.exports.pptx import write_pptx_report

            path = settings.output_dir / f"{client_id}_ICS_Presentation_{date_str}.pptx"
            write_pptx_report(
                settings,
                result.analyses,
                charts=result.charts,
                output_path=path,
            )
            generated.append(path)
        except Exception as e:
            logger.error("PowerPoint report failed: %s", e, exc_info=True)

    return generated
