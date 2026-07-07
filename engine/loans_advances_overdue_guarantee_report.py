from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from engine.loans_advances_guarantee_report import _find_latest_file, _find_retail_loan_csv_files, _to_decimal
from engine.rule_parser import find_report_rules


THOUSAND = Decimal("1000")
REPORT_KEYWORD = "五、6-4 发放贷款和垫款-按担保方式及逾期期限分布情况"

GUARANTEE_LABELS = {
    "01": "抵押贷款",
    "02": "质押贷款",
    "03": "信用贷款",
    "04": "保证贷款",
}

ROW_SPECS = [
    ("B0332", "逾期3个月以内(含3个月)信用贷款", "within_3m", "03"),
    ("B0333", "逾期3个月以内(含3个月)保证贷款", "within_3m", "04"),
    ("B0334", "逾期3个月以内(含3个月)抵押贷款", "within_3m", "01"),
    ("B0335", "逾期3个月以内(含3个月)质押贷款", "within_3m", "02"),
    ("B0336", "逾期3个月以内(含3个月)贷款", "within_3m", None),
    ("B0337", "逾期3个月至1年(含1年)信用贷款", "m3_to_1y", "03"),
    ("B0338", "逾期3个月至1年(含1年)保证贷款", "m3_to_1y", "04"),
    ("B0339", "逾期3个月至1年(含1年)抵押贷款", "m3_to_1y", "01"),
    ("B0340", "逾期3个月至1年(含1年)质押贷款", "m3_to_1y", "02"),
    ("B0341", "逾期3个月至1年(含1年)贷款", "m3_to_1y", None),
    ("B0342", "逾期1年以上3年以内(含3年)信用贷款", "y1_to_3y", "03"),
    ("B0343", "逾期1年以上3年以内(含3年)保证贷款", "y1_to_3y", "04"),
    ("B0344", "逾期1年以上3年以内(含3年)抵押贷款", "y1_to_3y", "01"),
    ("B0345", "逾期1年以上3年以内(含3年)质押贷款", "y1_to_3y", "02"),
    ("B0346", "逾期1年以上3年以内(含3年)贷款", "y1_to_3y", None),
    ("B0347", "逾期3年以上信用贷款", "over_3y", "03"),
    ("B0348", "逾期3年以上保证贷款", "over_3y", "04"),
    ("B0349", "逾期3年以上抵押贷款", "over_3y", "01"),
    ("B0350", "逾期3年以上质押贷款", "over_3y", "02"),
    ("B0351", "逾期3年以上贷款", "over_3y", None),
    ("B0352", "已逾期信用贷款", "overdue", "03"),
    ("B0353", "已逾期保证贷款", "overdue", "04"),
    ("B0354", "已逾期抵押贷款", "overdue", "01"),
    ("B0355", "已逾期质押贷款", "overdue", "02"),
    ("B0356", "已逾期贷款", "overdue", None),
]


def build_loans_advances_overdue_guarantee_6_4_report(
    upload_dir: str | Path,
    report_config: dict[str, Any],
    institution_context: dict[str, Any] | None = None,
    rule_file_path: str | Path | None = None,
) -> pd.DataFrame:
    upload_path = Path(upload_dir)
    rule_rows = _load_rule_rows(rule_file_path, report_config)
    period = str((institution_context or {}).get("period") or "")
    report_date = _report_date(period)
    overdue_basis = _overdue_basis_from_rules(rule_rows)
    retail_summary = _query_retail_summary(upload_path, report_date, overdue_basis)
    corporate_summary = _query_corporate_summary(upload_path, report_date, overdue_basis)
    scope = str((institution_context or {}).get("scope") or "本行")
    institution_code = str((institution_context or {}).get("code") or "")
    institution_name = str((institution_context or {}).get("name") or scope)

    rows = []
    for index, rule_row in enumerate(rule_rows, start=1):
        item_code = str(rule_row.get("指标编码") or "").strip()
        spec = _spec_by_code().get(item_code)
        if not spec:
            continue
        _code, default_name, bucket, guarantee_code = spec
        amount_yuan = _amount_for(retail_summary, bucket, guarantee_code) + _amount_for(corporate_summary, bucket, guarantee_code)
        row_count = _row_count_for(retail_summary, bucket, guarantee_code) + _row_count_for(corporate_summary, bucket, guarantee_code)
        amount_thousand = float(amount_yuan / THOUSAND)
        guarantee_note = GUARANTEE_LABELS.get(guarantee_code, "全部担保方式") if guarantee_code else "全部担保方式"
        rows.append(
            {
                "期间": period,
                "机构口径": scope,
                "机构编码": institution_code,
                "机构": institution_name,
                "序号": index,
                "报表名称": str(rule_row.get("报表名称") or report_config.get("display_name") or REPORT_KEYWORD),
                "指标编码": item_code,
                "指标名称": str(rule_row.get("指标名称") or default_name),
                "数据来源": str(rule_row.get("数据来源") or "5-7-3-2减值明细；5-6-4零售贷款CSV"),
                "指标类型": str(rule_row.get("指标类型") or "明细汇总"),
                "加工规则": str(rule_row.get("加工规则") or ""),
                "生成金额-集团": amount_thousand,
                "生成金额-本行": amount_thousand,
                "计算状态": "已计算",
                "计算说明": (
                    f"按{_overdue_basis_label(overdue_basis, report_date)}分档，担保方式：{guarantee_note}；"
                    f"明细行数：{row_count:,}；金额=CURRENT_BALNC+ACCR_INTEREST+对公利息调整，单位转换为千元。"
                ),
            }
        )
    return pd.DataFrame(rows)


def _load_rule_rows(rule_file_path: str | Path | None, report_config: dict[str, Any]) -> list[dict[str, Any]]:
    keyword = str(report_config.get("rule_keyword") or report_config.get("display_name") or REPORT_KEYWORD)
    if rule_file_path:
        rules = find_report_rules(rule_file_path, keyword)
        if not rules.empty:
            rows = []
            target_codes = set(_spec_by_code())
            for _, row in rules.iterrows():
                record = {str(column): row.get(column) for column in rules.columns}
                if str(record.get("指标编码") or "").strip() in target_codes:
                    rows.append(record)
            if rows:
                return rows
    return [
        {
            "报表名称": str(report_config.get("display_name") or REPORT_KEYWORD),
            "指标编码": code,
            "指标名称": name,
            "指标类型": "明细汇总",
            "数据来源": "",
            "加工规则": "",
        }
        for code, name, _bucket, _guarantee in ROW_SPECS
    ]


def _query_retail_summary(
    upload_dir: Path,
    report_date: str = "2025-12-31",
    overdue_basis: str = "OVRD_DAYS",
) -> dict[tuple[str, str], dict[str, Decimal | int]]:
    files = _find_retail_loan_csv_files(upload_dir)
    if not files:
        raise FileNotFoundError("未找到 5-6-4-20251231-02-零售贷款-01/02/03/04 CSV 文件。")
    file_list_sql = ", ".join(_sql_string(str(path.resolve()).replace("\\", "/")) for path in files)
    days_expr = (
        "try_cast(OVRD_DAYS as integer)"
        if overdue_basis == "OVRD_DAYS"
        else f"date_diff('day', try_cast(DUBIL_MATR_DT as date), date '{report_date}')"
    )
    date_filter = "and try_cast(DUBIL_MATR_DT as date) is not null" if overdue_basis == "DUBIL_MATR_DT" else ""
    sql = f"""
        select
            bucket,
            guarantee_type_cd,
            count(*) as row_count,
            sum(coalesce(try_cast(CURRENT_BALNC as decimal(38, 6)), 0)
                + coalesce(try_cast(ACCR_INTEREST as decimal(38, 6)), 0)) as amount
        from (
            select
                case
                    when {days_expr} > 0 and {days_expr} <= 90 then 'within_3m'
                    when {days_expr} > 90 and {days_expr} <= 365 then 'm3_to_1y'
                    when {days_expr} > 365 and {days_expr} <= 1095 then 'y1_to_3y'
                    when {days_expr} > 1095 then 'over_3y'
                    else null
                end as bucket,
                trim(GUARANTEE_TYPE_CD) as guarantee_type_cd,
                CURRENT_BALNC,
                ACCR_INTEREST
            from read_csv_auto([{file_list_sql}], all_varchar=true, union_by_name=true, sample_size=20480)
            where trim(coalesce(BIZ_TYPE, '')) = '02'
              {date_filter}
        )
        where bucket is not null and trim(coalesce(guarantee_type_cd, '')) <> ''
        group by 1, 2
    """
    with duckdb.connect() as connection:
        rows = connection.execute(sql).fetchall()
    return _summary_from_rows(rows)


def _query_corporate_summary(
    upload_dir: Path,
    report_date: str = "2025-12-31",
    overdue_basis: str = "OVRD_DAYS",
) -> dict[tuple[str, str], dict[str, Decimal | int]]:
    source_file = _find_latest_file(upload_dir, "5-7-3-2-20251231")
    if source_file is None:
        return {}
    df = pd.read_excel(source_file, sheet_name="20251231", dtype=object, engine="openpyxl")
    required = {"BIZ_TYPE", "GUARANTEE_TYPE_CD", "CURRENT_BALNC", "ACCR_INTEREST", overdue_basis}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{source_file.name} 缺少列：{', '.join(sorted(missing))}")
    if "利息调整" not in df.columns:
        df["利息调整"] = 0
    if overdue_basis == "OVRD_DAYS":
        days = df["OVRD_DAYS"].map(_to_int)
    else:
        days = (_to_timestamp(report_date) - pd.to_datetime(df["DUBIL_MATR_DT"], errors="coerce")).dt.days
    data = df[(df["BIZ_TYPE"].map(_normalize_code) == "01") & (days > 0)].copy()
    data["_bucket"] = days.loc[data.index].map(_bucket_for_days)
    data["_guarantee"] = data["GUARANTEE_TYPE_CD"].map(_normalize_code)
    data["_amount"] = data.apply(
        lambda row: _to_decimal(row.get("CURRENT_BALNC")) + _to_decimal(row.get("ACCR_INTEREST")) + _to_decimal(row.get("利息调整")),
        axis=1,
    )
    result: dict[tuple[str, str], dict[str, Decimal | int]] = {}
    for (bucket, guarantee), group in data.dropna(subset=["_bucket"]).groupby(["_bucket", "_guarantee"]):
        result[(str(bucket), str(guarantee))] = {
            "row_count": int(len(group)),
            "amount": sum(group["_amount"], Decimal("0")),
        }
    return result


def _summary_from_rows(rows: list[tuple[Any, Any, Any, Any]]) -> dict[tuple[str, str], dict[str, Decimal | int]]:
    result: dict[tuple[str, str], dict[str, Decimal | int]] = {}
    for bucket, guarantee, row_count, amount in rows:
        result[(str(bucket), str(guarantee))] = {
            "row_count": int(row_count or 0),
            "amount": _to_decimal(amount),
        }
    return result


def _amount_for(summary: dict[tuple[str, str], dict[str, Decimal | int]], bucket: str, guarantee_code: str | None) -> Decimal:
    buckets = ["within_3m", "m3_to_1y", "y1_to_3y", "over_3y"] if bucket == "overdue" else [bucket]
    guarantees = ["01", "02", "03", "04"] if guarantee_code is None else [guarantee_code]
    return sum((_to_decimal(summary.get((b, g), {}).get("amount")) for b in buckets for g in guarantees), Decimal("0"))


def _row_count_for(summary: dict[tuple[str, str], dict[str, Decimal | int]], bucket: str, guarantee_code: str | None) -> int:
    buckets = ["within_3m", "m3_to_1y", "y1_to_3y", "over_3y"] if bucket == "overdue" else [bucket]
    guarantees = ["01", "02", "03", "04"] if guarantee_code is None else [guarantee_code]
    return sum((int(summary.get((b, g), {}).get("row_count", 0)) for b in buckets for g in guarantees), 0)


def _bucket_for_days(value: Any) -> str | None:
    days = _to_int(value)
    if days <= 0:
        return None
    if days <= 90:
        return "within_3m"
    if days <= 365:
        return "m3_to_1y"
    if days <= 1095:
        return "y1_to_3y"
    return "over_3y"


def _overdue_basis_from_rules(rule_rows: list[dict[str, Any]]) -> str:
    text = "\n".join(
        str(row.get("加工规则") or row.get("指标加工规则") or row.get("数据来源") or "")
        for row in rule_rows
    ).upper()
    if "OVRD_DAYS" in text:
        return "OVRD_DAYS"
    if "DUBIL_MATR_DT" in text or "DUBIL_MATR" in text:
        return "DUBIL_MATR_DT"
    return "OVRD_DAYS"


def _overdue_basis_label(overdue_basis: str, report_date: str) -> str:
    if overdue_basis == "DUBIL_MATR_DT":
        return f"报告日{report_date}减DUBIL_MATR_DT到期日的天数"
    return "OVRD_DAYS逾期天数"


def _report_date(period: str) -> str:
    text = str(period or "").strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:8]}"
    return "2025-12-31"


def _to_timestamp(value: str) -> pd.Timestamp:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return pd.Timestamp("2025-12-31")
    return pd.Timestamp(parsed)


def _to_int(value: Any) -> int:
    try:
        if value is None or pd.isna(value):
            return 0
        return int(float(str(value).strip()))
    except Exception:
        return 0


def _normalize_code(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    if text.isdigit() and len(text) < 2:
        text = text.zfill(2)
    return text


def _spec_by_code() -> dict[str, tuple[str, str, str, str | None]]:
    return {code: spec for spec in ROW_SPECS for code in [spec[0]]}


def _sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"
