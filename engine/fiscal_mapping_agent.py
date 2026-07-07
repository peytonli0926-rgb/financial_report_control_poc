from __future__ import annotations

import re
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd
from openpyxl.styles import PatternFill


OUTPUT_COLUMNS = [
    "序号",
    "FSLine",
    "NoteLine",
    "Grouping_Consolidated",
    "Grouping_Standalone",
    "Confidence",
    "MappingBasis",
    "ReviewFlag",
    "AlternativeGrouping",
    "CompanyType",
]


@dataclass(frozen=True)
class FiscalMappingAgentConfig:
    company_type: str = "银行类"
    report_context: str = "合并及单体"
    use_history: bool = True
    use_cloud_agent: bool = True
    fiscal_requirement_items: tuple[str, ...] = ()


@dataclass(frozen=True)
class MappingRule:
    keywords: tuple[str, ...]
    consolidated: str
    standalone: str
    confidence: int
    basis: str
    alternatives: tuple[str, ...] = ()
    company_types: tuple[str, ...] = ()


class CloudAuditMappingClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("FRC_AUDIT_AGENT_API_KEY", "").strip()
        self.base_url = os.getenv("FRC_AUDIT_AGENT_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
        self.model = os.getenv("FRC_AUDIT_AGENT_MODEL", "").strip()
        self.timeout_seconds = int(os.getenv("FRC_AUDIT_AGENT_TIMEOUT_SECONDS", "90"))

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    def map_lines(
        self,
        rows: list[dict[str, str]],
        company_type: str,
        report_context: str,
        fiscal_requirement_items: tuple[str, ...] = (),
    ) -> dict[int, dict[str, object]]:
        if not self.enabled or not rows:
            return {}

        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一个金融行业20年以上经验的审计师，负责把上传的 FSLine/NoteLine 映射到财政部报表项目。"
                        "必须基于中国企业会计准则、金融企业财务报表列报经验、合并填报与单体填报口径做判断。"
                        "你必须为输入的每一行都给出映射结果，禁止漏行，禁止返回空字符串。"
                        "如果某行在某一口径确实不适用，使用 '-'，不要留空。"
                        "只能返回 JSON，不要返回 Markdown、解释文本或代码块。"
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": "为每一行生成合并口径列4和单体口径列5财政部报表项目。",
                            "company_type": company_type,
                            "report_context": report_context,
                            "candidate_fiscal_items": list(fiscal_requirement_items),
                            "requirements": [
                                "保留原始序号 row_id。",
                                "如果合并口径与单体口径相同，也要分别填写。",
                                "必须优先从 candidate_fiscal_items 中选择财政部报表项目；只有确实没有合适候选项时，才可使用审计经验补充项目。",
                                "必须先判断 FSLine 的报表大类，再用 NoteLine 判断明细归集；NoteLine 中出现资产、负债名称时，不得覆盖 FSLine 已经明确的损益类、权益类大类。",
                                "输出项目必须严格适配 candidate_fiscal_items 反映的准则版本：如果候选项不包含带星号项目，不得输出 *交易性金融资产、*债权投资、*其他债权投资、*其他权益工具投资、*信用减值损失、*其他资产减值损失。",
                                "如果候选项不包含带星号项目，应按旧金融工具准则映射：*交易性金融资产改为以公允价值计量且其变动计入当期损益的金融资产，*债权投资改为持有至到期投资，*其他债权投资和*其他权益工具投资改为可供出售金融资产，*信用减值损失和*其他资产减值损失改为资产减值损失。",
                                "如果 FSLine 是利息收入或利息支出，资产公司合并口径优先映射为（七）其他业务成本，单体口径优先映射为（三）利息净支出；不要映射到存放同业款项、拆出资金、买入返售金融资产、吸收存款等资产负债表项目。",
                                "如果 FSLine 是投资收益，所有投资收益明细优先映射为（三）投资收益；不要因 NoteLine 包含长期股权投资、交易性金融资产、可供出售金融资产、债权投资而映射到资产负债表项目。",
                                "如果 FSLine 是公允价值变动损益，所有明细优先映射为（四）公允价值变动收益；不要映射到交易性金融资产或交易性金融负债。",
                                "如果 FSLine 是业务及管理费，所有费用明细优先映射为（二）业务及管理费；不要因折旧、摊销、无形资产、长期待摊费用等词映射到资产项目。",
                                "如果 FSLine 是资产减值损失或信用减值损失，按损益表项目映射：信用风险相关明细映射为（三）*信用减值损失，非信用资产减值明细映射为（四）*其他资产减值损失；不要映射到被减值的资产负债表项目。",
                                "如果 FSLine 是所得税费用，映射为减：所得税费用；如果 FSLine 是营业外支出，映射为减：营业外支出；如果 FSLine 是少数股东损益，映射为少数股东损益。",
                                "必须为每一行返回 consolidated 和 standalone，不允许缺失、不允许空字符串。",
                                "如果某一口径不适用，填写 '-'。",
                                "如果不确定，仍然给出最可能映射并把 confidence 降低到 70 以下。",
                                "reason 必须说明映射依据。",
                                "alternative 可为空字符串。",
                                "资产类项目通常映射为货币资金、存放中央银行款项、存放同业款项、拆出资金、交易性金融资产、买入返售金融资产、应收款项、发放贷款和垫款、抵债资产、可供出售金融资产、长期股权投资、固定资产、无形资产、持有至到期投资、其他资产等。",
                                "负债类项目通常映射为短期借款、向中央银行借款、应付利息、拆入资金、卖出回购金融资产款、交易性金融负债、吸收存款、应付款项、应付职工薪酬、应交税费、其他负债、长期借款、应付债券、预计负债、递延所得税负债等。",
                                "权益类项目通常映射为股本、资本公积、其他权益工具、盈余公积、其他综合收益、未分配利润、少数股东权益。",
                                "损益类项目通常映射为主营业务净收入、利息净支出、中间业务净收入、手续费及佣金净收入、其他业务收入、公允价值变动收益、投资收益、营业外收入、税金及附加、其他业务成本、业务及管理费、资产减值损失、所得税费用、少数股东损益。",
                                "参考映射示例：现金/银行存款/定期存款/其他货币资金 -> 货币资金；存放中央银行款项 -> 存放中央银行款项；存放同业款项 -> 货币资金；存出保证金 -> 其他资产；结算备付金 -> 货币资金；拆出资金 -> 拆出资金。",
                                "参考映射示例：交易性金融资产-债券投资/基金投资/权益投资/其他投资，如果 candidate_fiscal_items 包含 *交易性金融资产，则映射为 *交易性金融资产；否则旧准则口径映射为以公允价值计量且其变动计入当期损益的金融资产。衍生工具/利率衍生工具/权益衍生工具/其他衍生工具也遵循同一准则版本判断；买入返售金融资产-证券/票据/贷款/其他/减值准备 -> 买入返售金融资产。",
                                "参考映射示例：应收票据/应收账款 -> 应收款项；应收款项类投资及其减值准备 -> 应收款项类金融资产；发放贷款和垫款及其减值准备 -> 发放贷款和垫款；应收利息及其明细 -> 应收利息；其他应收款 -> 其他资产。",
                                "参考映射示例：可供出售金融资产及其股票/债券/其他投资/减值准备 -> 可供出售金融资产；长期股权投资及联营合营企业/其他股权投资/减值准备 -> 长期股权投资；固定资产原值/累计折旧/减值准备/清理/在建工程 -> 固定资产；无形资产及摊销/减值准备 -> 无形资产。",
                                "参考映射示例：短期借款 -> 短期借款；向中央银行借款 -> 向中央银行借款；应付利息-向中央银行借款 -> 应付利息；拆入资金 -> 拆入资金；卖出回购金融资产及证券/票据/贷款 -> 卖出回购金融资产款；交易性金融负债/衍生金融负债 -> *交易性金融负债。",
                                "参考映射示例：应付账款/预收款项/应付手续费及佣金/应付分保账款/应付赔付款/应付保单红利 -> 应付款项；应付职工薪酬及工资/福利/其他 -> 应付职工薪酬；应交税费及增值税/营业税/所得税/其他 -> 应交税费；应付利息 -> 其他负债；长期借款 -> 长期借款；应付债券 -> 应付债券；预计负债 -> 预计负债。",
                                "参考映射示例：实收资本 -> 股本；资本公积 -> 资本公积；其他权益工具 -> 其他权益工具；盈余公积 -> 盈余公积；外币会计报表折算差额 -> 其他综合收益；未分配利润/利润分配 -> 未分配利润；少数股东权益 -> 少数股东权益。",
                                "参考映射示例：利息收入各明细在合并口径通常可归入（七）其他业务成本，单体口径归入（三）利息净支出；手续费及佣金收入各明细合并口径归入（二）中间业务净收入，单体口径归入（二）手续费及佣金净收入；投资收益各明细归入（三）投资收益；公允价值变动损益各明细归入（五）公允价值变动收益。",
                                "参考映射示例：业务及管理费各明细 -> （二）业务及管理费；资产减值损失各明细合并口径多为（四）*其他资产减值损失，单体口径多为（五）资产减值损失；所得税费用 -> 减：所得税费用；营业外收入 -> 加：营业外收入；营业外支出 -> 减：营业外支出。",
                            ],
                            "output_schema": {
                                "items": [
                                    {
                                        "row_id": "number",
                                        "consolidated": "string",
                                        "standalone": "string",
                                        "confidence": "integer 0-100",
                                        "reason": "string",
                                        "alternative": "string",
                                    }
                                ]
                            },
                            "rows": rows,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return {}

        content = (
            response_payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        parsed = _parse_cloud_agent_json(content)
        decisions: dict[int, dict[str, object]] = {}
        for item in parsed.get("items", []):
            try:
                row_id = int(item.get("row_id"))
            except (TypeError, ValueError):
                continue
            consolidated = clean_cell(item.get("consolidated", ""))
            standalone = clean_cell(item.get("standalone", "")) or consolidated
            if not consolidated:
                continue
            try:
                confidence = int(float(item.get("confidence", 70)))
            except (TypeError, ValueError):
                confidence = 70
            decisions[row_id] = {
                "consolidated": consolidated,
                "standalone": standalone,
                "confidence": max(0, min(confidence, 100)),
                "basis": f"云端审计 Agent：{clean_cell(item.get('reason', '')) or '基于FSLine/NoteLine和公司属性判断'}",
                "alternatives": clean_cell(item.get("alternative", "")),
            }
        return decisions


class FiscalReportMappingAgent:
    """Local audit-style agent for fiscal report item mapping.

    It is intentionally deterministic: confirmed mappings and explicit rules win,
    while judgement-based fallbacks are flagged for review.
    """

    def __init__(self, config: FiscalMappingAgentConfig, confirmed_mapping_path: str | Path | None = None) -> None:
        self.config = config
        self.confirmed_mapping_path = Path(confirmed_mapping_path) if confirmed_mapping_path else None
        self.confirmed_mappings = self._load_confirmed_mappings(self.confirmed_mapping_path)
        self.cloud_client = CloudAuditMappingClient()

    def map_dataframe(self, source_df: pd.DataFrame) -> pd.DataFrame:
        normalized_df = normalize_source_dataframe(source_df)
        normalized_rows: list[dict[str, object]] = []
        pending_cloud_rows: list[dict[str, str]] = []
        for index, row in normalized_df.iterrows():
            fs_line = clean_cell(row.get("FSLine", ""))
            note_line = clean_cell(row.get("NoteLine", ""))
            source_seq = clean_cell(row.get("???", "")) or clean_cell(row.get("序号", ""))
            source_grouping = clean_cell(row.get("SourceGrouping_Consolidated", ""))
            source_standalone = clean_cell(row.get("SourceGrouping_Standalone", ""))
            source_ifrs18 = clean_cell(row.get("SourceGrouping_IFRS18", ""))
            source_has_grouping = bool(row.get("SourceHasGrouping_Consolidated", False))
            source_has_standalone = bool(row.get("SourceHasGrouping_Standalone", False))
            source_has_ifrs18 = bool(row.get("SourceHasGrouping_IFRS18", False))
            source_decision = None
            source_provided = False
            if self.config.report_context == "group_rule_agent_first" and source_has_grouping:
                source_decision = mapping_decision(
                    source_grouping,
                    source_standalone or source_grouping,
                    99,
                    "集团科目口径：采用上传科目表中的集团科目口径映射列",
                )
                source_decision["locked"] = True
                source_provided = True
            elif (
                source_has_ifrs18
                and is_ifrs18_requirement(self.config.fiscal_requirement_items)
            ):
                source_decision = mapping_decision(
                    source_ifrs18,
                    source_ifrs18,
                    99,
                    f"{self.config.company_type} IFRS 18 口径：采用上传科目表中的 IFRS 18 映射列",
                )
                source_decision["locked"] = True
                source_provided = True
            elif (
                source_has_standalone
                and is_mof_requirement(self.config.fiscal_requirement_items)
            ):
                source_decision = mapping_decision(
                    source_standalone,
                    source_standalone,
                    99,
                    f"{self.config.company_type}财政部口径：采用上传科目表中的财政部口径映射列",
                )
                source_decision["locked"] = True
                source_provided = True
            confirmed = self._confirmed_mapping_for(fs_line, note_line, clean_cell(row.get("SubjectCode", "")), source_seq)
            row_id = index + 1
            normalized_rows.append(
                {
                    "row_id": row_id,
                    "seq": source_seq or row_id,
                    "fs_line": fs_line,
                    "note_line": note_line,
                    "subject_code": clean_cell(row.get("SubjectCode", "")),
                    "decision": source_decision or (self._decision_from_confirmed(confirmed) if confirmed else None),
                    "source_provided": source_provided,
                }
            )
            if confirmed is None and source_decision is None:
                pending_cloud_rows.append({"row_id": row_id, "FSLine": fs_line, "NoteLine": note_line})

        cloud_decisions: dict[int, dict[str, object]] = {}
        if self.config.use_cloud_agent and self.cloud_client.enabled and pending_cloud_rows:
            cloud_decisions = self.cloud_client.map_lines(
                pending_cloud_rows,
                company_type=self.config.company_type,
                report_context=self.config.report_context,
                fiscal_requirement_items=self.config.fiscal_requirement_items,
            )

        output_rows: list[dict[str, object]] = []
        for row in normalized_rows:
            if row["decision"]:
                if row.get("source_provided") or (isinstance(row["decision"], dict) and row["decision"].get("locked")):
                    decision = row["decision"]
                else:
                    decision = enforce_fsline_priority_decision(
                        row["decision"],
                        str(row["fs_line"]),
                        str(row["note_line"]),
                        self.config.company_type,
                        self.config.fiscal_requirement_items,
                    )
            else:
                decision = cloud_decisions.get(int(row["row_id"])) or self.map_line(
                    str(row["fs_line"]),
                    str(row["note_line"]),
                    allow_confirmed=False,
                )
                decision = enforce_fsline_priority_decision(
                    decision,
                    str(row["fs_line"]),
                    str(row["note_line"]),
                    self.config.company_type,
                    self.config.fiscal_requirement_items,
                )
            output_rows.append(
                {
                    "序号": row["seq"],
                    "FSLine": row["fs_line"],
                    "NoteLine": row["note_line"],
                    "Grouping_Consolidated": decision["consolidated"],
                    "Grouping_Standalone": decision["standalone"],
                    "Confidence": decision["confidence"],
                    "MappingBasis": decision["basis"],
                    "ReviewFlag": "否" if int(decision["confidence"]) >= 85 else "是",
                    "AlternativeGrouping": decision["alternatives"],
                    "CompanyType": self.config.company_type,
                }
            )
        return pd.DataFrame(output_rows, columns=OUTPUT_COLUMNS)

    def map_line(self, fs_line: str, note_line: str, allow_confirmed: bool = True) -> dict[str, object]:
        text = compact_text(f"{fs_line} {note_line}")
        confirmed = self._confirmed_mapping_for(fs_line, note_line) if allow_confirmed else None
        if confirmed:
            return align_decision_to_requirement_items(
                self._decision_from_confirmed(confirmed),
                self.config.fiscal_requirement_items,
            )

        priority_decision = fsline_priority_decision(
            fs_line,
            note_line,
            self.config.company_type,
            self.config.fiscal_requirement_items,
        )
        if priority_decision:
            return priority_decision

        if (
            self.config.company_type == "资产公司"
            and compact_text(note_line) == compact_text("以公允价值计量且其变动计入当期损益的金融资产")
        ):
            target = requirement_aligned_item(
                "*交易性金融资产",
                self.config.fiscal_requirement_items,
                "以公允价值计量且其变动计入当期损益的金融资产",
            )
            return mapping_decision(
                target,
                target,
                95,
                "资产公司模板口径：该明细项按当前合并填报要求归入对应金融资产项目",
            )

        for rule in mapping_rules():
            if rule.company_types and self.config.company_type not in rule.company_types:
                continue
            if any(compact_text(keyword) in text for keyword in rule.keywords):
                decision = {
                    "consolidated": rule.consolidated,
                    "standalone": rule.standalone,
                    "confidence": rule.confidence,
                    "basis": rule.basis,
                    "alternatives": "；".join(rule.alternatives),
                }
                return align_decision_to_requirement_items(
                    decision,
                    self.config.fiscal_requirement_items,
                )

        fs_guess = infer_from_fs_line(fs_line)
        if fs_guess:
            return {
                "consolidated": fs_guess,
                "standalone": fs_guess,
                "confidence": 72,
                "basis": "未命中明细规则，按FSLine主表项目推断，需人工复核",
                "alternatives": "其他资产；其他负债；其他综合收益",
            }

        requirement_guess = infer_from_requirement_items(fs_line, note_line, self.config.fiscal_requirement_items)
        if requirement_guess:
            return {
                "consolidated": requirement_guess,
                "standalone": requirement_guess,
                "confidence": 68,
                "basis": "未命中明确规则，按已上传合并填报要求候选项目兜底匹配，需人工复核",
                "alternatives": "",
            }

        generic_guess = generic_fallback_item(fs_line, note_line)
        if generic_guess:
            return {
                "consolidated": generic_guess,
                "standalone": generic_guess,
                "confidence": 55,
                "basis": "未命中规则和合并填报要求，按资产/负债/权益/损益关键词兜底，需人工复核",
                "alternatives": "",
            }

        return {
            "consolidated": "其他资产",
            "standalone": "其他资产",
            "confidence": 20,
            "basis": "最终兜底：无法识别具体项目，暂归入其他资产，必须人工复核",
            "alternatives": "",
        }

    @staticmethod
    def _decision_from_confirmed(confirmed: dict[str, str]) -> dict[str, object]:
        return {
            "consolidated": confirmed["consolidated"],
            "standalone": confirmed["standalone"],
            "confidence": 99,
            "basis": confirmed.get("basis", "历史人工确认映射命中"),
            "alternatives": "",
            "locked": confirmed.get("locked", False),
        }

    def _confirmed_mapping_for(self, fs_line: str, note_line: str, subject_code: str = "", source_seq: str = "") -> dict[str, str] | None:
        if not self.config.use_history:
            return None
        fs_key = compact_text(fs_line)
        note_key = compact_text(note_line)
        code_key = compact_text(subject_code)
        seq_key = compact_text(source_seq)
        company_keys = [self.config.company_type, "*"]
        candidate_keys = []
        for company_key in company_keys:
            if code_key and seq_key:
                candidate_keys.extend(
                    [
                        (fs_key, note_key, company_key, code_key, seq_key),
                        ("*", note_key, company_key, code_key, seq_key),
                    ]
                )
            if seq_key:
                candidate_keys.extend(
                    [
                        (fs_key, note_key, company_key, "", seq_key),
                        ("*", note_key, company_key, "", seq_key),
                    ]
                )
            if code_key:
                candidate_keys.extend(
                    [
                        (fs_key, note_key, company_key, code_key, ""),
                        ("*", note_key, company_key, code_key, ""),
                    ]
                )
            candidate_keys.extend(
                [
                    (fs_key, note_key, company_key, "", ""),
                    ("*", note_key, company_key, "", ""),
                ]
            )
        for key in candidate_keys:
            if key in self.confirmed_mappings:
                confirmed = dict(self.confirmed_mappings[key])
                confirmed["basis"] = "已确认映射库命中" if key[0] != "*" else "已确认映射库按NoteLine命中"
                return confirmed
        return None

    @staticmethod
    def _load_confirmed_mappings(path: Path | None) -> dict[tuple[str, str, str, str, str], dict[str, str]]:
        if not path or not path.exists():
            return {}
        try:
            df = pd.read_excel(path, sheet_name=0, dtype=object, engine="openpyxl").fillna("")
        except Exception:
            return {}

        mappings: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
        for row in normalize_confirmed_mapping_dataframe(df).to_dict("records"):
            fs_line = clean_cell(row.get("FSLine", "")) or "*"
            note_line = clean_cell(row.get("NoteLine", ""))
            company_type = clean_cell(row.get("CompanyType", "")) or "*"
            subject_code = clean_cell(row.get("SubjectCode", ""))
            source_seq = clean_cell(row.get("SourceSeq", ""))
            raw_consolidated = clean_cell(row.get("Grouping_Consolidated", ""))
            raw_standalone = clean_cell(row.get("Grouping_Standalone", ""))
            consolidated_is_blank_mapping = raw_consolidated == "__BLANK__"
            standalone_is_blank_mapping = raw_standalone == "__BLANK__"
            consolidated = "" if consolidated_is_blank_mapping else raw_consolidated
            standalone = "" if standalone_is_blank_mapping else raw_standalone
            if not standalone and not standalone_is_blank_mapping:
                standalone = consolidated
            locked = clean_cell(row.get("LockMapping", "")).lower() in {"1", "true", "yes", "y", "locked"}
            if note_line and (consolidated or consolidated_is_blank_mapping):
                mappings[(compact_text(fs_line) or "*", compact_text(note_line), company_type, compact_text(subject_code), compact_text(source_seq))] = {
                    "consolidated": consolidated,
                    "standalone": standalone,
                    "locked": locked,
                }
        return mappings



def normalize_confirmed_mapping_dataframe(df: pd.DataFrame, default_company_type: str = "") -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["SourceSeq", "SubjectCode", "FSLine", "NoteLine", "Grouping_Consolidated", "Grouping_Standalone", "CompanyType", "LockMapping"])

    source = df.copy().fillna("")
    columns = list(source.columns)
    fs_col = find_column(columns, ["FSLine", "FS Line", "报表主表项目", "报表项目"])
    note_col = find_column(columns, ["NoteLine", "Note Line", "附注明细项目", "附注明细", "模拟科目", "科目"])
    consolidated_col = find_column(columns, ["Grouping_Consolidated", "合并口径财政部报表项目", "列4", "列4合并口径财政部报表项目"])
    standalone_col = find_column(columns, ["Grouping_Standalone", "单体口径财政部报表项目", "列5", "列5单体口径财政部报表项目"])
    lock_col = find_column(columns, ["LockMapping", "Locked", "Lock"])
    subject_code_col = find_column(columns, ["SubjectCode", "\u79d1\u76ee\u7f16\u7801", "\u79d1\u76ee\u4ee3\u7801", "\u79d1\u76ee\u53f7"])
    source_seq_col = find_column(columns, ["SourceSeq", "\u5e8f\u53f7", "seq", "index"])
    company_col = find_column(columns, ["CompanyType", "公司类型", "机构类型"])

    if note_col is None and len(columns) >= 3:
        note_col = columns[2] if compact_text(columns[1]) in {"fsline", "fs"} else columns[0]
    if consolidated_col is None:
        if "Grouping" in columns:
            consolidated_col = "Grouping"
        elif len(columns) >= 4 and fs_col is not None and note_col is not None:
            consolidated_col = columns[3]
        elif len(columns) >= 2:
            consolidated_col = columns[1]
    if standalone_col is None:
        grouping_like = [column for column in columns if compact_text(column).startswith("grouping") and column != consolidated_col]
        if grouping_like:
            standalone_col = grouping_like[0]
        elif len(columns) >= 5 and fs_col is not None and note_col is not None:
            standalone_col = columns[4]
        elif len(columns) >= 3:
            standalone_col = columns[2]

    result = pd.DataFrame(
        {
            "SourceSeq": source[source_seq_col].map(clean_cell) if source_seq_col is not None else "",
            "SubjectCode": source[subject_code_col].map(clean_cell) if subject_code_col is not None else "",
            "FSLine": source[fs_col].map(clean_cell) if fs_col is not None else "",
            "NoteLine": source[note_col].map(clean_cell) if note_col is not None else "",
            "Grouping_Consolidated": source[consolidated_col].map(clean_cell) if consolidated_col is not None else "",
            "Grouping_Standalone": source[standalone_col].map(clean_cell) if standalone_col is not None else "",
            "CompanyType": source[company_col].map(clean_cell) if company_col is not None else default_company_type,
            "LockMapping": source[lock_col].map(clean_cell) if lock_col is not None else "",
        }
    )
    result["Grouping_Standalone"] = result["Grouping_Standalone"].where(result["Grouping_Standalone"] != "", result["Grouping_Consolidated"])
    result["CompanyType"] = result["CompanyType"].where(result["CompanyType"] != "", default_company_type)
    result = result[(result["NoteLine"] != "") & ((result["Grouping_Consolidated"] != "") | (result["Grouping_Consolidated"] == "__BLANK__"))].copy()
    return result.drop_duplicates(subset=["SourceSeq", "SubjectCode", "FSLine", "NoteLine", "CompanyType"], keep="last")


def update_confirmed_mapping_library(
    source: str | Path | BytesIO | BinaryIO,
    library_path: str | Path,
    company_type: str = "",
) -> Path:
    new_df = pd.read_excel(source, sheet_name=0, dtype=object, engine="openpyxl").fillna("")
    normalized_new = normalize_confirmed_mapping_dataframe(new_df, default_company_type=company_type)
    target = Path(library_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        try:
            existing_df = pd.read_excel(target, sheet_name=0, dtype=object, engine="openpyxl").fillna("")
            normalized_existing = normalize_confirmed_mapping_dataframe(existing_df)
        except Exception:
            normalized_existing = pd.DataFrame(columns=normalized_new.columns)
        combined = pd.concat([normalized_existing, normalized_new], ignore_index=True)
    else:
        combined = normalized_new
    combined = combined.drop_duplicates(subset=["SourceSeq", "SubjectCode", "FSLine", "NoteLine", "CompanyType"], keep="last")
    combined.to_excel(target, index=False, sheet_name="已确认映射库")
    return target


def _parse_cloud_agent_json(content: str) -> dict[str, object]:
    text = clean_cell(content)
    if not text:
        return {"items": []}
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return {"items": []}
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"items": []}
    if isinstance(parsed, list):
        return {"items": parsed}
    if isinstance(parsed, dict):
        if "items" not in parsed and "results" in parsed:
            parsed["items"] = parsed.get("results")
        if isinstance(parsed.get("items"), list):
            return parsed
    return {"items": []}


def run_fiscal_mapping_agent(
    source: str | Path | BytesIO | BinaryIO,
    output_path: str | Path,
    config: FiscalMappingAgentConfig | None = None,
    confirmed_mapping_path: str | Path | None = None,
) -> tuple[pd.DataFrame, Path]:
    source_df = read_source_excel(source)
    agent = FiscalReportMappingAgent(config or FiscalMappingAgentConfig(), confirmed_mapping_path)
    result_df = agent.map_dataframe(source_df)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_mapping_workbook(result_df, target)
    return result_df, target


def read_source_excel(source: str | Path | BytesIO | BinaryIO) -> pd.DataFrame:
    raw_df = pd.read_excel(source, sheet_name=0, header=None, dtype=object, engine="openpyxl")
    raw_df = raw_df.dropna(how="all").copy()
    if raw_df.empty:
        return pd.DataFrame(columns=["序号", "FSLine", "NoteLine"])

    header_index = detect_header_row(raw_df)
    headers = make_unique_headers(
        [clean_cell(value) or f"列{idx + 1}" for idx, value in enumerate(raw_df.iloc[header_index].tolist())]
    )
    data_df = raw_df.iloc[header_index + 1 :].copy()
    data_df.columns = headers
    return data_df.fillna("")


def make_unique_headers(headers: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    unique_headers: list[str] = []
    for header in headers:
        count = seen.get(header, 0)
        unique_headers.append(header if count == 0 else f"{header}.{count}")
        seen[header] = count + 1
    return unique_headers


def detect_header_row(raw_df: pd.DataFrame) -> int:
    best_index = 0
    best_score = -1
    for index in range(min(10, len(raw_df))):
        values = [compact_text(value) for value in raw_df.iloc[index].tolist()]
        row_text = " ".join(values)
        score = 0
        if "fsline" in row_text or "报表主表项目" in row_text or "报表项目" in row_text:
            score += 3
        if "noteline" in row_text or "noteline" in row_text.replace(" ", "") or "附注明细" in row_text or "模拟科目" in row_text:
            score += 3
        if "序号" in row_text or "行号" in row_text:
            score += 1
        if score > best_score:
            best_score = score
            best_index = index
    return best_index


def normalize_source_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "序号",
                "FSLine",
                "NoteLine",
                "SourceGrouping_Consolidated",
                "SourceGrouping_Standalone",
                "SourceGrouping_IFRS18",
                "SourceHasGrouping_Consolidated",
                "SourceHasGrouping_Standalone",
                "SourceHasGrouping_IFRS18",
            ]
        )

    columns = list(df.columns)
    seq_column = find_column(columns, ["序号", "行号", "no", "index"]) or columns[0]
    explicit_fs_column = find_column(columns, ["fsline", "fs line", "报表主表项目", "报表项目", "fs"])
    explicit_note_column = find_column(columns, ["noteline", "note line", "附注明细项目", "附注明细", "模拟科目", "科目"])
    account_name_column = find_column(columns, ["科目名称", "科目名", "accountname", "account name"])
    account_code_column = find_column(columns, ["科目编码", "科目代码", "科目号", "accountcode", "account code"])
    if account_name_column is None:
        account_name_column = find_column(columns, ["\u79d1\u76ee\u540d\u79f0", "\u79d1\u76ee\u540d"])
    if account_code_column is None:
        account_code_column = find_column(columns, ["\u79d1\u76ee\u7f16\u7801", "\u79d1\u76ee\u4ee3\u7801", "\u79d1\u76ee\u53f7"])
    if explicit_fs_column is None and explicit_note_column is None and account_name_column is not None:
        fs_column = account_name_column
        note_column = account_name_column
    else:
        fs_column = explicit_fs_column or (columns[1] if len(columns) > 1 else columns[0])
        note_column = explicit_note_column or (
            account_name_column if account_code_column is not None and account_name_column is not None else columns[2] if len(columns) > 2 else fs_column
        )
    grouping_column = find_column(columns, ["Grouping_Consolidated", "Grouping", "合并口径财政部报表项目", "集团科目口径映射", "集团科目口径", "列4", "正确答案"])
    standalone_column = find_column(
        columns,
        [
            "Grouping_Standalone",
            "单体口径财政部报表项目",
            "财政部口径映射",
            "财政部口径",
            "财政部报表口径",
            "单体口径映射",
            "列5",
        ],
    )
    ifrs18_column = find_column(columns, ["IFRS 18映射", "IFRS18映射", "IFRS 18口径映射", "IFRS18口径映射", "IFRS 18口径", "IFRS18口径", "列6"])
    if standalone_column is None and grouping_column is not None:
        grouping_index = columns.index(grouping_column)
        if grouping_index + 1 < len(columns) and compact_text(columns[grouping_index + 1]).startswith(compact_text(grouping_column)):
            standalone_column = columns[grouping_index + 1]
    if grouping_column in {seq_column, fs_column, note_column}:
        grouping_column = None
    if standalone_column in {seq_column, fs_column, note_column, grouping_column}:
        standalone_column = None
    grouping_values = df[grouping_column].map(clean_cell) if grouping_column is not None else pd.Series("", index=df.index)
    standalone_values = df[standalone_column].map(clean_cell) if standalone_column is not None else pd.Series("", index=df.index)
    ifrs18_values = df[ifrs18_column].map(clean_cell) if ifrs18_column is not None else pd.Series("", index=df.index)
    has_grouping_answers = grouping_column is not None and bool((grouping_values != "").any())
    has_standalone_answers = standalone_column is not None and bool((standalone_values != "").any())
    has_ifrs18_answers = ifrs18_column is not None and bool((ifrs18_values != "").any())

    normalized = pd.DataFrame(
        {
            "序号": df[seq_column].map(clean_cell),
            "SubjectCode": df[account_code_column].map(clean_cell) if account_code_column is not None else "",
            "FSLine": df[fs_column].map(clean_cell),
            "NoteLine": df[note_column].map(clean_cell),
            "SourceGrouping_Consolidated": grouping_values,
            "SourceGrouping_Standalone": standalone_values,
            "SourceGrouping_IFRS18": ifrs18_values,
            "SourceHasGrouping_Consolidated": has_grouping_answers,
            "SourceHasGrouping_Standalone": has_standalone_answers,
            "SourceHasGrouping_IFRS18": has_ifrs18_answers,
        }
    )
    normalized = normalized[
        normalized[["FSLine", "NoteLine"]].apply(lambda row: any(clean_cell(value) for value in row), axis=1)
    ].copy()
    return normalized.reset_index(drop=True)


def find_column(columns: list[object], aliases: list[str]) -> object | None:
    alias_texts = [compact_text(alias) for alias in aliases]
    for column in columns:
        column_text = compact_text(column)
        if column_text in alias_texts:
            return column
    for column in columns:
        column_text = compact_text(column)
        if any(len(alias) >= 3 and alias in column_text for alias in alias_texts):
            return column
    return None


def clean_cell(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).replace("\xa0", " ").replace("＊", "*").strip()
    text = re.sub(r"\.0$", "", text)
    return "" if text.lower() in {"nan", "none"} else text


def compact_text(value: object) -> str:
    return re.sub(r"[\s_　\-—/（）()]+", "", clean_cell(value)).lower()


def infer_from_fs_line(fs_line: str) -> str:
    text = compact_text(fs_line)
    known_items = [
        "货币资金",
        "存放中央银行款项",
        "存放同业款项",
        "拆出资金",
        "衍生金融资产",
        "买入返售金融资产",
        "发放贷款和垫款",
        "交易性金融资产",
        "债权投资",
        "其他债权投资",
        "其他权益工具投资",
        "可供出售金融资产",
        "长期股权投资",
        "固定资产",
        "无形资产",
        "递延所得税资产",
        "应收款项",
        "应收款项类金融资产",
        "其他资产",
        "向中央银行借款",
        "同业及其他金融机构存放款项",
        "拆入资金",
        "交易性金融负债",
        "衍生金融负债",
        "卖出回购金融资产款",
        "吸收存款",
        "应付职工薪酬",
        "应交税费",
        "应付债券",
        "递延所得税负债",
        "其他负债",
        "股本",
        "资本公积",
        "其他综合收益",
        "盈余公积",
        "一般风险准备",
        "未分配利润",
        "利息净收入",
        "手续费及佣金净收入",
        "投资收益",
        "公允价值变动收益",
        "业务及管理费",
        "信用减值损失",
        "所得税费用",
    ]
    for item in known_items:
        if compact_text(item) in text:
            return item
    return ""


def infer_from_requirement_items(fs_line: str, note_line: str, fiscal_requirement_items: tuple[str, ...]) -> str:
    if not fiscal_requirement_items:
        return ""
    text = compact_text(f"{fs_line} {note_line}")
    fs_text = compact_text(fs_line)
    note_text = compact_text(note_line)
    candidates = [clean_cell(item) for item in fiscal_requirement_items if clean_cell(item)]
    for item in candidates:
        item_text = compact_text(item)
        if item_text and item_text in {fs_text, note_text}:
            return item
    for item in candidates:
        item_text = compact_text(item)
        if item_text and (item_text in text or fs_text in item_text or note_text in item_text):
            return item
    return ""


def generic_fallback_item(fs_line: str, note_line: str) -> str:
    text = compact_text(f"{fs_line} {note_line}")
    if not text:
        return "其他资产"
    if any(token in text for token in ["应付", "负债", "借款", "拆入", "吸收存款", "卖出回购", "预收", "准备金", "保户储金"]):
        return "其他负债"
    if any(token in text for token in ["股本", "资本公积", "权益", "盈余公积", "未分配利润", "少数股东"]):
        return "其他综合收益" if "其他综合收益" in text else "其他权益工具"
    if any(token in text for token in ["收入", "收益", "损益", "利息收入", "手续费", "佣金"]):
        return "其他业务收入"
    if any(token in text for token in ["成本", "费用", "支出", "减值损失", "税金"]):
        return "其他业务成本"
    return "其他资产"


def mapping_decision(
    consolidated: str,
    standalone: str,
    confidence: int,
    basis: str,
    alternatives: str = "",
) -> dict[str, object]:
    return {
        "consolidated": consolidated,
        "standalone": standalone,
        "confidence": confidence,
        "basis": basis,
        "alternatives": alternatives,
    }


def requirement_item_exists(item: str, fiscal_requirement_items: tuple[str, ...]) -> bool:
    item_text = compact_text(item)
    item_without_number = strip_report_item_number(item_text)
    return any(
        compact_text(candidate) in {item_text, item_without_number}
        or item_text in compact_text(candidate)
        or item_without_number in compact_text(candidate)
        for candidate in fiscal_requirement_items
        if clean_cell(candidate)
    )


def strip_report_item_number(text: str) -> str:
    return re.sub(r"^（?[一二三四五六七八九十]+）?", "", text)


def requirement_aligned_item(
    preferred: str,
    fiscal_requirement_items: tuple[str, ...],
    fallback: str,
) -> str:
    if not fiscal_requirement_items:
        return preferred
    if requirement_item_exists(preferred, fiscal_requirement_items):
        return preferred
    if requirement_item_exists(fallback, fiscal_requirement_items):
        return fallback
    return fallback


def align_decision_to_requirement_items(
    decision: dict[str, object],
    fiscal_requirement_items: tuple[str, ...],
) -> dict[str, object]:
    if not fiscal_requirement_items:
        return decision
    replacements = {
        "*交易性金融资产": "以公允价值计量且其变动计入当期损益的金融资产",
        "*交易性金融负债": "以公允价值计量且其变动计入当期损益的金融负债",
        "*债权投资": "持有至到期投资",
        "*其他债权投资": "可供出售金融资产",
        "*其他权益工具投资": "可供出售金融资产",
        "*信用减值损失": "资产减值损失",
        "信用减值损失": "资产减值损失",
        "（三）*信用减值损失": "（三）资产减值损失",
        "（三）信用减值损失": "（三）资产减值损失",
        "*其他资产减值损失": "资产减值损失",
        "（四）*其他资产减值损失": "资产减值损失",
        "应收款项类金融资产": "应收款项类投资",
    }
    adjusted = dict(decision)
    changed = False
    for key in ("consolidated", "standalone"):
        value = clean_cell(adjusted.get(key, ""))
        replacement = replacements.get(value)
        if replacement and not requirement_item_exists(value, fiscal_requirement_items):
            adjusted[key] = replacement
            changed = True
    if changed:
        adjusted["basis"] = f"{clean_cell(adjusted.get('basis', ''))}；已按当前上传的合并填报要求修正候选项目"
        adjusted["confidence"] = min(int(adjusted.get("confidence", 80)), 92)
    return adjusted


def is_ifrs18_requirement(fiscal_requirement_items: tuple[str, ...]) -> bool:
    return requirement_item_exists("以公允价值计量且其变动计入当期损益的金融资产", fiscal_requirement_items)


def is_mof_requirement(fiscal_requirement_items: tuple[str, ...]) -> bool:
    return bool(fiscal_requirement_items) and not is_ifrs18_requirement(fiscal_requirement_items)


def is_asset_company_ifrs18_requirement(fiscal_requirement_items: tuple[str, ...]) -> bool:
    return is_ifrs18_requirement(fiscal_requirement_items)


def is_asset_company_group_requirement(fiscal_requirement_items: tuple[str, ...]) -> bool:
    return not any(clean_cell(item) for item in fiscal_requirement_items)


def is_asset_company_mof_requirement(fiscal_requirement_items: tuple[str, ...]) -> bool:
    return is_mof_requirement(fiscal_requirement_items)


def asset_company_ifrs18_priority_decision(
    fs_text: str,
    note_text: str,
    fiscal_requirement_items: tuple[str, ...],
) -> dict[str, object] | None:
    if not is_asset_company_ifrs18_requirement(fiscal_requirement_items):
        return None

    fvtpl_asset = "以公允价值计量且其变动计入当期损益的金融资产"
    trading_asset = "交易性金融资产的金融资产"
    if "存放同业款项" in note_text:
        return mapping_decision("存放同业款项", "存放同业款项", 96, "资产公司 IFRS 18 口径：存放同业款项按明细项目列示")
    if "存出保证金" in note_text:
        return mapping_decision("存出保证金", "存出保证金", 96, "资产公司 IFRS 18 口径：存出保证金按明细项目列示")
    if "结算备付金" in note_text:
        return mapping_decision("结算备付金", "结算备付金", 96, "资产公司 IFRS 18 口径：结算备付金按明细项目列示")
    if "定期存款" in note_text:
        return mapping_decision("货币资金", "货币资金", 96, "资产公司 IFRS 18 口径：定期存款归入货币资金")
    if (
        "交易性金融资产" in note_text
        or "以公允价值计量且其变动计入当期损益的金融资产" in note_text
        or "货币衍生工具" in note_text
        or "利率衍生工具" in note_text
        or "权益衍生工具" in note_text
        or "其他衍生工具" in note_text
    ):
        target = trading_asset
        return mapping_decision(target, target, 96, "资产公司 IFRS 18 口径：FVTPL 金融资产及相关衍生工具按 IFRS 18 填报说明列示")

    return None


def asset_company_profile_priority_decision(
    fs_line: str,
    note_line: str,
    fiscal_requirement_items: tuple[str, ...],
) -> dict[str, object] | None:
    fs_text = compact_text(fs_line)
    note_text = compact_text(note_line)
    full_text = compact_text(f"{fs_line} {note_line}")
    group_profile = is_asset_company_group_requirement(fiscal_requirement_items)
    ifrs18_profile = is_asset_company_ifrs18_requirement(fiscal_requirement_items)
    mof_profile = is_asset_company_mof_requirement(fiscal_requirement_items)

    if group_profile:
        group_pnl_items = (
            "利息收入",
            "利息支出",
            "手续费及佣金收入",
            "手续费及佣金支出",
            "投资收益",
            "公允价值变动损益",
            "营业税金及附加",
            "业务及管理费",
            "资产减值损失",
            "信用减值损失",
            "不良资产处置净收益",
            "已赚保费",
            "保险业务成本",
            "其他业务收入",
            "其他业务成本",
            "所得税费用",
            "营业外收入",
            "营业外支出",
            "少数股东损益",
        )
        for item in group_pnl_items:
            if compact_text(item) in fs_text:
                return mapping_decision(item, item, 97, "资产公司集团科目口径：损益类项目保留集团口径主表名称")

        group_balance_rules = [
            (("存放同业款项",), "存放同业款项"),
            (("定期存款",), "货币资金"),
            (("存出保证金",), "存出保证金"),
            (("结算备付金",), "结算备付金"),
            (("应付利息",), "应付利息"),
            (("应收利息",), "应收利息"),
            (("其他债权投资",), "其他债权投资"),
            (("其他权益工具投资",), "其他权益工具投资"),
            (("债权投资减值准备", "债权投资"), "债权投资投资"),
            (("划分为持有代售的资产", "划分为持有待售的资产"), "划分为持有代售的资产"),
            (("长期应收款",), "应收账款"),
            (("固定资产清理",), "固定资产清理"),
            (("继续涉入资产",), "继续涉入资产"),
            (("长期待摊费用",), "长期待摊费用"),
            (("卖出回购",), "卖出回购金融资产"),
            (("代理买卖证券款",), "代理买卖证券款"),
            (("其他应付款",), "其他应付款"),
        ]
        for keywords, target in group_balance_rules:
            if any(compact_text(keyword) in note_text for keyword in keywords):
                return mapping_decision(target, target, 97, "资产公司集团科目口径：资产负债表明细保留集团口径名称")

    if group_profile or ifrs18_profile:
        group_ifrs_rules = [
            (("应收利息",), "应收利息"),
            (("其他债权投资",), "其他债权投资"),
            (("其他权益工具投资",), "其他权益工具投资"),
            (("交易性金融资产", "以公允价值计量且其变动计入当期损益的金融资产", "货币衍生工具", "利率衍生工具", "权益衍生工具", "其他衍生工具", "待处置资产"), "交易性金融资产的金融资产"),
            (("应收票据",), "应收票据"),
            (("应收账款", "应收保费", "应收代位追偿款", "应收分保账款", "应收分保未到期责任准备金", "应收分保未决赔款准备金", "应收分保寿险责任准备金", "应收分保长期健康险责任准备金"), "应收账款"),
            (("预付账款",), "预付账款"),
            (("应收股利",), "应收股利"),
            (("其他应收款",), "其他应收款"),
            (("债权投资减值准备", "债权投资"), "债权投资投资" if ifrs18_profile and ("债权投资" in note_text and "债券" not in note_text and "权益工具" not in note_text) else "债权投资"),
            (("投资控股子企业", "其他股权投资", "长期股权投资"), "长期股权投资"),
            (("累计折旧", "固定资产"), "固定资产"),
            (("在建工程",), "在建工程" if ifrs18_profile else "在建工程"),
            (("无形资产",), "无形资产"),
            (("原材料", "在产品", "库存商品", "其他存货", "存货跌价准备", "存货"), "存货"),
            (("应付账款", "预收款项", "预收保费", "应付手续费及佣金", "应付分保账款", "应付赔付款", "应付保单红利"), "应付账款"),
            (("同业存放款项", "其他金融机构存放款项"), "同业及其他金融机构存放款项"),
            (("卖出回购",), "卖出回购金融资产" if ifrs18_profile else "卖出回购金融资产款"),
            (("保险合同准备金", "原保险合同未到期责任准备金", "再保险合同未到期责任准备金", "原保险合同未决赔款准备金", "再保险合同未决赔款准备金", "原保险合同寿险责任准备金", "再保险合同寿险责任准备金", "原保险合同长期健康险责任准备金", "再保险合同长期健康险责任准备金", "保户储金及投资款"), "保险合同准备金"),
            (("应付职工薪酬",), "应付职工薪酬"),
            (("应交税费",), "应交税费"),
            (("其他负债", "其他应付", "应付利息"), "其他负债"),
        ]
        for keywords, target in group_ifrs_rules:
            if any(compact_text(keyword) in note_text for keyword in keywords):
                return mapping_decision(target, target, 96, "资产公司集团/IFRS 18 口径：按高频差异规则保留或映射到管理口径项目")

    if ifrs18_profile:
        if "利息收入" in fs_text:
            return mapping_decision("利息收入（核心经营相关利息）", "利息收入（核心经营相关利息）", 96, "资产公司 IFRS 18 口径：利息收入映射为管理口径核心经营相关利息收入")
        if "利息支出" in fs_text:
            return mapping_decision("利息支出", "利息支出", 96, "资产公司 IFRS 18 口径：利息支出保留管理口径名称")
        if "手续费及佣金收入" in fs_text:
            return mapping_decision("佣金及手续费收入", "佣金及手续费收入", 96, "资产公司 IFRS 18 口径：手续费及佣金收入改为佣金及手续费收入")
        if "手续费及佣金支出" in fs_text:
            return mapping_decision("佣金及手续费支出", "佣金及手续费支出", 96, "资产公司 IFRS 18 口径：手续费及佣金支出改为佣金及手续费支出")
        if "投资收益" in fs_text:
            if "不良债权" in full_text:
                return mapping_decision("不良债权投资收益", "不良债权投资收益", 95, "资产公司 IFRS 18 口径：不良债权投资收益按管理口径列示")
            if "摊余成本" in full_text:
                return mapping_decision("以摊余成本计量的不良债权资产收入", "以摊余成本计量的不良债权资产收入", 95, "资产公司 IFRS 18 口径：摊余成本不良债权资产收入按管理口径列示")
            return mapping_decision("非核心投资收益", "非核心投资收益", 94, "资产公司 IFRS 18 口径：投资收益改为非核心投资收益")
        if "公允价值变动" in fs_text:
            if "不良债权" in full_text:
                return mapping_decision("不良债权资产公允价值变动（核心经营）", "不良债权资产公允价值变动（核心经营）", 95, "资产公司 IFRS 18 口径：不良债权公允价值变动按核心经营列示")
            return mapping_decision("其他金融工具公允价值变动（核心业务相关部分/财务性投资相关部分）", "其他金融工具公允价值变动（核心业务相关部分/财务性投资相关部分）", 94, "资产公司 IFRS 18 口径：公允价值变动改为管理口径金融工具公允价值变动")
        if "其他业务收入" in fs_text or "营业外收入" in fs_text or "已赚保费" in fs_text:
            return mapping_decision("其他经营收入", "其他经营收入", 94, "资产公司 IFRS 18 口径：其他收入类项目归入其他经营收入")
        if "其他业务成本" in fs_text or "保险业务成本" in fs_text or "营业外支出" in fs_text:
            return mapping_decision("其他经营费用", "其他经营费用", 94, "资产公司 IFRS 18 口径：其他成本费用类项目归入其他经营费用")
        if "业务及管理费" in fs_text:
            if any(token in note_text for token in ("折旧", "摊销")):
                return mapping_decision("折旧及摊销", "折旧及摊销", 95, "资产公司 IFRS 18 口径：折旧摊销类管理费用单列")
            return mapping_decision("其他经营费用", "其他经营费用", 94, "资产公司 IFRS 18 口径：业务及管理费归入其他经营费用")
        if "税金及附加" in fs_text or "营业税金及附加" in fs_text:
            return mapping_decision("税金及附加", "税金及附加", 96, "资产公司 IFRS 18 口径：税金及附加保留管理口径名称")
        if "信用减值损失" in full_text:
            return mapping_decision("信用减值损失", "信用减值损失", 96, "资产公司 IFRS 18 口径：信用减值损失保留管理口径名称")
        if "资产减值损失" in fs_text:
            return mapping_decision("其他资产减值损失", "其他资产减值损失", 96, "资产公司 IFRS 18 口径：非信用资产减值改为其他资产减值损失")

    if mof_profile:
        if "投资收益" in fs_text:
            return mapping_decision("（三）投资收益（损失以“-”号填列）", "（三）投资收益（损失以“-”号填列）", 96, "资产公司财政部口径：投资收益使用带损失说明的完整项目名")
        if "公允价值变动" in fs_text:
            return mapping_decision("（五）公允价值变动收益（损失以“-”号填列）", "（五）公允价值变动收益（损失以“-”号填列）", 96, "资产公司财政部口径：公允价值变动使用完整项目名")
        if "信用减值损失" in full_text:
            return mapping_decision("（三）*信用减值损失（转回金额以“-”号填列）", "（三）*信用减值损失（转回金额以“-”号填列）", 96, "资产公司财政部口径：信用减值损失按完整项目名列示")
        if "资产减值损失" in fs_text:
            return mapping_decision("（四）*其他资产减值损失（转回金额以“-”号填列）", "（四）*其他资产减值损失（转回金额以“-”号填列）", 96, "资产公司财政部口径：非信用资产减值按其他资产减值损失完整项目名列示")
        if "其他业务收入" in fs_text:
            return mapping_decision("（七）其他业务收入", "（七）其他业务收入", 96, "资产公司财政部口径：其他业务收入使用财政部完整项目名")
        if "资产处置收益" in fs_text or "资产处置损失" in fs_text:
            return mapping_decision("（八）资产处置收益（损失以“-”号填列）", "（八）资产处置收益（损失以“-”号填列）", 95, "资产公司财政部口径：资产处置收益/损失使用完整项目名")
        if "其他收益" in fs_text:
            return mapping_decision("（九）其他收益", "（九）其他收益", 95, "资产公司财政部口径：其他收益使用完整项目名")
        if "应收利息" in note_text:
            return mapping_decision("应收利息", "应收利息", 96, "资产公司财政部口径：应收利息各明细优先归入应收利息")
        if "定期存款" in note_text:
            return mapping_decision("货币资金", "货币资金", 96, "资产公司财政部口径：定期存款归入货币资金")
        if "交易性金融资产的金融资产" in note_text:
            return mapping_decision("*交易性金融资产", "*交易性金融资产", 96, "资产公司财政部口径：交易性金融资产的金融资产明细归入*交易性金融资产")
        if any(token in note_text for token in ("应收票据", "应收账款", "预付账款", "应收保费", "应收代位追偿款", "应收分保账款", "应收分保未到期责任准备金", "应收分保未决赔款准备金", "应收分保寿险责任准备金", "应收分保长期健康险责任准备金", "长期应收款")):
            return mapping_decision("债权投资", "债权投资", 96, "资产公司财政部口径：多类应收及保险类应收并入债权投资")
        if "其他债权投资" in note_text:
            return mapping_decision("其他债权投资", "其他债权投资", 96, "资产公司财政部口径：其他债权投资明细不加星号")
        if "债权投资" in note_text:
            target = "债权投资金融资产" if ("债权投资" == clean_cell(note_line) or "减值准备" in note_text) else "债权投资"
            return mapping_decision(target, target, 96, "资产公司财政部口径：债权投资本体及减值准备按债权投资金融资产/债权投资列示")
        if any(token in note_text for token in ("投资控股子企业", "其他股权投资")):
            return mapping_decision("长期股权投资", "长期股权投资", 96, "资产公司财政部口径：股权投资类明细归入长期股权投资")
        if "累计折旧" in note_text:
            return mapping_decision("固定资产", "固定资产", 96, "资产公司财政部口径：累计折旧归入固定资产")
        if "保户质押贷款" in note_text:
            return mapping_decision("其他资产", "其他资产", 96, "资产公司财政部口径：保户质押贷款归入其他资产")
        if any(token in note_text for token in ("保险合同准备金", "原保险合同未到期责任准备金", "再保险合同未到期责任准备金", "原保险合同未决赔款准备金", "再保险合同未决赔款准备金", "原保险合同寿险责任准备金", "再保险合同寿险责任准备金", "原保险合同长期健康险责任准备金", "再保险合同长期健康险责任准备金", "保费准备金", "保户储金及投资款")):
            return mapping_decision("0", "0", 96, "资产公司财政部口径：保险准备金及保户储金类负债按当前模板不适用填 0")
        if "同业存放款项" in note_text or "其他金融机构存放款项" in note_text:
            return mapping_decision("0", "0", 96, "资产公司财政部口径：同业存放类负债按当前模板不适用填 0")

    return None


def bank_profile_priority_decision(
    fs_line: str,
    note_line: str,
    fiscal_requirement_items: tuple[str, ...],
) -> dict[str, object] | None:
    fs_text = compact_text(fs_line)
    note_text = compact_text(note_line)
    full_text = compact_text(f"{fs_line} {note_line}")
    ifrs18_profile = is_ifrs18_requirement(fiscal_requirement_items)
    mof_profile = is_mof_requirement(fiscal_requirement_items)
    pnl_context = any(token in fs_text for token in ("利息收入", "利息支出", "投资收益", "公允价值变动", "资产减值损失", "信用减值损失", "业务及管理费"))

    if ifrs18_profile:
        if "利息收入" in fs_text:
            return mapping_decision("利息收入（经营相关）", "利息收入（经营相关）", 96, "银行类 IFRS 18 口径：经营相关利息收入按 IFRS 18 利息收入项目列示")
        if "手续费及佣金收入" in fs_text or "手续费及佣金收入" in note_text:
            return mapping_decision("佣金及手续费收入", "佣金及手续费收入", 96, "银行类 IFRS 18 口径：手续费及佣金收入改为佣金及手续费收入")
        if "利息支出" in fs_text:
            return mapping_decision("利息支出", "利息支出", 96, "银行类 IFRS 18 口径：融资相关利息支出按利息支出列示")
        if "投资收益" in fs_text:
            if "长期股权投资" in full_text:
                return mapping_decision("长期股权投资收益", "长期股权投资收益", 95, "银行类 IFRS 18 口径：长期股权投资收益单列")
            return mapping_decision("非核心投资收益", "非核心投资收益", 94, "银行类 IFRS 18 口径：投资收益改为非核心投资收益")
        if "公允价值变动" in fs_text:
            return mapping_decision("其他金融工具公允价值变动（投资部分）", "其他金融工具公允价值变动（投资部分）", 94, "银行类 IFRS 18 口径：公允价值变动改为其他金融工具公允价值变动")
        if "手续费及佣金支出" in fs_text:
            return mapping_decision("其他经营费用", "其他经营费用", 94, "银行类 IFRS 18 口径：手续费及佣金支出归入其他经营费用")
        if "业务及管理费" in fs_text:
            return mapping_decision("其他经营费用", "其他经营费用", 94, "银行类 IFRS 18 口径：业务及管理费归入其他经营费用")
        if "信用减值损失" in full_text or "资产减值损失" in fs_text:
            return mapping_decision("信用减值损失", "信用减值损失", 94, "银行类 IFRS 18 口径：减值损失按信用减值损失列示")
        if "其他业务收入" in fs_text or "营业外收入" in fs_text or "汇兑损益" in fs_text or "资产处置收益" in fs_text or "其他收益" in fs_text:
            return mapping_decision("其他经营收入", "其他经营收入", 94, "银行类 IFRS 18 口径：其他收入/收益类项目归入其他经营收入")
        if "其他业务成本" in fs_text or "营业外支出" in fs_text or "税金及附加" in fs_text:
            return mapping_decision("其他经营费用", "其他经营费用", 94, "银行类 IFRS 18 口径：其他成本/费用类项目归入其他经营费用")
        if "所得税费用" in fs_text:
            return mapping_decision("所得税", "所得税", 95, "银行类 IFRS 18 口径：所得税费用改为所得税")

    if "定期存款" in note_text:
        return mapping_decision("货币资金", "货币资金", 96, "银行类口径：定期存款归入货币资金")
    if "存放同业款项" in note_text:
        target = "存放同业款项" if ifrs18_profile else "拆出资金" if mof_profile else "存放同业款项"
        return mapping_decision(target, target, 96, "银行类口径：存放同业在财政部口径并入拆出资金，IFRS 18 保留存放同业款项")
    if "结算备付金" in note_text:
        target = "结算备付金" if ifrs18_profile else "货币资金"
        return mapping_decision(target, target, 96, "银行类口径：结算备付金在财政部口径归入货币资金，IFRS 18 保留明细名称")
    if "存出保证金" in note_text:
        target = "存出保证金" if ifrs18_profile else "-"
        return mapping_decision(target, target, 94, "银行类口径：存出保证金在 IFRS 18 保留明细名称，财政部口径按不适用列示")
    if not pnl_context and any(
        token in full_text
        for token in (
            "交易性金融资产的金融资产",
            "以公允价值计量且其变动计入当期损益的金融资产",
            "货币衍生工具",
            "利率衍生工具",
            "权益衍生工具",
            "其他衍生工具",
        )
    ):
        target = "以公允价值计量且其变动计入当期损益的金融资产" if ifrs18_profile else "*交易性金融资产" if mof_profile else "交易性金融资产的金融资产"
        return mapping_decision(target, target, 96, "银行类口径：财政部使用*交易性金融资产，IFRS 18 使用FVTPL长名称")

    return None


def securities_profile_priority_decision(
    fs_line: str,
    note_line: str,
    fiscal_requirement_items: tuple[str, ...],
) -> dict[str, object] | None:
    fs_text = compact_text(fs_line)
    note_text = compact_text(note_line)
    full_text = compact_text(f"{fs_line} {note_line}")
    group_profile = not any(clean_cell(item) for item in fiscal_requirement_items)
    ifrs18_profile = is_ifrs18_requirement(fiscal_requirement_items)

    group_pnl_targets = (
        ("利息收入", "利息收入"),
        ("利息支出", "利息支出"),
        ("手续费及佣金收入", "手续费及佣金收入"),
        ("手续费及佣金支出", "手续费及佣金支出"),
        ("投资收益", "投资收益"),
        ("公允价值变动", "公允价值变动损益"),
        ("业务及管理费", "业务及管理费"),
        ("资产减值损失", "资产减值损失"),
        ("信用减值损失", "信用减值损失"),
        ("其他业务收入", "其他业务收入"),
        ("其他业务成本", "其他业务成本"),
        ("营业外收入", "营业外收入"),
        ("营业外支出", "营业外支出"),
        ("所得税费用", "所得税费用"),
    )
    if group_profile:
        for token, target in group_pnl_targets:
            if token in fs_text:
                return mapping_decision(target, target, 96, "证券类集团科目口径：损益类科目保留证券科目主类，不并入财政部项目")

    if ifrs18_profile:
        if "利息收入" in fs_text:
            return mapping_decision("利息收入（经营相关）", "利息收入（经营相关）", 96, "证券类 IFRS 18 口径：经营相关利息收入按 IFRS 18 利息收入项目列示")
        if "手续费及佣金收入" in fs_text or "手续费及佣金收入" in note_text:
            return mapping_decision("佣金及手续费收入", "佣金及手续费收入", 96, "证券类 IFRS 18 口径：手续费及佣金收入改为佣金及手续费收入")
        if "利息支出" in fs_text:
            return mapping_decision("利息支出", "利息支出", 96, "证券类 IFRS 18 口径：融资相关利息支出按利息支出列示")
        if "投资收益" in fs_text:
            if "长期股权投资" in full_text:
                return mapping_decision("长期股权投资收益", "长期股权投资收益", 95, "证券类 IFRS 18 口径：长期股权投资收益单列")
            return mapping_decision("非核心投资收益", "非核心投资收益", 94, "证券类 IFRS 18 口径：投资收益改为非核心投资收益")
        if "公允价值变动" in fs_text:
            return mapping_decision("其他金融工具公允价值变动（投资部分）", "其他金融工具公允价值变动（投资部分）", 94, "证券类 IFRS 18 口径：公允价值变动改为其他金融工具公允价值变动")
        if "手续费及佣金支出" in fs_text or "业务及管理费" in fs_text:
            return mapping_decision("其他经营费用", "其他经营费用", 94, "证券类 IFRS 18 口径：手续费支出及管理费用归入其他经营费用")
        if "信用减值损失" in full_text or "资产减值损失" in fs_text:
            return mapping_decision("信用减值损失", "信用减值损失", 94, "证券类 IFRS 18 口径：减值损失按信用减值损失列示")
        if "其他业务收入" in fs_text or "营业外收入" in fs_text or "汇兑损益" in fs_text or "资产处置收益" in fs_text or "其他收益" in fs_text:
            return mapping_decision("其他经营收入", "其他经营收入", 94, "证券类 IFRS 18 口径：其他收入/收益类项目归入其他经营收入")
        if "其他业务成本" in fs_text or "营业外支出" in fs_text or "税金及附加" in fs_text:
            return mapping_decision("其他经营费用", "其他经营费用", 94, "证券类 IFRS 18 口径：其他成本/费用类项目归入其他经营费用")
        if "所得税费用" in fs_text:
            return mapping_decision("所得税", "所得税", 95, "证券类 IFRS 18 口径：所得税费用改为所得税")

    return None


def insurance_profile_priority_decision(
    fs_line: str,
    note_line: str,
    fiscal_requirement_items: tuple[str, ...],
) -> dict[str, object] | None:
    fs_text = compact_text(fs_line)
    note_text = compact_text(note_line)
    full_text = compact_text(f"{fs_line} {note_line}")
    group_profile = not any(clean_cell(item) for item in fiscal_requirement_items)
    ifrs18_profile = is_ifrs18_requirement(fiscal_requirement_items)

    group_pnl_targets = (
        ("利息收入", "利息收入"),
        ("利息支出", "利息支出"),
        ("手续费及佣金收入", "手续费及佣金收入"),
        ("手续费及佣金支出", "手续费及佣金支出"),
        ("已赚保费", "已赚保费"),
        ("保险业务收入", "保险业务收入"),
        ("保险业务成本", "保险业务成本"),
        ("投资收益", "投资收益"),
        ("公允价值变动", "公允价值变动损益"),
        ("业务及管理费", "业务及管理费"),
        ("资产减值损失", "资产减值损失"),
        ("信用减值损失", "信用减值损失"),
        ("其他业务收入", "其他业务收入"),
        ("其他业务成本", "其他业务成本"),
        ("营业外收入", "营业外收入"),
        ("营业外支出", "营业外支出"),
        ("所得税费用", "所得税费用"),
    )
    if group_profile:
        for token, target in group_pnl_targets:
            if token in fs_text:
                return mapping_decision(target, target, 96, "保险类集团科目口径：损益类科目保留保险科目主类，不并入财政部项目")

    if ifrs18_profile:
        if "利息收入" in fs_text and "证券投资" not in full_text:
            return mapping_decision("利息收入（经营相关）", "利息收入（经营相关）", 96, "保险类 IFRS 18 口径：经营相关利息收入按 IFRS 18 利息收入项目列示")
        if "手续费及佣金收入" in fs_text or "手续费及佣金收入" in note_text:
            return mapping_decision("佣金及手续费收入", "佣金及手续费收入", 96, "保险类 IFRS 18 口径：手续费及佣金收入改为佣金及手续费收入")
        if "利息支出" in fs_text:
            return mapping_decision("利息支出", "利息支出", 96, "保险类 IFRS 18 口径：融资相关利息支出按利息支出列示")
        if "房地产销售收入" in fs_text:
            return mapping_decision("存货销售收入", "存货销售收入", 94, "保险类 IFRS 18 口径：房地产销售收入按存货销售收入列示")
        if (
            "保险业务收入" in fs_text
            or "已赚保费" in fs_text
            or "分出保费" in fs_text
            or "摊回" in fs_text
            or "租赁收入" in fs_text
            or "其他业务收入" in fs_text
            or "汇兑损益" in fs_text
            or "营业外收入" in fs_text
            or "资产处置收益" in fs_text
            or "其他收益" in fs_text
        ):
            return mapping_decision("其他经营收入", "其他经营收入", 94, "保险类 IFRS 18 口径：保险业务收入、摊回类及其他收入归入其他经营收入")
        if "投资收益" in fs_text:
            if "长期股权投资" in full_text:
                return mapping_decision("长期股权投资收益", "长期股权投资收益", 95, "保险类 IFRS 18 口径：长期股权投资收益单列")
            if "证券投资" in full_text or "交易性金融资产" in full_text or "其他债权投资" in full_text or "指定类" in full_text:
                return mapping_decision("其他经营收入", "其他经营收入", 94, "保险类 IFRS 18 口径：保险类证券投资及金融工具投资收益归入其他经营收入")
            return mapping_decision("非核心投资收益", "非核心投资收益", 94, "保险类 IFRS 18 口径：不良资产处置等投资收益归入非核心投资收益")
        if "公允价值变动" in fs_text:
            return mapping_decision("其他经营收入", "其他经营收入", 94, "保险类 IFRS 18 口径：保险类公允价值变动收益归入其他经营收入")
        if "保险业务成本" in fs_text or "赔付支出" in fs_text or "退保金" in fs_text or "保单红利支出" in fs_text or "分保费用" in fs_text:
            return mapping_decision("保险服务费用", "保险服务费用", 94, "保险类 IFRS 18 口径：保险业务成本及赔付/分保费用归入保险服务费用")
        if "提取" in fs_text and ("准备金" in fs_text or "风险基金" in fs_text):
            return mapping_decision("保险合同负债变动", "保险合同负债变动", 94, "保险类 IFRS 18 口径：准备金提取类归入保险合同负债变动")
        if "手续费及佣金支出" in fs_text or "业务及管理费" in fs_text:
            return mapping_decision("其他经营费用", "其他经营费用", 94, "保险类 IFRS 18 口径：手续费支出及管理费用归入其他经营费用")
        if "信用减值损失" in full_text or "资产减值损失" in fs_text:
            return mapping_decision("信用减值损失", "信用减值损失", 94, "保险类 IFRS 18 口径：减值损失按信用减值损失列示")
        if "其他业务成本" in fs_text or "营业外支出" in fs_text or "税金及附加" in fs_text:
            return mapping_decision("其他经营费用", "其他经营费用", 94, "保险类 IFRS 18 口径：其他成本/费用类项目归入其他经营费用")
        if "所得税费用" in fs_text:
            return mapping_decision("所得税", "所得税", 95, "保险类 IFRS 18 口径：所得税费用改为所得税")

    return None


def fsline_priority_decision(
    fs_line: str,
    note_line: str,
    company_type: str,
    fiscal_requirement_items: tuple[str, ...] = (),
) -> dict[str, object] | None:
    fs_text = compact_text(fs_line)
    note_text = compact_text(note_line)
    full_text = compact_text(f"{fs_line} {note_line}")

    if fs_text in {"check", "检查"}:
        return mapping_decision("", "", 90, "检查行不是财政部报表项目，按正确答案口径留空不映射")

    if company_type == "资产公司":
        asset_company_decision = asset_company_profile_priority_decision(fs_line, note_line, fiscal_requirement_items)
        if asset_company_decision:
            return asset_company_decision
        ifrs18_decision = asset_company_ifrs18_priority_decision(fs_text, note_text, fiscal_requirement_items)
        if ifrs18_decision:
            return ifrs18_decision

    if company_type == "银行类":
        bank_decision = bank_profile_priority_decision(fs_line, note_line, fiscal_requirement_items)
        if bank_decision:
            return bank_decision

    if company_type == "证券类":
        securities_decision = securities_profile_priority_decision(fs_line, note_line, fiscal_requirement_items)
        if securities_decision:
            return securities_decision
        if "应付利息" in note_text:
            return mapping_decision("应付利息", "应付利息", 96, "证券类正确答案口径：应付利息各明细归入应付利息，底层借款类型不改变列报项目")
        if "利息收入" in fs_text or "利息支出" in fs_text:
            return mapping_decision(
                "（一）主营业务净收入",
                "（一）主营业务净收入",
                96,
                "证券类损益表口径：利息收入/利息支出均按主营业务净收入归集，NoteLine 仅作为明细来源",
            )
        if note_text == compact_text("期货风险准备金"):
            return mapping_decision("其他负债", "其他负债", 96, "证券类正确答案口径：期货风险准备金归入其他负债")
        securities_not_applicable_tokens = (
            "向中央银行借款",
            "同业存放款项",
            "其他金融机构存放款项",
            "吸收存款",
            "保险合同准备金",
            "原保险合同未到期责任准备金",
            "再保险合同未到期责任准备金",
            "原保险合同未决赔款准备金",
            "再保险合同未决赔款准备金",
            "原保险合同寿险责任准备金",
            "再保险合同寿险责任准备金",
            "原保险合同长期健康险责任准备金",
            "再保险合同长期健康险责任准备金",
            "保费准备金",
            "保户储金及投资款",
            "不良资产处置净收益",
            "房地产销售收入",
            "房地产销售成本",
            "已赚保费",
            "保险业务收入",
            "保险业务成本",
            "分出保费",
            "退保金",
            "赔付支出",
            "摊回赔付支出",
            "提取未到期责任准备金",
            "提取未决赔款准备金",
            "提取寿险责任准备金",
            "提取长期健康险责任准备金",
            "提取保费准备金",
            "提取期货风险准备金",
            "摊回未决赔款准备金",
            "摊回寿险责任准备金",
            "摊回长期健康险责任准备金",
            "保单红利支出",
            "分保费用",
            "摊回分保费用",
            "提取农业政策性风险基金",
            "转回农业政策性风险基金",
            "保险业务手续费及佣金支出",
        )
        if any(token in full_text for token in securities_not_applicable_tokens):
            return mapping_decision("", "", 96, "证券类公司通常不适用该类银行/保险/房地产/不良资产业务，按正确答案口径留空不映射")
        if "不良资产处置净收益" in fs_text:
            target = clean_cell(note_line) or "不良资产处置净收益"
            return mapping_decision(
                target,
                target,
                96,
                "证券类正确答案口径：不良资产处置净收益保留明细项目名，不并入主营业务净收入",
            )
        if "房地产销售收入" in fs_text:
            return mapping_decision("房地产销售收入", "房地产销售收入", 96, "证券类正确答案口径：房地产销售收入保留原项目列示")
        if "房地产销售成本" in fs_text:
            return mapping_decision("房地产销售成本", "房地产销售成本", 96, "证券类正确答案口径：房地产销售成本保留原项目列示")
        if "已赚保费" in fs_text or "保险业务收入" in fs_text:
            target = clean_cell(note_line) or clean_cell(fs_line)
            return mapping_decision(target, target, 96, "证券类正确答案口径：保险业务收入及相关明细保留原项目列示")
        if "保险业务成本" in fs_text:
            target = clean_cell(note_line) or clean_cell(fs_line)
            return mapping_decision(target, target, 96, "证券类正确答案口径：保险业务成本及相关明细保留原项目列示")
        if "其他业务收入" in fs_text:
            return mapping_decision("（七）其他业务收入", "（七）其他业务收入", 96, "证券类损益表口径：其他业务收入按带序号项目列示")
        if any(token in note_text for token in ("提取期货风险准备金", "提取农业政策性风险基金", "转回农业政策性风险基金")):
            target = clean_cell(note_line)
            return mapping_decision(target, target, 96, "证券类正确答案口径：风险基金及期货风险准备金保留明细项目列示")
        if "其他业务成本" in fs_text:
            return mapping_decision("（七）其他业务成本", "（七）其他业务成本", 96, "证券类损益表口径：其他业务成本按带序号项目列示")
        if "手续费及佣金收入" in fs_text or "手续费及佣金支出" in fs_text:
            return mapping_decision(
                "（一）主营业务净收入",
                "（一）主营业务净收入",
                96,
                "证券类损益表口径：手续费及佣金收入/支出均按主营业务净收入归集，NoteLine 仅作为明细来源",
            )
        if "投资收益" in fs_text:
            return mapping_decision(
                "（三）投资收益（损失以“-”号填列）",
                "（三）投资收益（损失以“-”号填列）",
                96,
                "证券类损益表口径：投资收益明细均按投资收益项目归集，不按底层资产项目列示",
            )
        if "公允价值变动" in fs_text:
            return mapping_decision(
                "（五）公允价值变动收益（损失以“-”号填列）",
                "（五）公允价值变动收益（损失以“-”号填列）",
                96,
                "证券类损益表口径：公允价值变动明细按公允价值变动收益项目归集",
            )
        if "业务及管理费" in fs_text:
            return mapping_decision(
                "（二）业务及管理费",
                "（二）业务及管理费",
                96,
                "证券类损益表口径：业务及管理费明细按业务及管理费归集，长期待摊费用等 NoteLine 不改变费用归属",
            )
        if "信用减值损失" in full_text:
            return mapping_decision(
                "（三）*信用减值损失（转回金额以“-”号填列）",
                "（三）*信用减值损失（转回金额以“-”号填列）",
                95,
                "证券类损益表口径：信用风险相关减值按*信用减值损失归集",
            )
        if "资产减值损失" in fs_text:
            return mapping_decision(
                "（四）资产减值损失（转回金额以“-”号填列）",
                "（四）资产减值损失（转回金额以“-”号填列）",
                95,
                "证券类损益表口径：资产减值损失明细按资产减值损失归集，不按被减值资产列示",
            )
        if "资产处置收益" in fs_text or "资产处置损失" in fs_text:
            return mapping_decision(
                "（八）资产处置收益（损失以“-”号填列）",
                "（八）资产处置收益（损失以“-”号填列）",
                94,
                "证券类损益表口径：资产处置收益/损失按资产处置收益列示",
            )
        if "其他收益" in fs_text:
            return mapping_decision("（九）其他收益", "（九）其他收益", 94, "证券类损益表口径：其他收益按其他收益项目列示")

    if company_type == "保险类":
        insurance_decision = insurance_profile_priority_decision(fs_line, note_line, fiscal_requirement_items)
        if insurance_decision:
            return insurance_decision
        if "应付利息" in note_text:
            return mapping_decision("应付利息", "应付利息", 96, "保险类口径：应付利息明细归入应付利息")
        if "应收利息" in note_text:
            return mapping_decision("应收利息", "应收利息", 96, "保险类口径：应收利息明细归入应收利息")
        if "结算备付金" in note_text:
            return mapping_decision("货币资金", "货币资金", 96, "保险类正确答案口径：结算备付金归入货币资金")
        if "划分为持有代售的资产" in note_text or "划分为持有待售的资产" in note_text:
            return mapping_decision("划分为持有代售的资产", "划分为持有代售的资产", 96, "保险类正确答案口径：划分为持有代售的资产保留原项目列示")
        if "在建工程" in note_text:
            return mapping_decision("固定资产", "固定资产", 96, "保险类正确答案口径：在建工程及减值准备归入固定资产")
        if "提取期货风险准备金" in note_text:
            return mapping_decision("（五）保险业务支出", "（五）保险业务支出", 96, "保险类正确答案口径：提取期货风险准备金按保险业务支出列示")
        if "利息收入" in fs_text or "利息支出" in fs_text or "投资收益" in fs_text:
            return mapping_decision(
                "（三）投资收益（损失以“-”号填列）",
                "（三）投资收益（损失以“-”号填列）",
                96,
                "保险类损益表口径：投资收益、利息收入和利息支出均按投资收益项目归集",
            )
        if "信用减值损失" in full_text:
            return mapping_decision(
                "（三）*信用减值损失（转回金额以“-”号填列）",
                "（三）*信用减值损失（转回金额以“-”号填列）",
                96,
                "保险类损益表口径：信用风险相关减值按信用减值损失归集",
            )
        if "交易性金融负债" in note_text or "衍生金融负债" in note_text:
            return mapping_decision("*交易性金融负债", "*交易性金融负债", 96, "保险类口径：交易性/衍生金融负债归入*交易性金融负债")
        pnl_context = any(token in fs_text for token in ("公允价值变动", "投资收益", "资产减值损失", "信用减值损失"))
        if not pnl_context and ("交易性金融资产的金融资产" in note_text or "以公允价值计量且其变动计入当期损益的金融资产" in note_text):
            return mapping_decision("*交易性金融资产", "*交易性金融资产", 96, "保险类当前准则口径：交易性金融资产的金融资产归入*交易性金融资产")
        if not pnl_context and "抵债资产" in note_text:
            return mapping_decision("抵债资产", "抵债资产", 96, "保险类口径：抵债资产及跌价准备归入抵债资产")
        if "保户质押贷款" in note_text:
            return mapping_decision("其他资产", "其他资产", 96, "保险类口径：保户质押贷款不按一般贷款列示，归入其他资产")
        if "原材料" in note_text:
            return mapping_decision("其他资产", "其他资产", 94, "保险类口径：原材料归入其他资产")
        if any(token in note_text for token in ("在产品", "库存商品", "其他存货", "存货跌价准备")):
            return mapping_decision("", "", 94, "保险类正确答案口径：该类存货明细不适用，留空不映射")
        if fs_text == compact_text("以公允价值计量且其变动计入当期损益的金融资产") and note_text == fs_text:
            return mapping_decision("*交易性金融资产", "*交易性金融资产", 96, "保险类当前准则口径：该金融资产本体归入*交易性金融资产")
        if fs_text == compact_text("债权投资") and note_text == compact_text("债权投资"):
            return mapping_decision("*债权投资", "*债权投资", 96, "保险类当前准则口径：债权投资本体归入*债权投资")
        if not pnl_context and "其他债权投资" in note_text and note_text != compact_text("其他债权投资"):
            return mapping_decision("其他债权投资", "其他债权投资", 96, "保险类口径：其他债权投资明细及减值准备归入其他债权投资")
        if fs_text == compact_text("其他债权投资") and note_text == compact_text("其他债权投资"):
            return mapping_decision("*其他债权投资", "*其他债权投资", 96, "保险类当前准则口径：其他债权投资本体归入*其他债权投资")
        if fs_text == compact_text("其他权益工具") and note_text == compact_text("其他权益工具投资"):
            return mapping_decision("*其他权益工具投资", "*其他权益工具投资", 96, "保险类当前准则口径：其他权益工具投资本体归入*其他权益工具投资")
        insurance_blank_tokens = (
            "存放中央银行款项",
            "存放同业款项",
            "向中央银行借款",
            "同业存放款项",
            "其他金融机构存放款项",
            "房地产销售成本",
            "不良资产处置净收益",
            "资产处置损失-不良贷款",
        )
        if any(token in full_text for token in insurance_blank_tokens):
            return mapping_decision("", "", 95, "保险类公司通常不适用该类银行/房地产/不良资产或存货业务，按正确答案口径留空不映射")
        if "保险合同准备金" in fs_text:
            return mapping_decision("责任准备金", "责任准备金", 96, "保险类负债表口径：保险合同准备金明细归入责任准备金")
        if "保户储金及投资款" in fs_text:
            return mapping_decision("吸收存款", "吸收存款", 94, "保险类口径：保户储金及投资款按吸收存款列示")
        if "预收款项" in fs_text:
            return mapping_decision("应付款项", "应付款项", 94, "保险类口径：预收款项归入应付款项")
        if "已赚保费" in fs_text:
            return mapping_decision("（一）主营业务净收入", "（一）主营业务净收入", 96, "保险类损益表口径：已赚保费归入主营业务净收入")
        if "手续费及佣金收入" in fs_text:
            return mapping_decision("（二）中间业务净收入", "（二）中间业务净收入", 96, "保险类损益表口径：手续费及佣金收入归入中间业务净收入")
        if "公允价值变动" in fs_text:
            return mapping_decision(
                "（五）公允价值变动收益（损失以“-”号填列）",
                "（五）公允价值变动收益（损失以“-”号填列）",
                96,
                "保险类损益表口径：公允价值变动明细按公允价值变动收益归集",
            )
        if "资产处置收益" in fs_text:
            return mapping_decision(
                "（八）资产处置收益（损失以“-”号填列）",
                "（八）资产处置收益（损失以“-”号填列）",
                94,
                "保险类损益表口径：资产处置收益按带序号项目列示",
            )
        if "其他收益" in fs_text:
            return mapping_decision("（九）其他收益", "（九）其他收益", 94, "保险类损益表口径：其他收益按带序号项目列示")
        if "房地产销售收入" in fs_text:
            return mapping_decision("（七）其他业务收入", "（七）其他业务收入", 92, "保险类口径：房地产销售收入归入其他业务收入")
        if "其他业务收入" in fs_text:
            return mapping_decision("（七）其他业务收入", "（七）其他业务收入", 94, "保险类损益表口径：其他业务收入按其他业务收入列示")
        if "其他业务成本" in fs_text:
            return mapping_decision("（七）其他业务成本", "（七）其他业务成本", 94, "保险类损益表口径：其他业务成本按其他业务成本列示")
        if "保险业务成本" in fs_text or "手续费及佣金支出" in fs_text:
            reserve_tokens = ("提取未决赔款准备金", "提取寿险责任准备金", "提取长期健康险责任准备金", "提取保费准备金", "摊回未决赔款准备金", "摊回寿险责任准备金", "摊回长期健康险责任准备金", "提取农业政策性风险基金", "转回农业政策性风险基金")
            if any(token in note_text for token in reserve_tokens):
                return mapping_decision("（六）提取保险责任准备", "（六）提取保险责任准备", 96, "保险类损益表口径：责任准备金提取/摊回归入提取保险责任准备")
            return mapping_decision("（五）保险业务支出", "（五）保险业务支出", 96, "保险类损益表口径：保险业务成本及手续费佣金支出归入保险业务支出")
        if "业务及管理费" in fs_text:
            return mapping_decision("（二）业务及管理费", "（二）业务及管理费", 96, "保险类损益表口径：业务及管理费明细按业务及管理费归集")
        if "资产减值损失" in fs_text:
            return mapping_decision(
                "（四）*其他资产减值损失（转回金额以“-”号填列）",
                "（四）*其他资产减值损失（转回金额以“-”号填列）",
                95,
                "保险类损益表口径：资产减值损失按其他资产减值损失归集",
            )

    if company_type == "银行类":
        if "提取期货风险准备金" in note_text:
            return mapping_decision("-", "-", 92, "银行类不适用提取期货风险准备金，按 '-' 填列")
        if "利息收入" in fs_text or "利息支出" in fs_text:
            return mapping_decision(
                "（一）主营业务净收入",
                "（一）主营业务净收入",
                95,
                "银行类损益表口径：利息收入/利息支出按主营业务净收入归集，NoteLine 仅作为明细来源",
            )
        if "手续费及佣金收入" in fs_text or "手续费及佣金支出" in fs_text:
            return mapping_decision(
                "（二）中间业务净收入",
                "（二）中间业务净收入",
                95,
                "银行类损益表口径：手续费及佣金收入/支出按中间业务净收入归集",
            )
        if "投资收益" in fs_text:
            return mapping_decision(
                "（三）投资收益（损失以“-”号填列）",
                "（三）投资收益（损失以“-”号填列）",
                95,
                "银行类损益表口径：投资收益明细均按投资收益项目归集",
            )
        if "公允价值变动" in fs_text:
            return mapping_decision(
                "（五）公允价值变动收益（损失以“-”号填列）",
                "（五）公允价值变动收益（损失以“-”号填列）",
                95,
                "银行类损益表口径：公允价值变动明细按公允价值变动收益项目归集",
            )
        if "汇兑损益" in fs_text:
            return mapping_decision(
                "（六）汇兑收益（损失以“-”号填列）",
                "（六）汇兑收益（损失以“-”号填列）",
                95,
                "银行类损益表口径：汇兑损益按汇兑收益项目列示",
            )
        if "其他业务收入" in fs_text:
            return mapping_decision(
                "（七）其他业务收入",
                "（七）其他业务收入",
                93,
                "银行类损益表口径：其他业务收入按其他业务收入项目列示",
            )
        if "其他业务成本" in fs_text:
            return mapping_decision(
                "（七）其他业务成本",
                "（七）其他业务成本",
                93,
                "银行类损益表口径：其他业务成本按其他业务成本项目列示",
            )
        if "业务及管理费" in fs_text:
            return mapping_decision(
                "（二）业务及管理费",
                "（二）业务及管理费",
                95,
                "银行类损益表口径：业务及管理费明细按业务及管理费归集",
            )
        if "资产减值损失" in fs_text or "信用减值损失" in fs_text:
            if "信用减值损失" in note_text:
                return mapping_decision(
                    "（三）*信用减值损失（转回金额以“-”号填列）",
                    "（三）*信用减值损失（转回金额以“-”号填列）",
                    94,
                    "银行类损益表口径：信用风险相关减值按*信用减值损失归集",
                )
            if "贷款" in note_text and "应收款项" not in note_text:
                return mapping_decision(
                    "（三）*信用减值损失（转回金额以“-”号填列）",
                    "（三）*信用减值损失（转回金额以“-”号填列）",
                    94,
                    "银行类损益表口径：贷款减值按*信用减值损失归集",
                )
            return mapping_decision(
                "（四）*其他资产减值损失（转回金额以“-”号填列）",
                "（四）*其他资产减值损失（转回金额以“-”号填列）",
                94,
                "银行类损益表口径：非信用资产减值按*其他资产减值损失归集",
            )
        if "已赚保费" in fs_text or "保险业务成本" in fs_text:
            return mapping_decision("-", "-", 90, "银行类不适用保险业务专属损益项目，按 '-' 填列")
        if "房地产销售收入" in fs_text:
            return mapping_decision("-", "-", 90, "银行类不适用房地产销售收入，按 '-' 填列")
        if "房地产销售成本" in fs_text:
            return mapping_decision("-", "-", 90, "银行类不适用房地产销售成本，按 '-' 填列")
        if "不良资产处置净收益" in fs_text:
            if "资产处置损失" in note_text and "不良贷款" in note_text:
                return mapping_decision(
                    "（一）主营业务净收入",
                    "（一）主营业务净收入",
                    94,
                    "银行类正确答案口径：资产处置损失-不良贷款归入主营业务净收入",
                )
            return mapping_decision(
                "-",
                "-",
                92,
                "银行类正确答案口径：不良资产处置净收益明细不适用，按 '-' 填列",
            )

    if company_type == "资产公司":
        if "应收利息" in note_text:
            return mapping_decision("应收利息", "应收利息", 96, "资产公司正确答案口径：应收利息各明细归入应收利息，底层资产类型不改变列报项目")
        if "应付利息-" in compact_text(note_line):
            return mapping_decision("应付利息", "应付利息", 96, "资产公司正确答案口径：应付利息各明细归入应付利息")
        asset_company_pnl_context = any(token in fs_text for token in ("资产减值损失", "信用减值损失", "投资收益", "公允价值变动"))
        if not asset_company_pnl_context and "抵债资产" in note_text:
            return mapping_decision("抵债资产", "抵债资产", 96, "资产公司正确答案口径：抵债资产及跌价准备归入抵债资产")
        if "在建工程" in note_text:
            return mapping_decision("固定资产", "固定资产", 96, "资产公司正确答案口径：在建工程及减值准备归入固定资产")
        if "预收款项" in note_text:
            return mapping_decision("应付款项", "应付款项", 96, "资产公司正确答案口径：预收款项归入应付款项")
        if note_text == compact_text("应付利息"):
            return mapping_decision("其他负债", "其他负债", 96, "资产公司正确答案口径：应付利息本体归入其他负债")
        if "衍生金融负债" in note_text or "交易性金融负债" in note_text:
            return mapping_decision("*交易性金融负债", "*交易性金融负债", 96, "资产公司正确答案口径：交易性/衍生金融负债归入*交易性金融负债")
        if "不良资产处置净收益" in fs_text:
            return mapping_decision(
                "（一）主营业务净收入",
                "（一）不良资产经营及处置净收入",
                96,
                "资产公司损益表口径：不良资产处置净收益明细归入主营业务净收入",
            )
        if "房地产销售成本" in fs_text:
            return mapping_decision("-", "-", 96, "资产公司正确答案口径：房地产销售成本不适用，填列 '-'")
        if "提取期货风险准备金" in note_text:
            return mapping_decision("", "", 96, "资产公司正确答案口径：提取期货风险准备金不适用，留空不映射")
        if "利息收入" in fs_text or "利息支出" in fs_text:
            return mapping_decision(
                "（七）其他业务成本",
                "（三）利息净支出",
                94,
                "资产公司损益表口径：利息收入/利息支出按利息净支出及其他业务成本口径归集，NoteLine 仅作为明细",
            )
        if "手续费及佣金收入" in fs_text or "手续费及佣金支出" in fs_text:
            return mapping_decision(
                "（二）中间业务净收入",
                "手续费及佣金净收入",
                94,
                "资产公司损益表口径：手续费及佣金收入/支出按净收入口径归集",
            )
        if "投资收益" in fs_text:
            return mapping_decision(
                "（三）投资收益",
                "投资收益",
                95,
                "损益类 FSLine 为投资收益，NoteLine 中的资产名称仅说明收益来源",
            )
        if "公允价值变动" in fs_text:
            return mapping_decision(
                "（四）公允价值变动收益",
                "公允价值变动收益",
                95,
                "损益类 FSLine 为公允价值变动损益，按利润表公允价值变动收益列示",
            )
        if "其他业务收入" in fs_text:
            return mapping_decision(
                "（六）其他业务收入",
                "其他业务收入",
                92,
                "资产公司损益表口径：其他业务收入按财政部其他业务收入项目列示",
            )
        if "其他业务成本" in fs_text:
            return mapping_decision(
                "（七）其他业务成本",
                "其他业务成本",
                92,
                "资产公司损益表口径：其他业务成本按财政部其他业务成本项目列示",
            )
        if "业务及管理费" in fs_text:
            return mapping_decision(
                "（二）业务及管理费",
                "业务及管理费",
                95,
                "损益类 FSLine 为业务及管理费，折旧摊销等 NoteLine 不改变费用归属",
            )
        if "信用减值损失" in full_text:
            return mapping_decision(
                "（三）*信用减值损失（转回金额以“-”号填列）",
                "*信用减值损失",
                94,
                "资产公司损益表口径：信用减值损失明细按信用减值损失归集",
            )
        if "资产减值损失" in fs_text:
            return mapping_decision(
                "（四）*其他资产减值损失（转回金额以“-”号填列）",
                "*其他资产减值损失",
                94,
                "资产公司损益表口径：非信用资产减值按当前合并填报要求归集",
            )

    if "营业税金及附加" in fs_text or "税金及附加" in fs_text:
        return mapping_decision("（一）税金及附加", "税金及附加", 94, "损益类税金附加按税金及附加列示")
    if "所得税费用" in fs_text:
        return mapping_decision("减：所得税费用", "减：所得税费用", 96, "所得税费用按利润表所得税费用项目列示")
    if "营业外收入" in fs_text:
        return mapping_decision("加：营业外收入", "加：营业外收入", 95, "营业外收入按利润表营业外收入项目列示")
    if "营业外支出" in fs_text:
        return mapping_decision("减：营业外支出", "减：营业外支出", 95, "营业外支出按利润表营业外支出项目列示")
    if "少数股东损益" in fs_text:
        return mapping_decision("少数股东损益", "少数股东损益", 95, "少数股东损益按利润表少数股东损益项目列示")
    if "以前年度损益调整" in fs_text:
        return mapping_decision("未分配利润", "未分配利润", 85, "以前年度损益调整通常结转未分配利润，需结合填报口径复核")

    return None


def enforce_fsline_priority_decision(
    decision: dict[str, object],
    fs_line: str,
    note_line: str,
    company_type: str,
    fiscal_requirement_items: tuple[str, ...] = (),
) -> dict[str, object]:
    priority_decision = fsline_priority_decision(fs_line, note_line, company_type, fiscal_requirement_items)
    if not priority_decision:
        return align_decision_to_requirement_items(decision, fiscal_requirement_items)
    return align_decision_to_requirement_items(priority_decision, fiscal_requirement_items)


def mapping_rules() -> list[MappingRule]:
    return [
        MappingRule(("存放中央银行款项", "存放同业款项", "结算备付金"), "货币资金", "货币资金", 96, "证券类填报口径：存放央行、同业款项和结算备付金归入货币资金", company_types=("证券类",)),
        MappingRule(("以公允价值计量且其变动计入当期损益的金融资产", "货币衍生工具", "利率衍生工具", "权益衍生工具", "其他衍生工具"), "*交易性金融资产", "*交易性金融资产", 96, "证券类填报口径：交易性金融资产及衍生工具明细归入*交易性金融资产", company_types=("证券类",)),
        MappingRule(("应收利息-", "应收利息坏账准备"), "应收利息", "应收利息", 95, "证券类填报口径：应收利息各明细归入应收利息", company_types=("证券类",)),
        MappingRule(("应收款项类投资", "应收款项类金融资产"), "应收款项类投资", "应收款项类投资", 96, "证券类填报口径：应收款项类投资及减值准备归入应收款项类投资", company_types=("证券类",)),
        MappingRule(("抵债资产",), "抵债资产", "抵债资产", 96, "证券类填报口径：抵债资产及跌价准备归入抵债资产", company_types=("证券类",)),
        MappingRule(("其他债权投资",), "其他债权投资", "其他债权投资", 96, "证券类填报口径：其他债权投资及减值准备归入其他债权投资", company_types=("证券类",)),
        MappingRule(("债权投资",), "债权投资", "债权投资", 96, "证券类填报口径：债权投资及减值准备归入债权投资", company_types=("证券类",)),
        MappingRule(("划分为持有代售的资产", "划分为持有待售的资产"), "划分为持有代售的资产", "划分为持有代售的资产", 94, "证券类正确答案口径：划分为持有代售的资产保留原项目列示", company_types=("证券类",)),
        MappingRule(("在建工程", "在建工程减值准备"), "固定资产", "固定资产", 94, "证券类填报口径：在建工程及减值准备归入固定资产", company_types=("证券类",)),
        MappingRule(("交易性金融负债", "衍生金融负债"), "*交易性金融负债", "*交易性金融负债", 96, "证券类填报口径：交易性金融负债及衍生金融负债归入*交易性金融负债", company_types=("证券类",)),
        MappingRule(("同业存放款项",), "同业存放款项", "同业存放款项", 96, "证券类正确答案口径：同业存放款项保留原项目列示", company_types=("证券类",)),
        MappingRule(("其他金融机构存放款项",), "其他金融机构存放款项", "其他金融机构存放款项", 96, "证券类正确答案口径：其他金融机构存放款项保留原项目列示", company_types=("证券类",)),
        MappingRule(("预收款项",), "应付款项", "应付款项", 94, "证券类填报口径：预收款项归入应付款项", company_types=("证券类",)),
        MappingRule(("原保险合同未到期责任准备金",), "原保险合同未到期责任准备金", "原保险合同未到期责任准备金", 96, "证券类正确答案口径：保险准备金负债保留原项目列示", company_types=("证券类",)),
        MappingRule(("再保险合同未到期责任准备金",), "再保险合同未到期责任准备金", "再保险合同未到期责任准备金", 96, "证券类正确答案口径：保险准备金负债保留原项目列示", company_types=("证券类",)),
        MappingRule(("原保险合同未决赔款准备金",), "原保险合同未决赔款准备金", "原保险合同未决赔款准备金", 96, "证券类正确答案口径：保险准备金负债保留原项目列示", company_types=("证券类",)),
        MappingRule(("再保险合同未决赔款准备金",), "再保险合同未决赔款准备金", "再保险合同未决赔款准备金", 96, "证券类正确答案口径：保险准备金负债保留原项目列示", company_types=("证券类",)),
        MappingRule(("原保险合同寿险责任准备金",), "原保险合同寿险责任准备金", "原保险合同寿险责任准备金", 96, "证券类正确答案口径：保险准备金负债保留原项目列示", company_types=("证券类",)),
        MappingRule(("再保险合同寿险责任准备金",), "再保险合同寿险责任准备金", "再保险合同寿险责任准备金", 96, "证券类正确答案口径：保险准备金负债保留原项目列示", company_types=("证券类",)),
        MappingRule(("原保险合同长期健康险责任准备金",), "原保险合同长期健康险责任准备金", "原保险合同长期健康险责任准备金", 96, "证券类正确答案口径：保险准备金负债保留原项目列示", company_types=("证券类",)),
        MappingRule(("再保险合同长期健康险责任准备金",), "再保险合同长期健康险责任准备金", "再保险合同长期健康险责任准备金", 96, "证券类正确答案口径：保险准备金负债保留原项目列示", company_types=("证券类",)),
        MappingRule(("保费准备金",), "保费准备金", "保费准备金", 96, "证券类正确答案口径：保费准备金保留原项目列示", company_types=("证券类",)),
        MappingRule(("期货风险准备金",), "期货风险准备金", "期货风险准备金", 96, "证券类正确答案口径：期货风险准备金保留原项目列示", company_types=("证券类",)),
        MappingRule(("保户储金及投资款",), "保户储金及投资款", "保户储金及投资款", 96, "证券类正确答案口径：保户储金及投资款保留原项目列示", company_types=("证券类",)),
        MappingRule(("存放同业款项",), "拆出资金", "拆出资金", 96, "银行类填报口径：存放同业款项并入拆出资金", company_types=("银行类",)),
        MappingRule(("存出保证金",), "-", "-", 92, "银行类填报要求未列示存出保证金，按不适用填 '-'", company_types=("银行类",)),
        MappingRule(("结算备付金",), "货币资金", "货币资金", 96, "银行类填报口径：结算备付金归入货币资金", company_types=("银行类",)),
        MappingRule(("以公允价值计量且其变动计入当期损益的金融资产-债券投资", "以公允价值计量且其变动计入当期损益的金融资产-基金投资", "以公允价值计量且其变动计入当期损益的金融资产-权益投资", "以公允价值计量且其变动计入当期损益的金融资产-其他投资", "货币衍生工具", "利率衍生工具", "权益衍生工具", "其他衍生工具"), "*交易性金融资产", "*交易性金融资产", 96, "银行类填报口径：交易性金融资产及衍生工具明细归入*交易性金融资产", company_types=("银行类",)),
        MappingRule(("应收款项类投资", "应收款项类金融资产"), "应收款项类金融资产", "应收款项类金融资产", 96, "银行类填报口径：应收款项类投资及减值准备归入应收款项类金融资产", company_types=("银行类",)),
        MappingRule(("应收利息-", "应收利息坏账准备"), "应收利息", "应收利息", 95, "银行类填报口径：应收利息各明细归入应收利息", company_types=("银行类",)),
        MappingRule(("应收保费", "应收保费坏账准备", "应收代位追偿款", "应收分保账款", "应收分保账款坏账准备", "应收分保未到期责任准备金", "应收分保未决赔款准备金", "应收分保寿险责任准备金", "应收分保长期健康险责任准备金"), "-", "-", 92, "银行类不适用保险应收及分保准备金明细，按 '-' 填列", company_types=("银行类",)),
        MappingRule(("其他债权投资",), "*其他债权投资", "*其他债权投资", 96, "银行类填报口径：其他债权投资及减值准备归入*其他债权投资", company_types=("银行类",)),
        MappingRule(("其他权益工具投资",), "*其他权益工具投资", "*其他权益工具投资", 96, "银行类填报口径：其他权益工具投资归入*其他权益工具投资", company_types=("银行类",)),
        MappingRule(("债权投资",), "*债权投资", "*债权投资", 96, "银行类填报口径：债权投资及减值准备归入*债权投资", company_types=("银行类",)),
        MappingRule(("抵债资产",), "抵债资产", "抵债资产", 96, "银行类填报口径：抵债资产及跌价准备归入抵债资产", company_types=("银行类",)),
        MappingRule(("划分为持有代售的资产", "划分为持有待售的资产"), "划分为持有代售的资产", "划分为持有代售的资产", 95, "银行类正确答案口径：划分为持有代售的资产保留原项目列示", company_types=("银行类",)),
        MappingRule(("在建工程", "在建工程减值准备"), "固定资产", "固定资产", 95, "银行类正确答案口径：在建工程及减值准备归入固定资产", company_types=("银行类",)),
        MappingRule(("短期借款", "长期借款"), "-", "-", 94, "银行类填报要求未列示短期借款/长期借款，按不适用填 '-'", company_types=("银行类",)),
        MappingRule(("同业存放款项", "其他金融机构存放款项"), "拆入资金", "拆入资金", 95, "银行类填报口径：同业及其他金融机构存放款项并入拆入资金", company_types=("银行类",)),
        MappingRule(("交易性金融负债", "衍生金融负债"), "*交易性金融负债", "*交易性金融负债", 96, "银行类填报口径：交易性金融负债及衍生金融负债归入*交易性金融负债", company_types=("银行类",)),
        MappingRule(("代理买卖证券款", "期货风险准备金"), "-", "-", 92, "银行类当前填报要求未列示证券/期货专属负债项目，按 '-' 填列", company_types=("银行类",)),
        MappingRule(("保险合同准备金", "原保险合同未到期责任准备金", "再保险合同未到期责任准备金", "原保险合同未决赔款准备金", "再保险合同未决赔款准备金", "原保险合同寿险责任准备金", "再保险合同寿险责任准备金", "原保险合同长期健康险责任准备金", "再保险合同长期健康险责任准备金", "保费准备金", "保户储金及投资款"), "-", "-", 92, "银行类不适用保险专属负债和准备金项目，按 '-' 填列", company_types=("银行类",)),
        MappingRule(("预收保费", "应付手续费及佣金", "应付分保账款", "应付赔付款", "应付保单红利"), "-", "-", 92, "银行类不适用保险应付及手续费佣金应付款明细，按 '-' 填列", company_types=("银行类",)),
        MappingRule(("预收款项",), "应付款项", "应付款项", 92, "银行类填报口径：预收款项归入应付款项", company_types=("银行类",)),
        MappingRule(("原材料", "在产品", "库存商品", "其他存货", "存货跌价准备", "存货"), "-", "-", 92, "银行类填报要求未列示存货明细，按不适用填 '-'", company_types=("银行类",)),
        MappingRule(("存放同业款项",), "货币资金", "货币资金", 96, "资产公司模板口径：存放同业款项归入货币资金", company_types=("资产公司",)),
        MappingRule(("结算备付金",), "货币资金", "货币资金", 96, "资产公司模板口径：结算备付金归入货币资金", company_types=("资产公司",)),
        MappingRule(("持有至到期投资",), "持有至到期投资", "持有至到期投资", 96, "财政部要求保留持有至到期投资项目，相关明细及减值准备归入持有至到期投资", company_types=("资产公司",)),
        MappingRule(("其他债权投资",), "*其他债权投资", "*其他债权投资", 96, "按当前准则版本归入其他债权投资或旧准则可供出售金融资产", company_types=("资产公司",)),
        MappingRule(("其他权益工具投资",), "*其他权益工具投资", "*其他权益工具投资", 96, "按当前准则版本归入其他权益工具投资或旧准则可供出售金融资产", company_types=("资产公司",)),
        MappingRule(("债权投资",), "*债权投资", "*债权投资", 96, "资产公司财政部要求：新金融工具准则债权投资归入*债权投资", company_types=("资产公司",)),
        MappingRule(("应付利息",), "应付利息", "应付利息", 96, "财政部要求单列应付利息项目"),
        MappingRule(("预计负债",), "预计负债", "预计负债", 96, "项目名称明确"),
        MappingRule(("递延所得税负债",), "递延所得税负债", "递延所得税负债", 96, "项目名称明确"),
        MappingRule(("库存现金", "现金", "银行存款", "其他货币资金", "货币资金"), "货币资金", "货币资金", 95, "货币资金及其附注明细直接归入货币资金"),
        MappingRule(("存放中央银行", "法定准备金", "超额准备金"), "存放中央银行款项", "存放中央银行款项", 96, "银行类金融机构专属资产项目"),
        MappingRule(("存放同业", "存放境内同业", "存放境外同业"), "存放同业款项", "存放同业款项", 94, "同业存放资产按金融企业报表项目列示"),
        MappingRule(("拆出资金", "拆放同业", "拆放非银"), "拆出资金", "拆出资金", 94, "拆借类资产按拆出资金列示"),
        MappingRule(("买入返售", "返售金融资产"), "买入返售金融资产", "买入返售金融资产", 94, "买入返售业务按金融资产项目列示"),
        MappingRule(("交易性金融资产-债券投资", "交易性金融资产-基金投资", "交易性金融资产-权益投资", "交易性金融资产-其他投资"), "*交易性金融资产", "*交易性金融资产", 95, "资产公司模板口径：交易性金融资产投资明细按当前填报要求归入*交易性金融资产；若当前候选项不含星号项目则自动回退旧准则长名称", company_types=("资产公司",)),
        MappingRule(("货币衍生工具", "利率衍生工具", "权益衍生工具", "其他衍生工具", "交易性金融资产-购入资产", "待处置资产", "待处置资产减值准备"), "*交易性金融资产", "*交易性金融资产", 94, "资产公司模板口径：衍生工具、购入资产、待处置资产归入*交易性金融资产", company_types=("资产公司",)),
        MappingRule(("交易性金融资产", "以公允价值计量且其变动计入当期损益的金融资产"), "交易性金融资产", "交易性金融资产", 88, "金融工具分类指向交易性金融资产；复杂产品需结合管理模式复核", ("债权投资", "其他债权投资", "其他权益工具投资")),
        MappingRule(("衍生金融资产", "远期", "掉期", "期权", "互换", "衍生工具"), "衍生金融资产", "衍生金融资产", 90, "衍生工具正公允价值通常列入衍生金融资产", ("交易性金融资产",)),
        MappingRule(("发放贷款", "贷款和垫款", "公司贷款", "个人贷款", "票据贴现"), "发放贷款和垫款", "发放贷款和垫款", 93, "信贷资产按发放贷款和垫款列示"),
        MappingRule(("应收票据", "应收账款", "预付账款"), "应收款项", "应收款项", 94, "应收票据、应收账款、预付账款按财政部报表项目归入应收款项"),
        MappingRule(("应收款项类投资", "应收款项类金融资产"), "应收款项类金融资产", "应收款项类金融资产", 94, "应收款项类投资及其减值准备按财政部报表项目归入应收款项类金融资产"),
        MappingRule(("应收股利",), "其他资产", "其他资产", 88, "应收股利通常归入其他资产"),
        MappingRule(("债权投资", "摊余成本", "持有至到期"), "债权投资", "债权投资", 90, "债务工具以摊余成本计量时通常列入债权投资", ("其他债权投资",)),
        MappingRule(("其他债权投资", "公允价值计量且其变动计入其他综合收益的债务工具"), "其他债权投资", "其他债权投资", 91, "FVOCI债务工具通常列入其他债权投资"),
        MappingRule(("其他权益工具投资", "指定为以公允价值计量且其变动计入其他综合收益的权益工具"), "其他权益工具投资", "其他权益工具投资", 91, "指定FVOCI权益工具通常列入其他权益工具投资"),
        MappingRule(("可供出售金融资产",), "可供出售金融资产", "可供出售金融资产", 95, "可供出售金融资产及其股票、债券、其他投资和减值准备明细归入可供出售金融资产"),
        MappingRule(("长期股权投资", "对子公司", "联营企业", "合营企业"), "长期股权投资", "长期股权投资", 90, "股权投资按长期股权投资或相关投资项目列示", ("其他权益工具投资",)),
        MappingRule(("投资性房地产",), "投资性房地产", "投资性房地产", 96, "项目名称明确"),
        MappingRule(("划分为持有代售的资产", "划分为持有待售的资产", "继续涉入资产"), "其他资产", "其他资产", 86, "持有待售或继续涉入资产按当前财政部口径兜底归入其他资产"),
        MappingRule(("固定资产", "房屋及建筑物", "机器设备", "运输工具"), "固定资产", "固定资产", 95, "固定资产附注明细归入固定资产"),
        MappingRule(("在建工程",), "在建工程", "在建工程", 95, "项目名称明确"),
        MappingRule(("使用权资产",), "使用权资产", "使用权资产", 95, "租赁准则项目名称明确"),
        MappingRule(("无形资产", "软件", "土地使用权"), "无形资产", "无形资产", 95, "无形资产附注明细归入无形资产"),
        MappingRule(("商誉",), "商誉", "商誉", 96, "项目名称明确"),
        MappingRule(("递延所得税资产",), "递延所得税资产", "递延所得税资产", 96, "项目名称明确"),
        MappingRule(("存出保证金", "结算备付金", "应收利息", "其他应收", "预付款项", "抵债资产", "长期待摊费用", "存货", "原材料", "在产品", "库存商品", "存货跌价准备"), "其他资产", "其他资产", 82, "通常归入其他资产，但需结合财政部填报明细口径复核", ("货币资金", "金融投资")),
        MappingRule(("短期借款",), "短期借款", "短期借款", 95, "项目名称明确"),
        MappingRule(("向中央银行借款",), "向中央银行借款", "向中央银行借款", 96, "项目名称明确"),
        MappingRule(("同业及其他金融机构存放", "同业存放款项", "其他金融机构存放款项"), "-", "-", 94, "资产公司模板口径：同业及其他金融机构存放款项不适用，填列 '-'", company_types=("资产公司",)),
        MappingRule(("同业及其他金融机构存放", "同业存放", "存放同业负债"), "同业及其他金融机构存放款项", "同业及其他金融机构存放款项", 92, "同业负债按金融企业报表项目列示"),
        MappingRule(("拆入资金",), "拆入资金", "拆入资金", 94, "项目名称明确"),
        MappingRule(("交易性金融负债",), "交易性金融负债", "交易性金融负债", 94, "项目名称明确"),
        MappingRule(("衍生金融负债",), "衍生金融负债", "衍生金融负债", 94, "衍生工具负公允价值通常列入衍生金融负债"),
        MappingRule(("卖出回购", "回购金融资产款"), "卖出回购金融资产款", "卖出回购金融资产款", 94, "卖出回购业务按金融负债项目列示"),
        MappingRule(("吸收存款", "活期存款", "定期存款负债", "保证金存款"), "吸收存款", "吸收存款", 92, "客户存款按吸收存款列示"),
        MappingRule(("应付职工薪酬", "工资", "福利费", "社保"), "应付职工薪酬", "应付职工薪酬", 94, "职工薪酬明细归入应付职工薪酬"),
        MappingRule(("应交税费", "所得税", "增值税"), "应交税费", "应交税费", 93, "税费负债归入应交税费"),
        MappingRule(("应付债券", "金融债", "二级资本债", "同业存单", "永续债"), "应付债券", "应付债券", 86, "发行债务工具通常列入应付债券；永续债需结合权益/负债分类复核", ("其他权益工具",)),
        MappingRule(("租赁负债",), "租赁负债", "租赁负债", 95, "租赁准则项目名称明确"),
        MappingRule(("递延所得税负债",), "递延所得税负债", "递延所得税负债", 96, "项目名称明确"),
        MappingRule(("应付账款", "预收保费", "应付分保账款", "应付赔付款", "应付保单红利"), "应付款项", "应付款项", 92, "应付账款及保险业务应付款项明细归入应付款项"),
        MappingRule(("长期借款",), "长期借款", "长期借款", 95, "项目名称明确"),
        MappingRule(("代理买卖证券款", "继续涉入负债", "专项应付款", "长期应付款"), "其他负债", "其他负债", 84, "该类负债按当前财政部口径兜底归入其他负债"),
        MappingRule(("保险合同准备金", "保户储金及投资款", "已赚保费", "保险业务成本"), "-", "-", 90, "当前机构口径下保险专属项目不适用，按要求填列 '-' ", company_types=("资产公司",)),
        MappingRule(("其他应付", "预收款项", "预计负债", "应付利息", "其他负债"), "其他负债", "其他负债", 82, "通常归入其他负债，但需结合填报明细口径复核"),
        MappingRule(("股本", "实收资本"), "股本", "实收资本", 90, "股份制主体合并口径通常列股本，单体可按实收资本/股本列示", ("实收资本",)),
        MappingRule(("其他权益工具", "优先股", "永续债权益"), "其他权益工具", "其他权益工具", 88, "权益工具分类需结合合同条款复核"),
        MappingRule(("资本公积",), "资本公积", "资本公积", 95, "项目名称明确"),
        MappingRule(("其他综合收益",), "其他综合收益", "其他综合收益", 95, "项目名称明确"),
        MappingRule(("盈余公积",), "盈余公积", "盈余公积", 95, "项目名称明确"),
        MappingRule(("一般风险准备",), "一般风险准备", "一般风险准备", 95, "金融企业权益项目名称明确"),
        MappingRule(("未分配利润",), "未分配利润", "未分配利润", 95, "项目名称明确"),
        MappingRule(("少数股东权益",), "少数股东权益", "少数股东权益", 95, "项目名称明确"),
        MappingRule(("不良资产处置净收益",), "（一）主营业务净收入", "（一）不良资产经营及处置净收入", 86, "资产公司不良资产处置净收益按主营业务净收入/不良资产经营及处置净收入列示"),
        MappingRule(("利息收入", "利息支出", "利息净收入"), "利息净收入", "利息净收入", 86, "损益类利息项目按利息净收入归集，收入/支出方向需复核"),
        MappingRule(("手续费及佣金",), "手续费及佣金净收入", "手续费及佣金净收入", 86, "手续费及佣金收入支出按净收入口径归集"),
        MappingRule(("投资收益",), "投资收益", "投资收益", 90, "项目名称明确"),
        MappingRule(("汇兑损益",), "（六）汇兑收益（损失以“-”号填列）", "（五）汇兑收益（损失以“-”号填列）", 88, "汇兑损益按汇兑收益项目列示"),
        MappingRule(("营业外收入",), "加：营业外收入", "加：营业外收入", 92, "项目名称明确"),
        MappingRule(("房地产销售收入",), "-", "-", 94, "资产公司模板口径：房地产销售收入不适用，填列 '-'", company_types=("资产公司",)),
        MappingRule(("其他业务收入", "租赁收入"), "（七）其他业务收入", "（六）其他业务收入", 84, "其他业务收入按财政部损益表其他业务收入项目列示"),
        MappingRule(("其他业务成本", "租赁成本"), "其他业务成本", "其他业务成本", 84, "其他业务成本按财政部损益表其他业务成本项目列示"),
        MappingRule(("营业税金及附加", "税金及附加"), "（一）税金及附加", "（一）税金及附加", 88, "税金及附加按财政部损益表税金及附加项目列示"),
        MappingRule(("公允价值变动",), "公允价值变动收益", "公允价值变动收益", 88, "公允价值变动损益按利润表项目列示"),
        MappingRule(("业务及管理费", "职工费用", "折旧费用", "摊销费用"), "业务及管理费", "业务及管理费", 88, "经营管理费用通常归入业务及管理费"),
        MappingRule(("信用减值损失", "减值损失", "预期信用损失"), "信用减值损失", "信用减值损失", 86, "减值类损益需结合资产类别复核"),
        MappingRule(("所得税费用",), "所得税费用", "所得税费用", 95, "项目名称明确"),
    ]


def write_mapping_workbook(result_df: pd.DataFrame, output_path: Path) -> None:
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        result_df.to_excel(writer, index=False, sheet_name="智能映射结果")
        workbook = writer.book
        worksheet = writer.sheets["智能映射结果"]
        worksheet.freeze_panes = "A2"
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 42)
        review_fill = PatternFill("solid", fgColor="FFF2CC")
        for row in range(2, worksheet.max_row + 1):
            if worksheet.cell(row=row, column=8).value == "是":
                for col in range(1, worksheet.max_column + 1):
                    worksheet.cell(row=row, column=col).fill = review_fill
        del workbook
