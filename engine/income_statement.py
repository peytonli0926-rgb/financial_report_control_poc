import pandas as pd

from engine.report_generator import OUTPUT_COLUMNS, build_report_from_rules


def build_income_statement(rule_df: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible wrapper for the generic report generation engine."""
    return build_report_from_rules(
        rule_df,
        {"display_name": "利润表", "output_prefix": "利润表"},
    )
