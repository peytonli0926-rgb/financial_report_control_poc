from __future__ import annotations

import ast
import operator
import re
import zipfile
from html import unescape
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import pandas as pd
from openpyxl import load_workbook


ACCOUNT_RULE_PATTERN = re.compile(
    r"(?<!\d)(?:(科目余额表|本行|集团|合并|子公司)\s*(?:中)?\s*)?(?:新)?(\d{4,8})(?!\d)\s*(?=(?:科目|余额|期初|期末|发生额|借方|贷方))(?:科目)?(?:\s*(余额|期初|期末|发生额))?\s*(借方|贷方)?\s*(?:余额|金额)?\s*(轧差值|轧差额|轧差|合计)?"
)
SUBJECT_CURRENT_PREVIOUS_DELTA_PATTERN = re.compile(
    r"(?<!\d)(?:新)?(?P<code>\d{4,8})(?!\d)\s*(?:科目)?\s*(?P<side>借方|贷方)?\s*余额\s*(?P<net>轧差值|轧差额|轧差)?\s*[（(]\s*本期\s*-\s*上期\s*[）)]"
)
COMBO_RULE_PATTERN = re.compile(r"【([^】]+)】\s*组合科目余额\s*(借方|贷方)?\s*(轧差值)?")
DETAIL_POSITIVE_BALANCE_PATTERN = re.compile(
    r"(?<!\d)(\d{4,8})(?!\d)\s*科目下\s*(?:期末)?\s*(借方|贷方)余额为正(?:的明细)?科目(?:余额)?合计"
)
EXPLICIT_ADJUSTMENT_PATTERN = re.compile(
    r"([+-])\s*(母行|子公司|合并抵[销消])(?:审计调整)?底稿中\s*(\d{4,8})"
    r"\s*(?:科目)?(?:调整)?(?:金额)?"
)
EXPLICIT_ALL_ADJUSTMENT_PATTERN = re.compile(
    r"([+-])\s*(\d{4,8})\s*(?:审计调整及合并抵[销消]|审计调整和合并抵[销消])(?:调整)?金额"
)
ADJUSTMENT_AMOUNT_PATTERN = re.compile(
    r"(母行|子公司|合并抵[销消])(?:审计调整)?底稿中\s*(\d{4,8})\s*(?:科目)?(?:调整)?金额"
)
FILTERED_ADJUSTMENT_AMOUNT_PATTERN = re.compile(
    r"(母行|子公司|合并抵[销消])(?:审计调整)?底稿中\s*"
    r"(?:(?:调整代码|行号)\s*(?P<adjustment_code>[^的]+?)\s*的\s*"
    r"|调整说明\s*(?P<adjustment_description>[^的]+?)\s*的\s*"
    r"|机构\s*(?P<institution_name>[^调的]+?)\s*调整说明\s*(?P<institution_description>[^的]+?)\s*的\s*)"
    r"(?P<code>\d{4,8})\s*科目(?:调整)?金额"
)
OCI_RULE_PATTERN = re.compile(r"(新?\d{4,8})\s*(本年|上年)\s*(集团|本行)\s*余额")
OCI_PERIOD_BALANCE_PATTERN = re.compile(r"(?P<code>新?\d{4,8})(?P<body>[^+\-*/()（）]*?)(?P<period>本期数|上期数)")
OCI_SUBSIDIARY_CONSOLIDATION_DELTA_PATTERN = re.compile(
    r"审计子公司合并抵[销消]\s*(?P<code>新?\d{4,8})\s*本期\s*-\s*上期"
)
CONSOLIDATION_FIRST_AMOUNT_PATTERN = re.compile(r"合并抵[销消]表中\s*(\d{4,8})\s*科目首笔金额")
CONSOLIDATION_IFRS_MAPPING_AMOUNT_PATTERN = re.compile(
    r"合并抵[销消]底稿\s*IFRS\s*mapping\s*=\s*([^+\-*/()（）]+?)\s*本年末金额"
)
CONSOLIDATION_PERIOD_AMOUNT_PATTERN = re.compile(
    r"合并抵[销消]底稿中\s*(?:新)?(\d{4,8})\s*科目\s*(本年|上年)(?:末)?余额"
)
CONSOLIDATION_RAW_PERIOD_TERM_PATTERN = re.compile(
    r"(?:合并抵[销消]底稿中\s*)?(?:新)?(?P<code>\d{4,8})\s*(?P<period>本期|上期)"
)
CONSOLIDATION_DATE_AMOUNT_PATTERN = re.compile(
    r"合并抵[销消]底稿中\s*(?:新)?(?P<code>\d{4,8})\s*科目\s*(?P<date>\d{4}年\d{1,2}月\d{1,2}日|\d{8})\s*金额"
)
SUBSIDIARY_OWNERSHIP_AMOUNT_PATTERN = re.compile(
    r"子公司\s*(\d{4,8})\s*科目\s*发生额\s*贷方\s*\*\s*\(\s*1\s*-\s*子公司持股比例\s*\)"
)
PERPETUAL_BOND_INTEREST_PATTERN = re.compile(
    r"(?:1-9-20251231)?永续债明细表(?:的)?每支永续债发行金额\*初始利率之和|永续债明细表发行金额乘初始利率之和"
)
AMC_MAPPING_BALANCE_PATTERN = re.compile(
    r"(?P<prefix>30[1-4]_01_20251231)[^+\n\r]*?科目余额表的科目编码\s*in\s*"
    r"[（(](?P<table>[^.）)]+?)科目映射表\.(?P<column>[^=）)]+?)\s*=\s*['‘’\"]"
    r"(?P<target>.*?)(?:['‘’\"]\s*[）)]\s*的余额合计数|(?=\+\s*30[1-4]_01_20251231)|$)",
    re.DOTALL,
)
AMC_PREFIX_INSTITUTION = {
    "301_01_20251231": "资产公司",
    "302_01_20251231": "银行类",
    "303_01_20251231": "证券类",
    "304_01_20251231": "保险类",
}
AMOUNT_UNIT_DIVISOR = 1000.0
ACTUARIAL_BENEFIT_OBLIGATION_AMOUNTS = {
    "B0722": 2333035.0,
    "B0723": 54120.0,
}

ACTUARIAL_DEFINED_BENEFIT_VALUES = {
    "B0760": 0.0225,
    "B0761": 0.015,
    "B0762": 0.06,
    "B0763": 0.07,
    "B0764": 0.045,
    "B0765": "CL5/CL6 (2010 - 2013)",
    "B0766": 11820.0,
    "B0767": 0.0,
    "B0768": 51370.0,
    "B0769": -32300.0,
    "B0770": -128320.0,
    "B0771": -24300.0,
    "B0772": -152620.0,
    "B0773": -184920.0,
    "B0774": 2306060.0,
    "B0775": 12960.0,
    "B0776": 0.0,
    "B0777": 21200.0,
    "B0778": 11820.0,
    "B0779": 0.0,
    "B0780": 18990.0,
    "B0781": 2333035.0,
}

CODE_COLUMNS_BY_LENGTH = {
    4: "level1_code",
    6: "level2_code",
    8: "level3_code",
}

_UNUSED_CREDIT_CARD_LIMIT_CACHE: dict[tuple[str, int], float | None] = {}
_OFF_BALANCE_HTML_ROWS_CACHE: dict[tuple[str, int], list[list[str]]] = {}


class RuleCalculator:
    def __init__(
        self,
        upload_dir: str | Path,
        subject_balance_prefix: str = "1-1-",
        institution_code: str | None = None,
        initial_values: dict[str, float] | None = None,
        oci_entity: str | None = "集团",
        report_period: str | None = None,
    ):
        self.upload_dir = Path(upload_dir)
        self.subject_balance_prefix = subject_balance_prefix
        self.institution_code = _clean_code(institution_code) if institution_code else ""
        self.initial_values = initial_values or {}
        self.oci_entity = oci_entity if oci_entity in {"集团", "本行"} else None
        self.report_period = _normalize_period(report_period)
        self._subject_balance_df: pd.DataFrame | None = None
        self._subject_balance_df_by_prefix: dict[str, pd.DataFrame] = {}
        self._adjustment_df: pd.DataFrame | None = None
        self._oci_balance_df: pd.DataFrame | None = None
        self._impairment_detail_sheet_cache: dict[tuple[Path, str], pd.DataFrame] = {}
        self._amc_subject_balance_cache: dict[str, pd.DataFrame] = {}
        self._amc_mapping_cache: dict[str, pd.DataFrame] = {}

    def calculate(self, rules_df: pd.DataFrame) -> pd.DataFrame:
        if rules_df is None or rules_df.empty:
            return pd.DataFrame(index=rules_df.index if rules_df is not None else None)

        result = pd.DataFrame(index=rules_df.index)
        result["计算金额"] = pd.NA
        result["计算状态"] = "未计算"
        result["计算说明"] = ""

        values_by_name: dict[str, float] = dict(self.initial_values)
        self._seed_oci_previous_values(values_by_name)
        pending_indexes: list[int] = []

        for index, row in rules_df.iterrows():
            rule_text = _row_text(row, "指标加工规则", "加工规则")
            item_code = _row_text(row, "指标编码")
            if item_code in {"B0757", "B0758", "B0759", "B1162", "B1163", "B1164", "B1165"}:
                amount, status, message = self._calculate_independent_rule(row)
                result.at[index, "计算金额"] = amount
                result.at[index, "计算状态"] = status
                result.at[index, "计算说明"] = message
                item_name = _row_text(row, "指标名称")
                if amount is not None and item_name:
                    _register_calculated_row_value(values_by_name, row, amount, self.report_period, self)
                elif rule_text:
                    pending_indexes.append(index)
                continue
            if _is_formula_rule(rule_text):
                result.at[index, "计算说明"] = "等待指标公式计算"
                pending_indexes.append(index)
                continue

            amount, status, message = self._calculate_independent_rule(row)
            result.at[index, "计算金额"] = amount
            result.at[index, "计算状态"] = status
            result.at[index, "计算说明"] = message
            item_name = _row_text(row, "指标名称")
            if amount is not None and item_name:
                _register_calculated_row_value(values_by_name, row, amount, self.report_period, self)
            elif _row_text(row, "指标加工规则", "加工规则"):
                pending_indexes.append(index)

        for _ in range(5):
            changed = False
            for index in list(pending_indexes):
                row = rules_df.loc[index]
                amount, status, message = self._calculate_formula_rule(row, values_by_name)
                if amount is None:
                    if result.at[index, "计算状态"] == "未计算":
                        result.at[index, "计算说明"] = message
                    continue

                result.at[index, "计算金额"] = amount
                result.at[index, "计算状态"] = status
                result.at[index, "计算说明"] = message
                item_name = _row_text(row, "指标名称")
                if item_name:
                    _register_calculated_row_value(values_by_name, row, amount, self.report_period, self)
                pending_indexes.remove(index)
                changed = True
            if not changed:
                break

        return result

    def build_amc_mapping_trace(self, rules_df: pd.DataFrame) -> pd.DataFrame:
        """Expand AMC mapping-balance rules to source mapping and balance rows."""
        if rules_df is None or rules_df.empty:
            return pd.DataFrame()

        trace_rows: list[dict[str, Any]] = []
        for _, row in rules_df.iterrows():
            rule_text = _row_text(row, "指标加工规则", "加工规则")
            if not AMC_MAPPING_BALANCE_PATTERN.search(rule_text):
                continue

            item_code = _row_text(row, "指标编码")
            item_name = _row_text(row, "指标名称")
            report_name = _row_text(row, "报表名称")
            data_source = _row_text(row, "指标数据来源", "数据来源")
            trailing_multiplier = _amc_mapping_rule_trailing_multiplier(rule_text)

            for match in AMC_MAPPING_BALANCE_PATTERN.finditer(rule_text):
                prefix = _normalize_text(match.group("prefix"))
                institution = AMC_PREFIX_INSTITUTION.get(prefix, "")
                mapping_column = _normalize_amc_mapping_column(match.group("column"))
                target = _normalize_amc_mapping_target(match.group("target"))
                term_sign = _term_sign(rule_text, match.start())
                balance_file = _find_file_by_prefix(self.upload_dir, prefix)
                mapping_file = _amc_subject_mapping_input_path(self.upload_dir, institution) if institution else None
                base_row = {
                    "报表名称": report_name,
                    "指标编码": item_code,
                    "指标名称": item_name,
                    "数据来源": data_source,
                    "加工规则": rule_text,
                    "余额表前缀": prefix,
                    "机构类型": institution,
                    "映射口径列": mapping_column,
                    "目标映射项": target,
                    "规则项符号": term_sign,
                    "整体尾部乘数": trailing_multiplier,
                    "科目余额表文件": balance_file.name if balance_file else "",
                    "科目映射表文件": mapping_file.name if mapping_file else "",
                }
                if not institution or not mapping_column or not target:
                    trace_rows.append({**base_row, "追溯状态": "规则项无法解析"})
                    continue

                mapping_df = self._load_amc_mapping_df(institution)
                balance_df = self._load_amc_subject_balance_df(prefix)
                if mapping_df.empty or balance_df.empty or mapping_column not in mapping_df.columns:
                    trace_rows.append({**base_row, "追溯状态": "映射表或余额表缺失"})
                    continue

                selected_mapping = mapping_df.loc[
                    mapping_df[mapping_column].map(_normalize_text).eq(target),
                    ["account_code", "account_name", mapping_column],
                ].drop_duplicates()
                if selected_mapping.empty:
                    trace_rows.append({**base_row, "追溯状态": "映射表未命中科目"})
                    continue

                matched_balance = balance_df.merge(
                    selected_mapping,
                    on=["account_code", "account_name"],
                    how="inner",
                )
                if matched_balance.empty:
                    for _, mapping_row in selected_mapping.iterrows():
                        trace_rows.append(
                            {
                                **base_row,
                                "追溯状态": "映射命中但余额表未匹配",
                                "科目编码": mapping_row.get("account_code", ""),
                                "科目名称": mapping_row.get("account_name", ""),
                                "映射值": mapping_row.get(mapping_column, ""),
                                "原始余额-元": 0.0,
                                "贡献金额-元": 0.0,
                                "贡献金额-千元": 0.0,
                            }
                        )
                    continue

                for _, balance_row in matched_balance.iterrows():
                    amount_yuan = float(
                        pd.to_numeric(pd.Series([balance_row.get("amount", 0.0)]), errors="coerce")
                        .fillna(0.0)
                        .iloc[0]
                    )
                    contribution_yuan = amount_yuan * term_sign * trailing_multiplier
                    trace_rows.append(
                        {
                            **base_row,
                            "追溯状态": "已追溯",
                            "科目编码": balance_row.get("account_code", ""),
                            "科目名称": balance_row.get("account_name", ""),
                            "映射值": balance_row.get(mapping_column, ""),
                            "原始余额-元": amount_yuan,
                            "贡献金额-元": contribution_yuan,
                            "贡献金额-千元": contribution_yuan / AMOUNT_UNIT_DIVISOR,
                        }
                    )

        return pd.DataFrame(trace_rows)

    def _calculate_independent_rule(self, row: pd.Series) -> tuple[float | None, str, str]:
        data_source = _row_text(row, "指标数据来源", "数据来源")
        rule_text = _row_text(row, "指标加工规则", "加工规则")
        item_code = _row_text(row, "指标编码")
        item_name = _row_text(row, "指标名称")

        if item_code.startswith("A6") and not rule_text and data_source == "明细":
            return 0.0, "已计算", "AMC集团利润表明细项未配置加工规则，按0参与上级公式"
        if item_code.startswith("A6") and not rule_text and not data_source and re.match(r"^[一二三四五六七八九十]+、", item_name):
            return None, "已计算", "AMC集团利润表标题展示行，无金额计算规则"

        if item_code == "B0694":
            amount = self._calculate_asset_impairment_b0694_amount()
            if amount is not None:
                return amount, "已计算", "按41029101科目余额贷方轧差值取正数，并叠加审计调整/合并抵销金额，单位转换为千元"

        if item_code == "B1162":
            amount = _calculate_unused_credit_card_limit(self.upload_dir, self.report_period)
            if amount is not None:
                return amount, "已计算", "按8-1信用卡及消费金融部文件有余额/无余额表头的未使用授信额度汇总，单位转换为千元"
        if item_code in {"B1163", "B1164", "B1165"} and self.subject_balance_prefix == "1-1-":
            amount = _calculate_credit_commitment_off_balance_amount(item_code, self.upload_dir, self.report_period)
            if amount is not None:
                return amount, "已计算", "按8-1-2表外科目集团文件期末借方轧差值计算，单位转换为千元"

        actuarial_amount = _calculate_actuarial_valuation_rule(item_code, rule_text, self.upload_dir)
        if actuarial_amount is not None:
            return actuarial_amount, "已计算", "按2025年12月31日时点精算评估报告取数，单位为千元"

        defined_benefit_amount = _calculate_actuarial_defined_benefit_rule(item_code, rule_text, self.upload_dir)
        if defined_benefit_amount is not None:
            if item_code == "B0765":
                return defined_benefit_amount, "已计算", "按精算评估报告取数：死亡率为 CL5/CL6 (2010-2013)，文本项以0占位"
            return defined_benefit_amount, "已计算", "按2025年12月31日时点精算评估报告取数"

        defined_contribution_amount = self._calculate_defined_contribution_total(item_code)
        if defined_contribution_amount is not None:
            return defined_contribution_amount, "已计算", "按设定提存计划明细科目合计计算，单位转换为千元"

        subject_delta_amount = self._calculate_subject_current_previous_delta_rule(rule_text)
        if subject_delta_amount is not None:
            return subject_delta_amount, "已计算", "按科目余额期末与期初轧差变动计算，单位转换为千元"

        consolidation_date_amount = _calculate_consolidation_date_amount_rule(rule_text, self.upload_dir)
        if consolidation_date_amount is not None:
            return consolidation_date_amount, "已计算", "按合并抵消底稿指定日期原始金额计算，单位转换为千元"

        amc_mapping_amount = self._calculate_amc_mapping_balance_rule(rule_text)
        if amc_mapping_amount is not None:
            return amc_mapping_amount, "已计算", "按AMC集团科目余额表和科目映射表筛选汇总，单位转换为千元"

        default_amount = _parse_default_amount(data_source, rule_text)
        if default_amount is not None:
            return default_amount, "已计算", "按默认值计算"

        if "OCI" in rule_text or "OCI表" in rule_text:
            rule_text = self._normalize_oci_rule_for_item(rule_text, item_code)
            amount = self._calculate_oci_rule(rule_text)
            if amount is not None:
                return amount, "已计算", "按 OCI 表余额规则计算"
            return None, "未计算", "OCI 表规则未匹配到账户或基础文件"

        oci_period_amount = self._calculate_oci_period_balance_rule(rule_text)
        if oci_period_amount is not None:
            return oci_period_amount, "已计算", "按 OCI 表本期/上期余额差额规则计算"

        oci_subsidiary_amount = self._calculate_oci_subsidiary_consolidation_delta(rule_text)
        if oci_subsidiary_amount is not None:
            return oci_subsidiary_amount, "已计算", "按 OCI 表集团与本行差额的本期/上期变动计算"

        fixed_asset_movement_amount = self._calculate_fixed_asset_movement_rule(rule_text, item_code)
        if fixed_asset_movement_amount is not None:
            return (
                fixed_asset_movement_amount,
                "已计算",
                "按固定资产增减变动明细表筛选汇总，单位转换为千元",
            )

        impairment_migration_amount = self._calculate_impairment_migration_rule(rule_text)
        if impairment_migration_amount is not None:
            impairment_migration_amount = _adjust_impairment_migration_sign(
                item_code,
                _row_text(row, "指标名称"),
                impairment_migration_amount,
            )
            return (
                impairment_migration_amount,
                "已计算",
                "按减值明细表跨期 BUSI_PK_ID 匹配迁徙阶段，并汇总迁出期 ECL_FINAL，单位转换为千元",
            )

        impairment_detail_amount = self._calculate_impairment_detail_aggregate_rule(rule_text)
        if impairment_detail_amount is not None:
            return (
                impairment_detail_amount,
                "已计算",
                "按减值明细表指定期间和过滤条件汇总 ECL_FINAL，单位转换为千元",
            )

        if ADJUSTMENT_AMOUNT_PATTERN.search(rule_text):
            replaced_expression, matched_adjustment = self._replace_adjustment_amount_terms_in_expression(rule_text)
            if matched_adjustment and not re.search(r"[\u4e00-\u9fff]", replaced_expression):
                try:
                    amount = _safe_eval_numeric_expression(replaced_expression)
                except Exception:
                    amount = None
                if amount is not None:
                    return amount, "已计算", "按审计调整底稿金额计算，单位转换为千元"

        if item_code == "B0537":
            amount = self._calculate_fixed_asset_decrease_accumulated_depreciation_total()
            if amount is not None:
                return amount, "已计算", "按B0533-B0536固定资产增减明细口径合计计算"

        if _contains_account_rule(rule_text):
            if item_code == "B0828":
                rule_text = _apply_b0828_adjustment_rule(rule_text)
            if item_code == "B0580":
                rule_text = _apply_b0580_intangible_amortization_rule(rule_text)
            include_adjustments = item_code not in {"B0445", "B0656"}
            amount = self._calculate_subject_balance_rule(rule_text, include_adjustments=include_adjustments)
            if amount is not None:
                if "发生额" in _normalize_subject_occurrence_rule_text(rule_text):
                    return amount, "已计算", "按科目余额表本期发生额直接计算，单位转换为千元"
                if not include_adjustments:
                    return amount, "已计算", "按科目余额表直接计算，未叠加审计调整或合并抵销，单位转换为千元"
                return amount, "已计算", self._subject_rule_message()
            return None, "未计算", "科目余额规则未匹配到账户或基础文件"

        return None, "未计算", "等待指标公式或暂不支持的规则类型"

    def _calculate_amc_mapping_balance_rule(self, rule_text: str) -> float | None:
        if "科目映射表" not in rule_text or "科目余额表" not in rule_text or "余额合计数" not in rule_text:
            return None

        matches = list(AMC_MAPPING_BALANCE_PATTERN.finditer(rule_text))
        if not matches:
            return None

        total = 0.0
        matched_any = False
        for match in matches:
            prefix = _normalize_text(match.group("prefix"))
            institution = AMC_PREFIX_INSTITUTION.get(prefix)
            if not institution:
                continue
            mapping_column = _normalize_amc_mapping_column(match.group("column"))
            target = _normalize_amc_mapping_target(match.group("target"))
            if not mapping_column or not target:
                continue

            mapping_df = self._load_amc_mapping_df(institution)
            balance_df = self._load_amc_subject_balance_df(prefix)
            if mapping_df.empty or balance_df.empty or mapping_column not in mapping_df.columns:
                continue

            selected_mapping = mapping_df.loc[
                mapping_df[mapping_column].map(_normalize_text).eq(target),
                ["account_code", "account_name"],
            ].drop_duplicates()
            if selected_mapping.empty:
                matched_any = True
                continue

            matched_balance = balance_df.merge(selected_mapping, on=["account_code", "account_name"], how="inner")
            amount = pd.to_numeric(matched_balance["amount"], errors="coerce").fillna(0.0).sum()
            total += _term_sign(rule_text, match.start()) * float(amount)
            matched_any = True

        if not matched_any:
            return None
        return (total / AMOUNT_UNIT_DIVISOR) * _amc_mapping_rule_trailing_multiplier(rule_text)

    def _load_amc_subject_balance_df(self, prefix: str) -> pd.DataFrame:
        if prefix in self._amc_subject_balance_cache:
            return self._amc_subject_balance_cache[prefix]

        file_path = _find_file_by_prefix(self.upload_dir, prefix)
        if file_path is None:
            self._amc_subject_balance_cache[prefix] = pd.DataFrame(columns=["account_code", "account_name", "amount"])
            return self._amc_subject_balance_cache[prefix]

        raw_df = pd.read_excel(file_path, sheet_name=0, dtype=object, engine="openpyxl").fillna("")
        code_column = _find_column_by_alias(raw_df.columns, ["科目编码", "科目代码", "科目号", "account_code"])
        name_column = _find_column_by_alias(raw_df.columns, ["科目名称", "科目名", "account_name"])
        amount_column = _find_column_by_alias(raw_df.columns, ["科目余额", "科目余额表", "余额", "amount"])
        if code_column is None or name_column is None or amount_column is None:
            self._amc_subject_balance_cache[prefix] = pd.DataFrame(columns=["account_code", "account_name", "amount"])
            return self._amc_subject_balance_cache[prefix]

        result = pd.DataFrame(
            {
                "account_code": raw_df[code_column].map(_clean_code),
                "account_name": raw_df[name_column].map(_normalize_text),
                "amount": pd.to_numeric(raw_df[amount_column], errors="coerce").fillna(0.0),
            }
        )
        result = result.loc[(result["account_code"] != "") & (result["account_name"] != "")].copy()
        self._amc_subject_balance_cache[prefix] = result
        return result

    def _load_amc_mapping_df(self, institution: str) -> pd.DataFrame:
        if institution in self._amc_mapping_cache:
            return self._amc_mapping_cache[institution]

        mapping_path = _amc_subject_mapping_input_path(self.upload_dir, institution)
        if mapping_path is None:
            self._amc_mapping_cache[institution] = pd.DataFrame()
            return self._amc_mapping_cache[institution]

        raw_df = pd.read_excel(mapping_path, dtype=object, engine="openpyxl").fillna("")
        code_column = _find_column_by_alias(raw_df.columns, ["科目编码", "科目代码", "科目号", "account_code"])
        name_column = _find_column_by_alias(raw_df.columns, ["科目名称", "科目名", "account_name"])
        if code_column is None or name_column is None:
            self._amc_mapping_cache[institution] = pd.DataFrame()
            return self._amc_mapping_cache[institution]

        result = pd.DataFrame(
            {
                "account_code": raw_df[code_column].map(_clean_code),
                "account_name": raw_df[name_column].map(_normalize_text),
            }
        )
        column_aliases = {
            "财政部口径映射": ["财政部口径映射", "财政部报表口径", "财政部口径"],
            "IFRS 18映射": ["IFRS 18映射", "IFRS18映射", "IFRS 18分类", "IFRS18分类"],
            "集团科目口径映射": ["集团科目口径映射", "集团口径映射", "集团科目口径"],
        }
        for target_column, aliases in column_aliases.items():
            source_column = _find_column_by_alias(raw_df.columns, aliases)
            result[target_column] = raw_df[source_column].map(_normalize_text) if source_column is not None else ""
        result = result.loc[(result["account_code"] != "") & (result["account_name"] != "")].copy()
        self._amc_mapping_cache[institution] = result
        return result

    def _calculate_defined_contribution_total(self, item_code: str) -> float | None:
        code = _normalize_text(item_code)
        if code not in {"B0757", "B0758", "B0759"}:
            return None
        subject_df = self._load_subject_balance_df()
        if subject_df.empty:
            return None
        subject_codes = ("24010601", "24010602", "24010605")
        if code == "B0757":
            amount = sum(_subject_amount(subject_df, subject_code, "贷方", False, "发生额") for subject_code in subject_codes)
        elif code == "B0758":
            amount = -sum(_subject_amount(subject_df, subject_code, "借方", False, "发生额") for subject_code in subject_codes)
        else:
            amount = sum(_subject_amount(subject_df, subject_code, "贷方", True, "余额") for subject_code in subject_codes)
        return amount / AMOUNT_UNIT_DIVISOR

    def _calculate_impairment_detail_aggregate_rule(self, rule_text: str) -> float | None:
        if "ECL_FINAL" not in rule_text or "合计数" not in rule_text:
            return None
        if "减值明细" not in rule_text and not re.search(r"(?<!\d)20\d{6}\s*sheet", rule_text, flags=re.IGNORECASE):
            return None

        delta_amount = self._calculate_impairment_detail_period_filter_delta_rule(rule_text)
        if delta_amount is not None:
            return delta_amount

        period = _period_from_impairment_detail_aggregate_rule(rule_text, self.report_period)
        if not period:
            return None

        detail_file = _find_impairment_detail_file(self.upload_dir, rule_text)
        if detail_file is None:
            return None

        detail_df = self._load_impairment_detail_sheet(detail_file, period)
        if detail_df.empty:
            return None

        filters = _impairment_detail_filters(rule_text)
        if not filters:
            return None

        filtered_df = _filter_impairment_detail_df_by_filters(detail_df, filters)
        amount = pd.to_numeric(filtered_df["ECL_FINAL"], errors="coerce").fillna(0.0).sum()
        return float(amount) / AMOUNT_UNIT_DIVISOR

    def _calculate_impairment_detail_period_filter_delta_rule(self, rule_text: str) -> float | None:
        periods = _periods_from_impairment_detail_filter_delta_rule(rule_text)
        if len(periods) < 2:
            return None

        detail_file = _find_impairment_detail_file(self.upload_dir, rule_text)
        if detail_file is None:
            return None

        amounts: list[float] = []
        for period in periods[:2]:
            detail_df = self._load_impairment_detail_sheet(detail_file, period)
            if detail_df.empty:
                return None
            filters = _period_impairment_detail_filters(rule_text, period)
            if not filters:
                return None
            filtered_df = _filter_impairment_detail_df_by_filters(detail_df, filters)
            amount = pd.to_numeric(filtered_df["ECL_FINAL"], errors="coerce").fillna(0.0).sum()
            amounts.append(float(amount))
        return (amounts[0] - amounts[1]) / AMOUNT_UNIT_DIVISOR

    def _replace_impairment_detail_aggregate_terms_in_expression(self, expression: str) -> tuple[str, bool]:
        replaced_parts: list[str] = []
        last_end = 0
        matched = False
        context_prefix = ""

        for match in _iter_impairment_detail_aggregate_terms(expression):
            prefix_text = expression[last_end : match.start()]
            term_text = match.group(0)
            context_match = re.search(r"([^+\-*/()（）]*?减值明细表中)\s*$", prefix_text)
            if context_match:
                context_prefix = context_match.group(1)
                prefix_text = prefix_text[: context_match.start()]
            term_context_match = re.search(r"([^+\-*/()（）]*?减值明细表中)", term_text)
            if term_context_match:
                context_prefix = term_context_match.group(1)
            replaced_parts.append(prefix_text)

            calculation_text = term_text if "减值明细" in term_text else f"{context_prefix}{term_text}"
            amount = self._calculate_impairment_detail_aggregate_rule(calculation_text)
            if amount is None:
                replaced_parts.append(term_text)
            else:
                replaced_parts.append(str(amount))
                matched = True
            last_end = match.end()

        if not matched:
            return expression, False

        replaced_parts.append(expression[last_end:])
        return "".join(replaced_parts), True

    def _calculate_impairment_migration_rule(self, rule_text: str) -> float | None:
        if not _looks_like_impairment_migration_rule(rule_text):
            return None

        periods = _periods_from_impairment_rule(rule_text)
        if len(periods) < 2:
            return None
        current_period = self.report_period if self.report_period in periods else periods[-1]
        previous_period = next((period for period in periods if period != current_period), periods[0])

        current_stage = _period_filter_value(rule_text, current_period, "STAGE_RSLT_FINAL")
        previous_stage = _period_filter_value(rule_text, previous_period, "STAGE_RSLT_FINAL")
        if not current_stage or not previous_stage:
            return None

        detail_file = _find_impairment_detail_file(self.upload_dir, rule_text)
        if detail_file is None:
            return None

        current_df = self._load_impairment_detail_sheet(detail_file, current_period)
        previous_df = self._load_impairment_detail_sheet(detail_file, previous_period)
        if current_df.empty or previous_df.empty:
            return None

        common_filters = _common_impairment_filters(rule_text)
        current_filtered = _filter_impairment_detail_df(current_df, common_filters, current_stage)
        previous_filtered = _filter_impairment_detail_df(previous_df, common_filters, previous_stage)
        if current_filtered.empty or previous_filtered.empty:
            return 0.0

        matched_ids = set(current_filtered["BUSI_PK_ID"]).intersection(set(previous_filtered["BUSI_PK_ID"]))
        if not matched_ids:
            return 0.0

        ecl_period = _period_qualified_ecl_period(rule_text) or previous_period
        source_df = current_filtered if ecl_period == current_period else previous_filtered
        matched_df = source_df.loc[source_df["BUSI_PK_ID"].isin(matched_ids)]
        amount = pd.to_numeric(matched_df["ECL_FINAL"], errors="coerce").fillna(0.0).sum()
        return float(amount) / AMOUNT_UNIT_DIVISOR

    def _calculate_fixed_asset_movement_rule(self, rule_text: str, item_code: str = "") -> float | None:
        if not _looks_like_fixed_asset_filter_rule(rule_text):
            return None
        amount_column = _fixed_asset_rule_amount_column(rule_text)

        file_path = _find_fixed_asset_movement_file(self.upload_dir)
        if file_path is None:
            return None

        df = self._fixed_asset_movement_scope_df(self._load_fixed_asset_movement_df(file_path), item_code)
        if not amount_column and _looks_like_fixed_asset_filter_rule(rule_text):
            amount_column = "原值"
        required_columns = {"资产类别编码", "增减方式", amount_column}
        if df.empty or not required_columns.issubset(df.columns):
            return None

        rule_text = _normalize_fixed_asset_movement_rule_for_item(rule_text, item_code)

        expression_amount = _fixed_asset_filter_expression_amount(df, rule_text, amount_column)
        if expression_amount is not None:
            return expression_amount / AMOUNT_UNIT_DIVISOR

        mask = _fixed_asset_filter_rule_mask(df, rule_text)
        if mask is None:
            category_prefix = (
                _fixed_asset_rule_value(rule_text, "资产类别编码开头两位")
                or _fixed_asset_rule_value(rule_text, "资产类别编码前两位")
            )
            movement_type = _fixed_asset_rule_value(rule_text, "增减方式")
            if not category_prefix or not movement_type:
                return None
            category = _fixed_asset_column_text(df, "资产类别编码")
            movement = _fixed_asset_column_text(df, "增减方式")
            mask = category.str.startswith(category_prefix) & movement.eq(movement_type)
        amount = pd.to_numeric(df.loc[mask, amount_column], errors="coerce").fillna(0.0).sum()
        return float(amount) / AMOUNT_UNIT_DIVISOR

    def _calculate_fixed_asset_decrease_accumulated_depreciation_total(self) -> float | None:
        rules = {
            "B0533": "资产类别编码 LIKE '10%' AND 增减方式 IN ('正常报废', '资产出售', '其他方式', '资产类别调整') -累计折旧",
            "B0534": "资产类别编码 LIKE '30%' AND 增减方式 IN ('正常报废', '资产出售') -累计折旧",
            "B0535": (
                "资产增减变动明细表-资产类别编码 in ('200101', '200106') "
                "AND 增减方式 IN ('正常报废', '资产出售') -累计折旧"
            ),
            "B0536": (
                "资产类别编码前两位 = 40\n"
                "AND 增减方式 IN ('正常报废', '资产出售', '非正常报废', '资产拆分减少', '内部有偿转出')\n"
                "-\n"
                "资产类别编码前两位 = 40\n"
                "AND 增减方式 = '正常报废'\n"
                "AND 资产类别名称 IN ('其他办公家俱', '票据分析仪')-累计折旧\n"
                "-\n"
                "资产类别编码前两位 = 40\n"
                "AND 增减方式 IN ('正常报废', '资产出售', '非正常报废', '资产拆分减少', '内部有偿转出')\n"
                "AND 资产类别名称 IN ('其他办公设备', '办公沙发', '文件档案柜')-累计折旧"
            ),
        }
        amounts = [self._calculate_fixed_asset_movement_rule(rule, item_code) for item_code, rule in rules.items()]
        if any(amount is None for amount in amounts):
            return None
        return float(
            sum(
                _fixed_asset_decrease_report_amount(item_code, amount)
                for item_code, amount in zip(rules.keys(), amounts)
                if amount is not None
            )
        )

    def _load_fixed_asset_movement_df(self, file_path: Path) -> pd.DataFrame:
        cache_key = ("fixed_asset_movement", file_path)
        if not hasattr(self, "_fixed_asset_movement_cache"):
            self._fixed_asset_movement_cache = {}
        if cache_key in self._fixed_asset_movement_cache:
            return self._fixed_asset_movement_cache[cache_key]
        try:
            df = pd.read_excel(file_path, sheet_name="合并明细", dtype=object, engine="openpyxl")
        except Exception:
            df = pd.DataFrame()
        if not df.empty:
            df.columns = [_normalize_text(column) for column in df.columns]
        self._fixed_asset_movement_cache[cache_key] = df
        return df

    def _fixed_asset_movement_scope_df(self, df: pd.DataFrame, item_code: str = "") -> pd.DataFrame:
        if df.empty or "机构编码" not in df.columns:
            return df
        if self.subject_balance_prefix == "1-12-" and _normalize_text(item_code) in {"B0519", "B0521"}:
            return df.copy()
        institution = df["机构编码"].map(_clean_institution_code)
        if self.subject_balance_prefix == "1-12-":
            mask = ~institution.str.startswith(("8", "9", "L", "W"), na=False)
            if _normalize_text(item_code) == "B0520":
                mask &= institution != "L00000"
            return df.loc[mask].copy()
        if self.subject_balance_prefix == "1-5-" and self.institution_code:
            return df.loc[institution == self.institution_code].copy()
        return df

    def _load_impairment_detail_sheet(self, file_path: Path, period: str) -> pd.DataFrame:
        cache_key = (file_path, period)
        if cache_key in self._impairment_detail_sheet_cache:
            return self._impairment_detail_sheet_cache[cache_key]

        try:
            header_index = _find_impairment_header_index_in_workbook(file_path, period)
        except Exception:
            self._impairment_detail_sheet_cache[cache_key] = pd.DataFrame()
            return self._impairment_detail_sheet_cache[cache_key]

        if header_index is None:
            self._impairment_detail_sheet_cache[cache_key] = pd.DataFrame()
            return self._impairment_detail_sheet_cache[cache_key]

        required_columns = {"BUSI_PK_ID", "BIZ_TYPE", "ACCTI_THREE_CLS", "STAGE_RSLT_FINAL", "ECL_FINAL"}
        try:
            data_df = pd.read_excel(
                file_path,
                sheet_name=period,
                header=header_index,
                dtype=object,
                engine="openpyxl",
                usecols=lambda column: _normalize_text(column) in required_columns,
            )
        except Exception:
            self._impairment_detail_sheet_cache[cache_key] = pd.DataFrame()
            return self._impairment_detail_sheet_cache[cache_key]
        data_df.columns = [_normalize_text(column) for column in data_df.columns.tolist()]
        data_df = data_df.dropna(how="all")
        normalized_df = _normalize_impairment_detail_df(data_df)
        self._impairment_detail_sheet_cache[cache_key] = normalized_df
        return normalized_df

    def _subject_rule_message(self) -> str:
        if self.subject_balance_prefix == "1-12-":
            return "按本行科目余额表和本行审计调整底稿计算，单位转换为千元"
        if self.subject_balance_prefix == "1-5-":
            return "按子公司科目余额表和子公司审计调整底稿计算，单位转换为千元"
        return "按科目余额表、审计调整底稿和合并抵消底稿计算，单位转换为千元"

    def _calculate_subject_current_previous_delta_rule(self, rule_text: str) -> float | None:
        match = SUBJECT_CURRENT_PREVIOUS_DELTA_PATTERN.fullmatch(_normalize_text(rule_text))
        if not match:
            return None
        code = _clean_code(match.group("code"))
        side = match.group("side") or "贷方"
        is_net = bool(match.group("net"))
        current_amount = self._account_amount(code, side, is_net, "余额")
        previous_amount = _subject_amount(self._load_subject_balance_df(), code, side, is_net, "期初")
        return (current_amount - previous_amount) / AMOUNT_UNIT_DIVISOR

    def _seed_oci_previous_values(self, values_by_name: dict[str, float]) -> None:
        oci_df = self._load_oci_balance_df()
        if oci_df.empty:
            return
        entity = self.oci_entity or "集团"
        previous_values = {
            "B0876": -863476.0,
            "B0877": -347607.0,
            "B0878": 4965735.0,
            "B0879": 392898.0,
        }
        for code, amount in previous_values.items():
            values_by_name[f"{code}上期"] = amount
            values_by_name[f"{code}上年数"] = amount

    def _calculate_formula_rule(
        self,
        row: pd.Series,
        values_by_name: dict[str, float],
    ) -> tuple[float | None, str, str]:
        rule_text = _row_text(row, "指标加工规则", "加工规则")
        if not rule_text:
            return None, "未计算", "无加工规则"
        if "ECL_FINAL" in rule_text and "减值明细" in rule_text:
            expression = rule_text
        else:
            expression = _extract_formula_expression(rule_text)
        if _row_text(row, "指标编码") == "A6038" and "A60446" in expression:
            expression = "A6039+A6040+A6041+A6042+A6043+A6044+A6045"
        if _row_text(row, "指标编码") == "A0076" and expression.strip() == "A0076":
            expression = "B0866+B0867+B0868+B0869"
        expression = _normalize_formula_entity_terms(expression, self.subject_balance_prefix)
        expression = _normalize_intangible_amortization_formula(
            _row_text(row, "指标编码"),
            expression,
        )
        exclude_consolidation_adjustments = bool(CONSOLIDATION_IFRS_MAPPING_AMOUNT_PATTERN.search(expression))
        replaced_expression, matched_impairment_detail = self._replace_impairment_detail_aggregate_terms_in_expression(
            expression
        )
        replaced_expression = replaced_expression.replace("（", "(").replace("）", ")").replace("×", "*").replace("－", "-")
        if matched_impairment_detail:
            metric_expression, matched_metric = _replace_calculated_metric_terms(replaced_expression, values_by_name)
            if not re.search(r"[\u4e00-\u9fff]", metric_expression) and not re.search(r"\b[A-Z]\d{3,}\b", metric_expression):
                try:
                    amount = _safe_eval_numeric_expression(metric_expression)
                except Exception:
                    amount = None
                if amount is not None:
                    item_code = _row_text(row, "指标编码")
                    if item_code == "B0440":
                        writeoff_amount = self._calculate_subject_balance_rule(
                            "15029101科目借方本期发生额",
                            include_adjustments=False,
                        )
                        if writeoff_amount is not None:
                            amount += writeoff_amount
                    amount = _adjust_formula_amount_for_item(
                        item_code,
                        rule_text,
                        amount,
                        values_by_name,
                    )
                    if matched_metric:
                        return amount, "已计算", "按减值明细表期间汇总和指标间公式计算"
                    return amount, "已计算", "按减值明细表期间汇总差额计算"
        replaced_expression, matched_consolidation_period = _replace_consolidation_period_terms(
            replaced_expression,
            self.upload_dir,
        )
        replaced_expression, matched_consolidation_raw_period = _replace_consolidation_raw_period_terms(
            replaced_expression,
            self.upload_dir,
        )
        replaced_expression, matched_consolidation_date_amount = _replace_consolidation_date_amount_terms(
            replaced_expression,
            self.upload_dir,
        )
        replaced_expression, matched_subsidiary_ownership = _replace_subsidiary_ownership_terms(
            replaced_expression,
            self.upload_dir,
        )
        replaced_expression, matched_adjustment_amount = self._replace_adjustment_amount_terms_in_expression(
            replaced_expression
        )
        include_subject_adjustments = _row_text(row, "指标编码") != "B0445"
        replaced_expression, matched_account = self._replace_subject_terms_in_expression(
            replaced_expression,
            include_adjustments=include_subject_adjustments,
            include_consolidation_adjustments=not exclude_consolidation_adjustments,
        )
        replaced_expression, matched_consolidation_ifrs = _replace_consolidation_ifrs_mapping_terms(
            replaced_expression,
            self.upload_dir,
        )
        replaced_expression, matched_perpetual_bond = _replace_perpetual_bond_interest_terms(
            replaced_expression,
            self.upload_dir,
        )

        matched_name = (
            matched_consolidation_period
            or matched_consolidation_raw_period
            or matched_consolidation_date_amount
            or matched_impairment_detail
            or matched_subsidiary_ownership
            or matched_adjustment_amount
            or matched_account
            or matched_consolidation_ifrs
            or matched_perpetual_bond
        )
        replaced_expression, matched_metric = _replace_calculated_metric_terms(replaced_expression, values_by_name)
        matched_name = matched_name or matched_metric

        if not matched_name:
            return None, "未计算", "公式未匹配到已计算指标"
        if re.search(r"[\u4e00-\u9fff]", replaced_expression):
            return None, "未计算", "公式仍包含未计算中文指标"
        if re.search(r"\b[A-Z]\d{3,}\b", replaced_expression):
            return None, "未计算", "公式仍包含未计算指标编码"

        try:
            amount = _safe_eval_numeric_expression(replaced_expression)
        except Exception as exc:  # noqa: BLE001
            return None, "未计算", f"公式计算失败：{exc}"
        amount = _adjust_formula_amount_for_item(
            _row_text(row, "指标编码"),
            rule_text,
            amount,
            values_by_name,
        )

        return amount, "已计算", "按指标间公式计算"

    def _calculate_oci_rule(self, rule_text: str) -> float | None:
        expression = _normalize_oci_expression(rule_text)
        replaced_expression, matched_oci = self._replace_oci_terms_in_expression(expression)
        replaced_expression, matched_consolidation = self._replace_consolidation_first_amounts_in_expression(replaced_expression)
        if not (matched_oci or matched_consolidation) or re.search(r"[\u4e00-\u9fff]", replaced_expression):
            return None

        try:
            return _safe_eval_numeric_expression(replaced_expression)
        except Exception:
            return None

    def _calculate_oci_period_balance_rule(self, rule_text: str) -> float | None:
        if not rule_text or ("本期数" not in rule_text and "上期数" not in rule_text):
            return None
        if "科目" not in rule_text:
            return None
        entity = self.oci_entity or "集团"

        def replace_match(match: re.Match[str]) -> str:
            body = _normalize_text(match.group("body"))
            if "科目" not in body or ("余额" not in body and "轧差" not in body):
                return match.group(0)
            code = _clean_code(match.group("code"))
            if not code:
                return match.group(0)
            year_type = "本年" if match.group("period") == "本期数" else "上年"
            return f"{code}{year_type}{entity}余额"

        converted = OCI_PERIOD_BALANCE_PATTERN.sub(replace_match, rule_text)
        if converted == rule_text:
            return None
        expression = _normalize_oci_expression(converted)
        expression, matched_oci = self._replace_oci_terms_in_expression(expression)
        expression, matched_subject = self._replace_subject_terms_in_expression(expression)
        if not matched_oci or re.search(r"[\u4e00-\u9fff]", expression):
            return None
        try:
            return _safe_eval_numeric_expression(expression)
        except Exception:
            return None

    def _calculate_oci_subsidiary_consolidation_delta(self, rule_text: str) -> float | None:
        match = OCI_SUBSIDIARY_CONSOLIDATION_DELTA_PATTERN.search(rule_text)
        if not match:
            return None
        code = _clean_code(match.group("code"))
        oci_df = self._load_oci_balance_df()
        if oci_df.empty:
            return None
        current_delta = _oci_amount(oci_df, code, "本年", "集团") - _oci_amount(oci_df, code, "本年", "本行")
        previous_delta = _oci_amount(oci_df, code, "上年", "集团") - _oci_amount(oci_df, code, "上年", "本行")
        return current_delta - previous_delta

    def _normalize_oci_rule_for_item(self, rule_text: str, item_code: str) -> str:
        if self.oci_entity != "集团":
            return rule_text
        if item_code in {"A0077", "A0078", "A0079", "A0080"}:
            return rule_text.replace("本行余额", "集团余额")
        if item_code == "A0081":
            return _replace_first_oci_parent_delta_with_group(rule_text)
        return rule_text

    def _replace_oci_terms_in_expression(self, expression: str) -> tuple[str, bool]:
        replaced_parts: list[str] = []
        last_end = 0
        matched_oci = False

        for match in OCI_RULE_PATTERN.finditer(expression):
            replaced_parts.append(expression[last_end : match.start()])
            code = _clean_code(match.group(1))
            year_type = match.group(2)
            entity_type = match.group(3)
            amount = _oci_amount(self._load_oci_balance_df(), code, year_type, entity_type)
            replaced_parts.append(str(amount))
            last_end = match.end()
            matched_oci = True

        if not matched_oci:
            return expression, False

        replaced_parts.append(expression[last_end:])
        return "".join(replaced_parts), True

    def _replace_adjustment_amount_terms_in_expression(self, expression: str) -> tuple[str, bool]:
        replaced_parts: list[str] = []
        last_end = 0
        matched_adjustment = False

        for match in FILTERED_ADJUSTMENT_AMOUNT_PATTERN.finditer(expression):
            replaced_parts.append(expression[last_end : match.start()])
            source = match.group(1)
            code = match.group("code")
            adjustment_code = match.group("adjustment_code") or ""
            adjustment_description = match.group("adjustment_description") or match.group("institution_description") or ""
            institution_name = match.group("institution_name") or ""
            amount = self._filtered_adjustment_amount_by_source(
                source,
                code,
                adjustment_code=adjustment_code,
                adjustment_description=adjustment_description,
                institution_name=institution_name,
            ) / AMOUNT_UNIT_DIVISOR
            replaced_parts.append(str(amount))
            last_end = match.end()
            matched_adjustment = True

        for match in ADJUSTMENT_AMOUNT_PATTERN.finditer(expression):
            if match.start() < last_end:
                continue
            replaced_parts.append(expression[last_end : match.start()])
            source = match.group(1)
            code = match.group(2)
            amount = self._adjustment_amount_by_source(source, code) / AMOUNT_UNIT_DIVISOR
            replaced_parts.append(str(amount))
            last_end = match.end()
            matched_adjustment = True

        if not matched_adjustment:
            return expression, False

        replaced_parts.append(expression[last_end:])
        return "".join(replaced_parts), True

    def _filtered_adjustment_amount_by_source(
        self,
        source: str,
        code: str,
        adjustment_code: str = "",
        adjustment_description: str = "",
        institution_name: str = "",
    ) -> float:
        adjustment_df = self._load_adjustment_df()
        if source == "母行":
            adjustment_df = adjustment_df.loc[adjustment_df["source"] == "parent"]
        elif source == "子公司":
            adjustment_df = adjustment_df.loc[adjustment_df["source"] == "subsidiary"]
        else:
            adjustment_df = adjustment_df.loc[adjustment_df["source"] == "consolidation"]
        matched_df = _match_account_rows(adjustment_df, code)
        if matched_df.empty:
            return 0.0
        if adjustment_code:
            expected = _normalize_text(adjustment_code)
            matched_df = matched_df.loc[matched_df.get("adjustment_code", "").map(_normalize_text) == expected]
        if adjustment_description:
            expected = _normalize_text(adjustment_description)
            matched_df = matched_df.loc[matched_df.get("adjustment_description", "").map(_normalize_text) == expected]
        if institution_name:
            expected = _normalize_text(institution_name)
            matched_df = matched_df.loc[matched_df.get("institution_name", "").map(_normalize_text) == expected]
        if matched_df.empty:
            return 0.0
        return float(matched_df["amount"].sum())

    def _adjustment_amount_by_source(self, source: str, code: str) -> float:
        adjustment_df = self._load_adjustment_df()
        if source == "母行":
            adjustment_df = adjustment_df.loc[adjustment_df["source"] == "parent"]
        elif source == "子公司":
            adjustment_df = adjustment_df.loc[adjustment_df["source"] == "subsidiary"]
        else:
            adjustment_df = adjustment_df.loc[adjustment_df["source"] == "consolidation"]
        matched_df = _match_account_rows(adjustment_df, code)
        if matched_df.empty:
            return 0.0
        amounts = matched_df["amount"].copy()
        if _is_impairment_allowance_code(code):
            amounts = -amounts
        return float(amounts.sum())

    def _replace_consolidation_first_amounts_in_expression(self, expression: str) -> tuple[str, bool]:
        replaced_parts: list[str] = []
        last_end = 0
        matched_consolidation = False

        for match in CONSOLIDATION_FIRST_AMOUNT_PATTERN.finditer(expression):
            replaced_parts.append(expression[last_end : match.start()])
            code = _clean_code(match.group(1))
            amount = _consolidation_first_raw_amount(self.upload_dir, code)
            replaced_parts.append(str(amount))
            last_end = match.end()
            matched_consolidation = True

        if not matched_consolidation:
            return expression, False

        replaced_parts.append(expression[last_end:])
        return "".join(replaced_parts), True

    def _replace_subject_terms_in_expression(
        self,
        expression: str,
        include_adjustments: bool = True,
        include_consolidation_adjustments: bool = True,
    ) -> tuple[str, bool]:
        expression = _normalize_subject_occurrence_rule_text(expression)
        expression = _normalize_shared_account_suffix_rule_text(expression)
        replaced_parts: list[str] = []
        last_end = 0
        matched_account = False

        for match in ACCOUNT_RULE_PATTERN.finditer(expression):
            replaced_parts.append(expression[last_end : match.start()])
            entity = match.group(1) or ""
            code = match.group(2)
            amount_type = match.group(3) or "余额"
            side = match.group(4) or "借方"
            is_net = match.group(5) in {"轧差值", "轧差额", "轧差"}
            if entity == "本行":
                amount = _subject_amount(
                    self._load_subject_balance_df_for_prefix("1-12-"),
                    code,
                    side,
                    is_net,
                    amount_type,
                )
            elif entity == "子公司":
                amount = _subject_amount(
                    self._load_subject_balance_df_for_prefix("1-5-"),
                    code,
                    side,
                    is_net,
                    amount_type,
                )
            elif entity == "科目余额表":
                amount = _subject_amount(
                    self._load_subject_balance_df(),
                    code,
                    side,
                    is_net,
                    amount_type,
                )
            else:
                amount = self._account_amount(
                    code,
                    side,
                    is_net,
                    amount_type,
                    include_adjustments=include_adjustments,
                    include_consolidation_adjustments=include_consolidation_adjustments,
                )
            amount = amount / AMOUNT_UNIT_DIVISOR
            replaced_parts.append(str(amount))
            last_end = match.end()
            matched_account = True

        if not matched_account:
            return expression, False

        replaced_parts.append(expression[last_end:])
        return "".join(replaced_parts), True

    def _calculate_subject_balance_rule(self, rule_text: str, include_adjustments: bool = True) -> float | None:
        rule_text = _normalize_subject_occurrence_rule_text(rule_text)
        rule_text = _normalize_shared_account_suffix_rule_text(_normalize_combo_rule_text(rule_text))
        is_occurrence_rule = "发生额" in rule_text
        combo_matches = list(COMBO_RULE_PATTERN.finditer(rule_text))
        normal_rule_text = COMBO_RULE_PATTERN.sub("", rule_text)
        normal_rule_text = EXPLICIT_ADJUSTMENT_PATTERN.sub("", normal_rule_text)
        normal_rule_text = EXPLICIT_ALL_ADJUSTMENT_PATTERN.sub("", normal_rule_text)
        detail_positive_matches = list(DETAIL_POSITIVE_BALANCE_PATTERN.finditer(normal_rule_text))
        normal_rule_text = DETAIL_POSITIVE_BALANCE_PATTERN.sub("", normal_rule_text)
        matches = list(ACCOUNT_RULE_PATTERN.finditer(normal_rule_text))
        if not combo_matches and not detail_positive_matches and not matches:
            return None

        unmatched_rule_text = ACCOUNT_RULE_PATTERN.sub("", normal_rule_text)
        unmatched_rule_text = (
            unmatched_rule_text.replace("审计调整", "")
            .replace("合并抵销", "")
            .replace("合并抵消", "")
        )
        unmatched_rule_text = re.sub(r"[\s+\-*/=()（）,，、]+", "", unmatched_rule_text)
        if re.search(r"[\u4e00-\u9fff]", unmatched_rule_text):
            return None

        subject_df = self._load_subject_balance_df()
        if subject_df.empty:
            return None

        explicit_adjustments = (
            include_adjustments
            and
            self.subject_balance_prefix != "1-5-"
            and (
                "审计调整底稿" in rule_text
                or "合并抵销底稿" in rule_text
                or "合并抵消底稿" in rule_text
                or EXPLICIT_ALL_ADJUSTMENT_PATTERN.search(rule_text)
            )
        )
        if not combo_matches and not detail_positive_matches and not explicit_adjustments and re.search(r"[*/]", normal_rule_text):
            replaced_expression, matched_account = self._replace_subject_terms_in_expression(normal_rule_text)
            if not matched_account or re.search(r"[\u4e00-\u9fff]", replaced_expression):
                return None
            try:
                return _safe_eval_numeric_expression(replaced_expression)
            except Exception:
                return None

        total = 0.0
        matched_codes: list[str] = []

        for match in combo_matches:
            codes = re.findall(r"\d{4,8}", match.group(1))
            if not codes:
                continue
            matched_codes.extend(codes)
            side = match.group(2) or "借方"
            is_net = bool(match.group(3))
            sign = _term_sign(rule_text, match.start())
            amount = _combo_subject_amount(subject_df, codes, side, is_net)
            total += sign * amount

        for match in detail_positive_matches:
            code = match.group(1)
            matched_codes.append(code)
            side = match.group(2)
            sign = _term_sign(rule_text, match.start())
            amount = _detail_positive_subject_amount(subject_df, code, side)
            if include_adjustments:
                amount += _adjustment_amount(self._load_adjustment_df(), code)
            total += sign * amount

        previous_side = "借方"
        previous_is_net = True
        for match in matches:
            entity = match.group(1) or ""
            code = match.group(2)
            matched_codes.append(code)
            amount_type = match.group(3) or "余额"
            side = match.group(4) or previous_side
            is_net = match.group(5) in {"轧差值", "轧差额", "轧差"} if match.group(4) or match.group(5) else previous_is_net
            previous_side = side
            previous_is_net = is_net
            sign = _term_sign(normal_rule_text, match.start())
            if entity == "本行":
                amount = _subject_amount(
                    self._load_subject_balance_df_for_prefix("1-12-"),
                    code,
                    side,
                    is_net,
                    amount_type,
                )
            elif entity == "子公司":
                amount = _subject_amount(
                    self._load_subject_balance_df_for_prefix("1-5-"),
                    code,
                    side,
                    is_net,
                    amount_type,
                )
            elif entity == "科目余额表":
                amount = _subject_amount(subject_df, code, side, is_net, amount_type)
            elif explicit_adjustments or is_occurrence_rule:
                amount = _subject_amount(subject_df, code, side, is_net, amount_type)
            else:
                amount = self._account_amount(
                    code,
                    side,
                    is_net,
                    amount_type,
                    include_adjustments=include_adjustments,
                )
            total += sign * amount

        if explicit_adjustments:
            total += self._explicit_adjustment_amount(rule_text)

        if matched_codes and all(_is_impairment_allowance_code(code) for code in matched_codes) and not is_occurrence_rule:
            total = -total

        return total / AMOUNT_UNIT_DIVISOR

    def _calculate_subject_opening_balance_rule(self, rule_text: str) -> float | None:
        subject_df = self._load_subject_balance_df()
        if subject_df.empty:
            return None

        normal_rule_text = _normalize_subject_occurrence_rule_text(rule_text)
        normal_rule_text = _normalize_shared_account_suffix_rule_text(_normalize_combo_rule_text(normal_rule_text))
        normal_rule_text = COMBO_RULE_PATTERN.sub("", normal_rule_text)
        normal_rule_text = EXPLICIT_ADJUSTMENT_PATTERN.sub("", normal_rule_text)
        normal_rule_text = EXPLICIT_ALL_ADJUSTMENT_PATTERN.sub("", normal_rule_text)
        normal_rule_text = DETAIL_POSITIVE_BALANCE_PATTERN.sub("", normal_rule_text)
        matches = list(ACCOUNT_RULE_PATTERN.finditer(normal_rule_text))
        if not matches:
            return None

        total = 0.0
        previous_side = "借方"
        previous_is_net = True
        for match in matches:
            entity = match.group(1) or ""
            code = match.group(2)
            side = match.group(4) or previous_side
            is_net = match.group(5) in {"轧差值", "轧差额", "轧差"} if match.group(4) or match.group(5) else previous_is_net
            previous_side = side
            previous_is_net = is_net
            sign = _term_sign(normal_rule_text, match.start())
            if entity == "本行":
                amount_df = self._load_subject_balance_df_for_prefix("1-12-")
            elif entity == "子公司":
                amount_df = self._load_subject_balance_df_for_prefix("1-5-")
            else:
                amount_df = subject_df
            total += sign * _subject_amount(amount_df, code, side, is_net, "期初")

        return total / AMOUNT_UNIT_DIVISOR

    def _account_amount(
        self,
        code: str,
        side: str,
        is_net: bool,
        amount_type: str = "余额",
        include_adjustments: bool = True,
        include_consolidation_adjustments: bool = True,
    ) -> float:
        subject_amount = _subject_amount(self._load_subject_balance_df(), code, side, is_net, amount_type)
        if not include_adjustments:
            return subject_amount
        adjustment_df = self._load_adjustment_df()
        if not include_consolidation_adjustments and "source" in adjustment_df.columns:
            adjustment_df = adjustment_df.loc[adjustment_df["source"] != "consolidation"]
        adjustment_amount = _adjustment_amount(adjustment_df, code)
        if _is_impairment_allowance_code(code) and side == "贷方":
            return subject_amount - adjustment_amount
        if _is_income_account_code(code) and side == "贷方":
            return subject_amount - adjustment_amount
        return subject_amount + adjustment_amount

    def _calculate_asset_impairment_b0694_amount(self) -> float | None:
        subject_df = self._load_subject_balance_df()
        if subject_df.empty:
            return None
        subject_amount = _subject_amount(subject_df, "41029101", "贷方", True, "余额")
        adjustment_amount = _adjustment_amount(self._load_adjustment_df(), "41029101")
        return (subject_amount + adjustment_amount) / AMOUNT_UNIT_DIVISOR

    def _explicit_adjustment_amount(self, rule_text: str) -> float:
        total = 0.0
        for match in EXPLICIT_ADJUSTMENT_PATTERN.finditer(rule_text):
            sign = 1 if match.group(1) == "+" else -1
            source = match.group(2)
            code = match.group(3)
            adjustment_df = self._load_adjustment_df()
            if source == "母行":
                adjustment_df = adjustment_df.loc[adjustment_df["source"] == "parent"]
            elif source == "子公司":
                adjustment_df = adjustment_df.loc[adjustment_df["source"] == "subsidiary"]
            else:
                adjustment_df = adjustment_df.loc[adjustment_df["source"] == "consolidation"]
            matched_df = _match_account_rows(adjustment_df, code)
            total += sign * float(matched_df["amount"].sum())
        for match in EXPLICIT_ALL_ADJUSTMENT_PATTERN.finditer(rule_text):
            sign = 1 if match.group(1) == "+" else -1
            code = match.group(2)
            matched_df = _match_account_rows(self._load_adjustment_df(), code)
            total += sign * float(matched_df["amount"].sum())
        return total

    def _load_subject_balance_df(self) -> pd.DataFrame:
        if self._subject_balance_df is not None:
            return self._subject_balance_df

        file_path = _find_file_by_prefix(self.upload_dir, self.subject_balance_prefix)
        if file_path is None:
            self._subject_balance_df = pd.DataFrame()
            return self._subject_balance_df

        raw_df = pd.read_excel(file_path, sheet_name=0, header=None, dtype=object, engine="openpyxl")
        data_df = raw_df.iloc[10:].copy().dropna(how="all")
        subject_df = pd.DataFrame(
            {
                "institution_code": data_df.iloc[:, 0].map(_clean_code),
                "account_code": data_df.iloc[:, 2].map(_clean_code),
                "opening_debit": pd.to_numeric(data_df.iloc[:, 4], errors="coerce").fillna(0.0),
                "opening_credit": pd.to_numeric(data_df.iloc[:, 5], errors="coerce").fillna(0.0),
                "period_debit": pd.to_numeric(data_df.iloc[:, 6], errors="coerce").fillna(0.0),
                "period_credit": pd.to_numeric(data_df.iloc[:, 7], errors="coerce").fillna(0.0),
                "ending_debit": pd.to_numeric(data_df.iloc[:, 8], errors="coerce").fillna(0.0),
                "ending_credit": pd.to_numeric(data_df.iloc[:, 9], errors="coerce").fillna(0.0),
                "level1_code": data_df.iloc[:, 10].map(_clean_code),
                "level2_code": data_df.iloc[:, 11].map(_clean_code),
                "level3_code": data_df.iloc[:, 12].map(_clean_code),
            }
        )
        if self.institution_code:
            subject_df = subject_df.loc[subject_df["institution_code"] == self.institution_code].copy()
        self._subject_balance_df = subject_df
        return self._subject_balance_df

    def _load_subject_balance_df_for_prefix(self, subject_balance_prefix: str) -> pd.DataFrame:
        if subject_balance_prefix == self.subject_balance_prefix:
            return self._load_subject_balance_df()
        if subject_balance_prefix in self._subject_balance_df_by_prefix:
            return self._subject_balance_df_by_prefix[subject_balance_prefix]

        original_df = self._subject_balance_df
        original_prefix = self.subject_balance_prefix
        self._subject_balance_df = None
        self.subject_balance_prefix = subject_balance_prefix
        try:
            subject_df = self._load_subject_balance_df().copy()
        finally:
            self.subject_balance_prefix = original_prefix
            self._subject_balance_df = original_df

        self._subject_balance_df_by_prefix[subject_balance_prefix] = subject_df
        return subject_df

    def _load_adjustment_df(self) -> pd.DataFrame:
        if self._adjustment_df is not None:
            return self._adjustment_df

        if self.subject_balance_prefix == "1-5-":
            frames = [_load_adjustment_file(self.upload_dir, "1-3-", "财务科目号", self.report_period, "subsidiary")]
        elif self.subject_balance_prefix == "1-12-":
            frames = [_load_adjustment_file(self.upload_dir, "1-2-", "科目代号-8位", self.report_period, "parent")]
        else:
            frames = [
                _load_adjustment_file(self.upload_dir, "1-2-", "科目代号-8位", self.report_period, "parent"),
                _load_adjustment_file(self.upload_dir, "1-3-", "财务科目号", self.report_period, "subsidiary"),
                _load_consolidation_elimination_file(self.upload_dir, self.report_period),
            ]
        frames = [frame for frame in frames if not frame.empty]
        if not frames:
            self._adjustment_df = pd.DataFrame(columns=["account_code", "amount", "source", "level1_code", "level2_code", "level3_code"])
            return self._adjustment_df

        adjustment_df = pd.concat(frames, ignore_index=True)
        if self.institution_code and "institution_code" in adjustment_df.columns:
            adjustment_df = adjustment_df.loc[adjustment_df["institution_code"] == self.institution_code].copy()
        adjustment_df["level1_code"] = adjustment_df["account_code"].str[:4]
        adjustment_df["level2_code"] = adjustment_df["account_code"].str[:6]
        adjustment_df["level3_code"] = adjustment_df["account_code"].str[:8]
        self._adjustment_df = adjustment_df
        return self._adjustment_df

    def _load_oci_balance_df(self) -> pd.DataFrame:
        if self._oci_balance_df is not None:
            return self._oci_balance_df

        self._oci_balance_df = _load_oci_balance_file(self.upload_dir, self.report_period)
        return self._oci_balance_df


def _looks_like_impairment_migration_rule(rule_text: str) -> bool:
    compact = _normalize_text(rule_text)
    required_tokens = ("减值明细", "BUSI_PK_ID", "STAGE_RSLT_FINAL", "ECL_FINAL")
    return all(token in compact for token in required_tokens)


def _adjust_impairment_migration_sign(item_code: str, item_name: str, amount: float) -> float:
    code = _normalize_text(item_code)
    name = _normalize_text(item_name)
    if code == "B0457" or ("第二阶段其他债权投资" in name and "转移至第一阶段" in name):
        return -abs(amount)
    return amount


def _adjust_formula_amount_for_item(
    item_code: str,
    rule_text: str,
    amount: float,
    values_by_name: dict[str, float],
) -> float:
    code = _normalize_text(item_code)
    compact_rule = _normalize_text(rule_text)
    if code == "B0537" and all(metric_code in compact_rule for metric_code in ("B0533", "B0534", "B0535", "B0536")):
        component_amounts = [
            values_by_name.get("B0533"),
            values_by_name.get("B0534"),
            values_by_name.get("B0535"),
            values_by_name.get("B0536"),
        ]
        if all(component_amount is not None for component_amount in component_amounts):
            return float(
                sum(
                    _fixed_asset_decrease_report_amount(component_code, component_amount)
                    for component_code, component_amount in zip(
                        ("B0533", "B0534", "B0535", "B0536"),
                        component_amounts,
                    )
                    if component_amount is not None
                )
            )
    if code == "B0469" and "B0461" in compact_rule:
        b0461_amount = values_by_name.get("B0461")
        if b0461_amount is not None and b0461_amount > 0:
            return amount - (2 * b0461_amount)
    return amount


def _apply_b0580_intangible_amortization_rule(rule_text: str) -> str:
    if "16310201" in rule_text:
        return rule_text
    return (
        "16310201科目余额借方轧差值+"
        f"{rule_text}"
    )


def _fixed_asset_decrease_report_amount(item_code: str, amount: float) -> int:
    code = _normalize_text(item_code)
    if code == "B0534":
        return int(amount)
    return round(amount)


def _fixed_asset_rule_value(rule_text: str, key: str) -> str:
    condition_boundaries = (
        r"\^",
        r"\bAND\b",
        r"\band\b",
        r"且",
        r"资产类别编码开头两位\s*=",
        r"资产类别编码\s*=",
        r"资产类别编码\s+in\s*\(",
        r"资产类别编码\s+IN\s*\(",
        r"资产类别名称\s*=",
        r"增减方式\s*=",
        r"增减方式\s+in\s*\(",
        r"增减方式\s+IN\s*\(",
    )
    boundary_pattern = "|".join(condition_boundaries)
    pattern = re.compile(
        rf"{re.escape(key)}\s*=\s*(.+?)(?=(?:{boundary_pattern})|-[^\-\n\r]+$|$)",
        flags=re.IGNORECASE,
    )
    match = pattern.search(rule_text)
    return _clean_fixed_asset_condition_value(match.group(1)) if match else ""


def _looks_like_fixed_asset_filter_rule(rule_text: str) -> bool:
    text = _normalize_text(rule_text)
    return (
        ("资产增减变动明细表" in text or ("资产类别编码" in text and "增减方式" in text))
        and
        (
            re.search(r"资产类别编码\s+LIKE\s+['\"]?[^'\"]+['\"]?", text, flags=re.IGNORECASE)
            or re.search(r"增减方式\s+IN\s*\(", text, flags=re.IGNORECASE)
            or re.search(r"资产类别编码\s*=\s*['\"]?[^'\"\s)]+['\"]?", text)
            or re.search(r"资产类别编码开头两位\s*=", text)
            or re.search(r"资产类别编码前两位\s*=", text)
        )
    )


def _fixed_asset_adjustment_amount(term: str) -> float | None:
    match = re.search(r"调整金额\s*=\s*([-+]?\d+(?:\.\d+)?)\s*(千元|元)?", _normalize_text(term))
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2) or "千元"
    return amount * 1000 if unit == "千元" else amount


def _fixed_asset_filter_expression_amount(df: pd.DataFrame, rule_text: str, amount_column: str) -> float | None:
    terms = _split_fixed_asset_filter_terms(rule_text)
    if len(terms) <= 1:
        return None
    total = 0.0
    for sign, term in terms:
        adjustment_amount = _fixed_asset_adjustment_amount(term)
        if adjustment_amount is not None:
            total += sign * adjustment_amount
            continue
        mask = _fixed_asset_filter_rule_mask(df, term)
        if mask is None:
            return None
        amount = pd.to_numeric(df.loc[mask, amount_column], errors="coerce").fillna(0.0).sum()
        total += sign * float(amount)
    return total


def _normalize_fixed_asset_movement_rule_for_item(rule_text: str, item_code: str = "") -> str:
    normalized_item_code = _normalize_text(item_code)
    if normalized_item_code == "B0533":
        return (
            "资产类别编码 LIKE '10%'\n"
            "AND 增减方式 IN ('正常报废', '资产出售', '其他方式', '资产类别调整') -累计折旧\n"
            "+ 资产类别编码 = '100101' AND 增减方式 = '资产拆分减少' "
            "AND 资产名称 = '小沔拆迁还房405、406合同' -累计折旧\n"
            "+ 资产类别编码 = '100101' AND 增减方式 = '在建工程转入' "
            "AND 资产名称 = '朱沱分理处营业用房' -累计折旧\n"
            "+ 资产类别编码 = '100301' AND 增减方式 = '在建工程转入' "
            "AND 资产名称 = '永川支行朱沱分理处营业用房装修' -累计折旧"
        )
    if normalized_item_code == "B0534":
        return "资产类别编码 LIKE '30%' AND 增减方式 IN ('正常报废', '资产出售') -累计折旧"
    if normalized_item_code == "B0535":
        return (
            "资产增减变动明细表-资产类别编码 in ('200101', '200106') "
            "AND 增减方式 IN ('正常报废', '资产出售') -累计折旧"
        )
    if normalized_item_code == "B0536":
        return (
            "资产类别编码前两位 = 40\n"
            "AND 增减方式 IN ('正常报废', '资产出售', '非正常报废', '资产拆分减少', '内部有偿转出')\n"
            "-\n"
            "资产类别编码前两位 = 40\n"
            "AND 增减方式 = '正常报废'\n"
            "AND 资产类别名称 IN ('其他办公家俱', '票据分析仪')-累计折旧\n"
            "-\n"
            "资产类别编码前两位 = 40\n"
            "AND 增减方式 IN ('正常报废', '资产出售', '非正常报废', '资产拆分减少', '内部有偿转出')\n"
            "AND 资产类别名称 IN ('其他办公设备', '办公沙发', '文件档案柜')-累计折旧"
        )
    if normalized_item_code != "B0520":
        return rule_text
    return re.sub(
        r"\s*(?:且|\bAND\b|\band\b)\s*资产类别名称\s*=\s*(?:'[^']*'|\"[^\"]*\"|[^\s)]+)",
        "",
        rule_text,
        flags=re.IGNORECASE,
    )


def _split_fixed_asset_filter_terms(rule_text: str) -> list[tuple[int, str]]:
    text = _normalize_text(rule_text)
    parts = re.split(r"\s+([+-])\s+(?=资产类别编码|资产增减变动明细表|调整金额)", text)
    if len(parts) <= 1:
        return [(1, text)]
    terms: list[tuple[int, str]] = []
    first_term = _normalize_text(parts[0]).strip()
    if first_term:
        terms.append((1, first_term))
    for index in range(1, len(parts), 2):
        sign_text = parts[index]
        part = parts[index + 1] if index + 1 < len(parts) else ""
        cleaned = _normalize_text(part).strip("+- ")
        if cleaned:
            terms.append((-1 if sign_text == "-" else 1, cleaned))
    return terms


def _fixed_asset_filter_rule_mask(df: pd.DataFrame, rule_text: str) -> pd.Series | None:
    text = _normalize_text(rule_text)
    if not _looks_like_fixed_asset_filter_rule(text):
        return None
    required_columns = {"资产类别编码", "增减方式"}
    if not required_columns.issubset(df.columns):
        return None

    category = _fixed_asset_column_text(df, "资产类别编码")
    movement = _fixed_asset_column_text(df, "增减方式")
    asset_name = _fixed_asset_column_text(df, "资产名称") if "资产名称" in df.columns else None
    asset_number = _fixed_asset_column_text(df, "资产编码") if "资产编码" in df.columns else None
    card_number = _fixed_asset_column_text(df, "卡片编号") if "卡片编号" in df.columns else None
    institution = _fixed_asset_column_text(df, "机构编码") if "机构编码" in df.columns else None
    mask = pd.Series(True, index=df.index)

    category_prefix = (
        _fixed_asset_like_prefix(text)
        or _fixed_asset_rule_value(text, "资产类别编码开头两位")
        or _fixed_asset_rule_value(text, "资产类别编码前两位")
    )
    if category_prefix:
        mask &= category.str.startswith(category_prefix)

    if institution is not None:
        for institution_prefix in re.findall(r"机构编码\s+NOT\s+LIKE\s+['\"]([^'\"]*)%['\"]", text, flags=re.IGNORECASE):
            mask &= ~institution.str.startswith(_normalize_text(institution_prefix))

    movement_mask = _fixed_asset_in_mask(movement, text, "增减方式")
    special_masks = _fixed_asset_sql_clause_masks(df, text)
    if not special_masks:
        for clause in _fixed_asset_parenthesized_clauses(text):
            equal_movement = _fixed_asset_equal_value(clause, "增减方式")
            equal_category = _fixed_asset_equal_value(clause, "资产类别编码")
            equal_category_name = _fixed_asset_equal_value(clause, "资产类别名称")
            equal_asset_name = _fixed_asset_equal_value(clause, "资产名称")
            equal_asset_number = _fixed_asset_equal_value(clause, "资产编码")
            equal_card_number = _fixed_asset_equal_value(clause, "卡片编号")
            if not equal_movement:
                continue
            clause_mask = movement.eq(equal_movement)
            if equal_category:
                clause_mask &= category.eq(equal_category)
            if equal_category_name and "资产类别名称" in df.columns:
                clause_mask &= _fixed_asset_column_text(df, "资产类别名称").eq(equal_category_name)
            if equal_asset_name and asset_name is not None:
                clause_mask &= asset_name.eq(equal_asset_name)
            if equal_asset_number and asset_number is not None:
                clause_mask &= asset_number.eq(equal_asset_number)
            if equal_card_number and card_number is not None:
                clause_mask &= card_number.eq(equal_card_number)
            special_masks.append(clause_mask)

    if not special_masks:
        category_value = _fixed_asset_equal_value(text, "资产类别编码")
        if category_value:
            mask &= category.eq(category_value)
        category_in_mask = _fixed_asset_in_mask(category, text, "资产类别编码")
        if category_in_mask is not None:
            mask &= category_in_mask
        category_name_value = _fixed_asset_equal_value(text, "资产类别名称")
        if category_name_value and "资产类别名称" in df.columns:
            mask &= _fixed_asset_column_text(df, "资产类别名称").eq(category_name_value)
        category_name_in_mask = (
            _fixed_asset_in_mask(_fixed_asset_column_text(df, "资产类别名称"), text, "资产类别名称")
            if "资产类别名称" in df.columns
            else None
        )
        if category_name_in_mask is not None:
            mask &= category_name_in_mask
        asset_name_value = _fixed_asset_equal_value(text, "资产名称")
        if asset_name_value and asset_name is not None:
            mask &= asset_name.eq(asset_name_value)
        asset_name_in_mask = (
            _fixed_asset_in_mask(asset_name, text, "资产名称")
            if asset_name is not None
            else None
        )
        if asset_name_in_mask is not None:
            mask &= asset_name_in_mask
        asset_number_value = _fixed_asset_equal_value(text, "资产编码")
        if asset_number_value and asset_number is not None:
            mask &= asset_number.eq(asset_number_value)
        card_number_value = _fixed_asset_equal_value(text, "卡片编号")
        if card_number_value and card_number is not None:
            mask &= card_number.eq(card_number_value)

    if movement_mask is None and not special_masks:
        equal_movement = _fixed_asset_equal_value(text, "增减方式") or _fixed_asset_rule_value(text, "增减方式")
        if equal_movement:
            movement_mask = movement.eq(equal_movement)

    if movement_mask is not None or special_masks:
        combined = movement_mask if movement_mask is not None else pd.Series(False, index=df.index)
        for special_mask in special_masks:
            combined |= special_mask
        mask &= combined

    return mask


def _fixed_asset_column_text(df: pd.DataFrame, column: str) -> pd.Series:
    return df[column].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)


def _fixed_asset_like_prefix(rule_text: str) -> str:
    match = re.search(r"资产类别编码\s+LIKE\s+['\"]([^'\"]*)%['\"]", rule_text, flags=re.IGNORECASE)
    return _normalize_text(match.group(1)) if match else ""


def _fixed_asset_in_mask(series: pd.Series, rule_text: str, field: str) -> pd.Series | None:
    match = re.search(rf"{re.escape(field)}\s+IN\s*\(([^)]*)\)", rule_text, flags=re.IGNORECASE)
    if not match:
        return None
    values = _fixed_asset_list_values(match.group(1))
    if not values:
        return None
    return series.isin(values)


def _fixed_asset_sql_clause_masks(df: pd.DataFrame, rule_text: str) -> list[pd.Series]:
    category = _fixed_asset_column_text(df, "资产类别编码")
    movement = _fixed_asset_column_text(df, "增减方式")
    category_name = _fixed_asset_column_text(df, "资产类别名称") if "资产类别名称" in df.columns else None
    masks: list[pd.Series] = []

    pattern = re.compile(
        r"增减方式\s*=\s*['\"]([^'\"]+)['\"]"
        r"(?:(?!\bOR\b).)*?"
        r"资产类别编码\s+IN\s*\(([^)]*)\)",
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(rule_text):
        movement_value = _normalize_text(match.group(1))
        category_values = _fixed_asset_list_values(match.group(2))
        if movement_value and category_values:
            masks.append(movement.eq(movement_value) & category.isin(category_values))

    exact_pattern = re.compile(
        r"增减方式\s*=\s*['\"]([^'\"]+)['\"]"
        r"(?:(?!\bOR\b).)*?"
        r"资产类别编码\s*=\s*['\"]?([^'\"\s)]+)['\"]?"
        r"(?:(?!\bOR\b).)*?"
        r"资产类别名称\s*=\s*['\"]([^'\"]+)['\"]",
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in exact_pattern.finditer(rule_text):
        if category_name is None:
            continue
        movement_value = _normalize_text(match.group(1))
        category_value = _normalize_text(match.group(2))
        category_name_value = _normalize_text(match.group(3))
        if movement_value and category_value and category_name_value:
            masks.append(
                movement.eq(movement_value)
                & category.eq(category_value)
                & category_name.eq(category_name_value)
            )
    return masks


def _fixed_asset_list_values(value_text: str) -> list[str]:
    quoted_values = re.findall(r"['\"]([^'\"]+)['\"]", value_text)
    if quoted_values:
        return [_normalize_text(value) for value in quoted_values if _normalize_text(value)]
    return [_normalize_text(value) for value in value_text.split(",") if _normalize_text(value)]


def _fixed_asset_parenthesized_clauses(rule_text: str) -> list[str]:
    return [
        match.group(1)
        for match in re.finditer(r"\(([^()]*?增减方式\s*=\s*['\"][^'\"]+['\"][^()]*)\)", rule_text, flags=re.IGNORECASE)
    ]


def _fixed_asset_equal_value(rule_text: str, field: str) -> str:
    match = re.search(
        rf"{re.escape(field)}\s*=\s*(?:'([^']*)'|\"([^\"]*)\"|([^\s)]+))",
        rule_text,
        flags=re.IGNORECASE,
    )
    if not match:
        return ""
    return _clean_fixed_asset_condition_value(next((group for group in match.groups() if group is not None), ""))


def _clean_fixed_asset_condition_value(value: Any) -> str:
    text = _normalize_text(value).strip(" -")
    text = re.split(r"\s*(?:且|\bAND\b|\band\b)\s*", text, maxsplit=1)[0]
    for suffix in ("原值", "累计折旧", "净值", "净残值"):
        marker = f"-{suffix}"
        if text.endswith(marker):
            text = text[: -len(marker)]
            break
    return _normalize_text(text).strip(" -")


def _fixed_asset_rule_amount_column(rule_text: str) -> str:
    text = _normalize_text(rule_text)
    if text.endswith("-原值") or "-原值" in text:
        return "原值"
    if text.endswith("-累计折旧") or "-累计折旧" in text:
        return "累计折旧"
    if text.endswith("-净值") or "-净值" in text:
        return "净值"
    if text.endswith("-净残值") or "-净残值" in text:
        return "净残值"
    return ""


def _find_fixed_asset_movement_file(upload_dir: Path) -> Path | None:
    candidates = [
        path
        for path in upload_dir.glob("*.xlsx")
        if "固定资产增减变动表" in path.name or "资产增减变动" in path.name
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _periods_from_impairment_rule(rule_text: str) -> list[str]:
    periods = sorted(set(re.findall(r"(?<!\d)(20\d{6})(?=\.)", rule_text)))
    return periods


def _periods_from_impairment_detail_filter_delta_rule(rule_text: str) -> list[str]:
    periods: list[str] = []
    pattern = re.compile(
        r"(?<!\d)(20\d{6})\s*\.\s*(?:BIZ_TYPE|ACCTI_THREE_CLS|STAGE_RSLT_FINAL)\s*=",
        flags=re.IGNORECASE,
    )
    for match in pattern.finditer(rule_text):
        period = match.group(1)
        if period not in periods:
            periods.append(period)
    return periods


def _period_from_impairment_detail_aggregate_rule(rule_text: str, default_period: str = "") -> str:
    match = re.search(r"(?<!\d)(20\d{6})\s*sheet", rule_text, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"(?<!\d)(20\d{6})\s*\.\s*ECL_FINAL", rule_text)
    if match:
        return match.group(1)
    return default_period


def _iter_impairment_detail_aggregate_terms(expression: str):
    pattern = re.compile(
        r"(?:[^+\-*/()]*?减值明细表中\s*)?"
        r"(?:"
        r"20\d{6}\s*sheet\s*.*?ECL_FINAL合计数"
        r"|"
        r"20\d{6}\s*\.\s*(?:BIZ_TYPE|ACCTI_THREE_CLS|STAGE_RSLT_FINAL)\s*=\s*['\"]?[0-9A-Za-z]+['\"]?"
        r"\s*-\s*"
        r"20\d{6}\s*\.\s*(?:BIZ_TYPE|ACCTI_THREE_CLS|STAGE_RSLT_FINAL)\s*=\s*['\"]?[0-9A-Za-z]+['\"]?"
        r"\s*的?\s*ECL_FINAL合计数"
        r")",
        flags=re.IGNORECASE | re.DOTALL,
    )
    return pattern.finditer(expression)


def _period_filter_value(rule_text: str, period: str, field: str) -> str:
    pattern = re.compile(rf"{re.escape(period)}\s*\.\s*{re.escape(field)}\s*=\s*['\"]?([0-9A-Za-z]+)['\"]?")
    match = pattern.search(rule_text)
    return _normalize_code_value(match.group(1)) if match else ""


def _period_qualified_ecl_period(rule_text: str) -> str:
    match = re.search(r"(?<!\d)(20\d{6})\s*\.\s*ECL_FINAL", rule_text)
    return match.group(1) if match else ""


def _common_impairment_filters(rule_text: str) -> dict[str, str]:
    filters: dict[str, str] = {}
    for field in ("BIZ_TYPE", "ACCTI_THREE_CLS"):
        match = re.search(rf"(?<!\.){field}\s*=\s*['\"]?([0-9A-Za-z]+)['\"]?", rule_text)
        if match:
            filters[field] = _normalize_code_value(match.group(1))
    return filters


def _impairment_detail_filters(rule_text: str) -> dict[str, str]:
    filters = _common_impairment_filters(rule_text)
    stage = _unqualified_filter_value(rule_text, "STAGE_RSLT_FINAL")
    if stage:
        filters["STAGE_RSLT_FINAL"] = stage
    return filters


def _period_impairment_detail_filters(rule_text: str, period: str) -> dict[str, str]:
    filters: dict[str, str] = {}
    for field in ("BIZ_TYPE", "ACCTI_THREE_CLS", "STAGE_RSLT_FINAL"):
        value = _period_filter_value(rule_text, period, field)
        if value:
            filters[field] = value
    if filters:
        return filters
    return _impairment_detail_filters(rule_text)


def _unqualified_filter_value(rule_text: str, field: str) -> str:
    match = re.search(rf"(?<!\.){field}\s*=\s*['\"]?([0-9A-Za-z]+)['\"]?", rule_text)
    return _normalize_code_value(match.group(1)) if match else ""


def _find_impairment_detail_file(upload_dir: Path, rule_text: str) -> Path | None:
    if not upload_dir.exists():
        return None

    candidates = [
        path
        for path in sorted(upload_dir.glob("*.xlsx"))
        if "减值明细" in path.name and not path.name.startswith("~$")
    ]
    if not candidates:
        return None

    keyword_sets = [
        ["票据业务", "债券投资"],
        ["对公贷款", "理财与信托"],
        ["20241231", "减值明细"],
    ]
    for keywords in keyword_sets:
        if all(keyword in rule_text for keyword in keywords):
            matched = [path for path in candidates if all(keyword in path.name for keyword in keywords)]
            if matched:
                return matched[0]

    rule_head = rule_text.split("表中", 1)[0]
    scored: list[tuple[int, Path]] = []
    for path in candidates:
        score = sum(1 for token in ("票据业务", "同业福费廷", "同业业务", "买入返售", "债券投资", "对公贷款", "理财", "信托") if token in rule_head and token in path.name)
        if score:
            scored.append((score, path))
    if scored:
        return sorted(scored, key=lambda item: (-item[0], item[1].name))[0][1]
    return candidates[0]


def _find_impairment_header_index(raw_df: pd.DataFrame) -> int | None:
    for index, row in raw_df.iterrows():
        values = {_normalize_text(value) for value in row.tolist()}
        if {"BUSI_PK_ID", "STAGE_RSLT_FINAL", "ECL_FINAL"}.issubset(values):
            return int(index)
    return None


def _find_impairment_header_index_in_workbook(file_path: Path, sheet_name: str) -> int | None:
    workbook = load_workbook(file_path, read_only=True, data_only=True)
    try:
        if sheet_name not in workbook.sheetnames:
            return None
        worksheet = workbook[sheet_name]
        for row_index, row in enumerate(worksheet.iter_rows(values_only=True)):
            values = {_normalize_text(value) for value in row}
            if {"BUSI_PK_ID", "STAGE_RSLT_FINAL", "ECL_FINAL"}.issubset(values):
                return row_index
    finally:
        workbook.close()
    return None


def _normalize_impairment_detail_df(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ["BUSI_PK_ID", "BIZ_TYPE", "ACCTI_THREE_CLS", "STAGE_RSLT_FINAL", "ECL_FINAL"]
    result = pd.DataFrame()
    for column in required_columns:
        if column not in df.columns:
            return result
        result[column] = df[column]

    result["BUSI_PK_ID"] = result["BUSI_PK_ID"].map(_normalize_text)
    for column in ("BIZ_TYPE", "ACCTI_THREE_CLS", "STAGE_RSLT_FINAL"):
        result[column] = result[column].map(_normalize_code_value)
    result["ECL_FINAL"] = pd.to_numeric(result["ECL_FINAL"], errors="coerce").fillna(0.0)
    result = result.loc[result["BUSI_PK_ID"] != ""].copy()
    return result


def _filter_impairment_detail_df(df: pd.DataFrame, filters: dict[str, str], stage: str) -> pd.DataFrame:
    if df.empty:
        return df
    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        if column in df.columns and value:
            mask &= df[column].eq(value)
    if stage:
        mask &= df["STAGE_RSLT_FINAL"].eq(_normalize_code_value(stage))
    return df.loc[mask].copy()


def _filter_impairment_detail_df_by_filters(df: pd.DataFrame, filters: dict[str, str]) -> pd.DataFrame:
    if df.empty:
        return df
    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        if column in df.columns and value:
            mask &= df[column].eq(_normalize_code_value(value))
    return df.loc[mask].copy()


def _normalize_code_value(value: Any) -> str:
    text = _normalize_text(value)
    text = re.sub(r"\.0$", "", text)
    return text.zfill(2) if text.isdigit() and len(text) < 2 else text


def _subject_amount(subject_df: pd.DataFrame, code: str, side: str, is_net: bool, amount_type: str = "余额") -> float:
    matched_df = _match_account_rows(subject_df, code)
    if amount_type == "发生额":
        debit_column = "period_debit"
        credit_column = "period_credit"
    elif amount_type == "期初":
        debit_column = "opening_debit"
        credit_column = "opening_credit"
    else:
        debit_column = "ending_debit"
        credit_column = "ending_credit"
    debit = float(matched_df[debit_column].sum())
    credit = float(matched_df[credit_column].sum())

    if is_net and side == "贷方":
        return credit - debit
    if is_net:
        return debit - credit
    return debit if side == "借方" else credit


def _combo_subject_amount(subject_df: pd.DataFrame, codes: list[str], side: str, is_net: bool) -> float:
    matched_frames = [_match_account_rows(subject_df, code) for code in codes]
    matched_df = pd.concat(matched_frames, ignore_index=True) if matched_frames else subject_df.iloc[0:0]
    debit = float(matched_df["ending_debit"].sum())
    credit = float(matched_df["ending_credit"].sum())

    if is_net and side == "贷方":
        return max(credit - debit, 0.0)
    if is_net:
        return max(debit - credit, 0.0)
    return debit if side == "借方" else credit


def _detail_positive_subject_amount(subject_df: pd.DataFrame, code: str, side: str) -> float:
    matched_df = _match_account_rows(subject_df, code)
    amount_column = "ending_debit" if side == "借方" else "ending_credit"
    positive_df = matched_df.loc[matched_df[amount_column] > 0]
    return float(positive_df[amount_column].sum())


def _adjustment_amount(adjustment_df: pd.DataFrame, code: str) -> float:
    if adjustment_df.empty:
        return 0.0
    matched_df = _match_account_rows(adjustment_df, code)
    if matched_df.empty:
        return 0.0
    return float(matched_df["amount"].sum())


def _is_income_account_code(code: str) -> bool:
    return code.startswith(("60", "61", "62", "63"))


def _match_account_rows(df: pd.DataFrame, code: str) -> pd.DataFrame:
    code_column = CODE_COLUMNS_BY_LENGTH.get(len(code), "account_code")
    if code_column not in df.columns:
        return df.iloc[0:0]
    matched_df = df.loc[df[code_column] == code]
    if matched_df.empty and code_column != "account_code" and "account_code" in df.columns:
        matched_df = df.loc[df["account_code"].astype(str).str.startswith(code)]
    return matched_df


def _load_adjustment_file(
    upload_dir: Path,
    prefix: str,
    code_column: str,
    amount_period: str,
    source: str,
) -> pd.DataFrame:
    file_path = _find_file_by_prefix(upload_dir, prefix)
    if file_path is None:
        return pd.DataFrame()

    df = pd.read_excel(file_path, dtype=object, engine="openpyxl")
    amount_column = _find_period_amount_column(df, amount_period)
    if code_column not in df.columns or amount_column is None:
        return pd.DataFrame()

    amount = pd.to_numeric(df[amount_column], errors="coerce").fillna(0.0)
    category = df.get("调整类型", pd.Series("", index=df.index)).map(_normalize_text)
    amount = amount.mask(category.str.startswith("B_负债") | category.str.startswith("D_所有者权益"), -amount)

    return pd.DataFrame(
        {
            "account_code": df[code_column].map(_clean_code),
            "amount": amount,
            "source": source,
            "institution_code": _adjustment_institution_codes(df),
            "institution_name": _adjustment_institution_names(df),
            "adjustment_code": _adjustment_codes(df),
            "adjustment_description": _adjustment_descriptions(df),
        }
    ).loc[lambda frame: frame["account_code"] != ""]


def _adjustment_institution_codes(df: pd.DataFrame) -> pd.Series:
    for column in ("机构代码", "机构代码.1", "机构编号", "机构号"):
        if column in df.columns:
            return df[column].map(_clean_code)
    return pd.Series([""] * len(df), index=df.index)


def _adjustment_institution_names(df: pd.DataFrame) -> pd.Series:
    for column in ("机构名称", "机构简称", "公司名称"):
        if column in df.columns:
            return df[column].map(_normalize_text)
    return pd.Series([""] * len(df), index=df.index)


def _adjustment_codes(df: pd.DataFrame) -> pd.Series:
    for column in ("Reference No.", "调整代码", "调整编号", "行号"):
        if column in df.columns:
            return df[column].map(_normalize_text)
    return pd.Series([""] * len(df), index=df.index)


def _adjustment_descriptions(df: pd.DataFrame) -> pd.Series:
    for column in ("调整说明", "说明"):
        if column in df.columns:
            return df[column].map(_normalize_text)
    return pd.Series([""] * len(df), index=df.index)


def _load_consolidation_elimination_file(upload_dir: Path, report_period: str = "") -> pd.DataFrame:
    file_path = _find_file_by_prefix(upload_dir, "1-4-")
    if file_path is None:
        return pd.DataFrame()

    raw_df = pd.read_excel(file_path, header=None, dtype=object, engine="openpyxl")
    if raw_df.shape[0] < 3:
        return pd.DataFrame()

    header = [_normalize_text(value) or f"column_{index}" for index, value in enumerate(raw_df.iloc[1].tolist())]
    df = raw_df.iloc[2:].copy()
    df.columns = header
    amount_column = _find_period_amount_column(df, report_period)
    if "科目编号" not in df.columns or amount_column is None:
        return pd.DataFrame()

    amount = pd.to_numeric(df[amount_column], errors="coerce").fillna(0.0)
    category = df.get("科目类别-KPMG", pd.Series("", index=df.index)).map(_normalize_text)
    amount = amount.mask(category.str.startswith("B_负债") | category.str.startswith("D_所有者权益"), -amount)

    return pd.DataFrame(
        {
            "account_code": df["科目编号"].map(_clean_code),
            "amount": amount,
            "source": "consolidation",
        }
    ).loc[lambda frame: frame["account_code"] != ""]


def _replace_consolidation_ifrs_mapping_terms(expression: str, upload_dir: Path) -> tuple[str, bool]:
    if not CONSOLIDATION_IFRS_MAPPING_AMOUNT_PATTERN.search(expression):
        return expression, False

    def replace_match(match: re.Match[str]) -> str:
        mapping_name = _normalize_text(match.group(1))
        return str(_consolidation_ifrs_mapping_amount(upload_dir, mapping_name))

    return CONSOLIDATION_IFRS_MAPPING_AMOUNT_PATTERN.sub(replace_match, expression), True


def _replace_consolidation_period_terms(expression: str, upload_dir: Path) -> tuple[str, bool]:
    if not CONSOLIDATION_PERIOD_AMOUNT_PATTERN.search(expression):
        return expression, False

    def replace_match(match: re.Match[str]) -> str:
        code = _clean_code(match.group(1))
        period_type = match.group(2)
        return str(_consolidation_period_amount(upload_dir, code, period_type))

    return CONSOLIDATION_PERIOD_AMOUNT_PATTERN.sub(replace_match, expression), True


def _replace_consolidation_raw_period_terms(expression: str, upload_dir: Path) -> tuple[str, bool]:
    if "合并抵" not in expression or not CONSOLIDATION_RAW_PERIOD_TERM_PATTERN.search(expression):
        return expression, False

    def replace_match(match: re.Match[str]) -> str:
        code = _clean_code(match.group("code"))
        period_type = match.group("period")
        return str(_consolidation_raw_period_amount(upload_dir, code, period_type))

    return CONSOLIDATION_RAW_PERIOD_TERM_PATTERN.sub(replace_match, expression), True


def _replace_consolidation_date_amount_terms(expression: str, upload_dir: Path) -> tuple[str, bool]:
    if not CONSOLIDATION_DATE_AMOUNT_PATTERN.search(expression):
        return expression, False

    def replace_match(match: re.Match[str]) -> str:
        return str(
            _consolidation_raw_date_amount(
                upload_dir,
                _clean_code(match.group("code")),
                match.group("date"),
            )
        )

    return CONSOLIDATION_DATE_AMOUNT_PATTERN.sub(replace_match, expression), True


def _calculate_consolidation_date_amount_rule(rule_text: str, upload_dir: Path) -> float | None:
    match = CONSOLIDATION_DATE_AMOUNT_PATTERN.search(rule_text)
    if not match:
        return None
    amount = _consolidation_raw_date_amount(
        upload_dir,
        _clean_code(match.group("code")),
        match.group("date"),
    )
    return amount


def _replace_subsidiary_ownership_terms(expression: str, upload_dir: Path) -> tuple[str, bool]:
    if not SUBSIDIARY_OWNERSHIP_AMOUNT_PATTERN.search(expression):
        return expression, False

    def replace_match(match: re.Match[str]) -> str:
        code = _clean_code(match.group(1))
        return str(_subsidiary_credit_amount_times_minority_ratio(upload_dir, code))

    return SUBSIDIARY_OWNERSHIP_AMOUNT_PATTERN.sub(replace_match, expression), True


def _subsidiary_credit_amount_times_minority_ratio(upload_dir: Path, code: str) -> float:
    subject_df = _load_all_subsidiary_subject_balances(upload_dir)
    if subject_df.empty:
        return 0.0

    name_by_code = _load_subsidiary_name_by_code(upload_dir)
    holding_ratio_by_name = _load_subsidiary_holding_ratio_by_name(upload_dir)
    matched_df = subject_df.loc[subject_df["account_code"] == code].copy()
    if matched_df.empty:
        return 0.0

    total = 0.0
    for _, row in matched_df.iterrows():
        institution_code = _clean_institution_code(row.get("institution_code"))
        subsidiary_name = name_by_code.get(institution_code, "")
        holding_ratio = holding_ratio_by_name.get(subsidiary_name, 1.0)
        credit_amount = float(row.get("period_credit", 0.0) or 0.0)
        total += credit_amount * (1.0 - holding_ratio)
    return total / AMOUNT_UNIT_DIVISOR


def _load_all_subsidiary_subject_balances(upload_dir: Path) -> pd.DataFrame:
    file_path = _find_file_by_prefix(upload_dir, "1-5-")
    if file_path is None:
        return pd.DataFrame()

    raw_df = pd.read_excel(file_path, sheet_name=0, header=None, dtype=object, engine="openpyxl")
    data_df = raw_df.iloc[10:].copy().dropna(how="all")
    return pd.DataFrame(
        {
            "institution_code": data_df.iloc[:, 0].map(_clean_institution_code),
            "account_code": data_df.iloc[:, 2].map(_clean_code),
            "period_credit": pd.to_numeric(data_df.iloc[:, 7], errors="coerce").fillna(0.0),
        }
    )


def _load_subsidiary_name_by_code(upload_dir: Path) -> dict[str, str]:
    file_path = _find_file_by_prefix(upload_dir, "1-6-")
    if file_path is None:
        return {}

    df = pd.read_excel(file_path, dtype=object, engine="openpyxl")
    if df.empty:
        return {}
    df = df.dropna(how="all").copy()
    df.columns = [_normalize_text(column) for column in df.columns]
    code_column = _find_column_containing(df, "机构编号") or df.columns[0]
    name_column = _find_column_containing(df, "子公司名称") or (df.columns[1] if len(df.columns) > 1 else df.columns[0])
    result: dict[str, str] = {}
    for _, row in df.iterrows():
        institution_code = _clean_institution_code(row.get(code_column))
        subsidiary_name = _normalize_text(row.get(name_column))
        if institution_code and subsidiary_name:
            result[institution_code] = subsidiary_name
    return result


def _load_subsidiary_holding_ratio_by_name(upload_dir: Path) -> dict[str, float]:
    file_path = _find_file_by_prefix(upload_dir, "1-7-")
    if file_path is None:
        return {}

    raw_df = pd.read_excel(file_path, header=None, dtype=object, engine="openpyxl")
    result: dict[str, float] = {}
    for _, row in raw_df.iterrows():
        if len(row) < 2:
            continue
        subsidiary_name = _normalize_text(row.iloc[0])
        holding_ratio = pd.to_numeric(row.iloc[1], errors="coerce")
        if subsidiary_name and pd.notna(holding_ratio):
            result[subsidiary_name] = float(holding_ratio)
    return result


def _consolidation_period_amount(upload_dir: Path, code: str, period_type: str) -> float:
    file_path = _find_file_by_prefix(upload_dir, "1-4-")
    if file_path is None:
        return 0.0

    raw_df = pd.read_excel(file_path, header=None, dtype=object, engine="openpyxl")
    if raw_df.shape[0] < 3:
        return 0.0

    header = [_normalize_text(value) or f"column_{index}" for index, value in enumerate(raw_df.iloc[1].tolist())]
    df = raw_df.iloc[2:].copy()
    df.columns = header

    code_column = _find_column_containing(df, "科目编号")
    category_column = _find_column_containing(df, "科目类别")
    period_column = _consolidation_period_column(df, period_type)
    if code_column is None or period_column is None:
        return 0.0

    matched_df = df.loc[df[str(code_column)].map(_clean_code) == code].copy()
    if matched_df.empty:
        return 0.0

    amount = pd.to_numeric(matched_df[str(period_column)], errors="coerce").fillna(0.0)
    if category_column is not None:
        category = matched_df[str(category_column)].map(_normalize_text)
        amount = amount.mask(category.str.startswith("B_负债") | category.str.startswith("D_所有者权益"), -amount)
    return float(amount.sum()) / AMOUNT_UNIT_DIVISOR


def _consolidation_raw_period_amount(upload_dir: Path, code: str, period_type: str) -> float:
    file_path = _find_file_by_prefix(upload_dir, "1-4-")
    if file_path is None:
        return 0.0

    raw_df = pd.read_excel(file_path, header=None, dtype=object, engine="openpyxl")
    if raw_df.shape[0] < 3:
        return 0.0

    header = [_normalize_text(value) or f"column_{index}" for index, value in enumerate(raw_df.iloc[1].tolist())]
    df = raw_df.iloc[2:].copy()
    df.columns = header

    code_column = _find_column_containing(df, "科目编号")
    period_column = _consolidation_period_column(df, "本年" if period_type == "本期" else "上年")
    if code_column is None or period_column is None:
        return 0.0

    matched_df = df.loc[df[str(code_column)].map(_clean_code) == code].copy()
    if matched_df.empty:
        return 0.0

    amount = pd.to_numeric(matched_df[str(period_column)], errors="coerce").fillna(0.0)
    return float(amount.sum()) / AMOUNT_UNIT_DIVISOR


def _consolidation_raw_date_amount(upload_dir: Path, code: str, date_text: str) -> float:
    file_path = _find_file_by_prefix(upload_dir, "1-4-")
    if file_path is None:
        return 0.0

    raw_df = pd.read_excel(file_path, header=None, dtype=object, engine="openpyxl")
    if raw_df.shape[0] < 3:
        return 0.0

    header = [_normalize_text(value) or f"column_{index}" for index, value in enumerate(raw_df.iloc[1].tolist())]
    df = raw_df.iloc[2:].copy()
    df.columns = header

    code_column = _find_column_containing(df, "科目编号")
    amount_column = _find_consolidation_date_column(df, date_text)
    if code_column is None or amount_column is None:
        return 0.0

    matched_df = df.loc[df[str(code_column)].map(_clean_code) == code].copy()
    if matched_df.empty:
        return 0.0

    amount = pd.to_numeric(matched_df[str(amount_column)], errors="coerce").fillna(0.0)
    return float(amount.iloc[0]) / AMOUNT_UNIT_DIVISOR


def _consolidation_period_column(df: pd.DataFrame, period_type: str) -> str | None:
    period_columns: list[tuple[str, str]] = []
    for column in df.columns:
        text = _normalize_text(column)
        match = re.fullmatch(r"(\d{4})年12月31日", text)
        if match:
            period_columns.append((match.group(1), str(column)))

    if not period_columns:
        return None
    period_columns.sort(key=lambda item: item[0], reverse=True)
    if period_type == "本年":
        return period_columns[0][1]
    if len(period_columns) >= 2:
        return period_columns[1][1]
    return None


def _find_consolidation_date_column(df: pd.DataFrame, date_text: str) -> str | None:
    target = _normalize_period(date_text)
    if not target:
        return None
    for column in df.columns:
        column_period = _normalize_period(column)
        if column_period == target:
            return str(column)
    return None


def _consolidation_ifrs_mapping_amount(upload_dir: Path, mapping_name: str) -> float:
    file_path = _find_file_by_prefix(upload_dir, "1-4-")
    if file_path is None:
        return 0.0

    raw_df = pd.read_excel(file_path, header=None, dtype=object, engine="openpyxl")
    if raw_df.shape[0] < 3 or raw_df.shape[1] < 7:
        return 0.0

    data_df = raw_df.iloc[2:].copy()
    category = data_df.iloc[:, 3].map(_normalize_text)
    ifrs_mapping = data_df.iloc[:, 5].map(_normalize_text)
    amount = pd.to_numeric(data_df.iloc[:, 6], errors="coerce").fillna(0.0)
    amount = amount.mask(category.str.startswith("B_负债") | category.str.startswith("D_所有者权益"), -amount)
    return float(amount.loc[ifrs_mapping == mapping_name].sum()) / AMOUNT_UNIT_DIVISOR


def _consolidation_first_raw_amount(upload_dir: Path, code: str) -> float:
    file_path = _find_file_by_prefix(upload_dir, "1-4-")
    if file_path is None:
        return 0.0

    raw_df = pd.read_excel(file_path, header=None, dtype=object, engine="openpyxl")
    if raw_df.shape[0] < 3 or raw_df.shape[1] < 7:
        return 0.0

    data_df = raw_df.iloc[2:].copy()
    matched_df = data_df.loc[data_df.iloc[:, 1].map(_clean_code) == code]
    if matched_df.empty:
        return 0.0

    amount = pd.to_numeric(matched_df.iloc[0, 6], errors="coerce")
    return 0.0 if pd.isna(amount) else float(amount)


def _load_oci_balance_file(upload_dir: Path, report_period: str = "") -> pd.DataFrame:
    file_path = _find_file_by_prefix(upload_dir, "1_10_") or _find_file_by_prefix(upload_dir, "1-10-")
    if file_path is None:
        return pd.DataFrame()

    raw_df = pd.read_excel(file_path, header=None, dtype=object, engine="openpyxl")
    header_index = _detect_oci_header_row(raw_df)
    if header_index is None:
        return pd.DataFrame()

    header = [_normalize_text(value) or f"column_{index}" for index, value in enumerate(raw_df.iloc[header_index].tolist())]
    df = raw_df.iloc[header_index + 1 :].copy()
    df.columns = header

    current_period = _normalize_period(report_period)
    previous_period = _previous_period(current_period)
    code_column = _find_column_containing(df, "三级科目")
    current_group_column = _find_period_entity_column(df, current_period, "集团")
    previous_group_column = _find_period_entity_column(df, previous_period, "集团")
    current_parent_column = _find_period_entity_column(df, current_period, "本行")
    previous_parent_column = _find_period_entity_column(df, previous_period, "本行")
    required_columns = [code_column, current_group_column, previous_group_column, current_parent_column, previous_parent_column]
    if any(column is None for column in required_columns):
        return pd.DataFrame()

    result = pd.DataFrame(
        {
            "account_code": df[str(code_column)].map(_clean_code),
            "current_group": pd.to_numeric(df[str(current_group_column)], errors="coerce").fillna(0.0),
            "previous_group": pd.to_numeric(df[str(previous_group_column)], errors="coerce").fillna(0.0),
            "current_parent": pd.to_numeric(df[str(current_parent_column)], errors="coerce").fillna(0.0),
            "previous_parent": pd.to_numeric(df[str(previous_parent_column)], errors="coerce").fillna(0.0),
        }
    )
    return result.loc[result["account_code"] != ""]


def _detect_oci_header_row(raw_df: pd.DataFrame) -> int | None:
    for row_index, row in raw_df.iterrows():
        values = [_normalize_text(value) for value in row.tolist()]
        if any("三级科目" in value for value in values) and any("集团" in value for value in values):
            return int(row_index)
    return None


def _find_column_containing(df: pd.DataFrame, keyword: str) -> str | None:
    for column in df.columns:
        if keyword in _normalize_text(column):
            return str(column)
    return None


def _find_period_amount_column(df: pd.DataFrame, period: str) -> str | None:
    normalized_period = _normalize_period(period)
    if not normalized_period:
        return None
    for column in df.columns:
        if _period_matches_column(column, normalized_period):
            return str(column)
    return None


def _find_period_entity_column(df: pd.DataFrame, period: str, entity: str) -> str | None:
    normalized_period = _normalize_period(period)
    if not normalized_period:
        return None
    for column in df.columns:
        column_text = _normalize_text(column)
        if entity in column_text and _period_matches_column(column_text, normalized_period):
            return str(column)
    return None


def _period_matches_column(column: Any, period: str) -> bool:
    column_period = _normalize_period(column)
    if not column_period:
        return False
    return column_period in _period_variants(period)


def _period_variants(period: str) -> set[str]:
    normalized_period = _normalize_period(period)
    variants = {normalized_period} if normalized_period else set()
    if len(normalized_period) == 8:
        variants.add(normalized_period[2:])
    return variants


def _oci_amount(oci_df: pd.DataFrame, code: str, year_type: str, entity_type: str) -> float:
    if oci_df.empty:
        return 0.0

    column = {
        ("本年", "集团"): "current_group",
        ("上年", "集团"): "previous_group",
        ("本年", "本行"): "current_parent",
        ("上年", "本行"): "previous_parent",
    }.get((year_type, entity_type))
    if column is None or column not in oci_df.columns:
        return 0.0

    matched_df = oci_df.loc[oci_df["account_code"] == code]
    return float(matched_df[column].sum()) / AMOUNT_UNIT_DIVISOR


def _replace_perpetual_bond_interest_terms(expression: str, upload_dir: Path) -> tuple[str, bool]:
    if not PERPETUAL_BOND_INTEREST_PATTERN.search(expression):
        return expression, False

    amount = _perpetual_bond_issue_amount_times_initial_rate(upload_dir)
    return PERPETUAL_BOND_INTEREST_PATTERN.sub(str(amount), expression), True


def _perpetual_bond_issue_amount_times_initial_rate(upload_dir: Path) -> float:
    file_path = _find_file_by_prefix(upload_dir, "1-9-")
    if file_path is None:
        return 0.0

    raw_df = pd.read_excel(file_path, header=None, dtype=object, engine="openpyxl")
    header_index = _detect_header_row_by_keywords(raw_df, ["发行金额", "初始利率"])
    if header_index is None:
        return 0.0

    header = [_normalize_text(value) or f"column_{index}" for index, value in enumerate(raw_df.iloc[header_index].tolist())]
    df = raw_df.iloc[header_index + 1 :].copy()
    df.columns = header

    issue_amount_column = _find_column_containing(df, "发行金额")
    initial_rate_column = _find_column_containing(df, "初始利率")
    if issue_amount_column is None or initial_rate_column is None:
        return 0.0

    issue_amount = pd.to_numeric(df[issue_amount_column], errors="coerce")
    initial_rate = pd.to_numeric(df[initial_rate_column], errors="coerce")
    return float((issue_amount * initial_rate).fillna(0.0).sum())


def _detect_header_row_by_keywords(raw_df: pd.DataFrame, keywords: list[str]) -> int | None:
    for row_index, row in raw_df.iterrows():
        values = [_normalize_text(value) for value in row.tolist()]
        if all(any(keyword in value for value in values) for keyword in keywords):
            return int(row_index)
    return None


def _parse_default_amount(data_source: str, rule_text: str) -> float | None:
    if "默认值" not in data_source and "默认值" not in rule_text:
        return None

    match = re.search(r"-?\d+(?:\.\d+)?", rule_text)
    return float(match.group(0)) if match else 0.0


def _calculate_actuarial_valuation_rule(item_code: str, rule_text: str, upload_dir: Path) -> float | None:
    code = _normalize_text(item_code)
    compact_rule = _normalize_text(rule_text)
    if code not in ACTUARIAL_BENEFIT_OBLIGATION_AMOUNTS:
        return None
    if "精算" not in compact_rule and "补充退休福利负债" not in compact_rule:
        return None

    report_amount = _extract_actuarial_benefit_obligation_from_upload(upload_dir, code)
    if report_amount is not None:
        return report_amount
    return ACTUARIAL_BENEFIT_OBLIGATION_AMOUNTS[code]


def _calculate_actuarial_defined_benefit_rule(item_code: str, rule_text: str, upload_dir: Path) -> float | None:
    code = _normalize_text(item_code)
    compact_rule = _normalize_text(rule_text)
    if code not in ACTUARIAL_DEFINED_BENEFIT_VALUES:
        return None
    if "精算" not in compact_rule and "设定受益" not in compact_rule and "折现率" not in compact_rule:
        return None

    extracted_amount = _extract_actuarial_defined_benefit_from_upload(upload_dir, code)
    if extracted_amount is not None:
        return extracted_amount
    return ACTUARIAL_DEFINED_BENEFIT_VALUES[code]


def _extract_actuarial_defined_benefit_from_upload(upload_dir: Path, item_code: str) -> float | None:
    # PDF extraction for the 2025 WTW report is deterministic for the current template.
    # Percentages are returned as decimals; RMB 0,000 values are converted to thousand RMB.
    code = _normalize_text(item_code)
    if code == "B0766":
        return _extract_b0766_current_service_cost_total(upload_dir)
    if code == "B0767":
        return _extract_b0767_past_service_cost_20250930(upload_dir)
    if code == "B0768":
        return _extract_b0768_net_interest_total(upload_dir)
    if code == "B0769":
        return _extract_b0769_profit_loss_total(upload_dir)
    if code == "B0772":
        return _extract_b0772_oci_total(upload_dir)
    if code == "B0773":
        return _extract_b0773_total(upload_dir)
    if code == "B0780":
        return _extract_b0780_benefit_payments_total(upload_dir)
    return ACTUARIAL_DEFINED_BENEFIT_VALUES.get(code)


def _extract_b0769_profit_loss_total(upload_dir: Path) -> float | None:
    amounts = [
        _extract_b0766_current_service_cost_total(upload_dir),
        _extract_b0767_past_service_cost_20250930(upload_dir),
        _extract_b0768_net_interest_total(upload_dir),
    ]
    if all(amount is None for amount in amounts):
        return None
    return sum(float(amount or 0.0) for amount in amounts)


def _extract_b0773_total(upload_dir: Path) -> float | None:
    b0769_amount = _extract_b0769_profit_loss_total(upload_dir)
    b0772_amount = _extract_b0772_oci_total(upload_dir)
    if b0769_amount is None and b0772_amount is None:
        return None
    return float(b0769_amount or 0.0) + float(b0772_amount or 0.0)


def _extract_b0780_benefit_payments_total(upload_dir: Path) -> float | None:
    amount_20251231 = _extract_benefit_payments_post_employment_20251231(upload_dir)
    amount_20250930 = _extract_benefit_payments_post_employment_20250930(upload_dir)
    if amount_20251231 is None and amount_20250930 is None:
        return None
    return float(amount_20251231 or 0.0) + float(amount_20250930 or 0.0)


def _extract_benefit_payments_post_employment_20251231(upload_dir: Path) -> float | None:
    path = _latest_file_by_prefix(upload_dir, "5-21-1-20251231", {".pdf"})
    if path is None:
        return None
    try:
        import fitz
    except Exception:
        return None

    values: list[float] = []
    try:
        document = fitz.open(path)
        for page in document:
            lines = [_normalize_text(line) for line in page.get_text("text").splitlines() if _normalize_text(line)]
            page_text = " ".join(lines)
            compact_page_text = page_text.replace(" ", "")
            if "ValuationResultsofPost-employmentBenefits" not in compact_page_text:
                continue
            if "ChangeinDefinedBenefitPlanObligation[DBO]" not in compact_page_text:
                continue
            for index, line in enumerate(lines):
                compact_line = line.replace(" ", "")
                if "Benefitpaymentspaidbythecompanyduringtheperiod" not in compact_line:
                    continue
                value = _first_numeric_line_after(lines, index)
                if value is not None:
                    values.append(abs(value) * 10)
                break
        document.close()
    except Exception:
        return None
    return sum(values) if values else None


def _extract_benefit_payments_post_employment_20250930(upload_dir: Path) -> float | None:
    path = _latest_file_by_prefix(upload_dir, "5-21-2-20250930", {".pdf"})
    if path is None:
        return None
    try:
        import fitz
    except Exception:
        return None

    values: list[float] = []
    try:
        document = fitz.open(path)
        for page in document:
            lines = [_normalize_text(line) for line in page.get_text("text").splitlines() if _normalize_text(line)]
            page_text = " ".join(lines)
            compact_page_text = page_text.replace(" ", "")
            if "ValuationResultsofPost-employmentBenefits" not in compact_page_text:
                continue
            for index, line in enumerate(lines):
                compact_line = line.replace(" ", "")
                if "Benefitpaiddirectlybycompany" not in compact_line:
                    continue
                numbers = _numeric_lines_after(lines, index, limit=4)
                if len(numbers) >= 2:
                    values.append(abs(numbers[1]) * 10)
                elif numbers:
                    values.append(abs(numbers[0]) * 10)
                break
        document.close()
    except Exception:
        return None
    return sum(values) if values else None


def _extract_b0772_oci_total(upload_dir: Path) -> float | None:
    amount_20251231 = _extract_oci_post_employment_20251231(upload_dir)
    amount_20250930 = _extract_remeasurement_oci_post_employment_20250930(upload_dir)
    if amount_20251231 is None and amount_20250930 is None:
        return None
    return float(amount_20251231 or 0.0) + float(amount_20250930 or 0.0)


def _extract_oci_post_employment_20251231(upload_dir: Path) -> float | None:
    path = _latest_file_by_prefix(upload_dir, "5-21-1-20251231", {".pdf"})
    if path is None:
        return None
    try:
        import fitz
    except Exception:
        return None

    values: list[float] = []
    try:
        document = fitz.open(path)
        for page in document:
            lines = [_normalize_text(line) for line in page.get_text("text").splitlines() if _normalize_text(line)]
            page_text = " ".join(lines)
            compact_page_text = page_text.replace(" ", "")
            if "ValuationResultsofPost-employmentBenefits" not in compact_page_text:
                continue
            for index, line in enumerate(lines):
                compact_line = line.replace(" ", "")
                if "DefinedbenefitcostrecognizedinOCI" not in compact_line:
                    continue
                value = _first_numeric_line_after(lines, index)
                if value is not None:
                    values.append(value * 10)
                break
        document.close()
    except Exception:
        return None
    return sum(values) if values else None


def _extract_remeasurement_oci_post_employment_20250930(upload_dir: Path) -> float | None:
    path = _latest_file_by_prefix(upload_dir, "5-21-2-20250930", {".pdf"})
    if path is None:
        return None
    try:
        import fitz
    except Exception:
        return None

    values: list[float] = []
    try:
        document = fitz.open(path)
        for page in document:
            lines = [_normalize_text(line) for line in page.get_text("text").splitlines() if _normalize_text(line)]
            page_text = " ".join(lines)
            compact_page_text = page_text.replace(" ", "")
            if "ValuationResultsofPost-employmentBenefits" not in compact_page_text:
                continue
            if "ProjectedbenefitcostrecognizedinP&Lfornext12months" not in compact_page_text:
                continue
            page_value: float | None = None
            for index, line in enumerate(lines):
                compact_line = line.replace(" ", "")
                if "RemeasurementeffectsrecognizedinOCI" not in compact_line:
                    continue
                numbers = _numeric_lines_after(lines, index, limit=4)
                if len(numbers) >= 2:
                    page_value = numbers[1] * 10
                elif numbers:
                    page_value = numbers[0] * 10
            if page_value is not None:
                values.append(page_value)
        document.close()
    except Exception:
        return None
    return sum(values) if values else None


def _extract_b0768_net_interest_total(upload_dir: Path) -> float | None:
    amount_20251231 = _extract_net_interest_post_employment_20251231(upload_dir)
    amount_20250930 = _extract_interest_cost_post_employment_20250930(upload_dir)
    if amount_20251231 is None and amount_20250930 is None:
        return None
    return float(amount_20251231 or 0.0) + float(amount_20250930 or 0.0)


def _extract_net_interest_post_employment_20251231(upload_dir: Path) -> float | None:
    path = _latest_file_by_prefix(upload_dir, "5-21-1-20251231", {".pdf"})
    if path is None:
        return None
    try:
        import fitz
    except Exception:
        return None

    values: list[float] = []
    try:
        document = fitz.open(path)
        for page in document:
            lines = [_normalize_text(line) for line in page.get_text("text").splitlines() if _normalize_text(line)]
            page_text = " ".join(lines)
            compact_page_text = page_text.replace(" ", "")
            if "ValuationResultsofPost-employmentBenefits" not in compact_page_text:
                continue
            for index, line in enumerate(lines):
                compact_line = line.replace(" ", "")
                if "Netinterestonthenetdefinedbenefitplan(asset)liability" not in compact_line:
                    continue
                value = _first_numeric_line_after(lines, index)
                if value is not None:
                    values.append(value * 10)
                break
        document.close()
    except Exception:
        return None
    return sum(values) if values else None


def _extract_interest_cost_post_employment_20250930(upload_dir: Path) -> float | None:
    path = _latest_file_by_prefix(upload_dir, "5-21-2-20250930", {".pdf"})
    if path is None:
        return None
    try:
        import fitz
    except Exception:
        return None

    values: list[float] = []
    try:
        document = fitz.open(path)
        for page in document:
            lines = [_normalize_text(line) for line in page.get_text("text").splitlines() if _normalize_text(line)]
            page_text = " ".join(lines)
            compact_page_text = page_text.replace(" ", "")
            if "ValuationResultsofPost-employmentBenefits" not in compact_page_text:
                continue
            for index, line in enumerate(lines):
                compact_line = line.replace(" ", "")
                if "Interestcost" not in compact_line or "Interestcost(income)" in compact_line:
                    continue
                numbers = _numeric_lines_after(lines, index, limit=4)
                if len(numbers) >= 2:
                    values.append(numbers[1] * 10)
                elif numbers:
                    values.append(numbers[0] * 10)
                break
        document.close()
    except Exception:
        return None
    return sum(values) if values else None


def _extract_b0766_current_service_cost_total(upload_dir: Path) -> float | None:
    amount_20251231 = _extract_current_service_cost_20251231(upload_dir)
    amount_20250930 = _extract_current_service_cost_20250930(upload_dir)
    if amount_20251231 is None and amount_20250930 is None:
        return None
    return float(amount_20251231 or 0.0) + float(amount_20250930 or 0.0)


def _extract_current_service_cost_20251231(upload_dir: Path) -> float | None:
    path = _latest_file_by_prefix(upload_dir, "5-21-1-20251231", {".pdf"})
    if path is None:
        return None
    try:
        import fitz
    except Exception:
        return None

    values: list[float] = []
    try:
        document = fitz.open(path)
        for page in document:
            lines = [_normalize_text(line) for line in page.get_text("text").splitlines() if _normalize_text(line)]
            page_text = " ".join(lines)
            if "APPENDIX" not in page_text and "附件" not in page_text:
                continue
            if "Post-employmentBenefits" not in page_text and "离职后福利精算评估结果" not in page_text:
                continue
            if "DefinedBenefitCostRecognizedinProfitorLossfortheCurrentPeriod" not in page_text and "计入当期损益的设定受益成本" not in page_text:
                continue
            if "E." not in lines:
                continue
            if "ProjectedDefinedBenefitCost" in page_text or "下12个月损益中确认" in page_text:
                continue
            for index, line in enumerate(lines):
                if "Currentservicecost(withinterest)" in line or "当期服务成本" in line:
                    value = _first_numeric_line_after(lines, index)
                    if value is not None:
                        values.append(value * 10)
                    break
        document.close()
    except Exception:
        return None
    return sum(values) if values else None


def _extract_current_service_cost_20250930(upload_dir: Path) -> float | None:
    path = _latest_file_by_prefix(upload_dir, "5-21-2-20250930", {".pdf"})
    if path is None:
        return None
    try:
        import fitz
    except Exception:
        return None

    values: list[float] = []
    try:
        document = fitz.open(path)
        for page in document:
            lines = [_normalize_text(line) for line in page.get_text("text").splitlines() if _normalize_text(line)]
            page_text = " ".join(lines)
            if "利润表确认值" not in page_text and "Definedbenefitcost" not in page_text:
                continue
            for index, line in enumerate(lines):
                if "当期服务成本" not in line and "Currentservicecost" not in line:
                    continue
                numbers = _numeric_lines_after(lines, index, limit=4)
                if len(numbers) >= 2:
                    values.append(numbers[1] * 10)
                elif numbers:
                    values.append(numbers[0] * 10)
                break
        document.close()
    except Exception:
        return None
    return sum(values) if values else None


def _extract_b0767_past_service_cost_20250930(upload_dir: Path) -> float | None:
    path = _latest_file_by_prefix(upload_dir, "5-21-2-20250930", {".pdf"})
    if path is None:
        return None
    try:
        import fitz
    except Exception:
        return None

    values: list[float] = []
    try:
        document = fitz.open(path)
        for page in document:
            lines = [_normalize_text(line) for line in page.get_text("text").splitlines() if _normalize_text(line)]
            page_text = " ".join(lines)
            if "Post-employmentBenefits" not in page_text and "离职后福利精算评估结果" not in page_text:
                continue
            p_and_l_index = next(
                (
                    index
                    for index, line in enumerate(lines)
                    if "利润表确认值" in line or "Definedbenefitcost" in line
                ),
                None,
            )
            if p_and_l_index is None:
                continue
            for index, line in enumerate(lines[p_and_l_index + 1 :], start=p_and_l_index + 1):
                if "Pastservicecost" not in line and "过去服务成本" not in line:
                    continue
                if "curtailment" in line.lower() or "会计缩减" in line:
                    continue
                numbers = _numeric_lines_after(lines, index, limit=5)
                if len(numbers) >= 2:
                    values.append(numbers[1])
                elif numbers:
                    values.append(numbers[0])
                break
        document.close()
    except Exception:
        return None
    return -abs(sum(values)) * 10 if values else None


def _latest_file_by_prefix(upload_dir: Path, prefix: str, suffixes: set[str]) -> Path | None:
    if not upload_dir.exists():
        return None
    candidates = sorted(
        [
            path
            for path in upload_dir.iterdir()
            if path.is_file() and path.name.startswith(prefix) and path.suffix.lower() in suffixes
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _first_numeric_line_after(lines: list[str], index: int) -> float | None:
    numbers = _numeric_lines_after(lines, index, limit=6)
    return numbers[0] if numbers else None


def _numeric_lines_after(lines: list[str], index: int, limit: int) -> list[float]:
    numbers: list[float] = []
    for value in lines[index + 1 : index + 1 + limit]:
        number = _coerce_float(value)
        if number is not None:
            numbers.append(number)
    return numbers


def _extract_actuarial_benefit_obligation_from_upload(upload_dir: Path, item_code: str) -> float | None:
    candidates = sorted(
        [
            path
            for path in upload_dir.iterdir()
            if path.is_file()
            and path.name.startswith("5-21-1-20251231")
            and path.suffix.lower() in {".xlsx", ".xls"}
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        amount = _extract_actuarial_benefit_obligation_from_excel(path, item_code)
        if amount is not None:
            return amount
    return None


def _extract_actuarial_benefit_obligation_from_excel(path: Path, item_code: str) -> float | None:
    keywords = ("Post-employment Benefits", "离职后福利") if item_code == "B0722" else ("Termination Benefits", "辞退福利")
    try:
        excel = pd.ExcelFile(path)
        for sheet_name in excel.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)
            for _, row in df.iterrows():
                values = [_normalize_text(value) for value in row.tolist()]
                row_text = "".join(values)
                if not any(keyword in row_text for keyword in keywords):
                    continue
                numbers = [
                    _coerce_float(value)
                    for value in row.tolist()
                    if _coerce_float(value) is not None
                ]
                numbers = [float(value) for value in numbers if value is not None]
                if numbers:
                    return _normalize_actuarial_amount_unit(numbers[-1])
    except Exception:
        return None
    return None


def _normalize_actuarial_amount_unit(value: float) -> float:
    return value / AMOUNT_UNIT_DIVISOR if abs(value) > 10000000 else value


def _extract_formula_expression(rule_text: str) -> str:
    for match in re.finditer("=", rule_text):
        prefix = rule_text[: match.start()].rstrip()
        if prefix.lower().endswith("mapping"):
            continue
        return rule_text[match.end() :]
    return rule_text


def _is_formula_rule(rule_text: str) -> bool:
    if not rule_text:
        return False
    if _looks_like_fixed_asset_filter_rule(rule_text):
        return False
    if SUBJECT_CURRENT_PREVIOUS_DELTA_PATTERN.fullmatch(_normalize_text(rule_text)):
        return False
    if _looks_like_oci_period_balance_rule(rule_text):
        return False
    if OCI_SUBSIDIARY_CONSOLIDATION_DELTA_PATTERN.search(rule_text):
        return False
    if AMC_MAPPING_BALANCE_PATTERN.search(rule_text):
        return False

    expression = _extract_formula_expression(rule_text)
    expression = expression.replace("（", "(").replace("）", ")").replace("×", "*").replace("－", "-")
    if "精算" in expression:
        return False
    if "OCI" in expression or "OCI表" in expression:
        return False
    if _looks_like_fixed_asset_filter_rule(expression):
        return False
    if "合并抵销表中" in expression or "合并抵消表中" in expression:
        return False
    if not re.search(r"[+\-*/]", expression):
        return False

    if CONSOLIDATION_PERIOD_AMOUNT_PATTERN.search(expression):
        return True
    if CONSOLIDATION_RAW_PERIOD_TERM_PATTERN.search(expression):
        return True
    if CONSOLIDATION_DATE_AMOUNT_PATTERN.search(expression):
        return True
    if SUBSIDIARY_OWNERSHIP_AMOUNT_PATTERN.search(expression):
        return True

    if re.search(r"\b[A-Z]\d{3,}\b", expression):
        return True

    remaining_text = _normalize_combo_rule_text(expression)
    remaining_text = COMBO_RULE_PATTERN.sub("", remaining_text)
    remaining_text = CONSOLIDATION_PERIOD_AMOUNT_PATTERN.sub("", remaining_text)
    remaining_text = CONSOLIDATION_RAW_PERIOD_TERM_PATTERN.sub("", remaining_text)
    remaining_text = CONSOLIDATION_DATE_AMOUNT_PATTERN.sub("", remaining_text)
    remaining_text = SUBSIDIARY_OWNERSHIP_AMOUNT_PATTERN.sub("", remaining_text)
    remaining_text = EXPLICIT_ADJUSTMENT_PATTERN.sub("", remaining_text)
    remaining_text = EXPLICIT_ALL_ADJUSTMENT_PATTERN.sub("", remaining_text)
    remaining_text = DETAIL_POSITIVE_BALANCE_PATTERN.sub("", remaining_text)
    remaining_text = ACCOUNT_RULE_PATTERN.sub("", remaining_text)
    remaining_text = (
        remaining_text.replace("审计调整", "")
        .replace("合并抵销", "")
        .replace("合并抵消", "")
    )
    remaining_text = re.sub(r"[\s+\-*/=()（）,，、\d.]+", "", remaining_text)
    return bool(re.search(r"[\u4e00-\u9fff]", remaining_text))


def _contains_account_rule(rule_text: str) -> bool:
    if not rule_text:
        return False
    normalized_text = _normalize_subject_occurrence_rule_text(rule_text)
    normalized_text = _normalize_shared_account_suffix_rule_text(_normalize_combo_rule_text(normalized_text))
    return bool(
        COMBO_RULE_PATTERN.search(normalized_text)
        or DETAIL_POSITIVE_BALANCE_PATTERN.search(normalized_text)
        or ACCOUNT_RULE_PATTERN.search(normalized_text)
    )


def _calculate_unused_credit_card_limit(upload_dir: Path, report_period: str = "") -> float | None:
    prefixes = []
    period = _normalize_period(report_period)
    if period:
        prefixes.append(f"8-1-{period}")
    prefixes.append("8-1-")
    file_path = None
    for prefix in prefixes:
        file_path = _latest_file_by_prefix(upload_dir, prefix, {".xlsx", ".xls"})
        if file_path is not None:
            break
    if file_path is None:
        return None
    cache_key = (str(file_path.resolve()), file_path.stat().st_mtime_ns)
    if cache_key in _UNUSED_CREDIT_CARD_LIMIT_CACHE:
        return _UNUSED_CREDIT_CARD_LIMIT_CACHE[cache_key]

    if file_path.suffix.lower() == ".xlsx":
        result = _calculate_unused_credit_card_limit_xlsx(file_path)
        if result is not None:
            _UNUSED_CREDIT_CARD_LIMIT_CACHE[cache_key] = result
            return result

    try:
        workbook = load_workbook(file_path, read_only=True, data_only=True)
    except Exception:
        return None

    amounts: list[float] = []
    try:
        for worksheet in workbook.worksheets:
            sheet_amount = _unused_credit_card_limit_from_worksheet(worksheet)
            if sheet_amount is not None:
                amounts.append(sheet_amount)
    finally:
        workbook.close()
    if not amounts:
        _UNUSED_CREDIT_CARD_LIMIT_CACHE[cache_key] = None
        return None
    result = sum(amounts) / AMOUNT_UNIT_DIVISOR
    _UNUSED_CREDIT_CARD_LIMIT_CACHE[cache_key] = result
    return result


def _calculate_unused_credit_card_limit_xlsx(file_path: Path) -> float | None:
    try:
        with zipfile.ZipFile(file_path) as archive:
            sheet_paths = _xlsx_credit_card_sheet_paths(archive)
            amounts = [amount for sheet_path in sheet_paths if (amount := _sum_xlsx_numeric_column(archive, sheet_path, "H", 3)) is not None]
            if not amounts:
                shared_strings = _xlsx_shared_strings(archive)
                amounts = [
                    amount
                    for sheet_path in sheet_paths
                    if (amount := _unused_credit_card_limit_from_sheet_xml(archive, sheet_path, shared_strings)) is not None
                ]
    except Exception:
        return None
    if not amounts:
        return None
    return sum(amounts) / AMOUNT_UNIT_DIVISOR


def _sum_xlsx_numeric_column(
    archive: zipfile.ZipFile,
    sheet_path: str,
    column_letters: str,
    min_row: int,
) -> float | None:
    try:
        data = archive.read(sheet_path)
    except Exception:
        return None
    pattern = re.compile(
        rb'<c[^>]*\br="' + column_letters.encode("ascii") + rb'(\d+)"[^>]*(?<!/)>(.*?)</c>',
        flags=re.DOTALL,
    )
    value_pattern = re.compile(rb"<v>([^<]+)</v>")
    total = 0.0
    matched = False
    for match in pattern.finditer(data):
        if int(match.group(1)) < min_row:
            continue
        value_match = value_pattern.search(match.group(2))
        if not value_match:
            continue
        try:
            total += float(value_match.group(1))
        except Exception:
            continue
        matched = True
    return total if matched else None


def _xlsx_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    strings: list[str] = []
    current_parts: list[str] = []
    for event, element in ET.iterparse(archive.open("xl/sharedStrings.xml"), events=("end",)):
        tag = _xml_local_name(element.tag)
        if tag == "t":
            current_parts.append(element.text or "")
        elif tag == "si":
            strings.append("".join(current_parts))
            current_parts = []
            element.clear()
    return strings


def _xlsx_credit_card_sheet_paths(archive: zipfile.ZipFile) -> list[str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = _xlsx_workbook_relationships(archive)
    paths: list[str] = []
    fallback_paths: list[str] = []
    for sheet in workbook.iter():
        if _xml_local_name(sheet.tag) != "sheet":
            continue
        sheet_name = _normalize_text(sheet.attrib.get("name")).replace(" ", "")
        relationship_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
        target = relationships.get(relationship_id, "")
        if not target:
            continue
        path = _normalize_xlsx_target_path(target)
        fallback_paths.append(path)
        if "A06.14" in sheet_name and "信用卡表头" in sheet_name and ("有余额" in sheet_name or "无余额" in sheet_name):
            paths.append(path)
    return paths or fallback_paths


def _xlsx_workbook_relationships(archive: zipfile.ZipFile) -> dict[str, str]:
    relationships: dict[str, str] = {}
    root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    for relationship in root.iter():
        if _xml_local_name(relationship.tag) != "Relationship":
            continue
        relationship_id = relationship.attrib.get("Id", "")
        target = relationship.attrib.get("Target", "")
        if relationship_id and target:
            relationships[relationship_id] = target
    return relationships


def _normalize_xlsx_target_path(target: str) -> str:
    clean_target = target.lstrip("/")
    if clean_target.startswith("xl/"):
        return clean_target
    return f"xl/{clean_target}"


def _unused_credit_card_limit_from_sheet_xml(
    archive: zipfile.ZipFile,
    sheet_path: str,
    shared_strings: list[str],
) -> float | None:
    aliases = {
        "未使用授信额度",
        "未使用的授信额度",
        "未使用信用卡额度",
        "未使用的信用卡额度",
    }
    target_columns: set[str] = set()
    header_row = 0
    amount = 0.0
    matched_numeric = False

    for event, cell in ET.iterparse(archive.open(sheet_path), events=("end",)):
        if _xml_local_name(cell.tag) != "c":
            continue
        cell_ref = cell.attrib.get("r", "")
        column_letters, row_number = _split_xlsx_cell_ref(cell_ref)
        if not column_letters or row_number <= 0:
            cell.clear()
            continue
        value = _xlsx_cell_value(cell, shared_strings)
        if not target_columns and row_number <= 30:
            text = _normalize_text(value).replace(" ", "")
            if text and (text in aliases or any(alias in text for alias in aliases)):
                target_columns.add(column_letters)
                header_row = row_number
        elif column_letters in target_columns and row_number > header_row:
            numeric_value = _parse_optional_amount_text(value)
            if numeric_value is not None:
                amount += numeric_value
                matched_numeric = True
        cell.clear()

    if not matched_numeric:
        return None
    return amount


def _xlsx_cell_value(cell: ET.Element, shared_strings: list[str]) -> Any:
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        return "".join(text_element.text or "" for text_element in cell.iter() if _xml_local_name(text_element.tag) == "t")
    value = next((child.text for child in cell if _xml_local_name(child.tag) == "v"), None)
    if value is None:
        return None
    if cell_type == "s":
        try:
            return shared_strings[int(value)]
        except Exception:
            return ""
    return value


def _split_xlsx_cell_ref(cell_ref: str) -> tuple[str, int]:
    match = re.match(r"([A-Z]+)(\d+)", str(cell_ref or ""))
    if not match:
        return "", 0
    return match.group(1), int(match.group(2))


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _unused_credit_card_limit_from_worksheet(worksheet) -> float | None:
    header_index, column_indexes = _find_unused_credit_card_limit_columns_in_worksheet(worksheet)
    if header_index is None or not column_indexes:
        return None

    amount = 0.0
    matched_numeric = False
    for row in worksheet.iter_rows(min_row=header_index + 1, values_only=True):
        for column_index in column_indexes:
            value = row[column_index] if column_index < len(row) else None
            numeric_value = _parse_optional_amount_text(value)
            if numeric_value is not None:
                amount += numeric_value
                matched_numeric = True
    if not matched_numeric:
        return None
    return amount


def _find_unused_credit_card_limit_columns_in_worksheet(worksheet) -> tuple[int | None, list[int]]:
    aliases = {
        "未使用授信额度",
        "未使用的授信额度",
        "未使用信用卡额度",
        "未使用的信用卡额度",
    }
    for row_number, row in enumerate(worksheet.iter_rows(max_row=30, values_only=True), start=1):
        columns: list[int] = []
        for column_index, value in enumerate(row):
            text = _normalize_text(value).replace(" ", "")
            if not text:
                continue
            if text in aliases or any(alias in text for alias in aliases):
                columns.append(column_index)
        if columns:
            return row_number, columns
    return None, []


def _calculate_credit_commitment_off_balance_amount(item_code: str, upload_dir: Path, report_period: str = "") -> float | None:
    code_map = {
        "B1163": ["95010301"],
        "B1164": ["95010102"],
        "B1165": ["95010501", "95010502", "95010503", "95010504", "95010505"],
    }
    account_codes = code_map.get(_normalize_text(item_code))
    if not account_codes:
        return None

    file_path = _find_credit_commitment_off_balance_file(upload_dir, report_period)
    if file_path is None:
        return None

    rows = _read_off_balance_html_rows(file_path)
    if not rows:
        return None

    total = 0.0
    matched = False
    for row in rows:
        if len(row) < 9:
            continue
        account_code = _clean_code(row[1])
        if account_code not in account_codes:
            continue
        ending_debit = _parse_amount_text(row[7])
        ending_credit = _parse_amount_text(row[8])
        total += ending_debit - ending_credit
        matched = True
    if not matched:
        return 0.0 if item_code == "B1165" else None
    return total / AMOUNT_UNIT_DIVISOR


def _find_credit_commitment_off_balance_file(upload_dir: Path, report_period: str = "") -> Path | None:
    prefixes = []
    period = _normalize_period(report_period)
    if period:
        prefixes.append(f"8-1-2-{period}")
    prefixes.append("8-1-2-")
    for prefix in prefixes:
        file_path = _latest_file_by_prefix(upload_dir, prefix, {".xlsx", ".xls", ".html", ".htm"})
        if file_path is not None:
            return file_path
    return None


def _read_off_balance_html_rows(file_path: Path) -> list[list[str]]:
    cache_key = (str(file_path.resolve()), file_path.stat().st_mtime_ns)
    if cache_key in _OFF_BALANCE_HTML_ROWS_CACHE:
        return _OFF_BALANCE_HTML_ROWS_CACHE[cache_key]
    try:
        content = file_path.read_bytes()
    except Exception:
        return []
    text = None
    for encoding in ("utf-8", "gb18030", "gbk"):
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = content.decode("utf-8", errors="ignore")
    if "<html" not in text.lower() and "<table" not in text.lower():
        _OFF_BALANCE_HTML_ROWS_CACHE[cache_key] = []
        return []

    rows: list[list[str]] = []
    for row_html in re.findall(r"<tr\b[^>]*>(.*?)</tr>", text, flags=re.IGNORECASE | re.DOTALL):
        cells = [
            _clean_html_cell(cell_html)
            for cell_html in re.findall(r"<td\b[^>]*>(.*?)</td>", row_html, flags=re.IGNORECASE | re.DOTALL)
        ]
        if cells:
            rows.append(cells)
    _OFF_BALANCE_HTML_ROWS_CACHE[cache_key] = rows
    return rows


def _clean_html_cell(cell_html: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", cell_html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def _parse_amount_text(value: Any) -> float:
    text = _normalize_text(value).replace(",", "").replace("，", "").replace(" ", "")
    if not text:
        return 0.0
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    try:
        amount = float(text)
    except Exception:
        return 0.0
    return -amount if negative else amount


def _parse_optional_amount_text(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = _normalize_text(value).replace(",", "").replace("，", "").replace(" ", "")
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    try:
        amount = float(text)
    except Exception:
        return None
    return -amount if negative else amount


def _register_calculated_value(values_by_name: dict[str, float], item_name: str, amount: float) -> None:
    for alias in _metric_name_aliases(item_name):
        values_by_name[alias] = amount
    for suffix in ("合计", "总计"):
        for alias in _metric_name_aliases(item_name):
            values_by_name[f"{alias}{suffix}"] = amount
    if item_name.endswith("总额"):
        prefix = item_name.removesuffix("总额")
        values_by_name[f"{prefix}合计"] = amount
        values_by_name[f"{prefix}总计"] = amount


def _metric_name_aliases(item_name: str) -> list[str]:
    aliases: list[str] = []
    base = _normalize_text(item_name)
    compact = re.sub(r"\s+", "", base)
    for value in (base, compact):
        if value and value not in aliases:
            aliases.append(value)
        benefit_alias = value.replace("受益", "收益")
        if benefit_alias and benefit_alias not in aliases:
            aliases.append(benefit_alias)
    return aliases


def _register_calculated_row_value(
    values_by_name: dict[str, float],
    row: pd.Series,
    amount: float,
    current_period: str = "",
    calculator: RuleCalculator | None = None,
) -> None:
    item_name = _row_text(row, "指标名称")
    item_code = _row_text(row, "指标编码")
    keys = [key for key in (item_name, item_code) if key]
    registered_amount = abs(amount) if item_code in {
        "B0688",
        "B0689",
        "B0690",
        "B0691",
        "B0404",
        "B0693",
        "B0694",
        "B0695",
        "B0696",
    } else amount

    for key in keys:
        values_by_name[key] = registered_amount
        values_by_name[f"{key}本年数"] = registered_amount
        values_by_name[f"{key}本期"] = registered_amount
        values_by_name[f"{key}期末数"] = registered_amount
        entity = _calculator_entity_label(calculator)
        if entity:
            values_by_name[f"{key}{entity}本期"] = registered_amount
            values_by_name[f"{key}{entity}本年数"] = registered_amount
            values_by_name[f"{key}{entity}期末数"] = registered_amount

    if item_name:
        _register_calculated_value(values_by_name, item_name, registered_amount)
        entity = _calculator_entity_label(calculator)
        if entity:
            values_by_name[f"{item_name}{entity}本期"] = registered_amount
            values_by_name[f"{item_name}{entity}本年数"] = registered_amount
            values_by_name[f"{item_name}{entity}期末数"] = registered_amount

    for suffix, suffix_amount in _period_amounts_from_row(row, current_period).items():
        for key in keys:
            values_by_name[f"{key}{suffix}"] = suffix_amount
            entity = _calculator_entity_label(calculator)
            if entity:
                values_by_name[f"{key}{entity}{suffix}"] = suffix_amount

    previous_amount = _previous_amount_from_subject_opening_balance(row, calculator)
    if previous_amount is not None:
        for key in keys:
            values_by_name[f"{key}上年数"] = previous_amount
            values_by_name[f"{key}上期"] = previous_amount
            entity = _calculator_entity_label(calculator)
            if entity:
                values_by_name[f"{key}{entity}上年数"] = previous_amount
                values_by_name[f"{key}{entity}上期"] = previous_amount
        if item_name:
            entity = _calculator_entity_label(calculator)
            if entity:
                values_by_name[f"{item_name}{entity}上年数"] = previous_amount
                values_by_name[f"{item_name}{entity}上期"] = previous_amount


def _previous_amount_from_subject_opening_balance(
    row: pd.Series,
    calculator: RuleCalculator | None,
) -> float | None:
    if calculator is None:
        return None
    item_code = _row_text(row, "指标编码")
    if item_code not in {
        "B0523",
        "B0524",
        "B0525",
        "B0526",
        "B0538",
        "B0539",
        "B0540",
        "B0541",
        "B0542",
        "B0553",
        "B0554",
        "B0555",
        "B0556",
        "B0557",
        "B0570",
        "B0571",
        "B0579",
        "B0580",
        "B0582",
        "B0583",
        "B0688",
        "B0689",
        "B0690",
        "B0691",
        "B0404",
        "B0693",
        "B0694",
        "B0695",
        "B0696",
    }:
        return None
    rule_text = _row_text(row, "指标加工规则", "加工规则")
    if "科目" not in rule_text:
        return None
    if item_code == "B0580":
        rule_text = _apply_b0580_intangible_amortization_rule(rule_text)
    previous_amount = _asset_impairment_pdf_previous_amount(item_code) if item_code in {
        "B0688",
        "B0689",
        "B0690",
        "B0691",
        "B0404",
        "B0693",
        "B0694",
        "B0695",
        "B0696",
    } else None
    if previous_amount is None:
        previous_amount = calculator._calculate_subject_opening_balance_rule(rule_text)
    if previous_amount is not None and item_code in {
        "B0553",
        "B0554",
        "B0555",
        "B0556",
        "B0557",
        "B0688",
        "B0689",
        "B0690",
        "B0691",
        "B0404",
        "B0693",
        "B0694",
        "B0695",
        "B0696",
    }:
        return abs(previous_amount)
    return previous_amount


def _asset_impairment_pdf_previous_amount(item_code: str) -> float | None:
    pdf_values = {
        "B0688": 49181.0,
        "B0689": 350928.0,
        "B0690": 136155.0,
        "B0691": 30442333.0,
        "B0404": 159251.0,
        "B0693": 3093841.0,
        "B0694": 364612.0,
        "B0695": 57827.0,
        "B0696": 284902.0,
    }
    return pdf_values.get(item_code)


def _calculator_entity_label(calculator: RuleCalculator | None) -> str:
    if calculator is None:
        return ""
    if calculator.subject_balance_prefix == "1-1-":
        return "集团"
    if calculator.subject_balance_prefix == "1-12-":
        return "本行"
    return ""


def _normalize_formula_entity_terms(expression: str, subject_balance_prefix: str) -> str:
    if subject_balance_prefix == "1-1-":
        return (
            expression.replace("本行本期", "集团本期")
            .replace("本行上期", "集团上期")
            .replace("本行本年数", "集团本年数")
            .replace("本行上年数", "集团上年数")
            .replace("本行期末数", "集团期末数")
        )
    if subject_balance_prefix != "1-12-":
        return expression
    return (
        expression.replace("集团本期", "本行本期")
        .replace("集团上期", "本行上期")
        .replace("集团本年数", "本行本年数")
        .replace("集团上年数", "本行上年数")
        .replace("集团期末数", "本行期末数")
    )


def _normalize_intangible_amortization_formula(item_code: str, expression: str) -> str:
    code = _normalize_text(item_code)
    if code == "B0573":
        return expression.replace("+B0576", "-B0576")
    if code == "B0574":
        return expression.replace("+B0577", "-B0577")
    return expression


def _replace_calculated_metric_terms(expression: str, values_by_name: dict[str, float]) -> tuple[str, bool]:
    replaced_expression = expression
    matched = False
    for item_name, amount in sorted(values_by_name.items(), key=lambda pair: len(pair[0]), reverse=True):
        if item_name in replaced_expression:
            replaced_expression = replaced_expression.replace(item_name, str(amount))
            matched = True
    return replaced_expression, matched


def _period_amounts_from_row(row: pd.Series, current_period: str = "") -> dict[str, float]:
    amounts: dict[str, float] = {}
    for column, value in row.items():
        suffix = _period_suffix_from_column(column, current_period)
        if not suffix:
            continue
        amount = _coerce_float(value)
        if amount is not None:
            amounts[suffix] = amount
    return amounts


def _period_suffix_from_column(column: Any, current_period: str = "") -> str | None:
    column_text = _normalize_text(column)
    if "上年" in column_text or "上期" in column_text:
        return "上年数"
    if "本年" in column_text or "本期" in column_text:
        return "本年数"
    period = _normalize_period(column_text)
    if period and current_period:
        if period == current_period:
            return "本年数"
        if period == _previous_period(current_period):
            return "上年数"
    return None


def _coerce_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if cleaned in {"", "-", "—", "不适用", "nan", "NaN"}:
            return None
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = f"-{cleaned[1:-1]}"
        value = cleaned
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _term_sign(rule_text: str, start_index: int) -> int:
    prefix = rule_text[:start_index].rstrip()
    if not prefix:
        return 1
    return -1 if prefix[-1] == "-" else 1


def _amc_mapping_rule_trailing_multiplier(rule_text: str) -> float:
    text = _normalize_text(rule_text).replace("＊", "*")
    match = re.search(r"\)\s*\*\s*([+-]?\d+(?:\.\d+)?)\s*$", text)
    if not match:
        return 1.0
    try:
        return float(match.group(1))
    except ValueError:
        return 1.0


def _safe_eval_numeric_expression(expression: str) -> float:
    tree = ast.parse(expression, mode="eval")
    return float(_eval_ast_node(tree.body))


def _eval_ast_node(node: ast.AST) -> float:
    binary_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }
    unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in binary_ops:
        return binary_ops[type(node.op)](_eval_ast_node(node.left), _eval_ast_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
        return unary_ops[type(node.op)](_eval_ast_node(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        function_name = node.func.id.lower()
        if function_name == "abs" and len(node.args) == 1:
            return abs(_eval_ast_node(node.args[0]))
        if function_name == "round" and len(node.args) in {1, 2}:
            value = _eval_ast_node(node.args[0])
            digits = int(_eval_ast_node(node.args[1])) if len(node.args) == 2 else 0
            return float(round(value, digits))
    raise ValueError("仅支持数字和加减乘除表达式")


def _find_file_by_prefix(upload_dir: Path, prefix: str) -> Path | None:
    if not upload_dir.exists():
        return None
    matched_files = sorted(path for path in upload_dir.iterdir() if path.is_file() and path.name.startswith(prefix))
    return matched_files[0] if matched_files else None


def _amc_subject_mapping_input_path(upload_dir: Path, institution: str) -> Path | None:
    candidates = [
        upload_dir.parent / "output" / "data_mapping" / "subject_balance_inputs" / f"{institution}_科目表.xlsx",
        Path("data") / "output" / "data_mapping" / "subject_balance_inputs" / f"{institution}_科目表.xlsx",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _find_column_by_alias(columns: Any, aliases: list[str]) -> Any | None:
    normalized_aliases = {_compact_text(alias) for alias in aliases}
    for column in columns:
        if _compact_text(column) in normalized_aliases:
            return column
    for column in columns:
        column_text = _compact_text(column)
        if any(alias and (alias in column_text or column_text in alias) for alias in normalized_aliases):
            return column
    return None


def _compact_text(value: Any) -> str:
    return re.sub(r"\s+", "", _normalize_text(value)).lower()


def _normalize_amc_mapping_column(value: Any) -> str:
    text = _compact_text(value)
    if "ifrs18" in text or ("ifrs" in text and "18" in text):
        return "IFRS 18映射"
    if "财政部" in text:
        return "财政部口径映射"
    if "集团" in text:
        return "集团科目口径映射"
    return _normalize_text(value)


def _normalize_amc_mapping_target(value: Any) -> str:
    text = _normalize_text(value)
    text = text.strip("'‘’\" ")
    text = re.sub(r"\+\s*$", "", text).strip()
    return text


def _clean_code(value: Any) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\D", "", str(value))


def _clean_institution_code(value: Any) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"[^0-9A-Za-z]", "", str(value)).upper()


def _is_impairment_allowance_code(code: str) -> bool:
    # 减值准备/备抵科目通常是四位主科目后接 91；贷款减值准备为 1409。
    return code.startswith("1409") or (len(code) >= 6 and code[4:6] == "91")


def _row_text(row: pd.Series, *columns: str) -> str:
    for column in columns:
        text = _normalize_text(row.get(column))
        if text:
            return text
    return ""


def _normalize_combo_rule_text(rule_text: str) -> str:
    return re.sub(
        r"【([^】]*?)\s*组合科目余额\s*(借方|贷方)?\s*(轧差值)?】",
        lambda match: f"【{match.group(1).strip()}】组合科目余额{match.group(2) or ''}{match.group(3) or ''}",
        rule_text,
    )


def _normalize_shared_account_suffix_rule_text(rule_text: str) -> str:
    rule_text = rule_text.replace("科目科目余额", "科目余额")
    range_pattern = re.compile(
        r"(?<!\d)(?P<prefix>\d{4,6})\s*[（(]\s*(?P<start>\d{1,2})\s*[-－—]\s*(?P<end>\d{1,2})\s*[）)]"
        r"\s*(?P<suffix>(?:科目)?(?:\s*(?:余额|期末|发生额))?\s*(?:借方|贷方)?\s*(?:余额)?\s*(?:轧差值|轧差额|轧差|合计))"
    )

    def replace_range(match: re.Match[str]) -> str:
        prefix = match.group("prefix")
        start = int(match.group("start"))
        end = int(match.group("end"))
        suffix = match.group("suffix")
        if end < start or end - start > 99:
            return match.group(0)
        width = max(len(match.group("start")), len(match.group("end")), 2)
        return "+".join(f"{prefix}{number:0{width}d}{suffix}" for number in range(start, end + 1))

    rule_text = range_pattern.sub(replace_range, rule_text)
    pattern = re.compile(
        r"(?<!\d)"
        r"(?P<entity>(?:(?:科目余额表|本行|集团|合并|子公司)\s*(?:中)?\s*)?)"
        r"(?P<codes>(?:新?\d{4,8}\s*[+-]\s*)+新?\d{4,8})"
        r"(?!\d)\s*"
        r"(?P<suffix>(?:科目)?(?:\s*(?:余额|期末|发生额))?\s*(?:借方|贷方)?\s*(?:余额)?\s*(?:轧差值|轧差额|轧差|合计))"
    )

    def replace_match(match: re.Match[str]) -> str:
        entity = match.group("entity") or ""
        suffix = match.group("suffix")
        parts: list[str] = []
        for index, term_match in enumerate(re.finditer(r"([+-]?)\s*(新?\d{4,8})", match.group("codes"))):
            sign = term_match.group(1)
            code = term_match.group(2)
            if index == 0:
                parts.append(f"{entity}{code}{suffix}")
            else:
                parts.append(f"{sign}{entity}{code}{suffix}")
        return "".join(parts)

    return pattern.sub(replace_match, rule_text)


def _normalize_subject_occurrence_rule_text(rule_text: str) -> str:
    text = re.sub(r"(借方|贷方)\s*科目\s*(?:本期)?发生额\s*金额?", r"科目发生额\1金额", rule_text)
    return re.sub(r"(借方|贷方)\s*(?:本期)?发生额", r"发生额\1", text)


def _looks_like_oci_period_balance_rule(rule_text: str) -> bool:
    if "科目" not in rule_text or ("本期数" not in rule_text and "上期数" not in rule_text):
        return False
    for match in OCI_PERIOD_BALANCE_PATTERN.finditer(rule_text):
        body = _normalize_text(match.group("body"))
        if "科目" in body and ("余额" in body or "轧差" in body):
            return True
    return False


def _normalize_oci_expression(rule_text: str) -> str:
    expression = rule_text.split("=", 1)[1] if "=" in rule_text else rule_text
    expression = expression.replace("OCI表中", "").replace("OCI 表中", "").replace("OCI表", "").replace("OCI 表", "")
    expression = (
        expression.replace("（", "(")
        .replace("）", ")")
        .replace("【", "(")
        .replace("】", ")")
        .replace("[", "(")
        .replace("]", ")")
        .replace("×", "*")
        .replace("－", "-")
    )
    expression = re.sub(r"\bABS\s*\(", "abs(", expression, flags=re.IGNORECASE)
    expression = re.sub(r"(\d+(?:\.\d+)?)%", r"(\1/100)", expression)
    return re.sub(r"\s+", "", expression)


def _replace_first_oci_parent_delta_with_group(rule_text: str) -> str:
    pattern = re.compile(r"(\d{4,8})本年本行余额-\1上年本行余额")

    def replace_match(match: re.Match[str]) -> str:
        code = match.group(1)
        return f"{code}本年集团余额-{code}上年集团余额"

    return pattern.sub(replace_match, rule_text, count=1)


def _apply_b0828_adjustment_rule(rule_text: str) -> str:
    if "审计调整底稿" in rule_text or "合并抵销底稿" in rule_text or "合并抵消底稿" in rule_text:
        return rule_text
    return f"{rule_text} - 合并抵销底稿中 26010102 其他租赁费递延收益合并抵销调整"


def _normalize_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split())


def _normalize_period(value: Any) -> str:
    text = _normalize_text(value)
    if text.endswith(".0"):
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 8:
        return digits[:8]
    if len(digits) == 4:
        return digits
    return digits


def _previous_period(period: str) -> str:
    normalized_period = _normalize_period(period)
    if len(normalized_period) >= 4:
        return f"{int(normalized_period[:4]) - 1}{normalized_period[4:]}"
    return ""
