from pathlib import Path
from typing import Any

import pandas as pd


BALANCE_SHEET_KEYWORD = "合并及母公司资产负债表"
INCOME_STATEMENT_KEYWORD = "合并及母公司利润表"
TARGET_COLUMNS = [
    "报表名称",
    "指标编码",
    "指标名称",
    "数据来源",
    "指标类型",
    "加工规则",
    "集团金额",
    "本行金额",
]


def read_excel_sheets(file_path: str | Path) -> dict[str, pd.DataFrame]:
    """Return every sheet name with its first 10 rows as a preview DataFrame."""
    path = Path(file_path)
    _validate_excel_path(path)

    try:
        excel_file = pd.ExcelFile(path, engine="openpyxl")
        previews: dict[str, pd.DataFrame] = {}

        for sheet_name in excel_file.sheet_names:
            preview = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                header=None,
                nrows=10,
                dtype=object,
            )
            previews[sheet_name] = _clean_dataframe_values(preview)

        return previews
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"读取 Excel sheet 预览失败：{exc}") from exc


def find_balance_sheet_rules(file_path: str | Path) -> pd.DataFrame:
    """Find rows related to the balance sheet rules across all Excel sheets."""
    return find_rules_by_report_name(file_path, BALANCE_SHEET_KEYWORD)


def find_income_statement_rules(file_path: str | Path) -> pd.DataFrame:
    """Find rows related to the income statement rules across all Excel sheets."""
    return find_rules_by_report_name(file_path, INCOME_STATEMENT_KEYWORD)


def find_rules_by_report_name(file_path: str | Path, report_name: str) -> pd.DataFrame:
    """Find rows related to one report name across all Excel sheets."""
    return find_report_rules(file_path, report_name)


def find_report_rules(file_path: str | Path, rule_keyword: str) -> pd.DataFrame:
    """Find report rules by configured keyword across all Excel sheets."""
    path = Path(file_path)
    _validate_excel_path(path)

    try:
        excel_file = pd.ExcelFile(path, engine="openpyxl")
        matched_frames: list[pd.DataFrame] = []

        for sheet_name in excel_file.sheet_names:
            raw_df = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                header=None,
                dtype=object,
            )
            raw_df = _clean_dataframe_values(raw_df)
            if raw_df.empty:
                continue

            matched_rows = _find_keyword_rows(raw_df, rule_keyword)
            if matched_rows.empty:
                continue

            parsed_rows = _apply_detected_header(raw_df, matched_rows)
            parsed_rows.insert(0, "_sheet_name", sheet_name)
            matched_frames.append(parsed_rows)

        if not matched_frames:
            return pd.DataFrame()

        result = pd.concat(matched_frames, ignore_index=True)
        result = normalize_columns(result)
        result = _select_target_columns_when_available(result)
        return result.reset_index(drop=True)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"查找{rule_keyword}加工规则失败：{exc}") from exc


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Clean spaces and line breaks in DataFrame column names."""
    normalized_df = df.copy()
    normalized_df.columns = [_normalize_text(column) for column in normalized_df.columns]
    return normalized_df


def _validate_excel_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Excel 文件不存在：{path}")
    if not path.is_file():
        raise ValueError(f"Excel 路径不是文件：{path}")


def _clean_dataframe_values(df: pd.DataFrame) -> pd.DataFrame:
    """Drop fully empty rows/columns and forward-fill sparse cells from merges."""
    cleaned = df.dropna(how="all").dropna(axis=1, how="all")
    if cleaned.empty:
        return cleaned

    cleaned = cleaned.ffill()
    cleaned = cleaned.map(_clean_cell_value)
    cleaned = cleaned.dropna(how="all").dropna(axis=1, how="all")
    return cleaned.reset_index(drop=True)


def _clean_cell_value(value: Any) -> Any:
    if pd.isna(value):
        return pd.NA
    if isinstance(value, str):
        value = _normalize_text(value)
        return value if value else pd.NA
    return value


def _normalize_text(value: Any) -> str:
    text = str(value)
    return " ".join(text.replace("\r", " ").replace("\n", " ").split())


def _find_keyword_rows(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    text_df = df.astype(str)
    mask = text_df.apply(
        lambda row: row.str.contains(keyword, regex=False, na=False).any(),
        axis=1,
    )
    return df.loc[mask].copy()


def _apply_detected_header(raw_df: pd.DataFrame, matched_rows: pd.DataFrame) -> pd.DataFrame:
    header_index = _detect_header_row(raw_df)
    if header_index is None:
        result = matched_rows.copy()
        result.columns = [f"原始列_{index + 1}" for index in range(len(result.columns))]
        return result.reset_index(drop=True)

    header_values = [_normalize_text(value) for value in raw_df.iloc[header_index].tolist()]
    header_values = _deduplicate_columns(header_values)

    matched_after_header = matched_rows.loc[matched_rows.index > header_index].copy()
    if matched_after_header.empty:
        matched_after_header = matched_rows.copy()

    matched_after_header.columns = header_values[: len(matched_after_header.columns)]
    matched_after_header = matched_after_header.dropna(how="all")
    return matched_after_header.reset_index(drop=True)


def _detect_header_row(df: pd.DataFrame) -> int | None:
    """Pick the row that contains the most known target column names."""
    best_index: int | None = None
    best_score = 0

    for row_index, row in df.iterrows():
        row_values = [_normalize_text(value) for value in row.tolist() if not pd.isna(value)]
        score = sum(
            1
            for target_column in TARGET_COLUMNS
            if any(target_column in value for value in row_values)
        )

        if score > best_score:
            best_score = score
            best_index = int(row_index)

    return best_index if best_score >= 2 else None


def _deduplicate_columns(columns: list[str]) -> list[str]:
    deduplicated: list[str] = []
    seen: dict[str, int] = {}

    for index, column in enumerate(columns):
        normalized_column = column or f"未命名列_{index + 1}"
        seen[normalized_column] = seen.get(normalized_column, 0) + 1

        if seen[normalized_column] == 1:
            deduplicated.append(normalized_column)
        else:
            deduplicated.append(f"{normalized_column}_{seen[normalized_column]}")

    return deduplicated


def _select_target_columns_when_available(df: pd.DataFrame) -> pd.DataFrame:
    """Return known business columns when detected; otherwise keep raw columns."""
    available_targets = [column for column in TARGET_COLUMNS if column in df.columns]
    if not available_targets:
        return df

    metadata_columns = [column for column in ["_sheet_name"] if column in df.columns]
    extra_columns = [
        column
        for column in df.columns
        if column not in metadata_columns and column not in available_targets
    ]
    return df[metadata_columns + available_targets + extra_columns]
