from typing import Any

import pandas as pd


OUTPUT_COLUMNS = [
    "报表名称",
    "指标编码",
    "指标名称",
    "数据来源",
    "指标类型",
    "加工规则",
    "生成金额-集团",
    "PDF披露金额-集团",
    "差异金额-集团",
    "是否一致-集团",
    "差异原因-集团",
    "生成金额-本行",
    "PDF披露金额-本行",
    "差异金额-本行",
    "是否一致-本行",
    "差异原因-本行",
    "PDF来源页码",
    "PDF原始行文本",
]

BALANCE_COLUMNS = [
    "报表名称",
    "指标编码",
    "指标名称",
    "数据来源",
    "指标类型",
    "加工规则",
    "生成金额-集团",
    "生成金额-本行",
]

PDF_COLUMNS = [
    "指标名称",
    "PDF披露金额-集团",
    "PDF披露金额-本行",
    "PDF来源页码",
    "PDF原始行文本",
]


def validate_with_pdf(
    balance_df: pd.DataFrame,
    pdf_df: pd.DataFrame,
    tolerance: float = 1,
) -> pd.DataFrame:
    """Compare generated balance sheet amounts with PDF disclosed amounts."""
    if balance_df is None:
        raise ValueError("balance_df 不能为空。")
    if pdf_df is None:
        raise ValueError("pdf_df 不能为空。")
    if not isinstance(balance_df, pd.DataFrame):
        raise TypeError("balance_df 必须是 pandas DataFrame。")
    if not isinstance(pdf_df, pd.DataFrame):
        raise TypeError("pdf_df 必须是 pandas DataFrame。")
    if tolerance < 0:
        raise ValueError("tolerance 不能小于 0。")

    try:
        normalized_balance_df = _prepare_balance_df(balance_df)
        normalized_pdf_df = _prepare_pdf_df(pdf_df)

        merged_df = normalized_balance_df.merge(
            normalized_pdf_df,
            on="指标名称",
            how="left",
        )

        merged_df["生成金额-集团"] = _to_number(merged_df["生成金额-集团"])
        merged_df["生成金额-本行"] = _to_number(merged_df["生成金额-本行"])
        merged_df["PDF披露金额-集团"] = _to_number(merged_df["PDF披露金额-集团"])
        merged_df["PDF披露金额-本行"] = _to_number(merged_df["PDF披露金额-本行"])

        merged_df["差异金额-集团"] = (
            merged_df["生成金额-集团"] - merged_df["PDF披露金额-集团"]
        )
        merged_df["差异金额-本行"] = (
            merged_df["生成金额-本行"] - merged_df["PDF披露金额-本行"]
        )

        group_results = merged_df.apply(
            lambda row: _judge_result(
                generated_amount=row["生成金额-集团"],
                pdf_amount=row["PDF披露金额-集团"],
                diff=row["差异金额-集团"],
                tolerance=tolerance,
            ),
            axis=1,
        )
        parent_results = merged_df.apply(
            lambda row: _judge_result(
                generated_amount=row["生成金额-本行"],
                pdf_amount=row["PDF披露金额-本行"],
                diff=row["差异金额-本行"],
                tolerance=tolerance,
            ),
            axis=1,
        )

        merged_df["是否一致-集团"] = [result["status"] for result in group_results]
        merged_df["差异原因-集团"] = [result["reason"] for result in group_results]
        merged_df["是否一致-本行"] = [result["status"] for result in parent_results]
        merged_df["差异原因-本行"] = [result["reason"] for result in parent_results]

        return merged_df[OUTPUT_COLUMNS]
    except Exception as exc:
        raise ValueError(f"PDF 披露金额校验失败：{exc}") from exc


def validate_report_with_pdf(
    report_df: pd.DataFrame,
    pdf_df: pd.DataFrame,
    tolerance: float = 1,
) -> pd.DataFrame:
    """Generic report-to-PDF amount validation entry point."""
    return validate_with_pdf(report_df, pdf_df, tolerance)


def _prepare_balance_df(balance_df: pd.DataFrame) -> pd.DataFrame:
    df = _normalize_columns(balance_df)
    if "指标名称" not in df.columns:
        raise ValueError("资产负债表生成结果缺少“指标名称”列。")

    prepared = pd.DataFrame()
    for column in BALANCE_COLUMNS:
        prepared[column] = df[column] if column in df.columns else pd.NA

    prepared["指标名称"] = prepared["指标名称"].map(_normalize_item_name)
    prepared = prepared[prepared["指标名称"] != ""]
    return prepared.reset_index(drop=True)


def _prepare_pdf_df(pdf_df: pd.DataFrame) -> pd.DataFrame:
    df = _normalize_columns(pdf_df)
    if "指标名称" not in df.columns:
        raise ValueError("PDF 解析结果缺少“指标名称”列。")

    prepared = pd.DataFrame()
    for column in PDF_COLUMNS:
        prepared[column] = df[column] if column in df.columns else pd.NA

    prepared["指标名称"] = prepared["指标名称"].map(_normalize_item_name)
    prepared = prepared[prepared["指标名称"] != ""]
    prepared = prepared.drop_duplicates(subset=["指标名称"], keep="first")
    return prepared.reset_index(drop=True)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [_normalize_text(column) for column in normalized.columns]
    return normalized


def _normalize_item_name(value: Any) -> str:
    if pd.isna(value):
        return ""
    return _normalize_text(value)


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split())


def _is_non_pdf_amount_item(item_name: str) -> bool:
    text = str(item_name)
    return "\u7f34\u5b58\u6bd4\u7387" in text

def _to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.map(_clean_number), errors="coerce")


def _clean_number(value: Any) -> Any:
    if pd.isna(value):
        return pd.NA
    if not isinstance(value, str):
        return value

    cleaned = (
        value.strip()
        .replace(",", "")
        .replace("，", "")
        .replace("人民币", "")
        .replace("千元", "")
        .replace("元", "")
    )
    if cleaned in {"", "不适用", "nan", "NaN", "None"}:
        return pd.NA
    if cleaned in {"-", "－", "—"}:
        return 0
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = f"-{cleaned[1:-1]}"
    return cleaned


def _judge_result(
    generated_amount: Any,
    pdf_amount: Any,
    diff: Any,
    tolerance: float,
) -> dict[str, str]:
    if pd.isna(pdf_amount):
        return {
            "status": "未提取到PDF披露值",
            "reason": "PDF解析未匹配到对应项目，需人工复核",
        }

    if pd.isna(generated_amount) or pd.isna(diff):
        return {
            "status": "不一致",
            "reason": "需检查加工规则、审计调整、合并抵消或PDF识别",
        }

    if abs(float(diff)) <= tolerance:
        return {
            "status": "一致",
            "reason": "金额一致或四舍五入差异",
        }

    return {
        "status": "不一致",
        "reason": "需检查加工规则、审计调整、合并抵消或PDF识别",
    }
