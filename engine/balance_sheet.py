from typing import Any

import pandas as pd

from engine.report_generator import build_report_from_rules


OUTPUT_COLUMNS = [
    "序号",
    "报表名称",
    "指标编码",
    "指标名称",
    "数据来源",
    "指标类型",
    "加工规则",
    "生成金额-集团",
    "生成金额-本行",
]

BASE_COLUMNS = [
    "报表名称",
    "指标编码",
    "指标名称",
    "数据来源",
    "指标类型",
    "加工规则",
]

GROUP_AMOUNT_CANDIDATES = ["集团金额", "合并金额", "生成金额-集团", "金额-集团"]
PARENT_AMOUNT_CANDIDATES = ["本行金额", "母公司金额", "母行金额", "生成金额-本行", "金额-本行"]


def build_balance_sheet(rule_df: pd.DataFrame) -> pd.DataFrame:
    """Build a standard balance sheet DataFrame from parsed rule rows."""
    return build_report_from_rules(
        rule_df,
        {"display_name": "资产负债表", "output_prefix": "资产负债表"},
    )


def check_balance(balance_df: pd.DataFrame) -> dict[str, Any]:
    """Check whether assets equal liabilities plus equity for group and parent."""
    if balance_df is None:
        raise ValueError("balance_df 不能为空。")
    if not isinstance(balance_df, pd.DataFrame):
        raise TypeError("balance_df 必须是 pandas DataFrame。")

    try:
        if balance_df.empty:
            return {
                "group_diff": None,
                "parent_diff": None,
                "group_balanced": False,
                "parent_balanced": False,
            }

        normalized_df = _normalize_columns(balance_df)
        asset_row = _find_total_row(normalized_df, ["资产总计"])
        liability_equity_row = _find_total_row(
            normalized_df,
            [
                "负债和股东权益总计",
                "负债及股东权益总计",
                "负债和所有者权益总计",
                "负债及所有者权益总计",
            ],
        )

        group_diff = _calculate_diff(
            asset_row,
            liability_equity_row,
            "生成金额-集团",
        )
        parent_diff = _calculate_diff(
            asset_row,
            liability_equity_row,
            "生成金额-本行",
        )

        return {
            "group_diff": group_diff,
            "parent_diff": parent_diff,
            "group_balanced": _is_balanced(group_diff),
            "parent_balanced": _is_balanced(parent_diff),
        }
    except Exception as exc:
        raise ValueError(f"资产负债平衡检查失败：{exc}") from exc


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [_normalize_text(column) for column in normalized.columns]
    return normalized


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split())


def _find_amount_column(
    df: pd.DataFrame,
    candidates: list[str],
    keyword: str,
) -> str | None:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate

    for column in df.columns:
        column_text = _normalize_text(column)
        if keyword in column_text and "金额" in column_text:
            return column

    return None


def _amount_series(df: pd.DataFrame, amount_column: str | None) -> pd.Series:
    if amount_column is None:
        return pd.Series([pd.NA] * len(df), index=df.index, dtype="Float64")

    return pd.to_numeric(
        df[amount_column].map(_clean_amount_value),
        errors="coerce",
    )


def _clean_amount_value(value: Any) -> Any:
    if pd.isna(value):
        return pd.NA
    if not isinstance(value, str):
        return value

    cleaned = (
        value.strip()
        .replace(",", "")
        .replace("，", "")
        .replace("人民币", "")
        .replace("元", "")
        .replace("千", "")
    )
    if cleaned in {"", "-", "—", "不适用", "nan", "NaN"}:
        return pd.NA
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = f"-{cleaned[1:-1]}"
    return cleaned


def _convert_amount_unit(
    amount_series: pd.Series,
    source_df: pd.DataFrame,
    amount_column: str | None,
) -> pd.Series:
    unit = _detect_amount_unit(source_df, amount_column)
    if unit == "yuan":
        return amount_series / 1000
    if unit == "ten_thousand_yuan":
        return amount_series * 10
    return amount_series


def _detect_amount_unit(source_df: pd.DataFrame, amount_column: str | None) -> str:
    """Detect amount unit. Unknown values are treated as already in thousand yuan."""
    texts: list[str] = []
    if amount_column is not None:
        texts.append(_normalize_text(amount_column))

    sample_values = source_df.head(20).astype(str).to_numpy().ravel().tolist()
    texts.extend(_normalize_text(value) for value in sample_values)
    joined_text = " ".join(texts)

    if "千元" in joined_text or "人民币千元" in joined_text:
        return "thousand_yuan"
    if "万元" in joined_text:
        return "ten_thousand_yuan"
    if "元" in joined_text:
        return "yuan"
    return "thousand_yuan"


def _find_total_row(df: pd.DataFrame, names: list[str]) -> pd.Series | None:
    if "指标名称" not in df.columns:
        return None

    name_series = df["指标名称"].fillna("").astype(str).map(_normalize_text)
    mask = name_series.apply(lambda value: any(name in value for name in names))
    matched = df.loc[mask]
    if matched.empty:
        return None

    return matched.iloc[-1]


def _calculate_diff(
    asset_row: pd.Series | None,
    liability_equity_row: pd.Series | None,
    amount_column: str,
) -> float | None:
    if asset_row is None or liability_equity_row is None:
        return None

    asset_total = pd.to_numeric(asset_row.get(amount_column), errors="coerce")
    liability_equity_total = pd.to_numeric(
        liability_equity_row.get(amount_column),
        errors="coerce",
    )
    if pd.isna(asset_total) or pd.isna(liability_equity_total):
        return None

    return float(asset_total - liability_equity_total)


def _is_balanced(diff: float | None, tolerance: float = 0.01) -> bool:
    if diff is None:
        return False
    return abs(diff) <= tolerance
