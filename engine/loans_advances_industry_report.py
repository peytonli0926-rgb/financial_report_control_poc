from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

from engine.trade_finance_interest_adjustment import find_latest_impairment_file


THOUSAND = Decimal("1000")
TARGET_BIZ_TYPE = "01"
B0326_EXTRA_PREFIX = "5-7-3-1-20251231"
B0326_EXTRA_BUSI_TYPE = "01004"
B0326_EXTRA_AMOUNT_COLUMNS = ("CURRENT_BALNC", "ACCR_INTEREST")

INDUSTRY_BY_CODE = {
    "B0313": ("租赁和商务服务业",),
    "B0314": ("制造业",),
    "B0315": ("水利、环境和公共设施管理业",),
    "B0316": ("交通运输、仓储和邮政业",),
    "B0317": ("电力、热力、燃气及水生产和供应业",),
    "B0318": ("批发和零售业",),
    "B0319": ("建筑业",),
    "B0320": ("卫生和社会工作",),
    "B0321": ("房地产业",),
    "B0322": ("农、林、牧、渔业",),
    "B0323": ("教育",),
    "B0324": ("文化、体育和娱乐业",),
    "B0325": ("信息传输、软件和信息技术服务业",),
    "B0326": ("金融业",),
    "B0327": ("科学研究和技术服务业",),
    "B0328": ("住宿和餐饮业", "居民服务、修理和其他服务业", "采矿业", "公共管理、社会保障和社会组织"),
}


def apply_loans_advances_industry_amounts(
    report_df: pd.DataFrame,
    upload_dir: str | Path,
) -> pd.DataFrame:
    if report_df is None or report_df.empty:
        return report_df

    source_file = find_latest_impairment_file(upload_dir)
    if source_file is None:
        return _mark_unavailable(report_df, "未找到 5-7-3-2-20251231 减值明细文件")

    detail_df = _load_detail_df(source_file)
    industry_amounts = _industry_amounts(detail_df)
    b0326_extra_file = _find_latest_file(upload_dir, B0326_EXTRA_PREFIX)
    b0326_extra_amount = _b0326_extra_amount(b0326_extra_file) if b0326_extra_file else Decimal("0")

    result = report_df.copy()
    code_column = _find_column(result, ["指标编码"])
    group_column = _find_column(result, ["生成金额-集团"])
    parent_column = _find_column(result, ["生成金额-本行"])
    status_column = _find_column(result, ["计算状态"])
    note_column = _find_column(result, ["计算说明"])
    source_column = _find_column(result, ["数据来源"])
    type_column = _find_column(result, ["指标类型"])
    rule_column = _find_column(result, ["加工规则"])

    if not code_column or not group_column or not parent_column:
        return result

    for item_code, default_industries in INDUSTRY_BY_CODE.items():
        mask = result[code_column].astype(str) == item_code
        if not mask.any():
            continue
        rule_text_from_file = str(result.loc[mask, rule_column].iloc[0]) if rule_column else ""
        effective_industries = _industries_from_rule(rule_text_from_file) or list(default_industries)
        if item_code == "B0326" and _is_latest_b0326_rule(rule_text_from_file):
            amount_yuan, b0326_note = _calculate_latest_b0326_amount(
                upload_dir,
                detail_df,
                b0326_extra_file,
            )
        else:
            amount_yuan = sum((industry_amounts.get(industry, Decimal("0")) for industry in effective_industries), Decimal("0"))
            b0326_note = ""
            if item_code == "B0326":
                amount_yuan += b0326_extra_amount
        amount_thousand = _to_thousand_yuan(amount_yuan)
        result.loc[mask, group_column] = amount_thousand
        result.loc[mask, parent_column] = amount_thousand
        if status_column:
            result.loc[mask, status_column] = "已计算"
        if source_column:
            source_names = source_file.name
            if item_code == "B0326" and b0326_extra_file is not None:
                source_names = f"{source_names}; {b0326_extra_file.name}"
            result.loc[mask, source_column] = source_names
        if type_column:
            result.loc[mask, type_column] = "明细汇总"
        if note_column:
            display_industries = ["空值" if industry == "" else industry for industry in effective_industries]
            note_text = f"行业范围：{', '.join(display_industries)}；金额单位已转换为千元。"
            if "" in effective_industries:
                blank_amount = industry_amounts.get("", Decimal("0"))
                note_text += f" 其中IND_FIR_GRA_CAT_NM为空金额：{_to_thousand_yuan(blank_amount)}千元。"
            if item_code == "B0326":
                if b0326_note:
                    note_text = b0326_note
                else:
                    note_text += f" 5-7-3-1追加金额：{_to_thousand_yuan(b0326_extra_amount)}千元。"
                    if b0326_extra_file is None:
                        note_text += " 未找到5-7-3-1文件，追加金额按0处理。"
            result.loc[mask, note_column] = note_text
    return result


def _load_detail_df(source_file: Path) -> pd.DataFrame:
    df = pd.read_excel(source_file, sheet_name="20251231", dtype=object, engine="openpyxl")
    required = {"BIZ_TYPE", "IND_FIR_GRA_CAT_NM", "CURRENT_BALNC", "ACCR_INTEREST"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"5-7-3-2减值明细缺少列：{', '.join(sorted(missing))}")
    if "利息调整" not in df.columns:
        df["利息调整"] = 0
    return df


def _industry_amounts(df: pd.DataFrame) -> dict[str, Decimal]:
    data = df[df["BIZ_TYPE"].map(_normalize_code) == TARGET_BIZ_TYPE].copy()
    data["_industry"] = data["IND_FIR_GRA_CAT_NM"].map(_clean_text)
    data["_amount"] = data.apply(
        lambda row: (
            _to_decimal(row.get("CURRENT_BALNC"))
            + _to_decimal(row.get("ACCR_INTEREST"))
            - _to_decimal(row.get("利息调整"))
        ),
        axis=1,
    )
    amounts: dict[str, Decimal] = {}
    for industry, values in data.groupby("_industry")["_amount"]:
        amounts[str(industry)] = sum(values, Decimal("0"))
    return amounts


def _industries_from_rule(rule_text: str) -> list[str]:
    industries: list[str] = []
    for value in re.findall(r"IND_FIR_GRA_CAT_NM\s*=\s*['\"]([^'\"]+)['\"]", rule_text, flags=re.IGNORECASE):
        _append_unique(industries, _clean_text(value))

    for group_text in re.findall(r"IND_FIR_GRA_CAT_NM\s+IN\s*\(([^)]*)\)", rule_text, flags=re.IGNORECASE):
        for value in re.findall(r"['\"]([^'\"]+)['\"]", group_text):
            _append_unique(industries, _clean_text(value))

    if _rule_includes_blank_industry(rule_text):
        _append_unique(industries, "")
    return industries


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _rule_includes_blank_industry(rule_text: str) -> bool:
    normalized = _clean_text(rule_text).upper()
    return any(
        token in normalized
        for token in (
            "IND_FIR_GRA_CAT_NMISNULL",
            "IND_FIR_GRA_CAT_NM=NULL",
            "IND_FIR_GRA_CAT_NM为空",
            "IND_FIR_GRA_CAT_NM空值",
            "IND_FIR_GRA_CAT_NM为NULL",
        )
    )


def _is_latest_b0326_rule(rule_text: str) -> bool:
    normalized = _clean_text(rule_text).upper()
    return "14011201" in normalized and "BUSI_TYPE='01004'" in normalized


def _calculate_latest_b0326_amount(
    upload_dir: str | Path,
    detail_df: pd.DataFrame,
    b0326_extra_file: Path | None,
) -> tuple[Decimal, str]:
    financial_detail = _detail_amount(
        detail_df,
        industry="金融业",
        adjustment_sign=Decimal("-1"),
    )
    busi_01004 = _b0326_extra_amount(b0326_extra_file) if b0326_extra_file else Decimal("0")
    subject_credit_net = _subject_14011201_credit_net_yuan(upload_dir)
    biz01_interest_adjustment = _detail_biz01_interest_adjustment(detail_df)
    amount = (
        financial_detail
        + busi_01004
        - subject_credit_net
        + biz01_interest_adjustment
    )
    note = (
        "按最新B0326规则计算，金额单位已转换为千元。"
        f" 5-7-3-2金融业减利息调整：{_to_thousand_yuan(financial_detail)}千元；"
        f"5-7-3-1 BUSI_TYPE=01004：{_to_thousand_yuan(busi_01004)}千元；"
        f"抵减14011201科目余额贷方轧差值：{_to_thousand_yuan(subject_credit_net)}千元；"
        f"加回5-7-3-2 BIZ_TYPE=01利息调整：{_to_thousand_yuan(biz01_interest_adjustment)}千元。"
    )
    return amount, note


def _detail_amount(df: pd.DataFrame, industry: str, adjustment_sign: Decimal) -> Decimal:
    data = df[
        (df["BIZ_TYPE"].map(_normalize_code) == TARGET_BIZ_TYPE)
        & (df["IND_FIR_GRA_CAT_NM"].map(_clean_text) == industry)
    ].copy()
    return sum(
        (
            _to_decimal(row.get("CURRENT_BALNC"))
            + _to_decimal(row.get("ACCR_INTEREST"))
            + adjustment_sign * _to_decimal(row.get("利息调整"))
            for _, row in data.iterrows()
        ),
        Decimal("0"),
    )


def _detail_biz01_interest_adjustment(df: pd.DataFrame) -> Decimal:
    data = df[df["BIZ_TYPE"].map(_normalize_code) == TARGET_BIZ_TYPE].copy()
    return sum((_to_decimal(value) for value in data["利息调整"]), Decimal("0"))


def _subject_14011201_credit_net_yuan(upload_dir: str | Path) -> Decimal:
    from engine.rule_calculator import RuleCalculator

    calculator = RuleCalculator(
        upload_dir,
        subject_balance_prefix="1-12-",
        report_period="20251231",
    )
    amount_thousand = calculator._calculate_subject_balance_rule("14011201科目余额贷方轧差值")
    if amount_thousand is None:
        return Decimal("0")
    return Decimal(str(amount_thousand)) * THOUSAND


def _find_latest_file(upload_dir: str | Path, prefix: str) -> Path | None:
    root = Path(upload_dir)
    candidates = sorted(
        (path for path in root.glob(f"{prefix}*.xlsx") if path.is_file() and not path.name.startswith("~$")),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _b0326_extra_amount(source_file: Path) -> Decimal:
    df = pd.read_excel(source_file, sheet_name="20251231", dtype=object, engine="openpyxl")
    required = {"BIZ_TYPE", "BUSI_TYPE", *B0326_EXTRA_AMOUNT_COLUMNS}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"5-7-3-1减值明细缺少列：{', '.join(sorted(missing))}")

    data = df[
        (df["BIZ_TYPE"].map(_normalize_code) == TARGET_BIZ_TYPE)
        & (df["BUSI_TYPE"].map(_normalize_busi_type) == B0326_EXTRA_BUSI_TYPE)
    ].copy()
    return sum(
        (
            sum((_to_decimal(row.get(column)) for column in B0326_EXTRA_AMOUNT_COLUMNS), Decimal("0"))
            for _, row in data.iterrows()
        ),
        Decimal("0"),
    )


def _mark_unavailable(report_df: pd.DataFrame, message: str) -> pd.DataFrame:
    result = report_df.copy()
    code_column = _find_column(result, ["指标编码"])
    status_column = _find_column(result, ["计算状态"])
    note_column = _find_column(result, ["计算说明"])
    if not code_column:
        return result
    mask = result[code_column].astype(str).isin(INDUSTRY_BY_CODE)
    if status_column:
        result.loc[mask, status_column] = "未计算"
    if note_column:
        result.loc[mask, note_column] = message
    return result


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {_clean_text(column): column for column in df.columns}
    for candidate in candidates:
        column = normalized.get(_clean_text(candidate))
        if column is not None:
            return str(column)
    return None


def _normalize_code(value: Any) -> str:
    text = _clean_text(value)
    if text.endswith(".0"):
        text = text[:-2]
    return text.zfill(2) if text.isdigit() else text


def _normalize_busi_type(value: Any) -> str:
    text = _clean_text(value)
    if text.endswith(".0"):
        text = text[:-2]
    return text.zfill(5) if text.isdigit() else text


def _clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return "".join(str(value).split())


def _to_decimal(value: Any) -> Decimal:
    if value is None or pd.isna(value):
        return Decimal("0")
    text = str(value).replace(",", "").strip()
    if not text or text.lower() == "nan" or text == "-":
        return Decimal("0")
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _to_thousand_yuan(value: Decimal) -> float:
    return float(value / THOUSAND)
