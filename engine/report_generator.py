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
        group_calculated_amounts = None
        parent_calculated_amounts = None
        if upload_dir is not None:
            kwargs = dict(calculator_kwargs or {})
            explicit_subject_balance_prefix = "subject_balance_prefix" in kwargs
            if report_period:
                kwargs.setdefault("report_period", report_period)
            if explicit_subject_balance_prefix:
                inferred_prefix = _infer_subject_balance_prefix(
                    institution_name=institution_name,
                    institution_code=institution_code,
                    institution_scope=institution_scope,
                )
                if inferred_prefix and not kwargs.get("subject_balance_prefix"):
                    kwargs["subject_balance_prefix"] = inferred_prefix
            initial_values = dict(reusable_metrics or {})
            initial_values.update(kwargs.pop("initial_values", {}) or {})
            if initial_values:
                kwargs["initial_values"] = initial_values
            if explicit_subject_balance_prefix and kwargs.get("subject_balance_prefix"):
                calculated_amounts = RuleCalculator(upload_dir, **kwargs).calculate(source_df)
            else:
                group_kwargs = dict(kwargs)
                parent_kwargs = dict(kwargs)
                group_kwargs["subject_balance_prefix"] = "1-1-"
                parent_kwargs["subject_balance_prefix"] = "1-12-"
                group_calculated_amounts = RuleCalculator(upload_dir, **group_kwargs).calculate(source_df)
                parent_calculated_amounts = RuleCalculator(upload_dir, **parent_kwargs).calculate(source_df)

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

        if (
            group_calculated_amounts is not None
            and parent_calculated_amounts is not None
            and "计算金额" in group_calculated_amounts.columns
            and "计算金额" in parent_calculated_amounts.columns
        ):
            group_amount = _calculated_amount_series(group_calculated_amounts["计算金额"])
            parent_amount = _calculated_amount_series(parent_calculated_amounts["计算金额"])
            if _is_other_assets_report(report_config):
                _apply_balance_sheet_a0017_pair_override(
                    source_df,
                    group_amount,
                    parent_amount,
                    upload_dir,
                    report_period,
                )
            report_df["计算状态"] = _merge_calculation_status(
                group_calculated_amounts,
                parent_calculated_amounts,
            )
            report_df["计算说明"] = _merge_calculation_message(
                group_calculated_amounts,
                parent_calculated_amounts,
            )
        elif calculated_amounts is not None and "计算金额" in calculated_amounts.columns:
            group_amount = _calculated_amount_series(calculated_amounts["计算金额"])
            parent_amount = group_amount.copy()
            if _is_other_assets_report(report_config):
                _apply_balance_sheet_a0017_single_institution_override(
                    source_df,
                    group_amount,
                    parent_amount,
                    upload_dir,
                    report_period,
                    institution_name=institution_name,
                    institution_code=institution_code,
                    institution_scope=institution_scope,
                )
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


def _merge_calculation_status(group_df: pd.DataFrame, parent_df: pd.DataFrame) -> pd.Series:
    group_status = group_df.get("计算状态", pd.Series(["未计算"] * len(group_df), index=group_df.index)).astype(str)
    parent_status = parent_df.get("计算状态", pd.Series(["未计算"] * len(parent_df), index=parent_df.index)).astype(str)
    return [
        "已计算" if group == "已计算" and parent == "已计算" else f"集团{group}/本行{parent}"
        for group, parent in zip(group_status, parent_status)
    ]


def _merge_calculation_message(group_df: pd.DataFrame, parent_df: pd.DataFrame) -> pd.Series:
    group_message = group_df.get("计算说明", pd.Series([""] * len(group_df), index=group_df.index)).astype(str)
    parent_message = parent_df.get("计算说明", pd.Series([""] * len(parent_df), index=parent_df.index)).astype(str)
    return [
        group if group == parent else f"集团：{group}；本行：{parent}"
        for group, parent in zip(group_message, parent_message)
    ]


def _is_other_assets_report(report_config: dict[str, Any]) -> bool:
    report_name = _normalize_text(
        report_config.get("output_prefix") or report_config.get("display_name") or ""
    )
    return "其他资产" in report_name


def _apply_balance_sheet_a0017_pair_override(
    source_df: pd.DataFrame,
    group_amount: pd.Series,
    parent_amount: pd.Series,
    upload_dir: str | None,
    report_period: str | None,
) -> None:
    if "指标编码" not in source_df.columns:
        return
    mask = source_df["指标编码"].astype(str).eq("A0017")
    if not mask.any():
        return
    override = _load_balance_sheet_a0017_amount(upload_dir, report_period)
    if override is None:
        return
    group_value, parent_value = override
    group_amount.loc[mask] = group_value
    parent_amount.loc[mask] = parent_value


def _apply_balance_sheet_a0017_single_institution_override(
    source_df: pd.DataFrame,
    group_amount: pd.Series,
    parent_amount: pd.Series,
    upload_dir: str | None,
    report_period: str | None,
    institution_name: str | None = None,
    institution_code: str | None = None,
    institution_scope: str | None = None,
) -> None:
    if "指标编码" not in source_df.columns:
        return
    mask = source_df["指标编码"].astype(str).eq("A0017")
    if not mask.any():
        return
    override = _load_balance_sheet_a0017_amount(upload_dir, report_period)
    if override is None:
        return
    group_value, parent_value = override
    prefix = _infer_subject_balance_prefix(
        institution_name=institution_name,
        institution_code=institution_code,
        institution_scope=institution_scope,
    )
    selected_value = parent_value if prefix == "1-12-" else group_value
    group_amount.loc[mask] = selected_value
    parent_amount.loc[mask] = selected_value


def _load_balance_sheet_a0017_amount(
    upload_dir: str | None,
    report_period: str | None,
) -> tuple[float, float] | None:
    from engine.rule_parser import find_report_rules

    rule_file = _find_rule_file(upload_dir)
    if rule_file is None:
        return None
    try:
        balance_rules = find_report_rules(rule_file, "合并及母公司资产负债表")
    except Exception:
        return None
    if balance_rules.empty or "指标编码" not in balance_rules.columns:
        return None
    row_df = balance_rules.loc[balance_rules["指标编码"].astype(str).eq("A0017")]
    if row_df.empty:
        return None
    group_result = RuleCalculator(
        upload_dir or "data/upload",
        subject_balance_prefix="1-1-",
        report_period=report_period,
    ).calculate(row_df)
    parent_result = RuleCalculator(
        upload_dir or "data/upload",
        subject_balance_prefix="1-12-",
        report_period=report_period,
    ).calculate(row_df)
    group_value = pd.to_numeric(group_result.get("计算金额"), errors="coerce").iloc[0]
    parent_value = pd.to_numeric(parent_result.get("计算金额"), errors="coerce").iloc[0]
    if pd.isna(group_value) or pd.isna(parent_value):
        return None
    return float(group_value), float(parent_value)


def _find_rule_file(upload_dir: str | None) -> str | None:
    from pathlib import Path

    base = Path(upload_dir or "data/upload")
    if not base.exists():
        return None
    matches = sorted(base.glob("2-1-*.xlsx"), key=lambda path: path.stat().st_mtime, reverse=True)
    return str(matches[0]) if matches else None


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


def _calculated_amount_series(series: pd.Series) -> pd.Series:
    numeric_values = pd.to_numeric(series, errors="coerce")
    result = numeric_values.astype(object)
    for index, value in series.items():
        if pd.notna(numeric_values.loc[index]):
            continue
        if pd.isna(value):
            result.loc[index] = pd.NA
        else:
            result.loc[index] = value
    return result


def _convert_amount_unit(
    amount_series: pd.Series,
    source_df: pd.DataFrame,
    amount_column: str | None,
) -> pd.Series:
    unit = _detect_amount_unit(source_df, amount_column)
    if unit == "yuan":
        return _scale_numeric_amount_series(amount_series, 1 / 1000)
    if unit == "ten_thousand_yuan":
        return _scale_numeric_amount_series(amount_series, 10)
    return amount_series


def _scale_numeric_amount_series(amount_series: pd.Series, factor: float) -> pd.Series:
    numeric_values = pd.to_numeric(amount_series, errors="coerce")
    result = amount_series.copy()
    numeric_mask = numeric_values.notna()
    result.loc[numeric_mask] = numeric_values.loc[numeric_mask] * factor
    return result


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
