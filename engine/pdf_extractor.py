from pathlib import Path
import re
from typing import Any

import fitz
import pandas as pd


DEFAULT_BALANCE_SHEET_KEYWORDS = [
    "合并及母公司资产负债表",
    "资产负债表",
    "现金及存放中央银行款项",
    "发放贷款和垫款",
    "负债和股东权益总计",
]
DEFAULT_INCOME_STATEMENT_KEYWORDS = [
    "合并及母公司利润表",
    "利润表",
    "利息净收入",
    "营业收入",
    "营业利润",
    "利润总额",
    "净利润",
]

AMOUNT_PATTERN = re.compile(
    r"""
    (?P<amount>
        \(?\s*-?
        (?:\d{1,3}(?:,\d{3})+|\d+)
        (?:\.\d+)?
        \s*\)?
    )
    """,
    re.VERBOSE,
)
PERCENT_PATTERN = re.compile(r"(?P<percent>-?\d+(?:\.\d+)?)\s*%")


def extract_pdf_text(pdf_path: str | Path) -> list[dict[str, Any]]:
    """Extract text from every page in a PDF with 1-based page numbers."""
    path = Path(pdf_path)
    _validate_pdf_path(path)

    try:
        pages: list[dict[str, Any]] = []
        with fitz.open(path) as document:
            for page_index, page in enumerate(document, start=1):
                pages.append(
                    {
                        "page_no": page_index,
                        "text": page.get_text("text") or "",
                    }
                )
        return pages
    except Exception as exc:
        raise ValueError(f"提取 PDF 文本失败：{exc}") from exc


def find_pages_by_keywords(
    pdf_path: str | Path,
    keywords: list[str] | tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    """Locate pages containing any of the supplied keywords."""
    search_keywords = list(keywords or DEFAULT_BALANCE_SHEET_KEYWORDS)
    pages = extract_pdf_text(pdf_path)
    matched_pages: list[dict[str, Any]] = []

    for page in pages:
        text = page["text"]
        matched_keywords = [keyword for keyword in search_keywords if keyword in text]
        if not matched_keywords:
            continue

        matched_pages.append(
            {
                "page_no": page["page_no"],
                "text": text,
                "matched_keywords": matched_keywords,
                "score": len(matched_keywords),
            }
        )

    return sorted(matched_pages, key=lambda item: (-item["score"], item["page_no"]))


def extract_balance_sheet_text(pdf_path: str | Path) -> list[dict[str, Any]]:
    """Return text from the pages most likely to contain balance sheet disclosure."""
    return extract_report_text(
        pdf_path,
        DEFAULT_BALANCE_SHEET_KEYWORDS,
        "合并及母公司资产负债表",
    )


def extract_income_statement_text(pdf_path: str | Path) -> list[dict[str, Any]]:
    """Return text from the pages most likely to contain income statement disclosure."""
    return extract_report_text(
        pdf_path,
        DEFAULT_INCOME_STATEMENT_KEYWORDS,
        "合并及母公司利润表",
    )


def extract_report_text(
    pdf_path: str | Path,
    keywords: list[str] | tuple[str, ...],
    title_keyword: str | None = None,
) -> list[dict[str, Any]]:
    """Return text from the pages most likely to contain one report disclosure."""
    matched_pages = find_pages_by_keywords(pdf_path, keywords)
    if not matched_pages:
        return []

    if title_keyword is None:
        title_keyword = str(keywords[0]) if keywords else ""
    selected_page_numbers = _select_report_page_numbers(matched_pages, title_keyword)
    standalone_title_pages = _standalone_title_page_numbers(matched_pages, title_keyword)
    if standalone_title_pages:
        selected_page_numbers = standalone_title_pages

    # Include neighboring pages because financial statements often span pages.
    expanded_page_numbers: set[int] = set()
    all_pages = extract_pdf_text(pdf_path)
    max_page_no = len(all_pages)
    # Note disclosures can continue onto the page immediately after a standalone
    # title/table page, for example the deposit reserve ratio rows.
    offsets = (0, 1) if standalone_title_pages else (-1, 0, 1, 2)
    for page_no in selected_page_numbers:
        for offset in offsets:
            candidate = page_no + offset
            if 1 <= candidate <= max_page_no:
                expanded_page_numbers.add(candidate)

    return [
        page
        for page in all_pages
        if page["page_no"] in sorted(expanded_page_numbers)
    ]


def parse_amounts_from_text(
    text: str | list[dict[str, Any]],
    item_names: list[str] | tuple[str, ...],
) -> pd.DataFrame:
    """Parse disclosed group and parent amounts for balance sheet items."""
    page_texts = _normalize_text_input(text)
    rows: list[dict[str, Any]] = []
    item_name_list = [str(item_name) for item_name in item_names]

    for item_name in item_name_list:
        matched_page_no: int | None = None
        matched_line = ""
        group_amount: float | None = None
        parent_amount: float | None = None

        for match_mode in ("exact", "partial"):
            for page in page_texts:
                parsed = _find_item_amounts_on_page(
                    page["text"],
                    item_name,
                    item_name_list,
                    match_mode,
                )
                if parsed is not None:
                    matched_page_no = page["page_no"]
                    matched_line = parsed["raw_text"]
                    group_amount = parsed["group_amount"]
                    parent_amount = parsed["parent_amount"]
                    break
            if matched_line:
                break

        rows.append(
            {
                "指标名称": item_name,
                "PDF披露金额-集团": group_amount,
                "PDF披露金额-本行": parent_amount,
                "PDF来源页码": matched_page_no,
                "PDF原始行文本": matched_line,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "指标名称",
            "PDF披露金额-集团",
            "PDF披露金额-本行",
            "PDF来源页码",
            "PDF原始行文本",
        ],
    )


def parse_note_table_amounts_from_text(
    text: str | list[dict[str, Any]],
    item_names: list[str] | tuple[str, ...],
    item_aliases: dict[str, list[str]] | None = None,
) -> pd.DataFrame:
    """Parse one-column note tables where each row label is followed by current/prior amounts."""
    page_texts = _normalize_text_input(text)
    aliases_by_item = item_aliases or {}
    all_aliases = [
        alias
        for item_name in item_names
        for alias in [str(item_name), *aliases_by_item.get(str(item_name), [])]
    ]
    page_texts = sorted(
        page_texts,
        key=lambda page: _note_table_alias_score(page["text"], all_aliases),
        reverse=True,
    )
    rows: list[dict[str, Any]] = []

    for item_name in [str(item_name) for item_name in item_names]:
        matched_page_no: int | None = None
        matched_line = ""
        group_amount: float | None = None
        parent_amount: float | None = None
        aliases = aliases_by_item.get(item_name) or [item_name]

        for page in page_texts:
            if "缴存比率" in item_name:
                parsed = _find_percentage_item_value(page["text"], aliases)
            else:
                parsed = _find_note_table_item_amount(page["text"], aliases)
            if parsed is None:
                continue
            matched_page_no = page["page_no"]
            matched_line = parsed["raw_text"]
            group_amount = parsed["group_amount"]
            parent_amount = parsed["parent_amount"]
            break

        rows.append(
            {
                "指标名称": item_name,
                "PDF披露金额-集团": group_amount,
                "PDF披露金额-本行": parent_amount,
                "PDF来源页码": matched_page_no,
                "PDF原始行文本": matched_line,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "指标名称",
            "PDF披露金额-集团",
            "PDF披露金额-本行",
            "PDF来源页码",
            "PDF原始行文本",
        ],
    )


def _find_percentage_item_value(text: str, aliases: list[str]) -> dict[str, Any] | None:
    lines = [_normalize_line(line) for line in text.splitlines() if line.strip()]
    compact_aliases = {_compact_text(alias) for alias in aliases if _compact_text(alias)}
    for index, line in enumerate(lines):
        compact_line = _compact_text(line)
        if not _note_label_matches_alias(compact_line, compact_aliases):
            continue
        raw_lines = [line]
        percent_values: list[float] = []
        for next_line in lines[index + 1 : index + 5]:
            normalized_next = _normalize_line(next_line)
            if _looks_like_item_label(normalized_next) and not PERCENT_PATTERN.search(normalized_next):
                break
            raw_lines.append(normalized_next)
            for match in PERCENT_PATTERN.finditer(normalized_next):
                percent_values.append(float(match.group("percent")) / 100)
            if len(percent_values) >= 2:
                break
        if percent_values:
            return {
                "group_amount": percent_values[0],
                "parent_amount": percent_values[0],
                "raw_text": " | ".join(raw_lines),
            }
    return None


def parse_detail_item_amounts_from_text(
    text: str | list[dict[str, Any]],
    item_names: list[str] | tuple[str, ...],
    item_aliases: dict[str, list[str]] | None = None,
) -> pd.DataFrame:
    """Parse detail tables by matching each item name inside the row segment."""
    page_texts = _normalize_text_input(text)
    aliases_by_item = item_aliases or {}
    all_aliases = [
        alias
        for item_name in item_names
        for alias in [str(item_name), *aliases_by_item.get(str(item_name), [])]
    ]
    page_texts = sorted(
        page_texts,
        key=lambda page: _note_table_alias_score(page["text"], all_aliases),
        reverse=True,
    )
    rows: list[dict[str, Any]] = []

    for item_name in [str(item_name) for item_name in item_names]:
        matched_page_no: int | None = None
        matched_line = ""
        group_amount: float | None = None
        parent_amount: float | None = None
        aliases = aliases_by_item.get(item_name) or [item_name]

        if not _is_generic_total_item(item_name, aliases):
            for page in page_texts:
                parsed = _find_detail_item_amount(page["text"], aliases, all_aliases)
                if parsed is None:
                    continue
                matched_page_no = page["page_no"]
                matched_line = parsed["raw_text"]
                group_amount = parsed["group_amount"]
                parent_amount = parsed["parent_amount"]
                break

        rows.append(
            {
                "指标名称": item_name,
                "PDF披露金额-集团": group_amount,
                "PDF披露金额-本行": parent_amount,
                "PDF来源页码": matched_page_no,
                "PDF原始行文本": matched_line,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "指标名称",
            "PDF披露金额-集团",
            "PDF披露金额-本行",
            "PDF来源页码",
            "PDF原始行文本",
        ],
    )


def _is_generic_total_item(item_name: str, aliases: list[str]) -> bool:
    compact_values = {_compact_text(value) for value in [item_name, *aliases]}
    return compact_values.issubset({"合计", "总计"})


def _find_note_table_item_amount(text: str, aliases: list[str]) -> dict[str, Any] | None:
    lines = [_normalize_line(line) for line in text.splitlines() if line.strip()]
    compact_aliases = {_compact_text(alias) for alias in aliases if _compact_text(alias)}

    multiline_result = _find_multiline_note_table_item_amount(lines, compact_aliases)
    if multiline_result is not None:
        return multiline_result

    for index, line in enumerate(lines):
        compact_line = _compact_text(line)
        if compact_line not in compact_aliases:
            continue

        amount_values: list[float | None] = []
        raw_lines = [line]
        for next_line in lines[index + 1 : index + 10]:
            normalized_next = _normalize_line(next_line)
            compact_next = _compact_text(normalized_next)
            if compact_next in compact_aliases:
                continue
            if _is_note_reference_line(normalized_next) or re.fullmatch(r"\(?\d+\)?", normalized_next):
                raw_lines.append(normalized_next)
                continue
            if _looks_like_item_label(normalized_next) and not _is_note_reference_line(normalized_next):
                break

            extracted = _extract_amount_or_dash_values(normalized_next)
            if extracted:
                amount_values.extend(extracted)
                raw_lines.append(normalized_next)
            if len(amount_values) >= 4:
                break

        if not amount_values:
            continue
        group_amount, parent_amount = _pick_current_year_group_parent(amount_values)
        return {
            "group_amount": group_amount,
            "parent_amount": parent_amount,
            "raw_text": " | ".join(raw_lines),
        }

    return None


def _find_multiline_note_table_item_amount(
    lines: list[str],
    compact_aliases: set[str],
) -> dict[str, Any] | None:
    """Match note rows whose label is split across multiple PDF text lines."""
    if not compact_aliases:
        return None

    for index, line in enumerate(lines):
        if _extract_amount_or_dash_values(line):
            continue

        label_lines: list[str] = _inherited_note_table_label_prefix(lines, index)
        amount_start_index: int | None = None
        for candidate_index in range(index, min(len(lines), index + 5)):
            candidate = _normalize_line(lines[candidate_index])
            if _is_note_reference_line(candidate) or re.fullmatch(r"\(?\d+\)?", candidate):
                continue
            if _extract_amount_or_dash_values(candidate):
                amount_start_index = candidate_index
                break
            if not _looks_like_item_label(candidate):
                break
            label_lines.append(candidate)

            compact_label = _compact_text("".join(label_lines))
            if _note_label_matches_alias(compact_label, compact_aliases):
                amount_start_index = candidate_index + 1
                break

        if amount_start_index is None or not label_lines:
            continue

        compact_label = _compact_text("".join(label_lines))
        if not _note_label_matches_alias(compact_label, compact_aliases):
            continue

        amount_values: list[float | None] = []
        raw_lines = label_lines.copy()
        for next_line in lines[amount_start_index : amount_start_index + 10]:
            normalized_next = _normalize_line(next_line)
            if _is_note_reference_line(normalized_next) or re.fullmatch(r"\(?\d+\)?", normalized_next):
                raw_lines.append(normalized_next)
                continue
            if _looks_like_item_label(normalized_next) and not _extract_amount_or_dash_values(normalized_next):
                break

            extracted = _extract_amount_or_dash_values(normalized_next)
            if extracted:
                amount_values.extend(extracted)
                raw_lines.append(normalized_next)
            if len(amount_values) >= 4:
                break

        if not amount_values:
            continue

        group_amount, parent_amount = _pick_current_year_group_parent(amount_values)
        return {
            "group_amount": group_amount,
            "parent_amount": parent_amount,
            "raw_text": " | ".join(raw_lines),
        }

    return None


def _note_label_matches_alias(compact_label: str, compact_aliases: set[str]) -> bool:
    if compact_label in compact_aliases:
        return True
    for alias in compact_aliases:
        if alias and compact_label.endswith(alias):
            return True
        if alias and "存放中央银行款项" in alias and "其他" in alias:
            if "存放中央银行款项" in compact_label and "其他" in compact_label:
                return True
    return False


def _inherited_note_table_label_prefix(lines: list[str], index: int) -> list[str]:
    """Reuse section labels such as 中国境内 for following '- 银行' rows."""
    current_line = _normalize_line(lines[index]) if index < len(lines) else ""
    if not current_line.lstrip().startswith(("-", "－", "—")):
        return []

    for previous_index in range(index - 1, max(-1, index - 20), -1):
        previous_line = _normalize_line(lines[previous_index])
        if _extract_amount_or_dash_values(previous_line):
            continue
        if not _looks_like_item_label(previous_line):
            continue
        if previous_line.lstrip().startswith(("-", "－", "—")):
            continue
        return [previous_line]
    return []


def _find_detail_item_amount(
    text: str,
    aliases: list[str],
    all_aliases: list[str],
) -> dict[str, Any] | None:
    lines = [_normalize_line(line) for line in text.splitlines() if line.strip()]
    compact_aliases = {_compact_text(alias) for alias in aliases if _compact_text(alias)}
    compact_all_aliases = sorted(
        {_compact_text(alias) for alias in all_aliases if _compact_text(alias)},
        key=len,
        reverse=True,
    )

    for index, line in enumerate(lines):
        compact_line = _compact_text(line)
        matched_alias = next((alias for alias in compact_aliases if alias and alias in compact_line), "")
        if not matched_alias:
            continue

        segment_lines = [line]
        current_segment = line
        current_compact_segment = compact_line
        if not _amount_values_after_alias(current_segment, matched_alias):
            for next_line in lines[index + 1 : index + 8]:
                normalized_next = _normalize_line(next_line)
                next_compact = _compact_text(normalized_next)
                if _line_starts_other_detail_item(next_compact, matched_alias, compact_all_aliases):
                    break
                segment_lines.append(normalized_next)
                current_segment = " ".join(segment_lines)
                current_compact_segment = _compact_text(current_segment)
                if _amount_values_after_alias(current_segment, matched_alias):
                    break

        amount_values = _amount_values_after_alias(current_segment, matched_alias)
        if not amount_values:
            continue
        group_amount, parent_amount = _pick_detail_current_amount(amount_values)
        return {
            "group_amount": group_amount,
            "parent_amount": parent_amount,
            "raw_text": " | ".join(segment_lines),
        }

    return None


def _pick_detail_current_amount(
    amount_values: list[float | None],
) -> tuple[float | None, float | None]:
    if not amount_values:
        return None, None
    # Detail note tables usually disclose current/prior period, not group/parent.
    # Use the current-period value for both validation columns so scope filtering
    # does not turn a correctly parsed row into a missing value.
    return amount_values[0], amount_values[0]


def _amount_values_after_alias(segment: str, compact_alias: str) -> list[float | None]:
    if not segment or not compact_alias:
        return []
    compact_segment = _compact_text(segment)
    alias_index = compact_segment.find(compact_alias)
    if alias_index < 0:
        return []

    prefix_amount_count = len(AMOUNT_PATTERN.findall(compact_segment[:alias_index]))
    values = [_parse_amount(match.group("amount")) for match in AMOUNT_PATTERN.finditer(segment)]
    if prefix_amount_count:
        values = values[prefix_amount_count:]
    return [value for value in values if value is not None]


def _line_starts_other_detail_item(
    compact_line: str,
    current_alias: str,
    compact_all_aliases: list[str],
) -> bool:
    if not compact_line:
        return False
    for alias in compact_all_aliases:
        if alias == current_alias:
            continue
        if compact_line.startswith(alias):
            return True
    return False


def _note_table_alias_score(text: str, aliases: list[str]) -> int:
    compact_text = _compact_text(text)
    return sum(1 for alias in aliases if _compact_text(alias) in compact_text)


def _select_report_page_numbers(
    matched_pages: list[dict[str, Any]],
    title_keyword: str,
) -> set[int]:
    """Prefer high-scoring pages with the exact report title over notes/summary pages."""
    title_pages = [
        page
        for page in matched_pages
        if title_keyword in page.get("matched_keywords", [])
    ]
    if title_pages:
        best_title_score = max(page["score"] for page in title_pages)
        return {
            page["page_no"]
            for page in title_pages
            if page["score"] == best_title_score
        }

    best_score = matched_pages[0]["score"]
    return {page["page_no"] for page in matched_pages if page["score"] == best_score}


def _standalone_title_page_numbers(
    matched_pages: list[dict[str, Any]],
    title_keyword: str,
) -> set[int]:
    """Return pages where the report title appears as its own PDF text line."""
    compact_title = _compact_text(title_keyword)
    if not compact_title:
        return set()
    pages: set[int] = set()
    for page in matched_pages:
        for line in str(page.get("text") or "").splitlines():
            if _compact_text(line) == compact_title:
                pages.add(page["page_no"])
                break
    return pages


def _validate_pdf_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"PDF 文件不存在：{path}")
    if not path.is_file():
        raise ValueError(f"PDF 路径不是文件：{path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"文件不是 PDF：{path}")


def _normalize_text_input(text: str | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(text, str):
        return [{"page_no": None, "text": text}]
    if isinstance(text, list):
        normalized: list[dict[str, Any]] = []
        for index, item in enumerate(text, start=1):
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "page_no": item.get("page_no", index),
                    "text": str(item.get("text", "")),
                }
            )
        return normalized
    raise TypeError("text 必须是字符串，或 extract_pdf_text 返回的页面列表。")


def _find_line_for_item(text: str, item_name: str) -> str:
    normalized_item_name = _compact_text(item_name)
    lines = [_normalize_line(line) for line in text.splitlines()]

    for line in lines:
        if normalized_item_name in _compact_text(line):
            return line
    return ""


def _find_item_amounts_on_page(
    text: str,
    item_name: str,
    all_item_names: list[str],
    match_mode: str,
) -> dict[str, Any] | None:
    lines = [_normalize_line(line) for line in text.splitlines() if line.strip()]
    item_aliases = {_compact_text(alias) for alias in _item_aliases(item_name)}

    for index, line in enumerate(lines):
        if _is_amount_only_line(line):
            continue

        candidate_name_text = " ".join(lines[index : index + 4])
        if not _line_matches_item(candidate_name_text, item_aliases, match_mode):
            continue

        raw_lines = [line]
        amount_values = _extract_amount_or_dash_values(line)

        for next_line in lines[index + 1 :]:
            if _is_next_item_line(next_line, item_name, all_item_names):
                break

            raw_lines.append(next_line)
            amount_values.extend(_extract_amount_or_dash_values(next_line))
            if len(amount_values) >= 4:
                break

        group_amount, parent_amount = _pick_current_year_group_parent(amount_values)
        if not amount_values:
            continue
        return {
            "group_amount": group_amount,
            "parent_amount": parent_amount,
            "raw_text": " | ".join(raw_lines),
        }

    return None


def _is_next_item_line(line: str, current_item_name: str, all_item_names: list[str]) -> bool:
    compact_line = _compact_text(line)
    compact_current = _compact_text(current_item_name)
    if not compact_line:
        return False

    for item_name in all_item_names:
        if item_name == current_item_name:
            continue
        item_aliases = {_compact_text(alias) for alias in _item_aliases(item_name)}
        if any(alias and alias in compact_current for alias in item_aliases):
            continue
        if _line_matches_item(line, item_aliases, "partial"):
            return True

    return False


def _line_matches_item(line: str, item_aliases: set[str], match_mode: str) -> bool:
    compact_line = _compact_text(line)
    if match_mode == "exact":
        return compact_line in item_aliases
    return any(_contains_item_alias(compact_line, alias) for alias in item_aliases)


def _contains_item_alias(compact_line: str, alias: str) -> bool:
    if not alias:
        return False
    start = compact_line.find(alias)
    if start < 0:
        return False

    end = start + len(alias)
    if start > 0:
        previous_char = compact_line[start - 1]
        if re.match(r"[\u4e00-\u9fff]", previous_char):
            return False

    if end >= len(compact_line):
        return True

    next_char = compact_line[end]
    if re.match(r"[\d,，()（）\-－—|:：/、]", next_char):
        return True
    if next_char in {"一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "附"}:
        return True
    return not re.match(r"[\u4e00-\u9fff]", next_char)


def _item_aliases(item_name: str) -> list[str]:
    aliases = [item_name]
    alias_map = {
        "资产总额": ["资产总计"],
        "负债总额": ["负债合计"],
        "股东权益": ["股东权益合计"],
        "归属于母公司股东权益": ["归属于母公司股东权益合计"],
        "负债和股东权益": ["负债和股东权益总计"],
        "营业收入": ["营业总收入"],
        "营业支出": ["营业总支出", "营业支出合计"],
        "业务及管理费用": ["业务及管理费"],
        "公允价值变动净（损失）/收益": ["公允价值变动净(损失)/收益"],
        "汇兑净收益": ["汇兑净(损失)/收益"],
        "营业外支出": ["减:营业外支出"],
        "所得税费用": ["减:所得税费用"],
        "归属于母公司股东净利润": ["归属于母公司股东的净利润"],
        "归属于母公司股东的净利润": ["归属于母公司股东的净利润"],
        "净利润": ["净利润"],
    }
    aliases.extend(alias_map.get(item_name, []))

    if item_name.endswith("总额"):
        aliases.append(f"{item_name[:-2]}总计")
    return list(dict.fromkeys(aliases))


def _normalize_line(line: str) -> str:
    return " ".join(line.replace("\t", " ").split())


def _compact_text(value: Any) -> str:
    text = str(value)
    replacements = {
        "（": "(",
        "）": ")",
        "／": "/",
        "：": ":",
        "\u200a": "",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return re.sub(r"\s+", "", text)


def _extract_group_parent_amounts(line: str) -> tuple[float | None, float | None]:
    if not line:
        return None, None

    amounts = [_parse_amount(match.group("amount")) for match in AMOUNT_PATTERN.finditer(line)]
    amounts = [amount for amount in amounts if amount is not None]

    if not amounts:
        return None, None
    if len(amounts) == 1:
        return amounts[0], None
    return amounts[0], amounts[1]


def _extract_amount_or_dash_values(line: str) -> list[float | None]:
    values: list[float | None] = []
    stripped = line.strip()
    if _is_note_reference_line(stripped):
        return values
    if stripped in {"-", "－", "—"}:
        return [0.0]
    amount_source = _strip_leading_item_number(stripped)
    if _looks_like_item_label(amount_source):
        return values

    for match in AMOUNT_PATTERN.finditer(amount_source):
        values.append(_parse_amount(match.group("amount")))
    return values


def _strip_leading_item_number(line: str) -> str:
    return re.sub(r"^\s*(?:\(?\d+\)|（\d+）|\d+[.、]\s+)\s*", "", line)


def _looks_like_item_label(line: str) -> bool:
    has_cjk = bool(re.search(r"[\u4e00-\u9fff]", line))
    has_amount_like_number = bool(re.search(r"\d{1,3}(?:,\d{3})+|\(\s*\d", line))
    return has_cjk and not has_amount_like_number


def _is_amount_only_line(line: str) -> bool:
    stripped = line.strip()
    if stripped in {"-", "－", "—"}:
        return True
    if re.fullmatch(r"\(?\s*-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*\)?", stripped):
        return True
    return False


def _is_note_reference_line(line: str) -> bool:
    return bool(re.fullmatch(r"[一二三四五六七八九十]+、\d+(?:\.\d+)?", line))


def _pick_current_year_group_parent(
    amount_values: list[float | None],
) -> tuple[float | None, float | None]:
    if not amount_values:
        return None, None
    if len(amount_values) >= 4:
        return amount_values[0], amount_values[2]
    if len(amount_values) >= 2:
        return amount_values[0], amount_values[1]
    return amount_values[0], None


def _parse_amount(value: str) -> float | None:
    cleaned = value.strip().replace(",", "")
    if not cleaned:
        return None

    is_parentheses_negative = cleaned.startswith("(") and cleaned.endswith(")")
    cleaned = cleaned.strip("()").strip()

    if cleaned.startswith("-"):
        cleaned = cleaned[1:]
        is_parentheses_negative = True

    try:
        amount = float(cleaned)
    except ValueError:
        return None

    return -amount if is_parentheses_negative else amount
