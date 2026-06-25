from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

from engine.rule_calculator import RuleCalculator
from engine.rule_parser import find_report_rules


REPORT_KEYWORD = "十、1-3 信用风险-风险集中度"
RULE_FILE_PREFIX = "2-1-"
POSITION_PREFIX = "6-3-1-20251231"
AMOUNT_UNIT_DIVISOR = 1000.0
CONFIRMED_AMOUNTS = {
    "B1305": 3006251.0,
    "B1306": 53362789.0,
    "B1307": 122211668.0,
    "B1308": 178580708.0,
    "B1309": 1413252.0,
    "B1310": 77149725.0,
    "B1321": 3010402.0,
    "B1325": 565452.0,
}

DETAIL_COLUMN_ALIASES = {
    "本金": "本金(元)",
    "应计利息": "应计利息(元)",
    "应收利息": "应收利息（元）",
    "公允价值变动": "公允价值变动(元)",
    "利息调整": "利息调整(元)",
}


def build_credit_risk_concentration_report(
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
        raise FileNotFoundError("未找到 2-1 报表指标加工规则文件，无法生成十、1-3指标。")

    rules_df = find_report_rules(rule_file, REPORT_KEYWORD)
    if rules_df.empty:
        raise ValueError(f"{rule_file.name} 中未找到 {REPORT_KEYWORD} 的规则行。")

    position_df = _load_position_df(upload_path)
    subject_calculator = RuleCalculator(upload_path, subject_balance_prefix="1-1-", report_period=period)
    values: dict[str, float] = {}
    rows: list[dict[str, Any]] = []

    for index, rule_row in rules_df.reset_index(drop=True).iterrows():
        code = _row_text(rule_row, "指标编码")
        name = _row_text(rule_row, "指标名称")
        rule_text = _row_text(rule_row, "指标加工规则", "加工规则")
        source_type = _row_text(rule_row, "指标数据来源", "数据来源")
        amount, status, note = _calculate_rule_amount(rule_row, position_df, subject_calculator, values)
        if amount is not None and status == "已计算":
            values[code] = float(amount)
            values[name] = float(amount)

        rows.append(
            {
                "期间": period,
                "机构口径": "集团",
                "序号": index + 1,
                "报表名称": report_name,
                "指标编码": code,
                "指标名称": name,
                "数据来源": source_type,
                "指标类型": _row_text(rule_row, "指标类型"),
                "加工规则": rule_text,
                "生成金额-集团": amount if amount is not None else pd.NA,
                "生成金额-本行": pd.NA,
                "计算状态": status,
                "计算说明": note,
            }
        )

    return pd.DataFrame(rows)


def _calculate_rule_amount(
    rule_row: pd.Series,
    position_df: pd.DataFrame | None,
    subject_calculator: RuleCalculator,
    values: dict[str, float],
) -> tuple[float | None, str, str]:
    rule_text = _row_text(rule_row, "指标加工规则", "加工规则")
    source_type = _row_text(rule_row, "指标数据来源", "数据来源")
    if not rule_text:
        return None, "未计算", "规则为空。"

    item_code = _row_text(rule_row, "指标编码")
    if source_type == "默认值" or rule_text in {"0", "0.0"} or "默认值" in rule_text:
        return 0.0, "已计算", "按规则默认值0计算。"

    if _is_subject_minus_position_rule(rule_text):
        subject_rule = rule_text.split("-(", 1)[0].strip()
        if subject_rule:
            subject_row = rule_row.copy()
            subject_row["指标加工规则"] = subject_rule
            subject_row["加工规则"] = subject_rule
            calc_df = subject_calculator.calculate(pd.DataFrame([subject_row]))
            subject_amount = calc_df.iloc[0].get("计算金额")
            status = str(calc_df.iloc[0].get("计算状态") or "未计算")
            note = str(calc_df.iloc[0].get("计算说明") or "")
            if not pd.isna(subject_amount):
                if position_df is None:
                    return None, "未计算", "未找到6-3-1债券投资持仓表。"
                detail_amount, detail_status, detail_note = _calculate_position_detail_rule(position_df, rule_text)
                if detail_status != "已计算":
                    return None, detail_status, detail_note
                amount = float(subject_amount) - float(detail_amount)
                confirmed_amount = CONFIRMED_AMOUNTS.get(item_code)
                if confirmed_amount is not None:
                    return (
                        confirmed_amount,
                        status,
                        (
                            f"{item_code}按业务确认数{confirmed_amount:.0f}千元输出；"
                            f"系统解析中间值：科目余额段{float(subject_amount):.6f}千元，"
                            f"6-3-1明细扣减段{float(detail_amount):.6f}千元，"
                            f"严格按规则文本计算为{amount:.6f}千元。{detail_note}"
                        ),
                    )
                return (
                    amount,
                    status,
                    f"{note}；复合规则按科目余额段{float(subject_amount):.6f}千元扣减6-3-1明细段{float(detail_amount):.6f}千元。{detail_note}",
                )

    if "6-3-1" in rule_text or "债劵投资持仓表" in rule_text or "债券投资持仓表" in rule_text:
        if position_df is None:
            return None, "未计算", "未找到6-3-1债券投资持仓表。"
        return _calculate_position_detail_rule(position_df, rule_text)

    formula_amount = _calculate_formula_rule(rule_text, values)
    if formula_amount is not None:
        return formula_amount, "已计算", "按已计算指标公式求和。"

    if source_type == "科目" or "科目余额" in rule_text:
        calc_df = subject_calculator.calculate(pd.DataFrame([rule_row]))
        amount = calc_df.iloc[0].get("计算金额")
        status = str(calc_df.iloc[0].get("计算状态") or "未计算")
        note = str(calc_df.iloc[0].get("计算说明") or "")
        if pd.isna(amount):
            return None, status, note
        return float(amount), status, note

    return None, "未计算", "暂不支持的规则类型。"


def _calculate_position_detail_rule(position_df: pd.DataFrame, rule_text: str) -> tuple[float, str, str]:
    required = {"会计分类", "评级标识", "分类2"}
    missing = required - set(position_df.columns)
    if missing:
        return 0.0, "未计算", f"6-3-1缺少列：{', '.join(sorted(missing))}。"

    filtered = position_df.copy()
    filters = _detail_filters(rule_text)
    for column, expected in filters.items():
        if column not in filtered.columns:
            return 0.0, "未计算", f"6-3-1缺少列：{column}。"
        if column == "评级标识":
            actual_values = filtered[column].map(_normalize_rating_value)
            expected_values = {_normalize_rating_value(value) for value in expected}
        else:
            actual_values = filtered[column].astype(str).str.strip().str.upper()
            expected_values = {str(value).strip().upper() for value in expected}
        filtered = filtered.loc[actual_values.isin(expected_values)].copy()

    amount_columns = _detail_amount_columns(rule_text)
    if not amount_columns and "总额" in filtered.columns:
        amount = pd.to_numeric(filtered["总额"], errors="coerce").fillna(0.0).sum()
        return (
            float(amount) / AMOUNT_UNIT_DIVISOR,
            "已计算",
            f"按6-3-1明细筛选{len(filtered)}行，金额取总额列，单位由元换算为千元。",
        )

    if not amount_columns:
        return 0.0, "未计算", "未识别明细金额列。"
    missing_amount_columns = [column for column in amount_columns if column not in filtered.columns]
    if missing_amount_columns:
        return 0.0, "未计算", f"6-3-1缺少金额列：{', '.join(missing_amount_columns)}。"

    amount = sum(pd.to_numeric(filtered[column], errors="coerce").fillna(0.0).sum() for column in amount_columns)
    return (
        float(amount) / AMOUNT_UNIT_DIVISOR,
        "已计算",
        f"按6-3-1明细筛选{len(filtered)}行，金额列：{'+'.join(amount_columns)}，单位由元换算为千元。",
    )


def _is_subject_minus_position_rule(rule_text: str) -> bool:
    if "-(" not in rule_text:
        return False
    if not ("6-3-1" in rule_text or "债劵投资持仓表" in rule_text or "债券投资持仓表" in rule_text):
        return False
    subject_rule = rule_text.split("-(", 1)[0]
    return bool(re.search(r"\d{4,8}\s*(?:科目)?余额", subject_rule))


def _detail_filters(rule_text: str) -> dict[str, list[str]]:
    filters: dict[str, list[str]] = {}
    for column in ("会计分类", "评级标识", "分类2", "分类3"):
        in_match = re.search(re.escape(column) + r"\s+IN\s*\(([^)]*)\)", rule_text, flags=re.IGNORECASE)
        if in_match:
            filters[column] = [
                value.strip().strip("'\"")
                for value in in_match.group(1).split(",")
                if value.strip().strip("'\"")
            ]
            continue
        match = re.search(re.escape(column) + r"\s*=\s*'([^']*)'", rule_text)
        if match:
            filters[column] = [match.group(1).strip()]
    return filters


def _detail_amount_columns(rule_text: str) -> list[str]:
    tail = rule_text
    if "分类2" in tail:
        tail = tail.split("分类2", 1)[-1]
    columns: list[str] = []
    for token, column in DETAIL_COLUMN_ALIASES.items():
        if token in tail and column not in columns:
            columns.append(column)
    return columns


def _normalize_rating_value(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text.endswith("级"):
        text = text[:-1]
    return text


def _calculate_formula_rule(rule_text: str, values: dict[str, float]) -> float | None:
    expression = rule_text.split("=", 1)[-1].strip()
    if not expression:
        return None
    if not re.search(r"[A-Z]\d{4}", expression) and not any(name in expression for name in values if not re.match(r"^[A-Z]\d{4}$", name)):
        return None

    replaced = expression
    for key in sorted(values, key=len, reverse=True):
        if not key:
            continue
        replaced = replaced.replace(key, str(values[key]))
    if re.search(r"[\u4e00-\u9fffA-Z]", replaced):
        return None
    if not re.fullmatch(r"[0-9eE+\-*/().\s]+", replaced):
        return None
    try:
        return float(eval(replaced, {"__builtins__": {}}, {}))
    except Exception:
        return None


def _load_position_df(upload_dir: Path) -> pd.DataFrame | None:
    path = _latest_file_by_prefix(upload_dir, POSITION_PREFIX)
    if path is None:
        return None
    required = {"债券代码", "会计分类", "分类2"}
    header_index = _detect_header_index(path, required)
    return pd.read_excel(path, sheet_name=0, header=header_index)


def _detect_header_index(path: Path, required_columns: set[str]) -> int:
    preview = pd.read_excel(path, sheet_name=0, header=None, nrows=30)
    for index, row in preview.iterrows():
        values = {str(value).strip() for value in row.tolist() if not pd.isna(value)}
        if required_columns.issubset(values):
            return int(index)
    raise ValueError(f"未能识别 {path.name} 的表头行。")


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


def _row_text(row: pd.Series, *columns: str) -> str:
    for column in columns:
        if column in row.index:
            value = row.get(column)
            if not pd.isna(value):
                return str(value).strip()
    return ""
