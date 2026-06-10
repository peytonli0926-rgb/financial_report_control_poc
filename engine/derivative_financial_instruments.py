from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

import pandas as pd

from engine.rule_calculator import RuleCalculator


THOUSAND = Decimal("1000")

AMOUNT_COLUMN_KEYWORDS = (
    "公允价值",
    "估值",
    "市值",
    "账面价值",
    "重估",
    "损益",
    "金额",
    "余额",
    "本金",
    "名义",
    "notional",
    "fair",
    "value",
    "amount",
    "balance",
)


def build_derivative_financial_instruments_report(
    upload_dir: str | Path,
    report_config: dict[str, Any],
    report_period: str | None = None,
) -> pd.DataFrame:
    upload_path = Path(upload_dir)
    report_name = report_config.get("display_name", "五、4 衍生金融工具")
    rows: list[dict[str, Any]] = []

    fx_forward_file = _find_file(upload_path, "5-4-1-1")
    fx_swap_file = _find_file(upload_path, "5-4-1-2")
    gold_swap_file = _find_file(upload_path, "5-4-1-3")
    crmw_file = _find_file(upload_path, "5-4-1-4")
    b0271_summary = _default_summary("暂未配置货币远期外汇名义金额加工来源，默认按0参与后续合计。")
    b0272_summary = _calculate_b0272(fx_forward_file, fx_swap_file)
    b0270_summary = _default_summary("B0270上传规则暂不加工，默认按0参与后续合计。")
    b0273_summary = _default_summary("暂未上传/配置利率衍生工具名义金额加工来源，默认按0参与后续合计。")
    b0274_summary = _default_summary("暂未上传/配置利率互换名义金额加工来源，默认按0参与后续合计。")
    b0275_summary = _calculate_b0275(gold_swap_file)
    b0277_summary = _calculate_b0277(crmw_file)
    uploaded_rule_map = _load_uploaded_rule_map(upload_path)
    b0280_summary = _calculate_uploaded_rule_summary(
        upload_path,
        code="B0280",
        name="外汇掉期公允价值资产",
        rule_text=_rule_text_for(uploaded_rule_map, "B0280", B0280_RULE_TEXT),
        report_period=report_period,
    )
    b0278_summary = _calculate_uploaded_rule_summary(
        upload_path,
        code="B0278",
        name="货币衍生工具公允价值资产",
        rule_text=_rule_text_for(uploaded_rule_map, "B0278"),
        report_period=report_period,
    )
    b0276_summary = _sum_summaries(
        code="B0276",
        components=[
            ("B0272", b0272_summary),
            ("B0273", b0273_summary),
            ("B0275", b0275_summary),
            ("B0277", b0277_summary),
        ],
        note_prefix="衍生金融工具名义金额按已加工名义金额求和：B0272外汇掉期名义金额+B0273利率衍生工具名义金额+B0275贵金属掉期名义金额+B0277信用风险缓释工具名义金额",
    )
    fair_value_summaries = {
        "B0278": b0278_summary,
        "B0280": b0280_summary,
    }
    fair_value_items = _fair_value_default_items()
    for item in fair_value_items:
        if item["code"] in fair_value_summaries:
            continue
        rule_text = _rule_text_for(uploaded_rule_map, item["code"], item["rule_text"])
        if _is_indicator_formula_rule(rule_text):
            continue
        fair_value_summaries[item["code"]] = _calculate_uploaded_rule_summary(
            upload_path,
            code=item["code"],
            name=item["name"],
            rule_text=rule_text,
            report_period=report_period,
        )

    for item in fair_value_items:
        if item["code"] in fair_value_summaries:
            continue
        rule_text = _rule_text_for(uploaded_rule_map, item["code"], item["rule_text"])
        fair_value_summaries[item["code"]] = _calculate_indicator_formula_summary(
            code=item["code"],
            rule_text=rule_text,
            summaries=fair_value_summaries,
        )

    rows.append(
        _report_row(
            index=1,
            report_period=report_period,
            report_name=report_name,
            code="B0270",
            name="货币衍生工具名义金额",
            data_source=_source_names([fx_forward_file, fx_swap_file]) or "B0271/B0272",
            item_type="复合指标",
            rule_text="上传规则暂不加工，默认0",
            amount_yuan=b0270_summary["amount_yuan"],
            status=b0270_summary["status"],
            note=b0270_summary["note"],
            row_count=b0270_summary["row_count"],
        )
    )

    rows.append(
        _report_row(
            index=2,
            report_period=report_period,
            report_name=report_name,
            code="B0271",
            name="货币远期外汇名义金额",
            data_source="待配置",
            item_type="基础指标",
            rule_text="外汇掉期持仓表-远端货币2金额（交易方式：Sell/Buy）",
            amount_yuan=b0271_summary["amount_yuan"],
            status=b0271_summary["status"],
            note=b0271_summary["note"],
            row_count=b0271_summary["row_count"],
        )
    )

    rows.append(
        _report_row(
            index=3,
            report_period=report_period,
            report_name=report_name,
            code="B0272",
            name="外汇掉期名义金额",
            data_source=_source_names([fx_forward_file, fx_swap_file]) or "5-4-1-1/5-4-1-2",
            item_type="基础指标",
            rule_text="外汇掉期持仓表交易方向=Buy/Sell且远端成交价不为空的远端货币2金额之和+外汇远期持仓表货币2金额之和",
            amount_yuan=b0272_summary["amount_yuan"],
            status=b0272_summary["status"],
            note=b0272_summary["note"],
            row_count=b0272_summary["row_count"],
        )
    )

    rows.append(
        _report_row(
            index=4,
            report_period=report_period,
            report_name=report_name,
            code="B0273",
            name="利率衍生工具名义金额",
            data_source="待配置",
            item_type="基础指标",
            rule_text="衍生品（结构性存款）-本金（条件：到期日>报告期末）",
            amount_yuan=b0273_summary["amount_yuan"],
            status=b0273_summary["status"],
            note=b0273_summary["note"],
            row_count=b0273_summary["row_count"],
        )
    )

    rows.append(
        _report_row(
            index=5,
            report_period=report_period,
            report_name=report_name,
            code="B0274",
            name="利率互换名义金额",
            data_source="待配置",
            item_type="基础指标",
            rule_text="衍生品（结构性存款）-本金（条件：到期日>报告期末）",
            amount_yuan=b0274_summary["amount_yuan"],
            status=b0274_summary["status"],
            note=b0274_summary["note"],
            row_count=b0274_summary["row_count"],
        )
    )

    rows.append(
        _report_row(
            index=6,
            report_period=report_period,
            report_name=report_name,
            code="B0275",
            name="贵金属掉期名义金额",
            data_source=gold_swap_file.name if gold_swap_file is not None else "5-4-1-3",
            item_type="基础指标",
            rule_text="2025年末黄金掉期持仓表远端货币1金额*远端成交价",
            amount_yuan=b0275_summary["amount_yuan"],
            amount_thousand=b0275_summary["amount_thousand"],
            status=b0275_summary["status"],
            note=b0275_summary["note"],
            row_count=b0275_summary["row_count"],
        )
    )

    rows.append(
        _report_row(
            index=7,
            report_period=report_period,
            report_name=report_name,
            code="B0276",
            name="衍生金融工具名义金额",
            data_source="B0272+B0273+B0275+B0277",
            item_type="复合指标",
            rule_text="外汇掉期名义金额+利率衍生工具名义金额+贵金属掉期名义金额+信用风险缓释工具名义金额",
            amount_yuan=b0276_summary["amount_yuan"],
            amount_thousand=b0276_summary["amount_thousand"],
            status=b0276_summary["status"],
            note=b0276_summary["note"],
            row_count=b0276_summary["row_count"],
        )
    )

    rows.append(
        _report_row(
            index=8,
            report_period=report_period,
            report_name=report_name,
            code="B0277",
            name="信用风险缓释工具名义金额",
            data_source=crmw_file.name if crmw_file is not None else "5-4-1-4",
            item_type="基础指标",
            rule_text="P&L-CRMW-251231估值-信用风险缓释凭证台账持仓名义本金（元）之和",
            amount_yuan=b0277_summary["amount_yuan"],
            status=b0277_summary["status"],
            note=b0277_summary["note"],
            row_count=b0277_summary["row_count"],
        )
    )

    for offset, item in enumerate(fair_value_items, start=9):
        summary = fair_value_summaries.get(item["code"])
        if summary is None:
            rule_text = _rule_text_for(uploaded_rule_map, item["code"], item["rule_text"])
            summary = _default_summary(f"{item['code']}暂未配置可解析的加工规则，默认按0输出。")
            summary["rule_text"] = rule_text
        rows.append(
            _report_row(
                index=offset,
                report_period=report_period,
                report_name=report_name,
                code=item["code"],
                name=item["name"],
                data_source="科目余额表",
                item_type=item["item_type"],
                rule_text=summary.get("rule_text") or item["rule_text"],
                amount_yuan=summary["amount_yuan"],
                amount_thousand=summary.get("amount_thousand"),
                status=summary["status"],
                note=summary["note"],
                row_count=summary["row_count"],
            )
        )

    return pd.DataFrame(rows)


def _calculate_b0272(forward_file: Path | None, swap_file: Path | None) -> dict[str, Any]:
    if forward_file is None or swap_file is None:
        missing = []
        if forward_file is None:
            missing.append("5-4-1-1 外汇远期持仓表")
        if swap_file is None:
            missing.append("5-4-1-2 外汇掉期持仓表")
        return {
            "amount_yuan": Decimal("0"),
            "row_count": 0,
            "status": "未计算",
            "note": f"缺少{', '.join(missing)}，请上传后重新生成。",
        }

    forward_df = _read_position_table(forward_file, required_columns=("货币2金额",))
    swap_df = _read_position_table(swap_file, required_columns=("交易方向", "远端成交价", "远端货币2金额"))

    forward_amount = _sum_numeric(forward_df["货币2金额"])
    swap_direction = swap_df["交易方向"].map(_clean_text)
    far_price = pd.to_numeric(swap_df["远端成交价"].map(_clean_number), errors="coerce")
    mask = swap_direction.eq("Buy/Sell") & far_price.notna()
    swap_amount = _sum_numeric(swap_df.loc[mask, "远端货币2金额"])
    amount_yuan = (forward_amount + swap_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "amount_yuan": amount_yuan,
        "row_count": int(len(forward_df) + mask.sum()),
        "status": "已计算",
        "note": (
            f"外汇远期货币2金额合计 {forward_amount} 元；"
            f"外汇掉期 Buy/Sell 且远端成交价不为空 {int(mask.sum())} 笔，远端货币2金额合计 {swap_amount} 元。"
        ),
    }


def _default_summary(note: str) -> dict[str, Any]:
    return {
        "amount_yuan": Decimal("0"),
        "amount_thousand": Decimal("0"),
        "row_count": 0,
        "status": "已计算",
        "note": note,
    }


B0280_RULE_TEXT = (
    "34011001科目借方余额+34011002科目借方余额+34011003科目借方余额+34011004科目借方余额+"
    "34011005科目借方余额+34011006科目借方余额+34011007科目借方余额+34011008科目借方余额+"
    "34011009科目借方余额+34011010科目借方余额+34011011科目借方余额+34011012科目借方余额+"
    "34011013科目借方余额+34011014科目借方余额+34011015科目借方余额+34011016科目借方余额+"
    "34019110科目借方余额+34011206科目借方余额"
)


def _load_uploaded_rule_map(upload_path: Path) -> dict[str, dict[str, str]]:
    rule_file = _find_file(upload_path, "2-1-")
    if rule_file is None:
        return {}

    try:
        raw = pd.read_excel(rule_file, sheet_name=0, header=None, dtype=object)
    except Exception:
        return {}

    header_index = _find_header_row(raw, ("指标编码", "指标名称", "指标加工规则"))
    if header_index is None:
        return {}
    df = raw.iloc[header_index + 1 :].copy()
    df.columns = [_clean_text(value) for value in raw.iloc[header_index].tolist()]
    df = df.dropna(how="all")

    rule_map: dict[str, dict[str, str]] = {}
    for _, row in df.iterrows():
        report_name = _clean_text(row.get("报表名称"))
        if report_name and report_name != "五、4 衍生金融工具":
            continue
        code = _clean_text(row.get("指标编码"))
        if not code:
            continue
        rule_map[code] = {
            "name": _clean_text(row.get("指标名称")),
            "rule_text": _clean_text(row.get("指标加工规则")),
            "data_source": _clean_text(row.get("指标数据来源")),
        }
    return rule_map


def _rule_text_for(rule_map: dict[str, dict[str, str]], code: str, fallback: str = "") -> str:
    rule_text = _clean_text(rule_map.get(code, {}).get("rule_text"))
    return rule_text or fallback


def _is_indicator_formula_rule(rule_text: str) -> bool:
    return bool(re.search(r"\bB\d{4}\b", _clean_text(rule_text)))


def _calculate_indicator_formula_summary(
    code: str,
    rule_text: str,
    summaries: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    clean_rule = _clean_text(rule_text)
    if not clean_rule:
        summary = _default_summary(f"{code}暂未配置加工规则，默认按0输出。")
        summary["rule_text"] = rule_text
        return summary

    referenced_codes = re.findall(r"\bB\d{4}\b", clean_rule)
    amount_thousand = Decimal("0")
    component_notes: list[str] = []
    for referenced_code in referenced_codes:
        referenced_summary = summaries.get(referenced_code)
        referenced_amount = _summary_thousand_amount(referenced_summary or _default_summary(""))
        amount_thousand += referenced_amount
        component_notes.append(f"{referenced_code}={referenced_amount}千元")

    amount_yuan = (amount_thousand * THOUSAND).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "amount_yuan": amount_yuan,
        "amount_thousand": amount_thousand.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "row_count": sum(int((summaries.get(referenced_code) or {}).get("row_count") or 0) for referenced_code in referenced_codes),
        "status": "已计算",
        "note": f"{code}按指标公式计算，引用指标为空或未计算时默认0：{', '.join(component_notes) or '无引用指标'}。",
        "rule_text": rule_text,
    }


def _calculate_uploaded_rule_summary(
    upload_path: Path,
    code: str,
    name: str,
    rule_text: str,
    report_period: str | None,
) -> dict[str, Any]:
    if not _clean_text(rule_text) or "科目" not in rule_text:
        summary = _default_summary(f"{code}暂未配置可解析的科目加工规则，默认按0输出。")
        summary["rule_text"] = rule_text
        return summary

    rules_df = pd.DataFrame(
        [
            {
                "指标编码": code,
                "指标名称": name,
                "指标数据来源": "科目",
                "指标加工规则": rule_text,
            }
        ]
    )
    result = RuleCalculator(upload_path, subject_balance_prefix="1-1-", report_period=report_period).calculate(rules_df)
    if result.empty or pd.isna(result.loc[result.index[0], "计算金额"]):
        summary = _default_summary("科目余额表规则未匹配到账户或基础文件，默认按0输出。")
        summary["rule_text"] = rule_text
        return summary

    amount_thousand = Decimal(str(result.loc[result.index[0], "计算金额"]))
    amount_yuan = (amount_thousand * THOUSAND).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    status = str(result.loc[result.index[0], "计算状态"] or "已计算")
    message = str(result.loc[result.index[0], "计算说明"] or "按科目余额表规则计算。")
    return {
        "amount_yuan": amount_yuan,
        "amount_thousand": amount_thousand.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "row_count": 1,
        "status": status,
        "note": f"{message}；原始计算金额 {amount_yuan} 元，折千元 {amount_thousand}。",
        "rule_text": rule_text,
    }


def _fair_value_default_items() -> list[dict[str, str]]:
    return [
        {
            "code": "B0278",
            "name": "货币衍生工具公允价值资产",
            "item_type": "复合指标",
            "rule_text": "货币衍生工具公允价值资产=货币远期外汇公允价值资产+外汇掉期公允价值资产",
        },
        {
            "code": "B0279",
            "name": "货币远期外汇公允价值资产",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目借方余额",
        },
        {
            "code": "B0280",
            "name": "外汇掉期公允价值资产",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目借方余额",
        },
        {
            "code": "B0281",
            "name": "利率衍生工具公允价值资产",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目借方余额",
        },
        {
            "code": "B0282",
            "name": "利率互换公允价值资产",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目借方余额",
        },
        {
            "code": "B0283",
            "name": "贵金属掉期公允价值资产",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目借方余额",
        },
        {
            "code": "B0284",
            "name": "衍生金融工具公允价值资产",
            "item_type": "复合指标",
            "rule_text": "衍生金融工具公允价值资产=货币衍生工具公允价值资产+利率衍生工具公允价值资产+其他衍生工具公允价值资产",
        },
        {
            "code": "B0285",
            "name": "信用风险缓释工具公允价值资产",
            "item_type": "复合指标",
            "rule_text": "科目余额表对应科目借方余额",
        },
        {
            "code": "B0286",
            "name": "货币衍生工具公允价值负债",
            "item_type": "复合指标",
            "rule_text": "货币衍生工具公允价值负债=货币远期外汇公允价值负债+外汇掉期公允价值负债",
        },
        {
            "code": "B0287",
            "name": "货币远期外汇公允价值负债",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目贷方余额",
        },
        {
            "code": "B0288",
            "name": "外汇掉期公允价值负债",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目贷方余额",
        },
        {
            "code": "B0289",
            "name": "利率衍生工具公允价值负债",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目贷方余额",
        },
        {
            "code": "B0290",
            "name": "利率互换公允价值负债",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目贷方余额",
        },
        {
            "code": "B0291",
            "name": "贵金属掉期公允价值负债",
            "item_type": "基础指标",
            "rule_text": "科目余额表对应科目贷方余额",
        },
        {
            "code": "B0292",
            "name": "衍生金融工具公允价值负债",
            "item_type": "复合指标",
            "rule_text": "衍生金融工具公允价值负债=货币衍生工具公允价值负债+利率衍生工具公允价值负债+其他衍生工具公允价值负债",
        },
        {
            "code": "B0293",
            "name": "信用风险缓释工具公允价值负债",
            "item_type": "复合指标",
            "rule_text": "科目余额表对应科目贷方余额",
        },
    ]


def _sum_summaries(
    code: str,
    components: list[tuple[str, dict[str, Any]]],
    note_prefix: str,
) -> dict[str, Any]:
    amount_yuan = sum((summary["amount_yuan"] for _, summary in components), Decimal("0"))
    amount_thousand = sum(
        (_summary_thousand_amount(summary) for _, summary in components),
        Decimal("0"),
    )
    row_count = sum(int(summary.get("row_count") or 0) for _, summary in components)
    component_text = " + ".join(
        f"{component_code}={_summary_thousand_amount(summary)}千元"
        for component_code, summary in components
    )
    return {
        "amount_yuan": amount_yuan.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "amount_thousand": amount_thousand.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "row_count": row_count,
        "status": "已计算",
        "note": f"{note_prefix}；{code}按已加工指标求和，未加工指标默认0：{component_text}。",
    }


def _summary_thousand_amount(summary: dict[str, Any]) -> Decimal:
    if "amount_thousand" in summary:
        return Decimal(str(summary["amount_thousand"]))
    return (Decimal(str(summary["amount_yuan"])) / THOUSAND).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _calculate_b0275(gold_swap_file: Path | None) -> dict[str, Any]:
    if gold_swap_file is None:
        return {
            "amount_yuan": Decimal("0"),
            "amount_thousand": Decimal("0"),
            "row_count": 0,
            "status": "未计算",
            "note": "缺少5-4-1-3 黄金掉期持仓表，请上传后重新生成。",
        }

    df = _read_position_table(gold_swap_file, required_columns=("远端货币1金额", "远端成交价"))
    amount_yuan = _sum_product(df["远端货币1金额"], df["远端成交价"])
    amount_thousand = (amount_yuan / THOUSAND).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return {
        "amount_yuan": amount_yuan.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "amount_thousand": amount_thousand,
        "row_count": len(df),
        "status": "已计算",
        "note": f"黄金掉期远端货币1金额*远端成交价合计 {amount_yuan} 元，按千元整数展示为 {amount_thousand} 千元。",
    }


def _calculate_b0277(crmw_file: Path | None) -> dict[str, Any]:
    if crmw_file is None:
        return {
            "amount_yuan": Decimal("0"),
            "row_count": 0,
            "status": "未计算",
            "note": "缺少5-4-1-4 P&L-CRMW-审计估值，请上传后重新生成。",
        }

    df = _read_position_table(
        crmw_file,
        required_columns=("持仓名义本金（元）",),
        sheet_name="信用风险缓释凭证台账",
    )
    detail_df = _exclude_total_rows(df)
    amount_yuan = _sum_numeric(detail_df["持仓名义本金（元）"])
    return {
        "amount_yuan": amount_yuan.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "row_count": len(detail_df),
        "status": "已计算",
        "note": f"信用风险缓释凭证台账剔除合计行后，持仓名义本金（元）明细合计 {amount_yuan} 元。",
    }


def _find_file(upload_dir: Path, prefix: str) -> Path | None:
    matches = sorted(upload_dir.glob(f"{prefix}*.xlsx"), key=lambda path: path.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def _source_names(paths: list[Path | None]) -> str:
    return " + ".join(path.name for path in paths if path is not None)


def _summarize_source_file(source_file: Path | None) -> dict[str, Any]:
    if source_file is None:
        return {
            "amount_yuan": Decimal("0"),
            "row_count": 0,
            "note": "尚未上传对应持仓表，请上传后重新生成。",
        }

    try:
        sheets = pd.read_excel(source_file, sheet_name=None, dtype=object)
    except Exception as exc:
        raise ValueError(f"读取衍生金融工具持仓表失败：{source_file.name}，{exc}") from exc

    amount_yuan = Decimal("0")
    row_count = 0
    used_columns: list[str] = []
    for sheet_name, sheet_df in sheets.items():
        df = _clean_dataframe(sheet_df)
        if df.empty:
            continue
        columns = _amount_columns(df)
        if not columns:
            columns = _numeric_columns(df)
        for column in columns:
            amount_yuan += _sum_numeric(df[column])
            used_columns.append(f"{sheet_name}.{column}")
        row_count += len(df)

    return {
        "amount_yuan": amount_yuan.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "row_count": row_count,
        "note": (
            f"读取 {source_file.name}，有效明细 {row_count} 行，汇总列：{', '.join(used_columns[:8]) or '无可识别金额列'}。"
        ),
    }


def _read_position_table(
    source_file: Path,
    required_columns: tuple[str, ...],
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    raw = pd.read_excel(source_file, sheet_name=sheet_name, header=None, dtype=object)
    header_index = _find_header_row(raw, required_columns)
    if header_index is None:
        raise ValueError(f"{source_file.name} 未找到表头列：{', '.join(required_columns)}")
    df = raw.iloc[header_index + 1 :].copy()
    df.columns = [_clean_text(value) for value in raw.iloc[header_index].tolist()]
    df = df.dropna(how="all").dropna(axis=1, how="all")
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"{source_file.name} 缺少列：{', '.join(missing_columns)}")
    return df.reset_index(drop=True)


def _find_header_row(raw: pd.DataFrame, required_columns: tuple[str, ...]) -> int | None:
    required = {_clean_text(column) for column in required_columns}
    for index, row in raw.iterrows():
        values = {_clean_text(value) for value in row.tolist()}
        if required.issubset(values):
            return int(index)
    return None


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned = cleaned.dropna(how="all").dropna(axis=1, how="all")
    cleaned.columns = [_clean_text(column) for column in cleaned.columns]
    return cleaned


def _amount_columns(df: pd.DataFrame) -> list[str]:
    columns: list[str] = []
    for column in df.columns:
        column_text = _clean_text(column).lower()
        if any(keyword.lower() in column_text for keyword in AMOUNT_COLUMN_KEYWORDS):
            if pd.to_numeric(df[column].map(_clean_number), errors="coerce").notna().any():
                columns.append(column)
    return columns


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    columns: list[str] = []
    for column in df.columns:
        numeric = pd.to_numeric(df[column].map(_clean_number), errors="coerce")
        if numeric.notna().sum() >= max(1, int(len(df) * 0.3)):
            columns.append(column)
    return columns


def _sum_numeric(series: pd.Series) -> Decimal:
    values = pd.to_numeric(series.map(_clean_number), errors="coerce").dropna()
    total = Decimal("0")
    for value in values:
        total += Decimal(str(value))
    return total


def _sum_product(left: pd.Series, right: pd.Series) -> Decimal:
    left_values = pd.to_numeric(left.map(_clean_number), errors="coerce")
    right_values = pd.to_numeric(right.map(_clean_number), errors="coerce")
    total = Decimal("0")
    for left_value, right_value in zip(left_values, right_values, strict=False):
        if pd.isna(left_value) or pd.isna(right_value):
            continue
        total += Decimal(str(left_value)) * Decimal(str(right_value))
    return total


def _exclude_total_rows(df: pd.DataFrame) -> pd.DataFrame:
    mask = df.apply(
        lambda row: any(_clean_text(value) == "合计" for value in row.tolist()),
        axis=1,
    )
    return df.loc[~mask].reset_index(drop=True)


def _clean_number(value: Any) -> Any:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().replace(",", "")
    if text in {"", "-", "--", "nan", "NaN", "None"}:
        return None
    if text.startswith("(") and text.endswith(")"):
        text = f"-{text[1:-1]}"
    return text


def _report_row(
    index: int,
    report_period: str | None,
    report_name: str,
    code: str,
    name: str,
    data_source: str,
    item_type: str,
    rule_text: str,
    amount_yuan: Decimal,
    status: str,
    note: str,
    row_count: int,
    amount_thousand: Decimal | float | None = None,
) -> dict[str, Any]:
    display_amount_thousand = float(amount_thousand) if amount_thousand is not None else _to_thousand_yuan(amount_yuan)
    return {
        "序号": index,
        "期间": report_period or "",
        "报表名称": report_name,
        "指标编码": code,
        "指标名称": name,
        "数据来源": data_source,
        "指标类型": item_type,
        "加工规则": rule_text,
        "明细笔数": row_count,
        "明细金额-元": float(amount_yuan),
        "生成金额-集团": display_amount_thousand,
        "生成金额-本行": display_amount_thousand,
        "计算状态": status,
        "计算说明": note,
    }


def _clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())


def _to_thousand_yuan(value: Decimal) -> float:
    return float((value / THOUSAND).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
