from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from engine.report_generator import build_report_from_rules
from engine.rule_calculator import RuleCalculator
from engine.rule_parser import find_report_rules


REPORT_KEYWORD = "十一、1-1 公允价值计量-公允计量的层次"
RULE_FILE_PREFIX = "2-1-"
BALANCE_SHEET_KEYWORD = "合并及母公司资产负债表"

FAIR_VALUE_ITEMS = [
    ("B1401", "交易性金融资产", "A0007"),
    ("B1402", "衍生金融资产", "A0004"),
    ("B1403", "其他债权投资", "A0009"),
    ("B1404", "其他权益工具投资", "A0010"),
    ("B1405", "金融资产合计", None),
    ("B1406", "交易性金融负债", "A0022"),
    ("B1407", "衍生金融负债", "A0023"),
    ("B1408", "金融负债合计", None),
]

ASSET_CODES = {"B1401", "B1402", "B1403", "B1404"}
LIABILITY_CODES = {"B1406", "B1407"}


def build_fair_value_hierarchy_report(
    upload_dir: str | Path,
    report_config: dict[str, Any],
    institution_context: dict[str, Any] | None = None,
) -> pd.DataFrame:
    upload_path = Path(upload_dir)
    context = institution_context or {}
    period = str(context.get("period") or "")
    report_name = str(report_config.get("display_name") or REPORT_KEYWORD)
    rule_file = _latest_file_by_prefix(upload_path, RULE_FILE_PREFIX)
    if rule_file is None:
        raise FileNotFoundError("未找到 2-1 报表指标加工规则文件，无法生成十一、1-1指标。")

    configured_rules = find_report_rules(rule_file, REPORT_KEYWORD)
    if not configured_rules.empty:
        return build_report_from_rules(
            configured_rules,
            report_config,
            upload_dir=str(upload_path),
            report_period=period,
        )

    balance_rules = find_report_rules(rule_file, BALANCE_SHEET_KEYWORD)
    if balance_rules.empty:
        raise ValueError(f"{rule_file.name} 中未找到 {BALANCE_SHEET_KEYWORD} 的规则行。")

    group_values, group_notes = _calculate_balance_values(upload_path, balance_rules, "1-1-", period)
    parent_values, parent_notes = _calculate_balance_values(upload_path, balance_rules, "1-12-", period)

    rows: list[dict[str, Any]] = []
    for index, (code, name, balance_code) in enumerate(FAIR_VALUE_ITEMS, start=1):
        if code == "B1405":
            group_amount = sum(group_values.get(item_code, 0.0) for item_code in ASSET_CODES)
            parent_amount = sum(parent_values.get(item_code, 0.0) for item_code in ASSET_CODES)
            note = "按已计算金融资产公允价值计量项目汇总。"
        elif code == "B1408":
            group_amount = sum(group_values.get(item_code, 0.0) for item_code in LIABILITY_CODES)
            parent_amount = sum(parent_values.get(item_code, 0.0) for item_code in LIABILITY_CODES)
            note = "按已计算金融负债公允价值计量项目汇总。"
        else:
            group_amount = group_values.get(code, pd.NA)
            parent_amount = parent_values.get(code, pd.NA)
            group_note = group_notes.get(code, "")
            parent_note = parent_notes.get(code, "")
            note = group_note if group_note == parent_note else f"集团：{group_note}；本行：{parent_note}"

        rows.append(
            {
                "期间": period,
                "机构口径": "集团/本行",
                "序号": index,
                "报表名称": report_name,
                "指标编码": code,
                "指标名称": name,
                "公允价值层次": "未拆分",
                "第一层次-集团": pd.NA,
                "第二层次-集团": pd.NA,
                "第三层次-集团": pd.NA,
                "合计-集团": group_amount,
                "第一层次-本行": pd.NA,
                "第二层次-本行": pd.NA,
                "第三层次-本行": pd.NA,
                "合计-本行": parent_amount,
                "数据来源": "资产负债表加工规则",
                "指标类型": "披露项",
                "加工规则": _fallback_rule_text(balance_code, name),
                "生成金额-集团": group_amount,
                "生成金额-本行": parent_amount,
                "计算状态": "已计算",
                "计算说明": f"{note} 当前未提供公允价值第一/第二/第三层次拆分明细，层次列留空。",
            }
        )

    return pd.DataFrame(rows)


def _calculate_balance_values(
    upload_path: Path,
    balance_rules: pd.DataFrame,
    subject_balance_prefix: str,
    period: str,
) -> tuple[dict[str, float], dict[str, str]]:
    needed_balance_codes = {
        balance_code
        for _, _, balance_code in FAIR_VALUE_ITEMS
        if balance_code
    }
    if "指标编码" not in balance_rules.columns:
        raise ValueError("资产负债表规则缺少“指标编码”列。")

    selected = balance_rules.loc[balance_rules["指标编码"].astype(str).isin(needed_balance_codes)].copy()
    calculator = RuleCalculator(
        upload_path,
        subject_balance_prefix=subject_balance_prefix,
        report_period=period,
        oci_entity="本行" if subject_balance_prefix == "1-12-" else "集团",
    )
    calculated = calculator.calculate(selected)
    value_by_balance_code: dict[str, float] = {}
    note_by_balance_code: dict[str, str] = {}
    for _, row in calculated.iterrows():
        balance_code = str(row.get("指标编码") or "").strip()
        amount = pd.to_numeric(pd.Series([row.get("计算金额")]), errors="coerce").iloc[0]
        if pd.notna(amount):
            value_by_balance_code[balance_code] = float(amount)
        note_by_balance_code[balance_code] = str(row.get("计算说明") or "")

    values: dict[str, float] = {}
    notes: dict[str, str] = {}
    for code, name, balance_code in FAIR_VALUE_ITEMS:
        if not balance_code:
            continue
        values[code] = value_by_balance_code.get(balance_code, 0.0)
        notes[code] = note_by_balance_code.get(balance_code) or f"复用资产负债表指标 {balance_code}（{name}）金额。"
    return values, notes


def _fallback_rule_text(balance_code: str | None, item_name: str) -> str:
    if balance_code:
        return f"复用资产负债表指标{balance_code}（{item_name}）作为合计金额。"
    return f"{item_name}=相关公允价值计量项目合计。"


def _latest_file_by_prefix(upload_dir: Path, prefix: str) -> Path | None:
    if not upload_dir.exists():
        return None
    files = sorted(
        [
            path
            for path in upload_dir.iterdir()
            if path.is_file()
            and path.name.startswith(prefix)
            and path.suffix.lower() in {".xlsx", ".xls"}
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None
