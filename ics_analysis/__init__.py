"""ICS (Insured Cash Sweep) account analysis and reporting tool."""

from pathlib import Path
from typing import Callable

__version__ = "1.0.0"


def run_client(
    data_file: str | Path,
    output_dir: str | Path = "output/",
    client_id: str | None = None,
    client_name: str | None = None,
    cohort_start: str = "2025-01",
    ics_not_in_dump: int = 0,
    on_progress: Callable | None = None,
):
    """Convenience function for Jupyter/REPL usage.

    Example:
        from ics_analysis import run_client
        result = run_client("data/1453_oddd.xlsx", client_id="1453")
        result.analyses  # list of AnalysisResult
        result.charts    # dict of Plotly figures
    """
    from ics_analysis.pipeline import export_outputs, run_pipeline
    from ics_analysis.settings import Settings

    settings = Settings.from_args(
        data_file=Path(data_file),
        output_dir=Path(output_dir),
        client_id=client_id,
        client_name=client_name,
        cohort_start=cohort_start,
        ics_not_in_dump=ics_not_in_dump,
    )

    result = run_pipeline(settings, on_progress=on_progress)
    export_outputs(result)

    return result
