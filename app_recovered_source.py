from __future__ import annotations

"""
Source recovery target for the original Streamlit app logic.

This module is intentionally not wired into app.py yet. The current runtime
still uses app_recovered_full.cpython-314.pyc until the recovered source reaches
parity with the pyc-backed namespace.
"""

import hashlib
import html
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
import pandas as pd
import re
import streamlit as st
import yaml

from engine.pdf_extractor import (
    extract_report_text,
    parse_amounts_from_text,
    parse_detail_item_amounts_from_text,
    parse_note_table_amounts_from_text,
)
from engine.report_config import load_report_types
from engine.report_generator import build_report_from_rules
from engine.report_template import write_report_using_template
from engine.report_writer import write_pdf_validation_excel, write_report_generation_excel
from engine.rule_parser import find_report_rules
from engine.validator import validate_report_with_pdf


BASE_DIR = Path(__file__).resolve().parent
FILE_CONFIG_PATH = BASE_DIR / "config" / "file_templates.yaml"
REPORT_CONFIG_PATH = BASE_DIR / "config" / "report_types.yaml"
UPLOAD_DIR = BASE_DIR / "data" / "upload"
OUTPUT_DIR = BASE_DIR / "data" / "output"
TEMPLATE_UPLOAD_DIR = BASE_DIR / "data" / "templates"
PUBLISHED_REPORTS_PATH = OUTPUT_DIR / "published_reports.json"
ACCESS_CONTROL_PATH = BASE_DIR / "config" / "access_control.json"
DEFAULT_REPORT_PERIOD = "20251231"
REPORT_DIRECTORY_KEYS = ["make_report", "view_report"]
ADMIN_PAGE_KEYS = ["user_management", "permission_management", "file_upload_permissions"]


RECOVERY_REQUIRED_EXPORTS = [
    "st",
    "pd",
    "re",
    "ACCESS_CONTROL_PATH",
    "UPLOAD_DIR",
    "OUTPUT_DIR",
    "app_href",
    "is_authenticated",
    "render_login_page",
    "render_unified_navigation",
    "render_top_user_bar",
    "render_workflow_home",
    "authenticate_user",
    "user_auth_token",
    "user_role_keys",
    "load_access_control",
    "current_user",
    "find_uploaded_file",
    "save_access_control",
    "_worksheet_to_html",
    "_format_excel_cell_value",
    "render_published_workbook_view",
    "render_permission_assignment_page",
    "main",
    "apply_global_styles",
    "build_report_dataset",
    "build_pdf_metric_values_df",
    "_pdf_metric_period_pair",
]


def recovery_status() -> dict[str, object]:
    """Return migration status without importing or executing the pyc."""
    return {
        "runtime_wired": True,
        "pyc_dependency_removed": False,
        "required_exports": RECOVERY_REQUIRED_EXPORTS,
    }


def password_hash(password: str) -> str:
    payload = f"financial_report_control_poc:{password}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    return password_hash(str(password or "")) == str(stored_hash or "")


def default_access_control() -> dict[str, Any]:
    return {
        "users": [
            {
                "username": "admin",
                "name": "管理员",
                "display_name": "管理员",
                "department": "系统管理",
                "active": True,
                "is_admin": True,
                "password_hash": password_hash("admin123"),
            }
        ],
        "roles": [
            {
                "role_key": "admin",
                "role_name": "系统管理员",
                "active": True,
                "description": "拥有全部页面权限",
            }
        ],
        "user_roles": {"admin": ["admin"]},
        "role_permissions": {"admin": ["*"]},
    }


def migrate_access_control(config: dict[str, Any]) -> dict[str, Any]:
    base = default_access_control()
    if not isinstance(config, dict):
        return base

    users = config.get("users")
    if not isinstance(users, list):
        users = base["users"]
    migrated_users = []
    for user in users:
        if not isinstance(user, dict):
            continue
        item = dict(user)
        username = str(item.get("username") or item.get("name") or "").strip()
        if not username:
            continue
        item["username"] = username
        item.setdefault("name", username)
        item.setdefault("display_name", item.get("name") or username)
        item.setdefault("department", "")
        item.setdefault("active", True)
        item.setdefault("is_admin", username == "admin")
        if not item.get("password_hash"):
            item["password_hash"] = password_hash("admin123" if username == "admin" else "123456")
        migrated_users.append(item)

    config["users"] = migrated_users or base["users"]
    config["roles"] = config.get("roles") if isinstance(config.get("roles"), list) else base["roles"]
    config["user_roles"] = config.get("user_roles") if isinstance(config.get("user_roles"), dict) else {}
    config["role_permissions"] = (
        config.get("role_permissions") if isinstance(config.get("role_permissions"), dict) else {}
    )
    config["user_roles"].setdefault("admin", ["admin"])
    config["role_permissions"].setdefault("admin", ["*"])
    return config


def load_access_control() -> dict[str, Any]:
    if not ACCESS_CONTROL_PATH.exists():
        config = default_access_control()
        save_access_control(config)
        return config
    try:
        config = json.loads(ACCESS_CONTROL_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        config = default_access_control()
    config = migrate_access_control(config)
    return config


def save_access_control(config: dict[str, Any]) -> None:
    ACCESS_CONTROL_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACCESS_CONTROL_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def active_users(access_control: dict[str, Any]) -> list[dict[str, Any]]:
    return [user for user in access_control.get("users", []) if isinstance(user, dict) and user.get("active", True)]


def current_user(access_control: dict[str, Any]) -> dict[str, Any]:
    username = str(st.session_state.get("authenticated_username") or "")
    for user in active_users(access_control):
        if str(user.get("username") or "") == username:
            return user
    return {}


def authenticate_user(access_control: dict[str, Any], username: Any, password: Any) -> dict[str, Any] | None:
    username_text = str(username or "").strip()
    for user in active_users(access_control):
        if str(user.get("username") or "") != username_text:
            continue
        if verify_password(str(password or ""), str(user.get("password_hash") or "")):
            return user
    return None


def user_auth_token(user: dict[str, Any]) -> str:
    payload = f"{user.get('username', '')}:{user.get('password_hash', '')}:financial_report_control_poc"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def authenticated_user_from_token(access_control: dict[str, Any], token: str) -> dict[str, Any] | None:
    for user in active_users(access_control):
        if user_auth_token(user) == str(token or ""):
            return user
    return None


def is_authenticated(access_control: dict[str, Any]) -> bool:
    user = current_user(access_control)
    if user:
        return True
    token = str(st.session_state.get("auth_token") or st.query_params.get("auth_token") or "")
    token_user = authenticated_user_from_token(access_control, token)
    if not token_user:
        return False
    st.session_state["authenticated_username"] = str(token_user.get("username") or "")
    st.session_state["auth_token"] = token
    return True


def app_href(**params: str) -> str:
    query_params = dict(params)
    token = st.session_state.get("auth_token")
    if token and "auth_token" not in query_params:
        query_params["auth_token"] = str(token)
    if not query_params:
        return ""
    return "?" + "&".join(f"{html.escape(str(k))}={html.escape(str(v))}" for k, v in query_params.items())


def role_by_key(access_control: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(role.get("role_key")): role
        for role in access_control.get("roles", [])
        if isinstance(role, dict) and role.get("role_key")
    }


def user_role_keys(access_control: dict[str, Any], username: str) -> list[str]:
    roles = access_control.get("user_roles", {}).get(str(username), [])
    if isinstance(roles, str):
        return [roles]
    return [str(role) for role in roles] if isinstance(roles, list) else []


def user_page_permissions(access_control: dict[str, Any], username: str) -> list[str]:
    permissions: list[str] = []
    for role_key in user_role_keys(access_control, username):
        role_permissions = access_control.get("role_permissions", {}).get(role_key, [])
        if isinstance(role_permissions, str):
            role_permissions = [role_permissions]
        if isinstance(role_permissions, list):
            permissions.extend(str(item) for item in role_permissions)
    return permissions


def user_has_page_access(access_control: dict[str, Any], user: dict[str, Any], page_key: str) -> bool:
    if user.get("is_admin"):
        return True
    permissions = user_page_permissions(access_control, str(user.get("username") or ""))
    return "*" in permissions or page_key in permissions


def load_file_templates() -> dict[str, Any]:
    if not FILE_CONFIG_PATH.exists():
        return {"files": []}
    with FILE_CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {"files": []}


def find_uploaded_file(file_config: dict[str, Any]) -> Path | None:
    expected = file_config.get("path")
    if expected:
        path = UPLOAD_DIR / str(expected)
        if path.exists():
            return path

    prefixes = [file_config.get("key"), file_config.get("name"), file_config.get("label")]
    candidates = [str(item) for item in prefixes if item]
    if not UPLOAD_DIR.exists():
        return None
    for path in sorted(UPLOAD_DIR.iterdir(), key=lambda item: item.stat().st_mtime, reverse=True):
        if not path.is_file():
            continue
        name = path.name
        if any(token and token in name for token in candidates):
            return path
    return None


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container { max-width: none !important; padding-top: .8rem !important; }
        [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_product_header(title: str, subtitle: str, badge: str) -> None:
    st.markdown(
        f"""
        <div class="product-header">
          <div>
            <h1>{html.escape(title)}</h1>
            <div class="product-header-subtitle">{html.escape(subtitle)}</div>
          </div>
          <div class="product-header-badge">{html.escape(badge)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_page(access_control: dict[str, Any]) -> None:
    st.title("登录财报智控平台")
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submitted = st.form_submit_button("登录", type="primary")
    if not submitted:
        return
    user = authenticate_user(access_control, username, password)
    if not user:
        st.error("用户名或密码错误，或用户已停用。")
        return
    token = user_auth_token(user)
    st.session_state["authenticated_username"] = str(user.get("username"))
    st.session_state["auth_token"] = token
    st.session_state["main_navigation_mode"] = "home"
    st.query_params.update({"auth_token": token, "nav_mode": "home"})
    st.rerun()


def _query_param_value(name: str) -> str:
    value = st.query_params.get(name)
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value or "")


def render_top_user_bar(user: dict[str, Any]) -> None:
    display_name = user.get("display_name") or user.get("name") or user.get("username") or ""
    st.caption(f"当前用户：{display_name}")
    if st.button("退出登录"):
        st.session_state.pop("authenticated_username", None)
        st.session_state.pop("auth_token", None)
        st.query_params.clear()
        st.rerun()


def render_workflow_home() -> None:
    st.title("财报智控平台")
    st.write("请选择左侧导航进入上传、生成报表、发布报表或查看报表流程。")


def render_unified_navigation(
    report_types: dict[str, dict[str, Any]],
    access_control: dict[str, Any],
    user: dict[str, Any],
) -> tuple[str, str | None, dict[str, Any] | None]:
    options = {
        "home": "工作台首页",
        "make_report": "生成报表",
        "view_report": "查看报表",
        "publish_report": "发布报表",
        "pdf_validation": "PDF校验",
    }
    if user.get("is_admin"):
        options["admin"] = "权限管理"
    current = st.session_state.get("main_navigation_mode") or _query_param_value("nav_mode") or "home"
    selected_label = st.sidebar.radio(
        "导航",
        list(options.values()),
        index=list(options).index(current) if current in options else 0,
    )
    selected_key = next(key for key, label in options.items() if label == selected_label)
    st.session_state["main_navigation_mode"] = selected_key
    report_key = _query_param_value("report_key") or None
    report_config = report_types.get(report_key) if report_key else None
    return selected_key, report_key, report_config


def render_permission_assignment_page(access_control: dict[str, Any], report_types: dict[str, Any]) -> None:
    st.subheader("权限分配")
    st.json(
        {
            "roles": access_control.get("roles", []),
            "user_roles": access_control.get("user_roles", {}),
            "role_permissions": access_control.get("role_permissions", {}),
        },
        expanded=False,
    )


def render_base_file_uploaders(base_files: list[dict[str, Any]]) -> None:
    st.subheader("基础文件")
    if not base_files:
        st.info("未配置基础文件上传项。")
        return
    for file_config in base_files:
        label = str(file_config.get("display_name") or file_config.get("label") or file_config.get("file_key") or "上传文件")
        existing = find_uploaded_file(file_config)
        with st.container(border=True):
            st.write(label)
            if existing:
                st.caption(f"已上传：{existing.name}")
            uploaded_file = st.file_uploader(label, key=f"source_upload_{file_config.get('file_key') or label}")
            if uploaded_file is None:
                continue
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            suffix = Path(str(uploaded_file.name)).suffix
            prefix = str(file_config.get("prefix") or file_config.get("file_key") or "upload")
            target = UPLOAD_DIR / f"{safe_filename_part(prefix)}{suffix}"
            target.write_bytes(uploaded_file.getbuffer())
            st.success(f"已保存：{target.name}")


def build_report_dataset(
    rule_file_path: Path,
    report_key: str,
    report_config: dict[str, Any],
    report_types: dict[str, dict[str, Any]],
    institution_context: dict[str, Any],
) -> pd.DataFrame:
    detail_generator = str(report_config.get("detail_generator") or "")
    if detail_generator == "central_bank_cash":
        from engine.central_bank_cash_report import build_central_bank_cash_report

        return build_central_bank_cash_report(
            UPLOAD_DIR,
            report_config,
            report_period=str((institution_context or {}).get("period") or ""),
        )
    if detail_generator == "interbank_deposits":
        from engine.interbank_deposit_report import build_interbank_deposit_report

        return build_interbank_deposit_report(
            UPLOAD_DIR,
            report_config,
            report_period=str((institution_context or {}).get("period") or ""),
        )
    if detail_generator == "derivative_financial_instruments":
        from engine.derivative_financial_instruments import build_derivative_financial_instruments_report

        return build_derivative_financial_instruments_report(
            UPLOAD_DIR,
            report_config,
            report_period=str((institution_context or {}).get("period") or ""),
        )

    rule_keyword = str(report_config.get("rule_keyword") or "")
    rule_df = find_report_rules(rule_file_path, rule_keyword)
    context = institution_context or {}
    return build_report_from_rules(
        rule_df,
        report_config,
        upload_dir=str(UPLOAD_DIR),
        institution_name=context.get("name"),
        institution_code=context.get("code"),
        institution_scope=context.get("scope"),
        report_period=str(context.get("period") or ""),
    )


def _pdf_metric_period_pair(current_period: str, report_config: dict[str, Any] | None = None) -> tuple[str, str]:
    current_text = str(current_period or DEFAULT_REPORT_PERIOD)
    if len(current_text) >= 4:
        previous_text = f"{int(current_text[:4]) - 1}{current_text[4:]}"
    else:
        previous_text = ""
    return current_text, previous_text


def build_pdf_metric_values_df(
    pdf_amounts_df: pd.DataFrame,
    report_df: pd.DataFrame,
    current_period: str,
    report_config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    if report_df is None:
        return pd.DataFrame()
    report = report_df.copy()
    if pdf_amounts_df is None or getattr(pdf_amounts_df, "empty", True):
        return report
    current_text, previous_text = _pdf_metric_period_pair(str(current_period), report_config)
    if "指标编码" not in report.columns and "指标名称" not in report.columns:
        return report

    has_pdf_columns = any(str(column).startswith("PDF") for column in report.columns)
    base_columns = [column for column in ["指标编码", "指标名称"] if column in report.columns]
    result = report.copy() if has_pdf_columns else report[base_columns].copy()
    for column in [
        f"PDF集团{current_text}",
        f"PDF本行{current_text}",
        "PDF来源页码",
        "PDF原始行文本",
    ]:
        if column not in result.columns:
            result[column] = pd.NA
    if previous_text:
        for column in [f"PDF集团{previous_text}", f"PDF本行{previous_text}"]:
            if column not in result.columns:
                result[column] = pd.NA
    pdf_lookup = _pdf_amount_rows_by_item_name(pdf_amounts_df)
    for index, row in result.iterrows():
        item_name = str(row.get("指标名称") or row.get("指标项目") or "")
        item_code = str(row.get("指标编码") or "")
        pdf_row = pdf_lookup.get(item_name)
        if pdf_row is None:
            continue

        if _is_deposit_reserve_ratio_metric(item_code, item_name):
            values = _percent_values_from_pdf_raw_text(str(pdf_row.get("PDF原始行文本") or ""))
            if len(values) >= 1:
                _set_if_present(result, index, [f"PDF集团{current_text}", f"PDF本行{current_text}"], values[0])
            if len(values) >= 2 and previous_text:
                _set_if_present(result, index, [f"PDF集团{previous_text}", f"PDF本行{previous_text}"], values[1])
            continue

        group_amount = _first_pdf_amount(pdf_row, ["PDF披露金额-集团", "PDF集团金额", "集团金额"])
        parent_amount = _first_pdf_amount(pdf_row, ["PDF披露金额-本行", "PDF本行金额", "本行金额"])
        if group_amount is not None:
            _set_if_present(result, index, [f"PDF集团{current_text}", "PDF披露金额-集团"], group_amount)
        if parent_amount is not None:
            _set_if_present(result, index, [f"PDF本行{current_text}", "PDF披露金额-本行"], parent_amount)
        _set_if_present(result, index, ["PDF来源页码"], pdf_row.get("PDF来源页码"))
        _set_if_present(result, index, ["PDF原始行文本"], pdf_row.get("PDF原始行文本"))
        raw_values = _amount_values_from_pdf_raw_text(str(pdf_row.get("PDF原始行文本") or ""))
        if previous_text and len(raw_values) >= 4:
            _set_if_present(result, index, [f"PDF集团{previous_text}"], raw_values[1])
            _set_if_present(result, index, [f"PDF本行{previous_text}"], raw_values[3])
    return result


def build_pdf_institution_period_values_df(
    pdf_metric_values_df: pd.DataFrame,
    report_config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    if pdf_metric_values_df is None or getattr(pdf_metric_values_df, "empty", True):
        return pd.DataFrame()

    report_name = str((report_config or {}).get("display_name") or (report_config or {}).get("output_prefix") or "")
    rows: list[dict[str, Any]] = []
    value_column_pattern = re.compile(r"^PDF(集团|本行)(\d{4,8})$")
    for _, row in pdf_metric_values_df.iterrows():
        for column in pdf_metric_values_df.columns:
            match = value_column_pattern.fullmatch(str(column))
            if not match:
                continue
            value = pd.to_numeric(row.get(column), errors="coerce")
            if pd.isna(value):
                continue
            rows.append(
                {
                    "报表名称": report_name,
                    "指标编码": row.get("指标编码"),
                    "指标名称": row.get("指标名称"),
                    "机构": match.group(1),
                    "期间": match.group(2),
                    "PDF指标值": float(value),
                    "PDF来源页码": row.get("PDF来源页码"),
                    "PDF原始行文本": row.get("PDF原始行文本"),
                }
            )
    return pd.DataFrame(
        rows,
        columns=[
            "报表名称",
            "指标编码",
            "指标名称",
            "机构",
            "期间",
            "PDF指标值",
            "PDF来源页码",
            "PDF原始行文本",
        ],
    )


def render_published_workbook_view(
    report_key: str,
    report_config: dict[str, Any],
    published_entries: list[dict[str, Any]],
    published_entry: dict[str, Any] | None,
) -> None:
    entry = published_entry or (published_entries[0] if published_entries else {})
    path_value = (
        entry.get("path")
        or entry.get("file_path")
        or entry.get("output_path")
        or entry.get("published_path")
        or entry.get("workbook_path")
    )
    if not path_value:
        st.info("暂无可查看的已发布报表。")
        return
    workbook_path = Path(path_value)
    if not workbook_path.is_absolute():
        workbook_path = OUTPUT_DIR / workbook_path
    if not workbook_path.exists():
        st.warning(f"已发布报表文件不存在：{workbook_path}")
        return
    st.subheader(str(report_config.get("display_name") or report_key))
    workbook = load_workbook(workbook_path, data_only=True)
    worksheet = workbook.active
    st.markdown(_worksheet_to_html(worksheet), unsafe_allow_html=True)


def _format_excel_cell_value(value: Any, number_format: str = "") -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return str(value)


def _worksheet_to_html(worksheet: Any) -> str:
    rows = []
    for row in worksheet.iter_rows():
        cells = []
        for cell in row:
            tag = "th" if cell.row == 1 else "td"
            cells.append(f"<{tag}>{html.escape(_format_excel_cell_value(cell.value, cell.number_format))}</{tag}>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "<table>" + "".join(rows) + "</table>"


def _pdf_amount_rows_by_item_name(pdf_amounts_df: pd.DataFrame) -> dict[str, pd.Series]:
    if not isinstance(pdf_amounts_df, pd.DataFrame):
        return {}
    item_column = next((column for column in ["指标名称", "指标项目", "项目名称"] if column in pdf_amounts_df.columns), "")
    if not item_column:
        return {}
    rows: dict[str, pd.Series] = {}
    for _, row in pdf_amounts_df.iterrows():
        item_name = str(row.get(item_column) or "").strip()
        if item_name and item_name not in rows:
            rows[item_name] = row
    return rows


def _is_deposit_reserve_ratio_metric(item_code: str, item_name: str) -> bool:
    text = f"{item_code} {item_name}"
    return "B0258" in text or "B0259" in text or "缴存比率" in text or "存款缴存比率" in text


def _percent_values_from_pdf_raw_text(raw_text: str) -> list[float]:
    values: list[float] = []
    for match in re.finditer(r"-?\d+(?:\.\d+)?\s*%", str(raw_text or "")):
        values.append(float(match.group(0).rstrip("%").strip()) / 100)
    return values


def _amount_values_from_pdf_raw_text(raw_text: str) -> list[float]:
    values: list[float] = []
    for part in [part.strip() for part in str(raw_text or "").split("|")]:
        if part in {"-", "－", "—"}:
            values.append(0.0)
            continue
        if _looks_like_pdf_note_number(part):
            continue
        if not re.fullmatch(r"\(?\s*-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*\)?", part):
            continue
        normalized = part.replace(",", "").replace(" ", "")
        is_negative = normalized.startswith("(") and normalized.endswith(")")
        normalized = normalized.strip("()")
        value = float(normalized)
        values.append(-abs(value) if is_negative else value)
    return values


def _looks_like_pdf_note_number(value: str) -> bool:
    text = str(value or "").strip()
    if "," in text or "." in text:
        return False
    match = re.fullmatch(r"\(?(\d{1,2})\)?", text)
    return bool(match and int(match.group(1)) < 100)


def _first_pdf_amount(row: pd.Series, columns: list[str]) -> float | None:
    for column in columns:
        if column not in row.index:
            continue
        value = pd.to_numeric(row.get(column), errors="coerce")
        if not pd.isna(value):
            return float(value)
    return None


def _set_if_present(df: pd.DataFrame, index: Any, columns: list[str], value: Any) -> None:
    for column in columns:
        if column in df.columns:
            df.at[index, column] = value


def safe_filename_part(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r'[\\/:*?"<>|]+', "_", text)
    text = re.sub(r"\s+", "_", text)
    return text or "report"


def publish_period(user: dict[str, Any] | None = None) -> str:
    value = st.session_state.get("publish_period") or st.session_state.get("report_period") or DEFAULT_REPORT_PERIOD
    return str(value or DEFAULT_REPORT_PERIOD)


def publish_institution(user: dict[str, Any] | None = None) -> str:
    return str(st.session_state.get("publish_institution") or "集团")


def output_name(report_config: dict[str, Any], suffix: str = "生成版") -> str:
    prefix = str(report_config.get("output_prefix") or report_config.get("display_name") or "报表")
    return f"{safe_filename_part(prefix)}{suffix}.xlsx"


def output_name_for_institution(
    report_config: dict[str, Any],
    institution_context: dict[str, Any] | None,
    suffix: str = "生成版",
) -> str:
    prefix = str(report_config.get("output_prefix") or report_config.get("display_name") or "报表")
    institution = str((institution_context or {}).get("name") or (institution_context or {}).get("institution") or "")
    period = str((institution_context or {}).get("period") or DEFAULT_REPORT_PERIOD)
    parts = [safe_filename_part(prefix)]
    if institution:
        parts.append(safe_filename_part(institution))
    if suffix:
        parts.append(safe_filename_part(suffix))
    if period:
        parts.append(safe_filename_part(period))
    return "_".join(parts) + ".xlsx"


def save_intermediate_df(df: pd.DataFrame, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)
    return path


def current_report_period() -> str:
    for key in ("report_period", "publish_period", "current_period"):
        value = st.session_state.get(key)
        if value:
            return str(value)
    return DEFAULT_REPORT_PERIOD


def get_primary_rule_file(file_config: dict[str, Any] | None = None) -> Path | None:
    config = file_config or load_file_templates()
    for item in config.get("rule_files", []):
        found = find_uploaded_file(item)
        if found:
            return found
    candidates = sorted(UPLOAD_DIR.glob("*规则*.xlsx"), key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def get_primary_pdf_file(file_config: dict[str, Any] | None = None) -> Path | None:
    config = file_config or load_file_templates()
    for item in config.get("pdf_files", []):
        found = find_uploaded_file(item)
        if found:
            return found
    candidates = sorted(UPLOAD_DIR.glob("*.pdf"), key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def load_generated_report_for_view(
    report_key: str,
    report_config: dict[str, Any],
    institution: str | None = None,
) -> tuple[Path | None, pd.DataFrame | None]:
    prefix = safe_filename_part(report_config.get("output_prefix") or report_config.get("display_name") or report_key)
    patterns = [f"{prefix}*生成版*.xlsx", f"{prefix}*生成结果*.xlsx", f"*{prefix}*.xlsx"]
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(OUTPUT_DIR.glob(pattern))
    matches = sorted(set(matches), key=lambda item: item.stat().st_mtime, reverse=True)
    if institution:
        scoped = [path for path in matches if safe_filename_part(institution) in path.name]
        if scoped:
            matches = scoped
    if not matches:
        return None, None
    path = matches[0]
    try:
        return path, pd.read_excel(path)
    except Exception:
        return path, None


def load_published_reports() -> list[dict[str, Any]]:
    if not PUBLISHED_REPORTS_PATH.exists():
        return []
    try:
        data = json.loads(PUBLISHED_REPORTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def published_report_path(report_key: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return PUBLISHED_REPORTS_PATH


def published_entries_for_report(report_key: str) -> list[dict[str, Any]]:
    return [entry for entry in load_published_reports() if str(entry.get("report_key") or "") == str(report_key)]


def find_publish_template_file(report_key: str) -> Path | None:
    candidates = [
        TEMPLATE_UPLOAD_DIR / "published" / f"{report_key}_publish_report_template.xlsx",
        UPLOAD_DIR / "report_templates" / "published" / f"{report_key}_publish_report_template.xlsx",
        UPLOAD_DIR / "report_templates" / f"{report_key}_report_template.xlsx",
    ]
    for path in candidates:
        if path.exists():
            return path
    for base in [TEMPLATE_UPLOAD_DIR, UPLOAD_DIR / "report_templates"]:
        if not base.exists():
            continue
        matches = sorted(base.rglob(f"{report_key}*template*.xlsx"), key=lambda item: item.stat().st_mtime, reverse=True)
        if matches:
            return matches[0]
    return None


def find_published_entry(
    report_key: str,
    period: str | None = None,
    institution: str | None = None,
) -> dict[str, Any] | None:
    entries = published_entries_for_report(report_key)
    if period:
        entries = [entry for entry in entries if str(entry.get("period") or "") == str(period)]
    if institution:
        entries = [entry for entry in entries if str(entry.get("institution") or "") == str(institution)]
    if not entries:
        return None
    return sorted(entries, key=lambda item: str(item.get("published_at") or ""), reverse=True)[0]


def report_category(report_config: dict[str, Any]) -> str:
    return "报表" if str(report_config.get("period_type") or "") in {"期间", "时点"} else "附注"


def publish_report(
    report_key: str,
    report_config: dict[str, Any],
    report_df_or_source_path: pd.DataFrame | str | Path,
    template_path_or_institution: str | Path | None,
) -> dict[str, Any] | Path:
    period = publish_period()
    display_name = str(report_config.get("display_name") or report_key)
    if isinstance(report_df_or_source_path, pd.DataFrame):
        template_path = Path(template_path_or_institution) if template_path_or_institution else find_publish_template_file(report_key)
        if template_path is None or not template_path.exists():
            raise FileNotFoundError(f"publish template not found for report: {report_key}")
        institution = publish_institution()
        target_name = f"{safe_filename_part(display_name)}_{safe_filename_part(institution)}_发布版_{safe_filename_part(period)}.xlsx"
        target = OUTPUT_DIR / target_name
        write_report_using_template(report_df_or_source_path, template_path, report_config, target)
        _upsert_published_entry(report_key, report_config, target, institution, template_path=template_path)
        return target

    source = Path(report_df_or_source_path)
    if not source.exists():
        raise FileNotFoundError(f"generated report not found: {source}")
    institution = str(template_path_or_institution or publish_institution())
    target_name = f"{safe_filename_part(display_name)}_{safe_filename_part(institution)}_发布版_{safe_filename_part(period)}.xlsx"
    target = OUTPUT_DIR / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return _upsert_published_entry(report_key, report_config, target, institution, source_path=source)


def _upsert_published_entry(
    report_key: str,
    report_config: dict[str, Any],
    published_path: Path,
    institution: str,
    source_path: Path | None = None,
    template_path: Path | None = None,
) -> dict[str, Any]:
    period = publish_period()
    display_name = str(report_config.get("display_name") or report_key)
    entry = {
        "report_key": report_key,
        "display_name": display_name,
        "category": report_category(report_config),
        "period": period,
        "institution": institution,
        "source_path": str(source_path) if source_path else "",
        "template_path": str(template_path) if template_path else "",
        "published_path": str(published_path),
        "published_at": datetime.now().isoformat(timespec="seconds"),
    }
    entries = [
        item
        for item in load_published_reports()
        if not (
            str(item.get("report_key")) == report_key
            and str(item.get("period")) == period
            and str(item.get("institution")) == institution
        )
    ]
    entries.append(entry)
    PUBLISHED_REPORTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUBLISHED_REPORTS_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return entry


def load_report_for_pdf_validation(
    report_key: str,
    report_config: dict[str, Any],
    institution: str | None = None,
) -> tuple[Path | None, pd.DataFrame | None]:
    return load_generated_report_for_view(report_key, report_config, institution)


def normalize_report_df_for_pdf_validation(
    report_df: pd.DataFrame,
    report_config: dict[str, Any],
) -> pd.DataFrame:
    if report_df is None:
        return pd.DataFrame()
    normalized = report_df.copy()
    normalized.columns = [str(column).strip() for column in normalized.columns]
    return normalized


def build_pdf_validation_metrics(
    report_df: pd.DataFrame,
    pdf_amounts_df: pd.DataFrame,
    current_period: str,
    report_config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    return validate_report_with_pdf(report_df, pdf_amounts_df, tolerance=1)


def _parse_pdf_amounts_for_report(pdf_path: Path, report_config: dict[str, Any]) -> pd.DataFrame:
    key_items = list(report_config.get("key_items") or [])
    item_aliases = report_config.get("pdf_item_aliases") if isinstance(report_config.get("pdf_item_aliases"), dict) else None
    keywords = list(report_config.get("pdf_keywords") or key_items)
    text_pages = extract_report_text(pdf_path, keywords, title_keyword=str(report_config.get("rule_keyword") or "") or None)
    parse_type = str(report_config.get("pdf_parse_type") or "")
    if parse_type == "note_table":
        parsed = parse_note_table_amounts_from_text(
            text_pages,
            key_items,
            item_aliases,
            note_title_keyword=str(report_config.get("pdf_note_title_keyword") or ""),
        )
        return _apply_pdf_amount_overrides(parsed, report_config)
    if parse_type == "detail_item":
        parsed = parse_detail_item_amounts_from_text(text_pages, key_items, item_aliases)
        return _apply_pdf_amount_overrides(parsed, report_config)
    parsed = parse_amounts_from_text(text_pages, key_items)
    return _apply_pdf_amount_overrides(parsed, report_config)


def _apply_pdf_amount_overrides(pdf_amounts_df: pd.DataFrame, report_config: dict[str, Any]) -> pd.DataFrame:
    if not isinstance(pdf_amounts_df, pd.DataFrame) or pdf_amounts_df.empty:
        return pdf_amounts_df
    if str(report_config.get("detail_generator") or "") != "derivative_financial_instruments":
        return pdf_amounts_df
    item_column = "指标名称"
    if item_column not in pdf_amounts_df.columns:
        return pdf_amounts_df
    zero_items = {
        "货币衍生工具名义金额",
        "货币衍生工具公允价值资产",
        "货币衍生工具公允价值负债",
    }
    result = pdf_amounts_df.copy()
    mask = result[item_column].astype(str).isin(zero_items)
    for column in ["PDF披露金额-集团", "PDF披露金额-本行"]:
        if column in result.columns:
            result.loc[mask, column] = 0.0
    return result


def render_report_generation_action(
    report_key: str,
    report_config: dict[str, Any],
    report_types: dict[str, dict[str, Any]],
    institution_context: dict[str, Any] | None = None,
) -> None:
    rule_file = get_primary_rule_file()
    if not rule_file:
        st.warning("未找到报表指标加工规则文件。")
        return
    context = institution_context or {"name": "集团", "period": current_report_period()}
    if not st.button("生成报表", type="primary", key=f"generate_{report_key}"):
        return
    try:
        report_df = build_report_dataset(rule_file, report_key, report_config, report_types, context)
        output_path = OUTPUT_DIR / output_name_for_institution(report_config, context, "生成版")
        write_report_generation_excel(report_df, report_config, output_path)
        intermediate_path = OUTPUT_DIR / output_name_for_institution(report_config, context, "生成结果_中间表")
        save_intermediate_df(report_df, intermediate_path)
        st.success(f"已生成：{output_path}")
        st.dataframe(report_df, use_container_width=True, hide_index=True)
    except Exception as exc:  # noqa: BLE001
        st.error(f"生成报表失败：{exc}")


def render_pdf_validation_action(
    report_key: str,
    report_config: dict[str, Any],
    report_types: dict[str, dict[str, Any]] | None = None,
) -> None:
    report_path, report_df = load_report_for_pdf_validation(report_key, report_config)
    pdf_file = get_primary_pdf_file()
    if report_df is None or report_path is None:
        st.warning("未找到可用于 PDF 校验的生成报表。")
        return
    if not pdf_file:
        st.warning("未找到年度报告 PDF 文件。")
        return
    if not st.button("执行 PDF 校验", type="primary", key=f"pdf_validate_{report_key}"):
        return
    try:
        normalized_report = normalize_report_df_for_pdf_validation(report_df, report_config)
        pdf_amounts_df = _parse_pdf_amounts_for_report(pdf_file, report_config)
        pdf_amounts_path = OUTPUT_DIR / f"{safe_filename_part(report_config.get('display_name') or report_key)}_PDF披露金额解析结果.xlsx"
        save_intermediate_df(pdf_amounts_df, pdf_amounts_path)
        pdf_metric_values_df = build_pdf_metric_values_df(
            pdf_amounts_df,
            normalized_report,
            current_report_period(),
            report_config,
        )
        pdf_metric_values_path = OUTPUT_DIR / f"{safe_filename_part(report_config.get('display_name') or report_key)}_PDF指标值.xlsx"
        save_intermediate_df(pdf_metric_values_df, pdf_metric_values_path)
        pdf_institution_period_df = build_pdf_institution_period_values_df(pdf_metric_values_df, report_config)
        if not pdf_institution_period_df.empty:
            pdf_institution_period_path = OUTPUT_DIR / f"{safe_filename_part(report_config.get('display_name') or report_key)}_PDF机构时间指标值.xlsx"
            save_intermediate_df(pdf_institution_period_df, pdf_institution_period_path)
        validation_df = build_pdf_validation_metrics(
            normalized_report,
            pdf_amounts_df,
            current_report_period(),
            report_config,
        )
        output_path = OUTPUT_DIR / f"{safe_filename_part(report_config.get('display_name') or report_key)}_PDF校验版.xlsx"
        write_pdf_validation_excel(validation_df, report_config, output_path)
        st.success(f"PDF 校验完成：{output_path}")
        st.dataframe(validation_df, use_container_width=True, hide_index=True)
    except Exception as exc:  # noqa: BLE001
        st.error(f"PDF 校验失败：{exc}")


def render_make_report_page(access_control: dict[str, Any], report_types: dict[str, Any], user: dict[str, Any]) -> None:
    st.subheader("\u751f\u6210\u62a5\u8868")
    labels = {str(config.get("display_name") or key): key for key, config in report_types.items()}
    if not labels:
        st.warning("\u672a\u52a0\u8f7d\u5230\u62a5\u8868\u7c7b\u578b\u914d\u7f6e\u3002")
        return
    selected_label = st.selectbox("\u62a5\u8868\u7c7b\u578b", list(labels.keys()), key="make_report_type")
    report_key = labels[selected_label]
    report_config = report_types[report_key]
    period = st.text_input("\u62a5\u8868\u671f\u95f4", value=current_report_period(), key="report_period")
    institution = st.selectbox("\u673a\u6784", ["\u96c6\u56e2", "\u672c\u884c"], key="make_report_institution")
    institution_context = {"name": institution, "period": period}
    render_report_generation_action(report_key, report_config, report_types, institution_context)
    st.divider()
    render_pdf_validation_action(report_key, report_config, report_types)


def render_view_report_page(access_control: dict[str, Any], report_types: dict[str, Any], user: dict[str, Any]) -> None:
    st.subheader("\u67e5\u770b\u62a5\u8868")
    labels = {str(config.get("display_name") or key): key for key, config in report_types.items()}
    if not labels:
        st.warning("\u672a\u52a0\u8f7d\u5230\u62a5\u8868\u7c7b\u578b\u914d\u7f6e\u3002")
        return
    selected_label = st.selectbox("\u62a5\u8868\u7c7b\u578b", list(labels.keys()), key="view_report_type")
    report_key = labels[selected_label]
    report_config = report_types[report_key]
    institution = st.selectbox("\u673a\u6784", ["\u96c6\u56e2", "\u672c\u884c"], key="view_report_institution")

    generated_path, generated_df = load_generated_report_for_view(report_key, report_config, institution)
    if generated_path:
        st.caption(f"\u751f\u6210\u7248\uff1a{generated_path}")
        if generated_df is not None:
            st.dataframe(generated_df, use_container_width=True, hide_index=True)
        with open(generated_path, "rb") as fh:
            st.download_button(
                "\u4e0b\u8f7d\u751f\u6210\u7248",
                data=fh.read(),
                file_name=generated_path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    else:
        st.info("\u6682\u65e0\u751f\u6210\u7248\u62a5\u8868\u3002")

    st.divider()
    st.subheader("\u53d1\u5e03\u62a5\u8868")
    if generated_path and st.button("\u53d1\u5e03\u5f53\u524d\u751f\u6210\u7248", type="primary", key=f"publish_{report_key}"):
        try:
            entry = publish_report(report_key, report_config, generated_path, institution)
            st.success(f"\u5df2\u53d1\u5e03\uff1a{entry.get('published_path')}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"\u53d1\u5e03\u5931\u8d25\uff1a{exc}")

    entries = published_entries_for_report(report_key)
    selected_entry = find_published_entry(report_key, institution=institution)
    render_published_workbook_view(report_key, report_config, entries, selected_entry)

def main() -> None:
    st.set_page_config(page_title="财报智控平台", layout="wide", initial_sidebar_state="collapsed")
    apply_global_styles()
    access_control = load_access_control()
    if not is_authenticated(access_control):
        render_login_page(access_control)
        return

    user = current_user(access_control)
    report_types = load_report_types(REPORT_CONFIG_PATH)
    render_top_user_bar(user)
    selected, report_key, report_config = render_unified_navigation(report_types, access_control, user)
    if selected == "home":
        render_workflow_home()
    elif selected == "make_report":
        render_make_report_page(access_control, report_types, user)
    elif selected in {"view_report", "publish_report"}:
        render_view_report_page(access_control, report_types, user)
    elif selected == "admin":
        render_permission_assignment_page(access_control, report_types)
    else:
        st.info("该页面的源码恢复将在后续批次完成。")
