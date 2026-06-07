from __future__ import annotations

import ast
import operator
import re
from pathlib import Path
from typing import Any

import pandas as pd


ACCOUNT_RULE_PATTERN = re.compile(
    r"(?<!\d)(?:(科目余额表|本行|集团|合并)\s*(?:中)?\s*)?(\d{4,8})(?!\d)\s*(?=(?:科目|余额|期末|发生额|借方|贷方))(?:科目)?(?:\s*(余额|期末|发生额))?\s*(借方|贷方)?\s*(?:余额)?\s*(轧差值|轧差额|轧差|合计)?"
)
COMBO_RULE_PATTERN = re.compile(r"【([^】]+)】\s*组合科目余额\s*(借方|贷方)?\s*(轧差值)?")
DETAIL_POSITIVE_BALANCE_PATTERN = re.compile(
    r"(?<!\d)(\d{4,8})(?!\d)\s*科目下\s*(?:期末)?\s*(借方|贷方)余额为正(?:的明细)?科目(?:余额)?合计"
)
EXPLICIT_ADJUSTMENT_PATTERN = re.compile(r"([+-])\s*(母行|子公司|合并抵[销消])(?:审计调整)?底稿中\s*(\d{4,8})")
ADJUSTMENT_AMOUNT_PATTERN = re.compile(
    r"(母行|子公司|合并抵[销消])(?:审计调整)?底稿中\s*(\d{4,8})\s*科目(?:调整)?金额"
)
OCI_RULE_PATTERN = re.compile(r"(新?\d{4,8})\s*(本年|上年)\s*(集团|本行)\s*余额")
CONSOLIDATION_FIRST_AMOUNT_PATTERN = re.compile(r"合并抵[销消]表中\s*(\d{4,8})\s*科目首笔金额")
CONSOLIDATION_IFRS_MAPPING_AMOUNT_PATTERN = re.compile(
    r"合并抵[销消]底稿\s*IFRS\s*mapping\s*=\s*([^+\-*/()（）]+?)\s*本年末金额"
)
CONSOLIDATION_PERIOD_AMOUNT_PATTERN = re.compile(
    r"合并抵[销消]底稿中\s*(?:新)?(\d{4,8})\s*科目\s*(本年|上年)(?:末)?余额"
)
SUBSIDIARY_OWNERSHIP_AMOUNT_PATTERN = re.compile(
    r"子公司\s*(\d{4,8})\s*科目\s*发生额\s*贷方\s*\*\s*\(\s*1\s*-\s*子公司持股比例\s*\)"
)
PERPETUAL_BOND_INTEREST_PATTERN = re.compile(
    r"(?:1-9-20251231)?永续债明细表(?:的)?每支永续债发行金额\*初始利率之和|永续债明细表发行金额乘初始利率之和"
)
AMOUNT_UNIT_DIVISOR = 1000.0

CODE_COLUMNS_BY_LENGTH = {
    4: "level1_code",
    6: "level2_code",
    8: "level3_code",
}


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

    def calculate(self, rules_df: pd.DataFrame) -> pd.DataFrame:
        if rules_df is None or rules_df.empty:
            return pd.DataFrame(index=rules_df.index if rules_df is not None else None)

        result = pd.DataFrame(index=rules_df.index)
        result["计算金额"] = pd.NA
        result["计算状态"] = "未计算"
        result["计算说明"] = ""

        values_by_name: dict[str, float] = dict(self.initial_values)
        pending_indexes: list[int] = []

        for index, row in rules_df.iterrows():
            rule_text = _row_text(row, "指标加工规则", "加工规则")
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
                _register_calculated_row_value(values_by_name, row, amount, self.report_period)
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
                    _register_calculated_row_value(values_by_name, row, amount, self.report_period)
                pending_indexes.remove(index)
                changed = True
            if not changed:
                break

        return result

    def _calculate_independent_rule(self, row: pd.Series) -> tuple[float | None, str, str]:
        data_source = _row_text(row, "指标数据来源", "数据来源")
        rule_text = _row_text(row, "指标加工规则", "加工规则")
        item_code = _row_text(row, "指标编码")

        default_amount = _parse_default_amount(data_source, rule_text)
        if default_amount is not None:
            return default_amount, "已计算", "按默认值计算"

        if "OCI" in rule_text or "OCI表" in rule_text:
            rule_text = self._normalize_oci_rule_for_item(rule_text, item_code)
            amount = self._calculate_oci_rule(rule_text)
            if amount is not None:
                return amount, "已计算", "按 OCI 表余额规则计算"
            return None, "未计算", "OCI 表规则未匹配到账户或基础文件"

        if ADJUSTMENT_AMOUNT_PATTERN.search(rule_text):
            replaced_expression, matched_adjustment = self._replace_adjustment_amount_terms_in_expression(rule_text)
            if matched_adjustment and not re.search(r"[\u4e00-\u9fff]", replaced_expression):
                try:
                    amount = _safe_eval_numeric_expression(replaced_expression)
                except Exception:
                    amount = None
                if amount is not None:
                    return amount, "已计算", "按审计调整底稿金额计算，单位转换为千元"

        if "科目" in rule_text:
            if item_code == "B0828":
                rule_text = _apply_b0828_adjustment_rule(rule_text)
            amount = self._calculate_subject_balance_rule(rule_text)
            if amount is not None:
                return amount, "已计算", self._subject_rule_message()
            return None, "未计算", "科目余额规则未匹配到账户或基础文件"

        return None, "未计算", "等待指标公式或暂不支持的规则类型"

    def _subject_rule_message(self) -> str:
        if self.subject_balance_prefix == "1-12-":
            return "按本行科目余额表和本行审计调整底稿计算，单位转换为千元"
        if self.subject_balance_prefix == "1-5-":
            return "按子公司科目余额表和子公司审计调整底稿计算，单位转换为千元"
        return "按科目余额表、审计调整底稿和合并抵消底稿计算，单位转换为千元"

    def _calculate_formula_rule(
        self,
        row: pd.Series,
        values_by_name: dict[str, float],
    ) -> tuple[float | None, str, str]:
        rule_text = _row_text(row, "指标加工规则", "加工规则")
        if not rule_text:
            return None, "未计算", "无加工规则"
        expression = _extract_formula_expression(rule_text)
        expression = expression.replace("（", "(").replace("）", ")").replace("×", "*").replace("－", "-")
        exclude_consolidation_adjustments = bool(CONSOLIDATION_IFRS_MAPPING_AMOUNT_PATTERN.search(expression))
        replaced_expression, matched_consolidation_period = _replace_consolidation_period_terms(
            expression,
            self.upload_dir,
        )
        replaced_expression, matched_subsidiary_ownership = _replace_subsidiary_ownership_terms(
            replaced_expression,
            self.upload_dir,
        )
        replaced_expression, matched_adjustment_amount = self._replace_adjustment_amount_terms_in_expression(
            replaced_expression
        )
        replaced_expression, matched_account = self._replace_subject_terms_in_expression(
            replaced_expression,
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
            or matched_subsidiary_ownership
            or matched_adjustment_amount
            or matched_account
            or matched_consolidation_ifrs
            or matched_perpetual_bond
        )
        for item_name, amount in sorted(values_by_name.items(), key=lambda pair: len(pair[0]), reverse=True):
            if item_name in replaced_expression:
                replaced_expression = replaced_expression.replace(item_name, str(amount))
                matched_name = True

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

        for match in ADJUSTMENT_AMOUNT_PATTERN.finditer(expression):
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
        include_consolidation_adjustments: bool = True,
    ) -> tuple[str, bool]:
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

    def _calculate_subject_balance_rule(self, rule_text: str) -> float | None:
        rule_text = _normalize_combo_rule_text(rule_text)
        combo_matches = list(COMBO_RULE_PATTERN.finditer(rule_text))
        normal_rule_text = COMBO_RULE_PATTERN.sub("", rule_text)
        normal_rule_text = EXPLICIT_ADJUSTMENT_PATTERN.sub("", normal_rule_text)
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
            self.subject_balance_prefix != "1-5-"
            and ("审计调整底稿" in rule_text or "合并抵销底稿" in rule_text or "合并抵消底稿" in rule_text)
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
            elif entity == "科目余额表":
                amount = _subject_amount(subject_df, code, side, is_net, amount_type)
            elif explicit_adjustments:
                amount = _subject_amount(subject_df, code, side, is_net, amount_type)
            else:
                amount = self._account_amount(code, side, is_net, amount_type)
            total += sign * amount

        if explicit_adjustments:
            total += self._explicit_adjustment_amount(rule_text)

        if matched_codes and all(_is_impairment_allowance_code(code) for code in matched_codes):
            total = -total

        return total / AMOUNT_UNIT_DIVISOR

    def _account_amount(
        self,
        code: str,
        side: str,
        is_net: bool,
        amount_type: str = "余额",
        include_consolidation_adjustments: bool = True,
    ) -> float:
        subject_amount = _subject_amount(self._load_subject_balance_df(), code, side, is_net, amount_type)
        adjustment_df = self._load_adjustment_df()
        if not include_consolidation_adjustments and "source" in adjustment_df.columns:
            adjustment_df = adjustment_df.loc[adjustment_df["source"] != "consolidation"]
        adjustment_amount = _adjustment_amount(adjustment_df, code)
        if _is_income_account_code(code) and side == "贷方":
            return subject_amount - adjustment_amount
        return subject_amount + adjustment_amount

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
            total += sign * abs(float(matched_df["amount"].sum()))
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


def _subject_amount(subject_df: pd.DataFrame, code: str, side: str, is_net: bool, amount_type: str = "余额") -> float:
    matched_df = _match_account_rows(subject_df, code)
    debit_column = "period_debit" if amount_type == "发生额" else "ending_debit"
    credit_column = "period_credit" if amount_type == "发生额" else "ending_credit"
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
    amounts = matched_df["amount"].copy()
    if _is_impairment_allowance_code(code):
        amounts = -amounts
    return float(amounts.sum())


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
        }
    ).loc[lambda frame: frame["account_code"] != ""]


def _adjustment_institution_codes(df: pd.DataFrame) -> pd.Series:
    for column in ("机构代码", "机构代码.1", "机构编号", "机构号"):
        if column in df.columns:
            return df[column].map(_clean_code)
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
    return float(matched_df[column].sum())


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

    expression = _extract_formula_expression(rule_text)
    expression = expression.replace("（", "(").replace("）", ")").replace("×", "*").replace("－", "-")
    if "OCI" in expression or "OCI表" in expression:
        return False
    if "合并抵销表中" in expression or "合并抵消表中" in expression:
        return False
    if not re.search(r"[+\-*/]", expression):
        return False

    if CONSOLIDATION_PERIOD_AMOUNT_PATTERN.search(expression):
        return True
    if SUBSIDIARY_OWNERSHIP_AMOUNT_PATTERN.search(expression):
        return True

    if re.search(r"\b[A-Z]\d{3,}\b", expression):
        return True

    remaining_text = _normalize_combo_rule_text(expression)
    remaining_text = COMBO_RULE_PATTERN.sub("", remaining_text)
    remaining_text = CONSOLIDATION_PERIOD_AMOUNT_PATTERN.sub("", remaining_text)
    remaining_text = SUBSIDIARY_OWNERSHIP_AMOUNT_PATTERN.sub("", remaining_text)
    remaining_text = EXPLICIT_ADJUSTMENT_PATTERN.sub("", remaining_text)
    remaining_text = DETAIL_POSITIVE_BALANCE_PATTERN.sub("", remaining_text)
    remaining_text = ACCOUNT_RULE_PATTERN.sub("", remaining_text)
    remaining_text = (
        remaining_text.replace("审计调整", "")
        .replace("合并抵销", "")
        .replace("合并抵消", "")
    )
    remaining_text = re.sub(r"[\s+\-*/=()（）,，、\d.]+", "", remaining_text)
    return bool(re.search(r"[\u4e00-\u9fff]", remaining_text))


def _register_calculated_value(values_by_name: dict[str, float], item_name: str, amount: float) -> None:
    values_by_name[item_name] = amount
    for suffix in ("合计", "总计"):
        values_by_name[f"{item_name}{suffix}"] = amount
    if item_name.endswith("总额"):
        prefix = item_name.removesuffix("总额")
        values_by_name[f"{prefix}合计"] = amount
        values_by_name[f"{prefix}总计"] = amount


def _register_calculated_row_value(
    values_by_name: dict[str, float],
    row: pd.Series,
    amount: float,
    current_period: str = "",
) -> None:
    item_name = _row_text(row, "指标名称")
    item_code = _row_text(row, "指标编码")
    keys = [key for key in (item_name, item_code) if key]

    for key in keys:
        values_by_name[key] = amount
        values_by_name[f"{key}本年数"] = amount
        values_by_name[f"{key}期末数"] = amount

    if item_name:
        _register_calculated_value(values_by_name, item_name, amount)

    for suffix, suffix_amount in _period_amounts_from_row(row, current_period).items():
        for key in keys:
            values_by_name[f"{key}{suffix}"] = suffix_amount


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
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "abs" and len(node.args) == 1:
        return abs(_eval_ast_node(node.args[0]))
    raise ValueError("仅支持数字和加减乘除表达式")


def _find_file_by_prefix(upload_dir: Path, prefix: str) -> Path | None:
    if not upload_dir.exists():
        return None
    matched_files = sorted(path for path in upload_dir.iterdir() if path.is_file() and path.name.startswith(prefix))
    return matched_files[0] if matched_files else None


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
