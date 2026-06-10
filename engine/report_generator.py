from typing import Any

import pandas as pd

from engine.rule_calculator import RuleCalculator


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


def build_report_from_rules(
    rule_df: pd.DataFrame,
    report_config: dict[str, Any],
    upload_dir: str | None = None,
    calculator_kwargs: dict[str, Any] | None = None,
    institution_name: str | None = None,
    institution_code: str | None = None,
    institution_scope: str | None = None,
    report_period: str | None = None,
    reusable_metrics: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Build a standard report DataFrame from parsed rule rows."""
    if rule_df is None:
        raise ValueError("rule_df 不能为空。")
    if not isinstance(rule_df, pd.DataFrame):
        raise TypeError("rule_df 必须是 pandas DataFrame。")
    if rule_df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    try:
        source_df = _normalize_columns(rule_df)
        calculated_amounts = None
        if upload_dir is not None:
            kwargs = dict(calculator_kwargs or {})
            if report_period:
                kwargs.setdefault("report_period", report_period)
            if "subject_balance_prefix" not in kwargs:
                inferred_prefix = _infer_subject_balance_prefix(
                    institution_name=institution_name,
                    institution_code=institution_code,
                    institution_scope=institution_scope,
                )
                if inferred_prefix:
                    kwargs["subject_balance_prefix"] = inferred_prefix
            initial_values = dict(reusable_metrics or {})
            initial_values.update(kwargs.pop("initial_values", {}) or {})
            if initial_values:
                kwargs["initial_values"] = initial_values
            calculated_amounts = RuleCalculator(upload_dir, **kwargs).calculate(source_df)

        group_amount_column = _find_amount_column(source_df, GROUP_AMOUNT_CANDIDATES, "集团")
        parent_amount_column = _find_amount_column(source_df, PARENT_AMOUNT_CANDIDATES, "本行")

        report_df = pd.DataFrame()
        report_df["序号"] = range(1, len(source_df) + 1)
        if report_period:
            report_df["期间"] = str(report_period)
        if institution_scope:
            report_df["机构口径"] = str(institution_scope)
        if institution_code:
            report_df["机构编码"] = str(institution_code)
        if institution_name:
            report_df["机构"] = institution_name

        for column in BASE_COLUMNS:
            report_df[column] = source_df[column] if column in source_df.columns else pd.NA
        report_df["报表名称"] = report_config.get("display_name", report_df["报表名称"])

        if calculated_amounts is not None and "计算金额" in calculated_amounts.columns:
            group_amount = pd.to_numeric(calculated_amounts["计算金额"], errors="coerce")
            parent_amount = group_amount.copy()
            report_df["计算状态"] = calculated_amounts["计算状态"]
            report_df["计算说明"] = calculated_amounts["计算说明"]
        else:
            group_amount = _amount_series(source_df, group_amount_column)
            parent_amount = _amount_series(source_df, parent_amount_column)

        report_df["生成金额-集团"] = _convert_amount_unit(
            group_amount,
            source_df,
            group_amount_column,
        )
        report_df["生成金额-本行"] = _convert_amount_unit(
            parent_amount,
            source_df,
            parent_amount_column,
        )

        extra_columns = [column for column in ["计算状态", "计算说明"] if column in report_df.columns]
        leading_columns = [
            column
            for column in ["期间", "机构口径", "机构编码", "机构"]
            if column in report_df.columns
        ]
        return report_df[leading_columns + OUTPUT_COLUMNS + extra_columns]
    except Exception as exc:
        display_name = report_config.get("display_name", "报表")
        raise ValueError(f"生成{display_name}失败：{exc}") from exc


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [_normalize_text(column) for column in normalized.columns]
    return normalized


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split())


def _infer_subject_balance_prefix(
    institution_name: str | None = None,
    institution_code: str | None = None,
    institution_scope: str | None = None,
) -> str | None:
    context_text = " ".join(
        _normalize_text(value)
        for value in (institution_name, institution_code, institution_scope)
        if value
    )
    if any(keyword in context_text for keyword in ("本行", "母行", "PARENT")):
        return "1-12-"
    if any(keyword in context_text for keyword in ("集团", "合并", "GROUP")):
        return "1-1-"
    if any(keyword in context_text for keyword in ("子公司", "SUBSIDIARY")):
        return "1-5-"
    return None


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
