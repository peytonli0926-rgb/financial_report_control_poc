from __future__ import annotations

import html
import json
import marshal
from io import BytesIO
from pathlib import Path

from openpyxl.styles import Font

BASE_DIR = Path(__file__).resolve().parent
RECOVERED_PYC_PATH = BASE_DIR / "app_recovered_full.cpython-314.pyc"


def _load_recovered_app() -> dict:
    data = RECOVERED_PYC_PATH.read_bytes()
    code = marshal.loads(data[16:])
    namespace = {
        "__name__": "_recovered_financial_report_app",
        "__file__": str(BASE_DIR / "app.py"),
        "__package__": None,
        "__builtins__": __builtins__,
    }
    exec(code, namespace)
    return namespace


_app = _load_recovered_app()
st = _app["st"]

pd = _app["pd"]
re = _app["re"]
ACCESS_CONTROL_PATH = _app["ACCESS_CONTROL_PATH"]
UPLOAD_DIR = _app["UPLOAD_DIR"]
OUTPUT_DIR = _app["OUTPUT_DIR"]
UPLOAD_METADATA_PATH = OUTPUT_DIR / "upload_metadata.json"

app_href = _app["app_href"]
is_authenticated = _app["is_authenticated"]
render_login_page = _app["render_login_page"]
render_unified_navigation = _app["render_unified_navigation"]
render_top_user_bar = _app["render_top_user_bar"]
render_workflow_home = _app["render_workflow_home"]


def render_product_header(title: str, subtitle: str, badge: str) -> None:
    return None


def apply_prd_styles() -> None:
    st.markdown(
        """
        <style>
        .dashboard-welcome {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sync_remembered_login_token(access_control: dict) -> None:
    """Compatibility hook used by older login patches."""
    return None


def handle_login_submit(access_control: dict, username: str, password: str) -> bool:
    user = _app["authenticate_user"](access_control, username, password)
    if not user:
        return False
    token = _app["user_auth_token"](user)
    st.session_state["authenticated_username"] = str(user.get("username"))
    st.session_state["auth_token"] = token
    st.session_state["main_navigation_mode"] = "home"
    st.session_state["make_workflow_step"] = None
    st.query_params.update({"auth_token": token, "nav_mode": "home"})
    return True


def render_login_page(access_control: dict) -> None:
    """Render the active login screen without falling back to the recovered legacy UI."""
    import base64

    visual_path = BASE_DIR / "assets" / "login_left_visual.png"
    visual_data_uri = ""
    if visual_path.exists():
        visual_data_uri = "data:image/png;base64," + base64.b64encode(visual_path.read_bytes()).decode("ascii")

    title = "\u767b\u5f55\u8d22\u62a5\u667a\u63a7\u5e73\u53f0"
    subtitle = "\u4f7f\u7528\u5df2\u6388\u6743\u8d26\u53f7\u8fdb\u5165\u62a5\u8868\u7f16\u5236\u3001\u6570\u636e\u6821\u9a8c\u548c\u62ab\u9732\u7ba1\u7406\u5de5\u4f5c\u53f0\u3002"
    footer = "\u6570\u636e\u5b89\u5168\u4fdd\u62a4\u4e2d · \u4f20\u8f93\u52a0\u5bc6 · \u6743\u9650\u7ba1\u63a7 · \u64cd\u4f5c\u53ef\u8ffd\u6eaf"

    st.markdown(
        """
        <style>
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
        }
        .block-container {
            max-width: 1180px !important;
            padding: 1.35rem 3.4rem .8rem !important;
        }
        .stApp {
            background:
                radial-gradient(circle at 13% 18%, rgba(134, 188, 37, .20), transparent 30%),
                radial-gradient(circle at 88% 18%, rgba(18, 76, 120, .15), transparent 27%),
                linear-gradient(132deg, #f4f8ee 0%, #edf5f6 50%, #f8fbf4 100%) !important;
            color: #122019;
        }
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background: repeating-linear-gradient(90deg, rgba(13, 54, 42, .035) 0 1px, transparent 1px 42px);
        }
        div[data-testid="column"] {
            position: relative;
            z-index: 1;
        }
        .login-visual-card {
            max-width: 560px;
            margin: .6rem auto 0;
            padding: 1.05rem;
            border-radius: 28px;
            background: rgba(255, 255, 255, .62);
            border: 1px solid rgba(199, 215, 198, .88);
            box-shadow: 0 26px 72px rgba(25, 72, 62, .12);
            backdrop-filter: blur(12px);
        }
        .login-visual-card img {
            width: 100%;
            display: block;
            border-radius: 20px;
        }
        .login-copy {
            max-width: 430px;
            margin: .6rem auto 0;
            padding: 2rem 2.35rem 1.25rem;
            border-radius: 24px 24px 0 0;
            background: rgba(255, 255, 255, .88);
            border: 1px solid rgba(205, 219, 203, .95);
            border-bottom: 0;
            box-shadow: 0 22px 62px rgba(18, 64, 54, .12);
        }
        .login-brand {
            color: #111814;
            font-size: 1.32rem;
            line-height: 1;
            font-weight: 950;
            letter-spacing: -.04em;
            margin-bottom: 1.35rem;
        }
        .login-brand span { color: #86bc25; }
        .login-kicker {
            display: inline-flex;
            align-items: center;
            min-height: 23px;
            padding: 0 .68rem;
            border-radius: 999px;
            background: rgba(134, 188, 37, .15);
            color: #315c15;
            font-size: .72rem;
            font-weight: 850;
            margin-bottom: .78rem;
        }
        .login-title {
            color: #101c17;
            font-size: 1.78rem;
            line-height: 1.12;
            font-weight: 950;
            letter-spacing: -.055em;
            margin-bottom: .45rem;
        }
        .login-subtitle {
            color: #6f7d75;
            font-size: .88rem;
            line-height: 1.52;
        }
        div[data-testid="stForm"] {
            max-width: 430px;
            margin: -1px auto 0;
            padding: 0 2.35rem 2rem;
            border: 1px solid rgba(205, 219, 203, .95) !important;
            border-top: 0 !important;
            border-radius: 0 0 24px 24px !important;
            background: rgba(255, 255, 255, .88) !important;
            box-shadow: 0 22px 62px rgba(18, 64, 54, .12) !important;
        }
        div[data-testid="stForm"] div[data-testid="stTextInput"] { margin-bottom: .74rem; }
        div[data-testid="stForm"] input {
            min-height: 2.82rem;
            border-radius: 13px !important;
            border: 1px solid #d9e3d5 !important;
            background: #fbfdf9 !important;
            color: #14231b !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.8) !important;
        }
        div[data-testid="stForm"] input:focus {
            border-color: #86bc25 !important;
            box-shadow: 0 0 0 3px rgba(134, 188, 37, .16) !important;
        }
        div[data-testid="stForm"] input::placeholder { color: #9aa79e !important; }
        .login-helper {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #7a877f;
            font-size: .78rem;
            margin: -.05rem 0 1.05rem;
        }
        .login-helper a {
            color: #315c15 !important;
            text-decoration: none !important;
            font-weight: 850;
        }
        div[data-testid="stForm"] button,
        div[data-testid="stForm"] [data-testid="stBaseButton-primary"] {
            min-height: 2.9rem !important;
            border-radius: 13px !important;
            border: 1px solid #65931a !important;
            background: linear-gradient(135deg, #91c83e 0%, #5b8f13 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 16px 28px rgba(93, 143, 19, .22) !important;
            font-weight: 950 !important;
        }
        div[data-testid="stForm"] button p,
        div[data-testid="stForm"] button span,
        div[data-testid="stForm"] [data-testid="stBaseButton-primary"] p,
        div[data-testid="stForm"] [data-testid="stBaseButton-primary"] span {
            color: #ffffff !important;
            font-weight: 950 !important;
        }
        .login-browser {
            max-width: 430px;
            margin: .9rem auto 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: .45rem;
            color: #75827a;
            font-size: .76rem;
        }
        .chrome-dot {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: conic-gradient(#38a852 0 33%, #fbbc05 33% 66%, #ea4335 66% 82%, #4285f4 82% 100%);
        }
        .login-footer {
            position: relative;
            z-index: 1;
            text-align: center;
            color: #75827a;
            font-size: .74rem;
            margin-top: 1.15rem;
        }
        @media (max-width: 980px) {
            .block-container { padding: 1rem !important; }
            .login-visual-card { display: none; }
            .login-copy { margin-top: 1rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.28, 0.92], gap="large")
    with left:
        if visual_data_uri:
            st.markdown(
                f'<div class="login-visual-card"><img src="{visual_data_uri}" alt="Financial report control" /></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="login-visual-card"><div style="padding:4rem 2rem;text-align:center;color:#10261d;font-size:2rem;font-weight:950;">Financial Report Control</div></div>',
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            f"""
            <div class="login-copy">
                <div class="login-brand">Deloitte<span>.</span></div>
                <div class="login-kicker">Financial Report Control</div>
                <div class="login-title">{title}</div>
                <div class="login-subtitle">{subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("\u7528\u6237\u540d", placeholder="\u8bf7\u8f93\u5165\u8d26\u53f7 / \u624b\u673a\u53f7 / \u90ae\u7bb1", label_visibility="collapsed")
            password = st.text_input("\u5bc6\u7801", type="password", placeholder="\u8bf7\u8f93\u5165\u5bc6\u7801", label_visibility="collapsed")
            st.markdown('<div class="login-helper"><span>&#9633; \u8bb0\u4f4f\u6211</span><a href="#">\u5fd8\u8bb0\u5bc6\u7801\uff1f</a></div>', unsafe_allow_html=True)
            submitted = st.form_submit_button("\u767b\u5f55\u7cfb\u7edf", type="primary", use_container_width=True)
        st.markdown(
            '<div class="login-browser"><span class="chrome-dot"></span><span>\u63a8\u8350\u4f7f\u7528 Chrome / Edge \u6700\u65b0\u7248\u672c\u6d4f\u89c8\u5668</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown(f'<div class="login-footer">&copy; 2026 Deloitte Financial Report Control<br>{footer}</div>', unsafe_allow_html=True)

    if submitted:
        if handle_login_submit(access_control, username, password):
            st.rerun()
        st.error("\u7528\u6237\u540d\u6216\u5bc6\u7801\u9519\u8bef\uff0c\u6216\u7528\u6237\u5df2\u505c\u7528\u3002")
FILE_PERMISSION_SCOPE_LABELS = {
    "all": "\u5168\u90e8\u90e8\u95e8",
    "data_provider": "\u6570\u636e\u63d0\u4f9b\u90e8\u95e8\uff08R\u5217\uff09",
    "owner": "\u5f52\u53e3\u90e8\u95e8\uff08O\u5217\uff09",
    "lead": "\u7275\u5934\u90e8\u95e8\uff08Q\u5217\uff09",
}
FILE_PERMISSION_ACTION_LABELS = {
    "view": "\u67e5\u770b",
    "upload": "\u4e0a\u4f20",
    "upload_view": "\u4e0a\u4f20+\u67e5\u770b",
}

FILE_SOURCE_ALIASES = {
    "subject_balance": ["\u79d1\u76ee\u4f59\u989d\u8868"],
    "parent_subject_balance": ["\u672c\u884c\u79d1\u76ee\u4f59\u989d\u8868"],
    "audit_adjustment_parent": ["\u5ba1\u8ba1\u8c03\u6574\u8868", "\u5ba1\u8ba1\u8c03\u6574_\u5e95\u7a3f_\u672c\u884c", "\u672c\u884c\u5ba1\u8ba1\u8c03\u6574"],
    "audit_adjustment_subsidiary": ["\u5ba1\u8ba1\u8c03\u6574\u8868", "\u5ba1\u8ba1\u8c03\u6574_\u5e95\u7a3f_\u5b50\u516c\u53f8", "\u5b50\u516c\u53f8\u5ba1\u8ba1\u8c03\u6574"],
    "consolidation_elimination": ["\u5408\u5e76\u62a5\u8868\u62b5\u9500\u8868", "\u5408\u5e76\u62b5\u6d88", "\u5408\u5e76\u62b5\u9500", "\u5408\u5e76\u62b5\u6d88\u5e95\u7a3f"],
    "subsidiary_subject_balance": ["\u5b50\u516c\u53f8\u79d1\u76ee\u4f59\u989d\u8868"],
    "subsidiary_institution_mapping": ["\u5b50\u516c\u53f8\u673a\u6784\u6620\u5c04\u8868", "\u673a\u6784\u6620\u5c04\u8868"],
    "subsidiary_shareholding_ratio": ["\u5b50\u516c\u53f8\u6301\u80a1\u6bd4\u4f8b", "\u6301\u80a1\u6bd4\u4f8b"],
    "subsidiary_income_statement": ["\u5b50\u516c\u53f8\u5229\u6da6\u8868"],
    "perpetual_bond_detail": ["\u6c38\u7eed\u503a\u660e\u7ec6\u8868", "\u6c38\u7eed\u503a"],
    "oci_detail": ["OCI\u8868", "OCI"],
    "long_term_investment_subsidiary_data": ["\u957f\u6295\u5b50\u516c\u53f8\u6570\u636e", "\u957f\u671f\u80a1\u6743\u6295\u8d44\u5bf9\u5b50\u516c\u53f8\u660e\u7ec6\u6570\u636e"],
    "profit_distribution_proposal": ["\u5229\u6da6\u5206\u914d\u65b9\u6848", "\u5229\u6da6\u5206\u914d\u65b9\u6848\u8bae\u6848"],
    "disclosure_consolidation_structure_chart": ["\u4e2d\u56fd\u4e1c\u65b9\u8d44\u4ea7\u96c6\u56e2\u4fe1\u606f\u62ab\u9732\u5408\u5e76\u67b6\u6784\u56fe", "\u5408\u5e76\u67b6\u6784\u56fe"],
    "central_bank_deposit_tenday": ["存放中央银行款项_旬报表", "存放中央银行款项旬报表", "存放中央银行款项"],
    "interbank_deposit_parent": ["存放同业明细母行"],
    "interbank_deposit_risk": ["存放同业风险明细"],
    "interbank_deposit_yujinzu": ["存放同业明细渝金租"],
    "interbank_deposit_yulicai": ["存放同业明细渝理财"],
    "interbank_deposit_yunnan_xishan": ["存放同业明细云南西山"],
    "interbank_deposit_fujian_shishi": ["存放同业明细福建石狮"],
    "interbank_deposit_yunnan_heqing": ["存放同业明细云南鹤庆"],
    "interbank_deposit_fujian_pingtan": ["存放同业明细福建平潭"],
    "interbank_deposit_jiangsu_zhangjiagang": ["存放同业明细江苏张家港"],
    "interbank_deposit_sichuan_dazhu": ["存放同业明细四川大竹"],
    "interbank_deposit_yunnan_xiangyun": ["存放同业明细云南祥云"],
    "interbank_deposit_guangxi_luzhai": ["存放同业明细广西鹿寨"],
    "interbank_deposit_yunnan_shangrila": ["存放同业明细云南香格里拉"],
    "interbank_deposit_yunnan_dali": ["存放同业明细云南大理"],
    "interbank_deposit_fujian_fuan": ["存放同业明细福建福安"],
    "interbank_deposit_fujian_shaxian": ["存放同业明细福建沙县"],
}


def _split_permission_values(value) -> set[str]:
    if value is None or str(value).strip().lower() == "nan":
        return set()
    return {item.strip() for item in re.split(r"[\u3001,\uff0c;/\uff1b\n]+", str(value)) if item and item.strip()}


def _compact_permission_text(value) -> str:
    return re.sub(r"\s+", "", str(value or "")).lower()


def _rule_file_path() -> Path | None:
    candidates = sorted(UPLOAD_DIR.glob("2-1-*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _file_source_tokens_for_config(file_config: dict) -> list[str]:
    tokens = list(FILE_SOURCE_ALIASES.get(str(file_config.get("file_key")), []))
    display_name = str(file_config.get("display_name") or "")
    stem = Path(display_name).stem
    tokens.extend([display_name, stem])
    prefix = str(file_config.get("prefix") or "")
    if prefix and stem.startswith(prefix):
        tokens.append(stem[len(prefix):])
    return [token for token in tokens if token]


def _rule_source_matches_file(source_token: str, file_config: dict) -> bool:
    source = _compact_permission_text(source_token)
    if not source:
        return False
    for token in _file_source_tokens_for_config(file_config):
        compact = _compact_permission_text(token)
        if compact and (compact == source or compact in source):
            return True
    return False


def build_rule_file_permission_index(base_files: list[dict]) -> dict[str, dict[str, set[str]]]:
    index = {
        str(file_config.get("file_key")): {"data_provider": set(), "owner": set(), "lead": set(), "source": set()}
        for file_config in base_files
    }
    rule_path = _rule_file_path()
    if rule_path is None:
        return index
    try:
        excel = pd.ExcelFile(rule_path)
        for sheet_name in excel.sheet_names:
            df = pd.read_excel(rule_path, sheet_name=sheet_name, header=None, dtype=object)
            if df.shape[1] < 21 or df.shape[0] < 3:
                continue
            for _, row in df.iloc[2:].iterrows():
                owner_values = _split_permission_values(row.iloc[14])
                lead_values = _split_permission_values(row.iloc[16])
                data_provider_values = _split_permission_values(row.iloc[17])
                source_values = _split_permission_values(row.iloc[20])
                if not source_values:
                    continue
                for file_config in base_files:
                    file_key = str(file_config.get("file_key"))
                    if any(_rule_source_matches_file(source, file_config) for source in source_values):
                        index[file_key]["owner"].update(owner_values)
                        index[file_key]["lead"].update(lead_values)
                        index[file_key]["data_provider"].update(data_provider_values)
                        index[file_key]["source"].update(source_values)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"\u8bfb\u53d6\u89c4\u5219\u6587\u4ef6\u90e8\u95e8\u6743\u9650\u5931\u8d25\uff1a{exc}")
    return index


def departments_from_rule_file() -> list[str]:
    rule_path = _rule_file_path()
    departments: set[str] = set()
    if rule_path is None:
        return []
    try:
        excel = pd.ExcelFile(rule_path)
        for sheet_name in excel.sheet_names:
            df = pd.read_excel(rule_path, sheet_name=sheet_name, header=None, dtype=object)
            if df.shape[1] < 18 or df.shape[0] < 3:
                continue
            for column_index in (14, 16, 17):
                for value in df.iloc[2:, column_index].tolist():
                    departments.update(_split_permission_values(value))
    except Exception:
        return []
    return sorted(departments)


def file_upload_permissions(access_control: dict, username: str) -> list[dict]:
    permissions = access_control.setdefault("file_upload_permissions", {})
    value = permissions.get(username, [])
    return value if isinstance(value, list) else []


def user_file_permission(access_control: dict, user: dict, file_config: dict, permission_index: dict) -> tuple[bool, bool, str]:
    if user.get("is_admin") or "admin" in _app["user_role_keys"](access_control, str(user.get("username"))):
        return True, True, "\u7ba1\u7406\u5458\uff1a\u5168\u90e8\u90e8\u95e8 / \u4e0a\u4f20+\u67e5\u770b"
    username = str(user.get("username") or "")
    file_key = str(file_config.get("file_key"))
    file_departments = permission_index.get(file_key, {})
    can_upload = False
    can_view = False
    reasons: list[str] = []
    for permission in file_upload_permissions(access_control, username):
        scope = str(permission.get("scope") or "")
        action = str(permission.get("action") or "")
        departments = {str(item).strip() for item in permission.get("departments", []) if str(item).strip()}
        matched = False
        if scope == "all":
            matched = True
            reason_scope = "\u5168\u90e8\u90e8\u95e8"
        elif scope in {"data_provider", "owner", "lead"}:
            file_scope_departments = set(file_departments.get(scope, set()))
            matched_departments = file_scope_departments & departments
            matched = bool(matched_departments)
            reason_scope = f"{FILE_PERMISSION_SCOPE_LABELS.get(scope, scope)}?{', '.join(sorted(matched_departments))}"
        else:
            reason_scope = scope
        if not matched:
            continue
        if action in {"upload", "upload_view"}:
            can_upload = True
        if action in {"view", "upload_view"}:
            can_view = True
        reasons.append(f"{reason_scope} / {FILE_PERMISSION_ACTION_LABELS.get(action, action)}")
    return can_upload, can_view, "?".join(reasons)


def _file_type_label(file_config: dict) -> str:
    value = file_config.get("file_type")
    if isinstance(value, list):
        return " / ".join(str(item).upper() for item in value)
    return str(value or "").upper()


def _file_uploader_types(file_config: dict) -> list[str] | str:
    value = file_config.get("file_type")
    return [str(item) for item in value] if isinstance(value, list) else str(value or "")


def _apply_upload_page_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --upload-primary: #2f6bff;
            --upload-primary-light: #5caeff;
            --upload-success: #20b26b;
            --upload-warning: #f59e0b;
            --upload-danger: #ef4444;
            --upload-bg: #f6f9fc;
            --upload-card: #ffffff;
            --upload-title: #172b4d;
            --upload-text: #5b6b83;
            --upload-muted: #8a9ab0;
            --upload-border: #e8eef5;
        }
        .upload-shell {
            background:
                radial-gradient(circle at 12% 0%, rgba(47, 107, 255, 0.10), transparent 28%),
                linear-gradient(180deg, #f7fbff 0%, #f6f9fc 100%);
            border: 1px solid #e8eef5;
            border-radius: 22px;
            padding: 22px 24px 18px;
            margin-bottom: 18px;
            box-shadow: 0 12px 34px rgba(23, 43, 77, 0.06);
        }
        .upload-breadcrumb {
            color: var(--upload-muted);
            font-size: 13px;
            margin-bottom: 8px;
        }
        .upload-title-row {
            display: flex;
            justify-content: space-between;
            gap: 18px;
            align-items: flex-start;
            margin-bottom: 18px;
        }
        .upload-title {
            color: var(--upload-title);
            font-size: 30px;
            line-height: 1.16;
            font-weight: 800;
            letter-spacing: -0.03em;
        }
        .upload-subtitle {
            color: var(--upload-text);
            margin-top: 8px;
            font-size: 14px;
        }
        .upload-summary-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 16px;
        }
        .upload-summary-card {
            height: 126px;
            box-sizing: border-box;
            border-radius: 18px;
            background: var(--upload-card);
            box-shadow: 0 8px 24px rgba(47, 107, 255, 0.08);
            border: 1px solid var(--upload-border);
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            overflow: hidden;
            text-decoration: none !important;
            transition: transform .18s ease, box-shadow .18s ease;
        }
        .upload-summary-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(47, 107, 255, 0.14);
        }
        .upload-summary-icon {
            width: 54px;
            height: 54px;
            border-radius: 16px;
            display: grid;
            place-items: center;
            font-size: 25px;
            font-weight: 800;
        }
        .upload-summary-label {
            color: var(--upload-text);
            font-size: 13px;
            font-weight: 700;
            white-space: nowrap;
        }
        .upload-summary-value {
            color: var(--upload-title);
            font-size: 36px;
            line-height: 1;
            font-weight: 850;
            margin: 8px 0 6px;
        }
        .upload-summary-desc {
            color: var(--upload-muted);
            font-size: 12px;
            line-height: 1.35;
            min-height: 32px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .upload-panel {
            background: #fff;
            border: 1px solid var(--upload-border);
            border-radius: 18px;
            padding: 18px;
            margin: 16px 0;
            box-shadow: 0 8px 24px rgba(47, 107, 255, 0.06);
        }
        .upload-table-header {
            color: #6b7c93;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: .02em;
            text-transform: uppercase;
            background: #f7faff;
            border: 1px solid var(--upload-border);
            border-radius: 14px;
            padding: 10px 12px;
            margin-top: 12px;
        }
        .upload-file-name {
            color: var(--upload-title);
            font-size: 14px;
            font-weight: 800;
            line-height: 1.35;
            word-break: break-all;
        }
        .upload-file-desc {
            color: var(--upload-muted);
            font-size: 12px;
            line-height: 1.35;
            margin-top: 4px;
            word-break: break-all;
        }
        .upload-type-pill {
            display: inline-flex;
            align-items: center;
            min-height: 24px;
            padding: 2px 9px;
            border-radius: 999px;
            background: #ecfdf5;
            color: #047857;
            font-size: 12px;
            font-weight: 800;
        }
        .upload-status {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 34px;
            padding: 0 14px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 800;
            border: 1px solid transparent;
            white-space: nowrap;
        }
        .upload-status-pending_upload {
            color: #b45309;
            background: #fffbeb;
            border-color: #fde68a;
        }
        .upload-status-uploaded, .upload-status-check_passed {
            color: #047857;
            background: #ecfdf5;
            border-color: #a7f3d0;
        }
        .upload-status-quality_issue, .upload-status-check_failed, .upload-status-data_inconsistent {
            color: #b91c1c;
            background: #fef2f2;
            border-color: #fecaca;
        }
        .upload-cell-muted {
            color: var(--upload-muted);
            font-size: 13px;
        }
        .upload-empty {
            text-align: center;
            color: var(--upload-muted);
            border: 1px dashed #cbd8ea;
            background: #fbfdff;
            border-radius: 18px;
            padding: 34px 16px;
            margin-top: 12px;
        }
        [data-testid="stFileUploader"] {
            margin: 0 !important;
        }
        [data-testid="stFileUploader"] section {
            min-height: 34px !important;
            padding: 0 !important;
            border: 0 !important;
            background: transparent !important;
        }
        [data-testid="stFileUploader"] section > div {
            display: none !important;
        }
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] svg,
        [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
        }
        [data-testid="stFileUploader"] button {
            min-height: 34px !important;
            height: 34px !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 14px !important;
            border-radius: 999px !important;
            font-size: 13px !important;
            font-weight: 800 !important;
        }
        [data-testid="stFileUploader"] button p {
            font-size: 0 !important;
        }
        [data-testid="stFileUploader"] button p::after {
            content: "上传";
            font-size: 13px !important;
            font-weight: 800 !important;
        }
        .stDownloadButton button {
            min-height: 34px !important;
            height: 34px !important;
            padding: 0 14px !important;
            border-radius: 999px !important;
            font-size: 13px !important;
            font-weight: 800 !important;
        }
        @media (max-width: 1100px) {
            .upload-summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .upload-title-row { display: block; }
        }
        @media (max-width: 700px) {
            .upload-summary-grid { grid-template-columns: 1fr; }
            .upload-shell { padding: 18px 14px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _format_file_size(file_path: Path | None) -> str:
    if file_path is None or not file_path.exists():
        return "--"
    size = file_path.stat().st_size
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024
    return "--"


def _uploaded_time_text(file_path: Path | None) -> str:
    if file_path is None or not file_path.exists():
        return "--"
    meta = upload_metadata_for_source(file_path.name)
    uploaded_at = str(meta.get("uploaded_at") or "")
    if uploaded_at:
        return uploaded_at
    return pd.Timestamp(file_path.stat().st_mtime, unit="s").strftime("%Y-%m-%d %H:%M:%S")


def _extract_department_text(reason: str, permission_index: dict, file_config: dict) -> str:
    if "全部部门" in str(reason):
        return "全部部门"
    file_key = str(file_config.get("file_key"))
    departments: set[str] = set()
    for scope in ("owner", "lead", "data_provider"):
        departments.update(permission_index.get(file_key, {}).get(scope, set()))
    if departments:
        return "、".join(sorted(departments)[:3])
    if reason:
        return str(reason).split("/")[0].replace("?", "：")
    return "未配置部门"


def _build_upload_records(visible_rows: list[tuple[dict, bool, bool, str]], permission_index: dict) -> list[dict]:
    records = []
    for file_config, can_upload, can_view, reason in visible_rows:
        uploaded_path = find_uploaded_file_for_config(file_config)
        status = "uploaded" if uploaded_path else "pending_upload"
        upload_time = _uploaded_time_text(uploaded_path)
        records.append(
            {
                "file_config": file_config,
                "can_upload": can_upload,
                "can_view": can_view,
                "reason": reason,
                "uploaded_path": uploaded_path,
                "file_name": str((uploaded_path.name if uploaded_path else file_config.get("display_name")) or ""),
                "description": str(file_config.get("description") or ""),
                "department": _extract_department_text(reason, permission_index, file_config),
                "file_type": _file_type_label(file_config),
                "file_size": _format_file_size(uploaded_path),
                "upload_time": upload_time,
                "status": status,
                "required": bool(file_config.get("required")),
            }
        )
    return records


def _status_label(status: str) -> str:
    return {
        "all": "全部状态",
        "uploaded_group": "已上传文件",
        "quality_issue_group": "数据质量异常",
        "pending_upload": "待上传",
        "uploaded": "已上传",
        "processing": "处理中",
        "check_passed": "校验通过",
        "check_failed": "校验失败",
        "quality_issue": "数据质量异常",
        "data_inconsistent": "数据不一致",
    }.get(status, status)


def _status_badge(status: str) -> str:
    label = _status_label(status)
    return f'<span class="upload-status upload-status-{html.escape(status)}">{html.escape(label)}</span>'


def _render_upload_summary_cards(records: list[dict]) -> None:
    total = len(records)
    uploaded = sum(1 for item in records if item["uploaded_path"] is not None)
    pending = max(0, total - uploaded)
    quality_issue = sum(1 for item in records if item["status"] in {"quality_issue", "check_failed", "data_inconsistent"})
    cards = [
        ("all", "≡", "共需上传文件", total, "当前账号可见的文件任务总数", "#2f6bff", "#eef4ff"),
        ("uploaded_group", "✓", "已上传文件", uploaded, "已完成上传并进入管理范围", "#20b26b", "#ecfdf5"),
        ("pending_upload", "○", "待上传文件", pending, "尚未上传，需尽快补齐", "#f59e0b", "#fffbeb"),
        ("quality_issue_group", "!", "数据质量异常文件", quality_issue, "已上传但存在校验异常或不一致", "#ef4444", "#fef2f2"),
    ]
    columns = st.columns(4)
    for column, (status, icon, label, value, desc, color, bg) in zip(columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="upload-summary-card">
                  <div class="upload-summary-icon" style="color:{color};background:{bg};">{icon}</div>
                  <div>
                    <div class="upload-summary-label">{html.escape(label)}</div>
                    <div class="upload-summary-value">{value}<span style="font-size:15px;margin-left:4px;">个</span></div>
                    <div class="upload-summary-desc">{html.escape(desc)}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"筛选：{label}", key=f"upload_summary_filter_{status}", use_container_width=True):
                st.session_state["upload_filter_status"] = status
                st.session_state["upload_table_page"] = 1
                st.rerun()


def _filter_upload_records(records: list[dict]) -> list[dict]:
    status = st.session_state.get("upload_filter_status", "all")
    department = st.session_state.get("upload_filter_department", "全部部门")
    keyword = str(st.session_state.get("upload_filter_keyword", "") or "").strip().lower()
    date_range = st.session_state.get("upload_filter_date_range")

    filtered = records
    if status == "uploaded_group":
        filtered = [item for item in filtered if item["uploaded_path"] is not None]
    elif status == "quality_issue_group":
        filtered = [item for item in filtered if item["status"] in {"quality_issue", "check_failed", "data_inconsistent"}]
    elif status != "all":
        filtered = [item for item in filtered if item["status"] == status]
    if department and department != "全部部门":
        filtered = [item for item in filtered if department in item["department"]]
    if keyword:
        filtered = [
            item for item in filtered
            if keyword in item["file_name"].lower() or keyword in item["description"].lower()
        ]
    if isinstance(date_range, tuple) and len(date_range) == 2 and all(date_range):
        start_date, end_date = date_range
        filtered = [
            item for item in filtered
            if item["upload_time"] != "--"
            and start_date <= pd.Timestamp(item["upload_time"]).date() <= end_date
        ]
    return filtered


def _render_upload_filters(records: list[dict]) -> None:
    departments = sorted({item["department"] for item in records if item["department"]})
    department_options = ["全部部门"] + departments
    status_options = ["all", "pending_upload", "uploaded", "uploaded_group", "quality_issue_group"]
    filter_columns = st.columns([1.2, 1.5, 1.4, 2.4, 0.8, 0.8])
    with filter_columns[0]:
        st.selectbox(
            "状态",
            status_options,
            format_func=_status_label,
            key="upload_filter_status",
            on_change=lambda: st.session_state.update({"upload_table_page": 1}),
        )
    with filter_columns[1]:
        st.date_input(
            "上传日期",
            value=None,
            key="upload_filter_date_range",
            on_change=lambda: st.session_state.update({"upload_table_page": 1}),
        )
    with filter_columns[2]:
        st.selectbox(
            "所属部门",
            department_options,
            key="upload_filter_department",
            on_change=lambda: st.session_state.update({"upload_table_page": 1}),
        )
    with filter_columns[3]:
        st.text_input(
            "文件名称",
            placeholder="请输入文件名称或编码",
            key="upload_filter_keyword",
            on_change=lambda: st.session_state.update({"upload_table_page": 1}),
        )
    with filter_columns[4]:
        st.markdown("<div style='height: 1.78rem'></div>", unsafe_allow_html=True)
        if st.button("重置", use_container_width=True):
            for key in ("upload_filter_status", "upload_filter_department", "upload_filter_keyword", "upload_filter_date_range"):
                st.session_state.pop(key, None)
            st.session_state["upload_table_page"] = 1
            st.rerun()
    with filter_columns[5]:
        st.markdown("<div style='height: 1.78rem'></div>", unsafe_allow_html=True)
        if st.button("刷新", use_container_width=True):
            st.rerun()


def _render_batch_upload_panel(records: list[dict]) -> None:
    if not st.session_state.get("upload_batch_panel_open"):
        return
    with st.expander("批量上传文件", expanded=True):
        st.caption("支持多文件选择。系统按文件名前缀匹配当前可上传任务，匹配成功后沿用现有保存与校验逻辑。")
        uploadable_records = [item for item in records if item["can_upload"]]
        uploaded_files = st.file_uploader(
            "选择文件",
            type=["xlsx", "xls", "csv", "docx", "pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="batch_upload_files",
        )
        if st.button("开始批量上传", type="primary", disabled=not uploaded_files, use_container_width=True):
            success_count = 0
            failed_messages = []
            for uploaded_file in uploaded_files or []:
                name = Path(str(uploaded_file.name)).name
                matched_record = next(
                    (
                        item for item in uploadable_records
                        if name.startswith(str(item["file_config"].get("prefix") or ""))
                    ),
                    None,
                )
                if matched_record is None:
                    failed_messages.append(f"{name}：未匹配到当前账号可上传的文件任务")
                    continue
                try:
                    save_uploaded_file_for_config(uploaded_file, matched_record["file_config"])
                    success_count += 1
                    render_interbank_upload_validation(str(matched_record["file_config"].get("file_key") or ""))
                except Exception as exc:  # noqa: BLE001
                    failed_messages.append(f"{name}：{exc}")
            if success_count:
                st.success(f"批量上传完成：成功 {success_count} 个")
            for message in failed_messages:
                st.warning(message)


def _render_upload_table_header() -> None:
    st.markdown('<div class="upload-table-header">', unsafe_allow_html=True)
    header_columns = st.columns([0.45, 0.55, 2.85, 1.35, 0.8, 0.95, 1.25, 0.9, 2.8])
    labels = ["", "#", "文件名称", "所属部门", "类型", "大小", "上传时间", "状态", "操作"]
    for column, label in zip(header_columns, labels):
        column.markdown(f"**{label}**")
    st.markdown("</div>", unsafe_allow_html=True)


def render_permission_limited_upload_row(index: int, record: dict) -> None:
    file_config = record["file_config"]
    uploaded_path = record["uploaded_path"]
    file_key = str(file_config.get("file_key") or "")
    row_columns = st.columns([0.45, 0.55, 2.85, 1.35, 0.8, 0.95, 1.25, 0.9, 2.8])
    with row_columns[0]:
        st.checkbox("选择", key=f"upload_select_{file_config.get('file_key')}", label_visibility="collapsed")
    row_columns[1].markdown(f"**{index}**")
    row_columns[2].markdown(
        f"""
        <div class="upload-file-name">{html.escape(record["file_name"])}</div>
        <div class="upload-file-desc">{html.escape(record["description"])}</div>
        """,
        unsafe_allow_html=True,
    )
    row_columns[3].markdown(f'<span class="upload-cell-muted">{html.escape(record["department"])}</span>', unsafe_allow_html=True)
    row_columns[4].markdown(f'<span class="upload-type-pill">{html.escape(record["file_type"])}</span>', unsafe_allow_html=True)
    row_columns[5].markdown(f'<span class="upload-cell-muted">{html.escape(record["file_size"])}</span>', unsafe_allow_html=True)
    row_columns[6].markdown(f'<span class="upload-cell-muted">{html.escape(record["upload_time"])}</span>', unsafe_allow_html=True)
    row_columns[7].markdown(_status_badge(record["status"]), unsafe_allow_html=True)
    with row_columns[8]:
        action_columns = st.columns([1, 1])
        with action_columns[0]:
            if uploaded_path and record["can_view"]:
                st.download_button(
                    "下载",
                    data=uploaded_path.read_bytes(),
                    file_name=uploaded_path.name,
                    key=f"permission_download_{file_config.get('file_key')}",
                    use_container_width=True,
                )
            elif uploaded_path:
                st.caption("不可查看")
            else:
                st.caption("暂无文件")
        with action_columns[1]:
            if record["can_upload"]:
                upload_nonce_key = f"permission_upload_nonce_{file_key}"
                upload_nonce = int(st.session_state.get(upload_nonce_key, 0))
                uploaded_file = st.file_uploader(
                    "重传" if uploaded_path else "上传",
                    type=_file_uploader_types(file_config),
                    key=f"permission_upload_{file_key}_{upload_nonce}",
                    label_visibility="collapsed",
                )
                if uploaded_file is not None:
                    try:
                        uploaded_path = save_uploaded_file_for_config(uploaded_file, file_config)
                        st.session_state["upload_success_message"] = f"上传成功：{uploaded_path.name}"
                        st.session_state[upload_nonce_key] = upload_nonce + 1
                        render_interbank_upload_validation(file_key)
                        st.rerun()
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"保存文件失败：{exc}")
            else:
                st.caption("不可上传")
    st.divider()


def render_base_file_uploaders(base_files: list[dict]) -> None:
    _apply_upload_page_styles()
    query_status = st.query_params.get("upload_status_filter")
    if query_status in {"all", "uploaded_group", "pending_upload", "quality_issue_group"}:
        if st.session_state.get("upload_filter_status") != query_status:
            st.session_state["upload_filter_status"] = query_status
            st.session_state["upload_table_page"] = 1
    access_control = _app["load_access_control"]()
    user = _app["current_user"](access_control)
    permission_index = build_rule_file_permission_index(base_files)
    visible_rows = []
    for file_config in base_files:
        can_upload, can_view, reason = user_file_permission(access_control, user, file_config, permission_index)
        if can_upload or can_view:
            visible_rows.append((file_config, can_upload, can_view, reason))

    render_pending_interbank_validation_messages()
    upload_success_message = st.session_state.pop("upload_success_message", "")
    if upload_success_message:
        st.success(upload_success_message)
    if not visible_rows:
        st.markdown('<div class="upload-empty">当前账号没有匹配的上传文件权限，请联系系统管理员配置。</div>', unsafe_allow_html=True)
        return

    records = _build_upload_records(visible_rows, permission_index)
    _render_upload_summary_cards(records)
    _render_batch_upload_panel(records)

    filtered_records = records

    page_size = 10
    total_pages = max(1, (len(filtered_records) + page_size - 1) // page_size)
    current_page = max(1, min(int(st.session_state.get("upload_table_page", 1)), total_pages))
    st.session_state["upload_table_page"] = current_page

    start_index = (current_page - 1) * page_size
    page_rows = filtered_records[start_index:start_index + page_size]
    _render_upload_table_header()
    if not page_rows:
        st.markdown('<div class="upload-empty">未找到符合条件的文件</div>', unsafe_allow_html=True)
    for offset, record in enumerate(page_rows, start=1):
        render_permission_limited_upload_row(start_index + offset, record)

    nav_left, nav_mid, nav_jump, nav_right = st.columns([1.1, 2.5, 1.2, 1.1])
    if nav_left.button("上一页", disabled=current_page <= 1, use_container_width=True):
        st.session_state["upload_table_page"] = current_page - 1
        st.rerun()
    nav_mid.markdown(
        f"<div style='text-align:center;padding-top:.55rem;color:#5b6b83;'>共 {len(filtered_records)} 条，第 {current_page} / {total_pages} 页</div>",
        unsafe_allow_html=True,
    )
    jump_page = nav_jump.number_input(
        "跳至",
        min_value=1,
        max_value=total_pages,
        value=current_page,
        step=1,
        label_visibility="collapsed",
    )
    if int(jump_page) != current_page:
        st.session_state["upload_table_page"] = int(jump_page)
        st.rerun()
    if nav_right.button("下一页", disabled=current_page >= total_pages, use_container_width=True):
        st.session_state["upload_table_page"] = current_page + 1
        st.rerun()

    render_interbank_interest_mapping_action()
    render_interbank_generated_downloads()


def render_interbank_interest_mapping_action() -> None:
    st.markdown("### 存放同业应计利息映射")
    st.caption("使用 5-2-2-1 风险明细 AB列更新 5-2-1-1 母行明细 K列，并合并 5-2-1-1 到 5-2-1-15 明细。")
    mode = st.radio(
        "零本金有利息处理模式",
        ["strict", "force_full"],
        index=1,
        horizontal=True,
        format_func=lambda value: "严格模式" if value == "strict" else "全量映射模式",
        key="interbank_mapping_mode",
    )
    if not st.button("生成存放同业映射结果", type="primary", use_container_width=True):
        return
    try:
        from engine.interbank_interest_mapper import MapperConfig, run_interbank_interest_mapping

        principal_file = _find_upload_file_by_prefix("5-2-1-1-1231")
        risk_file = _find_upload_file_by_prefix("5-2-2-1-1231")
        if principal_file is None:
            st.error("未找到 5-2-1-1-1231 存放同业明细母行文件，请先上传。")
            return
        if risk_file is None:
            st.error("未找到 5-2-2-1-1231 存放同业风险明细文件，请先上传。")
            return
        detail_files = [
            path
            for path in sorted(UPLOAD_DIR.glob("5-2-1-*-1231*.xlsx"))
            if not path.name.startswith("5-2-1-1-")
        ]
        output_path = BASE_DIR / "data" / "output" / "5-2-1-1_ACCR_INTEREST_自动映射结果.xlsx"
        run_interbank_interest_mapping(
            principal_file=principal_file,
            risk_file=risk_file,
            detail_files=detail_files,
            output_file=output_path,
            config=MapperConfig(mapping_mode=mode),
        )
        st.success(f"已生成：{output_path.name}")
        render_interbank_mapping_validation(output_path)
        st.download_button(
            "下载映射结果",
            data=output_path.read_bytes(),
            file_name=output_path.name,
            use_container_width=True,
        )
    except Exception as exc:  # noqa: BLE001
        st.error(f"生成存放同业映射结果失败：{exc}")


def render_interbank_generated_downloads() -> None:
    output_dir = BASE_DIR / "data" / "output"
    files = [
        ("\u4e0b\u8f7d5-2-1\u5408\u5e76\u68c0\u67e5\u6587\u4ef6", output_dir / "interbank_deposit_5-2-1_merged_check.xlsx"),
        ("\u4e0b\u8f7dB0260-B0264\u62a5\u8868\u7ed3\u679c", output_dir / "interbank_deposit_report_B260_B264.xlsx"),
        ("\u4e0b\u8f7d5-2-1-1\u6620\u5c04\u7ed3\u679c", output_dir / "5-2-1-1_ACCR_INTEREST_\u81ea\u52a8\u6620\u5c04\u7ed3\u679c.xlsx"),
    ]
    available = [(label, path) for label, path in files if path.exists()]
    if not available:
        return
    st.markdown("### \u5df2\u751f\u6210\u6587\u4ef6\u4e0b\u8f7d")
    columns = st.columns(min(len(available), 3))
    for index, (label, path) in enumerate(available):
        with columns[index % len(columns)]:
            st.download_button(
                label,
                data=path.read_bytes(),
                file_name=path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"interbank_generated_download_{path.name}",
                use_container_width=True,
            )


def _find_upload_file_by_prefix(prefix: str) -> Path | None:
    matches = sorted(UPLOAD_DIR.glob(f"{prefix}*.xlsx"), key=lambda path: path.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def find_uploaded_file_for_config(file_config: dict) -> Path | None:
    prefix = str(file_config.get("prefix") or "")
    if not prefix:
        return _app["find_uploaded_file"](file_config)
    file_types = _file_uploader_types(file_config)
    suffixes = [file_types] if isinstance(file_types, str) else list(file_types)
    suffixes = [str(item).lower().lstrip(".") for item in suffixes if str(item).strip()]
    matches = [
        path
        for path in UPLOAD_DIR.iterdir()
        if path.is_file()
        and path.name.startswith(prefix)
        and (not suffixes or path.suffix.lower().lstrip(".") in suffixes)
    ]
    return sorted(matches, key=lambda path: path.stat().st_mtime, reverse=True)[0] if matches else None


def save_uploaded_file_for_config(uploaded_file, file_config: dict) -> Path:
    if uploaded_file is None:
        raise ValueError("上传文件不能为空。")
    source_name = Path(str(getattr(uploaded_file, "name", ""))).name
    if not source_name:
        raise ValueError("上传文件缺少文件名。")
    prefix = str(file_config.get("prefix") or "")
    if prefix and not source_name.startswith(prefix):
        raise ValueError(f"文件名必须以 {prefix} 开头。")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / source_name
    with save_path.open("wb") as output_file:
        if hasattr(uploaded_file, "getbuffer"):
            output_file.write(uploaded_file.getbuffer())
        else:
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            content = uploaded_file.read()
            if isinstance(content, str):
                content = content.encode("utf-8")
            output_file.write(content)
    record_upload_metadata(save_path, file_config)
    return save_path


def load_upload_metadata() -> dict:
    if not UPLOAD_METADATA_PATH.exists():
        return {}
    try:
        data = json.loads(UPLOAD_METADATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_upload_metadata(metadata: dict) -> None:
    UPLOAD_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    UPLOAD_METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def record_upload_metadata(file_path: Path, file_config: dict) -> None:
    try:
        access_control = _app["load_access_control"]()
        user = _app["current_user"](access_control) or {}
    except Exception:
        user = {}
    username = str(user.get("username") or st.session_state.get("authenticated_username") or "")
    display_name = str(user.get("name") or user.get("display_name") or username or "未知")
    stat = file_path.stat()
    metadata = load_upload_metadata()
    metadata[file_path.name] = {
        "file_name": file_path.name,
        "file_key": str(file_config.get("file_key") or ""),
        "display_name": str(file_config.get("display_name") or file_path.name),
        "uploaded_by": username or "未知",
        "uploaded_by_name": display_name,
        "uploaded_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_mtime": pd.Timestamp(stat.st_mtime, unit="s").strftime("%Y-%m-%d %H:%M:%S"),
        "file_size": stat.st_size,
    }
    save_upload_metadata(metadata)


def upload_metadata_for_source(source_file: str) -> dict:
    metadata = load_upload_metadata()
    if source_file in metadata:
        return metadata[source_file]
    path = OUTPUT_DIR / source_file
    if not path.exists():
        path = UPLOAD_DIR / source_file
    if path.exists():
        stat = path.stat()
        return {
            "file_name": source_file,
            "file_key": "",
            "display_name": source_file,
            "uploaded_by": "未知",
            "uploaded_by_name": "历史上传/未知",
            "uploaded_at": pd.Timestamp(stat.st_mtime, unit="s").strftime("%Y-%m-%d %H:%M:%S"),
            "file_mtime": pd.Timestamp(stat.st_mtime, unit="s").strftime("%Y-%m-%d %H:%M:%S"),
            "file_size": stat.st_size,
        }
    return {
        "file_name": source_file,
        "file_key": "",
        "display_name": source_file,
        "uploaded_by": "未知",
        "uploaded_by_name": "历史上传/未知",
        "uploaded_at": "",
        "file_mtime": "",
        "file_size": "",
    }


def _interbank_trace_metric_config(metric_code: str) -> dict:
    from engine.interbank_deposit_report import (
        B0260_CONSOLIDATION_ADJUSTMENTS,
        DOMESTIC_BANK,
        DOMESTIC_NON_BANK,
        OVERSEAS_BANK,
    )

    adjustments = [
        {
            "调整科目": account_code,
            "调整说明": description,
            "调整金额-元": float(amount),
            "调整金额-千元": float(amount / 1000),
            "数据来源": "程序内置B0260指定合并抵销金额",
        }
        for account_code, description, amount in B0260_CONSOLIDATION_ADJUSTMENTS
    ]
    configs = {
        "B0260": {
            "metric_name": "存放中国境内银行款项",
            "category": DOMESTIC_BANK,
            "rule": "按交易对手分类汇总5-2-1明细M列折合人民币余额+K列应计利息，并加B0260指定合并抵销金额",
            "adjustments": adjustments,
        },
        "B0261": {
            "metric_name": "存放中国境内其他金融机构款项",
            "category": DOMESTIC_NON_BANK,
            "rule": "按交易对手分类汇总5-2-1明细M列折合人民币余额+K列应计利息",
            "adjustments": [],
        },
        "B0262": {
            "metric_name": "存放中国境外银行款项",
            "category": OVERSEAS_BANK,
            "rule": "按交易对手分类汇总5-2-1明细M列折合人民币余额+K列应计利息",
            "adjustments": [],
        },
    }
    metric_code = str(metric_code or "").strip().upper()
    if metric_code not in configs:
        raise ValueError(f"暂不支持 {metric_code or '空'} 指标追溯。")
    return configs[metric_code]


def build_interbank_metric_trace_workbook(metric_code: str) -> bytes:
    from engine.interbank_deposit_report import (
        load_interbank_details,
    )

    metric_code = str(metric_code or "").strip().upper()
    metric_config = _interbank_trace_metric_config(metric_code)
    details = load_interbank_details(UPLOAD_DIR)
    details = details[details["COUNTERPARTY_CATEGORY"] == metric_config["category"]].copy()
    if details.empty:
        raise ValueError(f"未找到 {metric_code} 对应的明细数据。")

    details["本金余额-元"] = pd.to_numeric(details["BALANCE"], errors="coerce")
    details["应计利息-元"] = pd.to_numeric(details["ACCR_INTEREST"], errors="coerce")
    details["明细金额-元"] = pd.to_numeric(details["TOTAL_AMOUNT"], errors="coerce")
    details["明细金额-千元"] = details["明细金额-元"] / 1000
    details["来源文件"] = details["SOURCE_FILE"].astype(str)
    details["来源范围"] = details["SOURCE_SCOPE"].astype(str)
    details["Excel行号"] = details.get("EXCEL_ROW_NO", pd.NA)

    source_rows = []
    for source_file, source_df in details.groupby("来源文件", dropna=False):
        meta = upload_metadata_for_source(str(source_file))
        source_rows.append(
            {
                "来源文件": source_file,
                "明细笔数": int(len(source_df)),
                "明细金额-元": float(source_df["明细金额-元"].sum()),
                "明细金额-千元": float(source_df["明细金额-千元"].sum()),
                "上传时间": meta.get("uploaded_at", ""),
                "上传人": meta.get("uploaded_by_name", ""),
                "上传账号": meta.get("uploaded_by", ""),
                "文件修改时间": meta.get("file_mtime", ""),
                "文件大小": meta.get("file_size", ""),
            }
        )
    source_df = pd.DataFrame(source_rows)

    adjustments_df = pd.DataFrame(
        metric_config["adjustments"],
        columns=["调整科目", "调整说明", "调整金额-元", "调整金额-千元", "数据来源"],
    )

    detail_amount = float(details["明细金额-元"].sum())
    adjustment_amount = float(adjustments_df["调整金额-元"].sum()) if not adjustments_df.empty else 0.0
    generated_amount = (detail_amount + adjustment_amount) / 1000
    summary_df = pd.DataFrame(
        [
            {"项目": "指标编码", "内容": metric_code},
            {"项目": "指标名称", "内容": metric_config["metric_name"]},
            {"项目": "期间", "内容": "20251231"},
            {"项目": "加工规则", "内容": metric_config["rule"]},
            {"项目": "明细金额-元", "内容": detail_amount},
            {"项目": "合并抵销金额-元", "内容": adjustment_amount},
            {"项目": "生成金额-千元", "内容": generated_amount},
            {"项目": "明细笔数", "内容": int(len(details))},
            {"项目": "来源文件数", "内容": int(details["来源文件"].nunique())},
        ]
    )

    detail_columns = [
        "来源范围",
        "来源文件",
        "Excel行号",
        "COUNTERPARTY_CATEGORY",
        "本金余额-元",
        "应计利息-元",
        "明细金额-元",
        "明细金额-千元",
    ]
    detail_export = details[detail_columns].rename(columns={"COUNTERPARTY_CATEGORY": "交易对手分类"})

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="加工规则与汇总", index=False)
        detail_export.to_excel(writer, sheet_name="明细数据", index=False)
        source_df.to_excel(writer, sheet_name="来源文件", index=False)
        adjustments_df.to_excel(writer, sheet_name="合并抵销调整", index=False)
        for worksheet in writer.book.worksheets:
            for cell in worksheet[1]:
                cell.font = Font(bold=True)
            for column_cells in worksheet.columns:
                header = column_cells[0].value
                max_len = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells[:200])
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_len + 2, len(str(header)) + 2), 60)
    output.seek(0)
    return output.getvalue()


def build_b0260_trace_workbook() -> bytes:
    return build_interbank_metric_trace_workbook("B0260")


def render_interbank_upload_validation(file_key: str) -> None:
    if not file_key.startswith("interbank_deposit_"):
        return
    messages = []
    try:
        from engine.interbank_upload_validator import (
            validate_parent_interbank_principal,
            validate_subsidiary_interbank_file_interest,
            validate_subsidiary_interbank_file_principal,
        )

        results = []
        if file_key == "interbank_deposit_parent":
            results.append(validate_parent_interbank_principal(UPLOAD_DIR))
        elif file_key == "interbank_deposit_risk":
            messages.extend(run_interbank_mapping_after_risk_upload())
        else:
            uploaded_path = find_uploaded_file_for_config({"prefix": _interbank_prefix_for_file_key(file_key), "file_type": "xlsx"})
            if uploaded_path is not None:
                results.append(validate_subsidiary_interbank_file_principal(UPLOAD_DIR, uploaded_path))
                results.append(validate_subsidiary_interbank_file_interest(UPLOAD_DIR, uploaded_path))
        for result in [item for item in results if item is not None]:
            messages.append(("success" if result.passed else "warning", result.message))
    except Exception as exc:  # noqa: BLE001
        messages.append(("warning", f"存放同业上传校验失败：{exc}"))
    if messages:
        st.session_state["interbank_validation_messages"] = messages
        for level, message in messages:
            if level == "success":
                st.success(message)
            else:
                st.warning(message)


def render_pending_interbank_validation_messages() -> None:
    messages = st.session_state.pop("interbank_validation_messages", [])
    for level, message in messages:
        if level == "success":
            st.success(message)
        else:
            st.warning(message)


def run_interbank_mapping_after_risk_upload() -> list[tuple[str, str]]:
    messages: list[tuple[str, str]] = []
    try:
        from engine.interbank_interest_mapper import MapperConfig, run_interbank_interest_mapping
        from engine.interbank_upload_validator import validate_parent_interbank_interest

        principal_file = _find_upload_file_by_prefix("5-2-1-1-1231")
        risk_file = _find_upload_file_by_prefix("5-2-2-1-1231")
        if principal_file is None:
            return [("warning", "已上传风险明细，但未找到 5-2-1-1-1231 存放同业明细母行，暂不能把 AB 列更新到 K 列。")]
        if risk_file is None:
            return [("warning", "未找到 5-2-2-1-1231 存放同业风险明细，暂不能执行应计利息映射。")]
        detail_files = [
            path
            for path in sorted(UPLOAD_DIR.glob("5-2-1-*-1231*.xlsx"))
            if not path.name.startswith("5-2-1-1-")
        ]
        output_path = BASE_DIR / "data" / "output" / "5-2-1-1_ACCR_INTEREST_自动映射结果.xlsx"
        run_interbank_interest_mapping(
            principal_file=principal_file,
            risk_file=risk_file,
            detail_files=detail_files,
            output_file=output_path,
            config=MapperConfig(mapping_mode="force_full"),
        )
        messages.append(("success", f"已将 5-2-2-1 AB列映射更新到 5-2-1-1 K列，结果文件：{output_path.name}"))
        result = validate_parent_interbank_interest(UPLOAD_DIR, mapped_file=output_path)
        if result is not None:
            messages.append(("success" if result.passed else "warning", result.message))
    except Exception as exc:  # noqa: BLE001
        messages.append(("warning", f"5-2-2-1 上传后自动映射或K列校验失败：{exc}"))
    return messages


def _interbank_prefix_for_file_key(file_key: str) -> str:
    prefix_by_key = {
        "interbank_deposit_yujinzu": "5-2-1-2-1231",
        "interbank_deposit_yulicai": "5-2-1-3-1231",
        "interbank_deposit_yunnan_xishan": "5-2-1-4-1231",
        "interbank_deposit_fujian_shishi": "5-2-1-5-1231",
        "interbank_deposit_yunnan_heqing": "5-2-1-6-1231",
        "interbank_deposit_fujian_pingtan": "5-2-1-7-1231",
        "interbank_deposit_jiangsu_zhangjiagang": "5-2-1-8-1231",
        "interbank_deposit_sichuan_dazhu": "5-2-1-9-1231",
        "interbank_deposit_yunnan_xiangyun": "5-2-1-10-1231",
        "interbank_deposit_guangxi_luzhai": "5-2-1-11-1231",
        "interbank_deposit_yunnan_shangrila": "5-2-1-12-1231",
        "interbank_deposit_yunnan_dali": "5-2-1-13-1231",
        "interbank_deposit_fujian_fuan": "5-2-1-14-1231",
        "interbank_deposit_fujian_shaxian": "5-2-1-15-1231",
    }
    return prefix_by_key.get(file_key, "")


def render_interbank_mapping_validation(output_path: Path) -> None:
    try:
        from engine.interbank_upload_validator import validate_parent_interbank_interest

        result = validate_parent_interbank_interest(UPLOAD_DIR, mapped_file=output_path)
        if result is None:
            return
        if result.passed:
            st.success(result.message)
        else:
            st.warning(result.message)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"存放同业映射后利息校验失败：{exc}")


def render_file_upload_permission_admin(access_control: dict) -> None:
    st.markdown("---")
    st.subheader("\u4e0a\u4f20\u6587\u4ef6\u6743\u9650")
    st.caption("\u6309\u89c4\u5219\u6587\u4ef6\u4e2d\u7684\u90e8\u95e8\u5217\u6388\u6743\uff1aO\u5217\u5f52\u53e3\u90e8\u95e8\u3001Q\u5217\u7275\u5934\u90e8\u95e8\u3001R\u5217\u6570\u636e\u63d0\u4f9b\u90e8\u95e8\uff1b\u6743\u9650\u52a8\u4f5c\u5206\u4e3a\u67e5\u770b\u3001\u4e0a\u4f20\u3001\u4e0a\u4f20+\u67e5\u770b\u3002")
    users = [user for user in access_control.get("users", []) if user.get("active", True)]
    usernames = [str(user.get("username")) for user in users]
    if not usernames:
        st.info("\u6682\u65e0\u53ef\u6388\u6743\u7528\u6237\u3002")
        return
    selected_username = st.selectbox("\u6388\u6743\u7528\u6237", usernames, format_func=lambda value: next((f"{u.get('name') or u.get('display_name') or value}\uff08{value}\uff09" for u in users if str(u.get('username')) == value), value), key="file_permission_user")
    current_permissions = file_upload_permissions(access_control, selected_username)
    if current_permissions:
        display_rows = [
            {
                "\u8303\u56f4": FILE_PERMISSION_SCOPE_LABELS.get(str(item.get("scope")), str(item.get("scope"))),
                "\u90e8\u95e8": "\u3001".join(item.get("departments", [])) if item.get("scope") != "all" else "\u5168\u90e8",
                "\u6743\u9650": FILE_PERMISSION_ACTION_LABELS.get(str(item.get("action")), str(item.get("action"))),
            }
            for item in current_permissions
        ]
        st.dataframe(display_rows, use_container_width=True, hide_index=True)
    else:
        st.info("\u8be5\u7528\u6237\u5c1a\u672a\u914d\u7f6e\u4e0a\u4f20\u6587\u4ef6\u6743\u9650\u3002")
    department_options = departments_from_rule_file()
    with st.form("file_upload_permission_form"):
        scope = st.selectbox("\u6388\u6743\u8303\u56f4", list(FILE_PERMISSION_SCOPE_LABELS), format_func=lambda key: FILE_PERMISSION_SCOPE_LABELS[key])
        departments = st.multiselect("\u6388\u6743\u90e8\u95e8", department_options, disabled=scope == "all", help="\u9009\u62e9\u5168\u90e8\u90e8\u95e8\u65f6\u65e0\u9700\u9009\u62e9\u90e8\u95e8\u3002")
        action = st.selectbox("\u6743\u9650\u52a8\u4f5c", list(FILE_PERMISSION_ACTION_LABELS), index=2, format_func=lambda key: FILE_PERMISSION_ACTION_LABELS[key])
        columns = st.columns([1, 1, 1])
        add_clicked = columns[0].form_submit_button("\u65b0\u589e\u6743\u9650", type="primary", use_container_width=True)
        replace_clicked = columns[1].form_submit_button("\u8986\u76d6\u4fdd\u5b58", use_container_width=True)
        clear_clicked = columns[2].form_submit_button("\u6e05\u7a7a\u6743\u9650", use_container_width=True)
    permissions = access_control.setdefault("file_upload_permissions", {})
    if add_clicked or replace_clicked:
        if scope != "all" and not departments:
            st.warning("\u8bf7\u9009\u62e9\u81f3\u5c11\u4e00\u4e2a\u6388\u6743\u90e8\u95e8\u3002")
            return
        new_permission = {"scope": scope, "departments": [] if scope == "all" else departments, "action": action}
        if replace_clicked:
            permissions[selected_username] = [new_permission]
        else:
            permissions.setdefault(selected_username, [])
            permissions[selected_username].append(new_permission)
        _app["save_access_control"](access_control)
        st.success("\u4e0a\u4f20\u6587\u4ef6\u6743\u9650\u5df2\u4fdd\u5b58\u3002")
        st.rerun()
    if clear_clicked:
        permissions[selected_username] = []
        _app["save_access_control"](access_control)
        st.success("\u4e0a\u4f20\u6587\u4ef6\u6743\u9650\u5df2\u6e05\u7a7a\u3002")
        st.rerun()


_original_worksheet_to_html = _app["_worksheet_to_html"]


def _query_param_value(name: str, default: str = "") -> str:
    value = st.query_params.get(name, default)
    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value) if value is not None else default


def _worksheet_to_html(worksheet) -> str:
    html_text = _original_worksheet_to_html(worksheet)
    try:
        is_deposit_report = str(worksheet["A1"].value or "").strip() == "存放同业及其他金融机构款项"
        if not (is_deposit_report and str(worksheet["B2"].value or "").strip() == "20251231"):
            return html_text
        metric_cells = {
            "B0260": "B4",
            "B0261": "B5",
            "B0262": "B7",
        }
        for metric_code, cell_ref in metric_cells.items():
            cell = worksheet[cell_ref]
            display_value = _app["_format_excel_cell_value"](cell.value, cell.number_format)
            if not display_value:
                continue
            escaped_value = html.escape(display_value)
            trace_url = (
                app_href(
                    nav_mode="view",
                    view_report="deposits_with_banks",
                    trace_report="deposits_with_banks",
                    trace_metric=metric_code,
                    trace_period="20251231",
                )
                + f"#{metric_code.lower()}-trace-download"
            )
            link_html = (
                f'<a href="{html.escape(trace_url, quote=True)}" target="_self" '
                'style="color:#0f5b8c;font-weight:700;text-decoration:underline;">'
                f"{escaped_value}</a>"
            )
            html_text = html_text.replace(f">{escaped_value}<", f">{link_html}<", 1)
        return html_text
    except Exception:
        return html_text


def render_interbank_deposit_trace_panel(report_key: str) -> None:
    if report_key != "deposits_with_banks":
        return
    selected_metric = _query_param_value("trace_metric")
    selected_period = _query_param_value("trace_period")
    st.markdown("---")
    st.subheader("指标追溯下载")
    st.caption("导出内容包含：指标加工规则、明细数据、每笔明细来源文件、上传时间、上传人，以及合并抵销调整。")
    metrics = [
        ("B0260", "存放中国境内银行款项"),
        ("B0261", "存放中国境内其他金融机构款项"),
        ("B0262", "存放中国境外银行款项"),
    ]
    for metric_code, metric_name in metrics:
        st.markdown(f'<div id="{metric_code.lower()}-trace-download"></div>', unsafe_allow_html=True)
        if selected_metric == metric_code and selected_period == "20251231":
            st.info(f"已定位到 20251231 下 {metric_code} 指标，可下载加工规则与明细追溯文件。")
        try:
            trace_bytes = build_interbank_metric_trace_workbook(metric_code)
        except Exception as exc:  # noqa: BLE001
            st.warning(f"{metric_code} 明细追溯文件生成失败：{exc}")
            continue
        st.download_button(
            f"下载 {metric_code}_20251231 明细追溯.xlsx（{metric_name}）",
            data=trace_bytes,
            file_name=f"五2_{metric_code}_20251231_明细追溯.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_{metric_code.lower()}_20251231_trace",
            use_container_width=True,
        )


_original_render_published_workbook_view = _app["render_published_workbook_view"]


def render_published_workbook_view(report_key: str, report_config: dict, published_entries: list, published_entry: dict | None) -> None:
    _original_render_published_workbook_view(report_key, report_config, published_entries, published_entry)
    render_interbank_deposit_trace_panel(report_key)


def _clean_cell_text(value) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).strip()


def _indicator_code_tokens(value) -> set[str]:
    text = _clean_cell_text(value).upper()
    return {item.strip() for item in re.split(r"[/,，、;；\s]+", text) if item.strip()}


def _normalize_indicator_query(query: str) -> str:
    query_text = _clean_cell_text(query)

    def normalize_code(match) -> str:
        prefix = match.group(1).upper()
        digits = match.group(2)
        digits = digits.lstrip("0") or "0"
        if len(digits) <= 4:
            digits = digits.zfill(4)
        return f"{prefix}{digits}"

    return re.sub(r"\b([AB])0?(\d{3,5})\b", normalize_code, query_text, flags=re.IGNORECASE)


def _query_semantic_terms(text: str) -> list[str]:
    compact = re.sub(r"\s+", "", _clean_cell_text(text))
    if not compact:
        return []
    terms: list[str] = []
    for length in range(min(8, len(compact)), 1, -1):
        for start in range(0, len(compact) - length + 1):
            term = compact[start : start + length]
            if re.fullmatch(r"[A-Za-z0-9]+", term):
                continue
            if term in {"的余", "余额", "年余", "本年", "本期"}:
                continue
            if term in terms:
                continue
            terms.append(term)
    return terms[:30]


def _smart_query_features(query: str) -> dict:
    query_text = _normalize_indicator_query(query)
    compact = re.sub(r"\s+", "", query_text)
    explicit_codes = re.findall(r"\b[AB]\d{4}\b", query_text.upper())
    semantic_text = compact
    for token in (
        "给我一下",
        "请问",
        "帮我查",
        "查询",
        "是多少",
        "多少",
        "一下",
        "这个",
        "那个",
        "的",
        "指标",
        "机构",
        "数据",
        "金额",
        "数值",
        "余额",
        "本年",
        "本期",
        "当年",
        "今年",
        "年末",
        "年",
        "集团",
        "合并",
        "本行",
        "母公司",
        "2025",
        "2024",
        "20251231",
        "20241231",
        "境内",
        "境外",
        "银行",
        "非银行",
        "其他金融",
        "减值",
        "准备",
        "小计",
    ):
        semantic_text = semantic_text.replace(token, "")
    semantic_terms = _query_semantic_terms(semantic_text)
    dimension_terms = [
        token
        for token in ("境内", "境外", "银行", "非银行", "其他金融", "减值", "准备", "小计")
        if token in compact
    ]
    return {
        "query_text": query_text,
        "compact": compact,
        "explicit_codes": explicit_codes,
        "terms": semantic_terms,
        "dimension_terms": dimension_terms,
        "period": "20251231" if any(token in compact for token in ("2025", "本年", "本期")) else "",
        "amount_scope": "parent" if any(token in compact for token in ("本行", "母公司")) else ("group" if any(token in compact for token in ("集团", "合并")) else "both"),
        "asks_balance": any(token in compact for token in ("余额", "账面余额", "总额", "合计")),
        "has_detail_dimension": bool(dimension_terms),
    }


def _smart_query_preferred_codes(query: str) -> list[str]:
    features = _smart_query_features(query)
    explicit_codes = features["explicit_codes"]
    if explicit_codes:
        return explicit_codes
    return []


def _latest_generated_indicator_rows() -> pd.DataFrame:
    rows = []
    for path in sorted(OUTPUT_DIR.glob("*生成结果_中间表.xlsx"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            df = pd.read_excel(path, dtype=object)
        except Exception:
            continue
        if "指标编码" not in df.columns or "指标名称" not in df.columns:
            continue
        df = df.copy()
        df["来源中间表"] = path.name
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    combined = pd.concat(rows, ignore_index=True, sort=False)
    combined["指标编码"] = combined["指标编码"].map(_clean_cell_text)
    combined["指标名称"] = combined["指标名称"].map(_clean_cell_text)
    combined = combined[(combined["指标编码"] != "") | (combined["指标名称"] != "")]
    return combined


def _rule_indicator_index() -> dict[str, dict]:
    rule_path = _rule_file_path()
    if rule_path is None:
        return {}
    try:
        df = pd.read_excel(rule_path, sheet_name=0, header=1, dtype=object)
    except Exception:
        return {}
    if "指标编码" not in df.columns:
        return {}
    index: dict[str, dict] = {}
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        for code in _indicator_code_tokens(row_dict.get("指标编码")):
            index.setdefault(code, row_dict)
    return index


def _indicator_search_results(query: str, limit: int = 20) -> pd.DataFrame:
    query_text = _normalize_indicator_query(query)
    if not query_text:
        return pd.DataFrame()
    query_upper = query_text.upper()
    features = _smart_query_features(query_text)
    preferred_codes = _smart_query_preferred_codes(query_text)
    semantic_terms = features["terms"]
    rule_index = _rule_indicator_index()
    indicators = _latest_generated_indicator_rows()
    if indicators.empty:
        return indicators

    def score(row) -> int:
        code = _clean_cell_text(row.get("指标编码")).upper()
        name = _clean_cell_text(row.get("指标名称"))
        report_name = _clean_cell_text(row.get("报表名称"))
        data_source = _clean_cell_text(row.get("数据来源"))
        rule_text = _clean_cell_text(row.get("加工规则"))
        rule_row = {}
        for code_token in _indicator_code_tokens(code):
            if code_token in rule_index:
                rule_row = rule_index[code_token]
                break
        rule_source = _clean_cell_text(rule_row.get("指标数据来源"))
        rule_detail = _clean_cell_text(rule_row.get("指标加工规则"))
        rule_definition = _clean_cell_text(rule_row.get("指标定义"))
        rule_scope = _clean_cell_text(rule_row.get("指标口径"))
        rule_file = _clean_cell_text(rule_row.get("对应文件"))
        period = _clean_cell_text(row.get("期间"))
        institution = _clean_cell_text(row.get("机构")) or _clean_cell_text(row.get("机构口径"))
        tokens = _indicator_code_tokens(code)
        row_score = 0
        searchable = f"{name} {report_name} {data_source} {rule_text} {rule_source} {rule_detail} {rule_definition} {rule_scope} {rule_file}"
        if features["dimension_terms"] and not all(term in name for term in features["dimension_terms"]):
            return 0
        if semantic_terms:
            max_len = max(len(term) for term in semantic_terms)
            max_terms = [term for term in semantic_terms if len(term) == max_len]
            if not any(term in searchable for term in max_terms):
                return 0
        if code in preferred_codes or bool(tokens & set(preferred_codes)):
            row_score = 110
        if query_upper in tokens:
            row_score = max(row_score, 100)
        if code == query_upper:
            row_score = max(row_score, 95)
        if query_upper and query_upper in code:
            row_score = max(row_score, 80)
        if query_text and query_text in name:
            row_score = max(row_score, 70)
        if query_upper and query_upper in name.upper():
            row_score = max(row_score, 60)
        matched_terms = [term for term in semantic_terms if term in searchable]
        matched_weight = sum(min(len(term), 6) for term in matched_terms)
        if matched_terms:
            row_score = max(row_score, 30 + matched_weight * 5)
        name_matches = [term for term in semantic_terms if term in name]
        if name_matches:
            row_score += 20 + sum(min(len(term), 6) for term in name_matches) * 4
        report_matches = [term for term in semantic_terms if term in report_name]
        if report_matches:
            row_score += 8 + sum(min(len(term), 6) for term in report_matches) * 2
        if row_score <= 0:
            return 0
        if features["asks_balance"] and not features["has_detail_dimension"] and "资产负债表" in report_name:
            row_score += 80
        if features["asks_balance"] and not features["has_detail_dimension"] and "资产负债表" not in report_name:
            row_score -= 20
        if features["asks_balance"] and not features["has_detail_dimension"] and any(token in name for token in ("账面余额", "小计", "减值准备")):
            row_score -= 15
        if not any(token in features["compact"] for token in ("减值", "准备")) and any(token in name for token in ("减值", "准备")):
            row_score -= 60
        if not any(token in features["compact"] for token in ("账面余额", "小计")) and any(token in name for token in ("账面余额", "小计")):
            row_score -= 100
        if features["period"] and period == features["period"]:
            row_score += 8
        if features["amount_scope"] == "group" and institution == "集团":
            row_score += 5
        if features["amount_scope"] == "parent" and institution == "本行":
            row_score += 5
        return row_score

    result = indicators.copy()
    result["_score"] = result.apply(score, axis=1)
    result = result[result["_score"] > 0].sort_values("_score", ascending=False)
    if preferred_codes:
        preferred_set = set(preferred_codes)
        preferred_result = result[
            result["指标编码"].map(lambda value: bool(_indicator_code_tokens(value) & preferred_set))
        ]
        if not preferred_result.empty:
            result = preferred_result
    dedupe_columns = [
        column
        for column in ["指标编码", "指标名称", "报表名称", "期间", "机构", "机构口径", "生成金额-集团", "生成金额-本行"]
        if column in result.columns
    ]
    if dedupe_columns:
        result = result.drop_duplicates(subset=dedupe_columns, keep="first")
    return result.head(limit).drop(columns=["_score"], errors="ignore")


def _first_existing_value(row, columns: list[str]) -> str:
    for column in columns:
        if column in row.index:
            value = _clean_cell_text(row.get(column))
            if value:
                return value
    return ""


def _format_indicator_amount(value) -> str:
    text = _clean_cell_text(value)
    if not text:
        return "无"
    try:
        return f"{float(value):,.2f}"
    except Exception:
        return text


def _preferred_amount_column(query: str) -> str:
    scope = _smart_query_features(query)["amount_scope"]
    if scope == "parent":
        return "生成金额-本行"
    return "生成金额-集团"


def _display_institution(row, query: str) -> str:
    institution = _first_existing_value(row, ["机构", "机构口径"])
    if institution:
        return institution
    scope = _smart_query_features(query)["amount_scope"]
    if scope == "parent":
        return "本行"
    if scope == "group":
        return "集团"
    return "集团/本行"


def _smart_answer_text(row, query: str) -> str:
    features = _smart_query_features(query)
    period_text = "本期/2025年" if features["period"] == "20251231" else (_first_existing_value(row, ["期间"]) or "当前已加工期间")
    if features["amount_scope"] == "parent":
        return f"{_format_indicator_amount(row.get('生成金额-本行'))} 千元（本行，{period_text}）"
    if features["amount_scope"] == "group":
        return f"{_format_indicator_amount(row.get('生成金额-集团'))} 千元（集团，{period_text}）"
    return (
        f"集团：{_format_indicator_amount(row.get('生成金额-集团'))} 千元；"
        f"本行：{_format_indicator_amount(row.get('生成金额-本行'))} 千元（{period_text}）"
    )


def _direct_interbank_impairment_answer(query: str) -> dict | None:
    compact = re.sub(r"\s+", "", _clean_cell_text(query))
    if "存放同业" not in compact or not any(token in compact for token in ("减值", "准备")):
        return None
    candidates = [
        OUTPUT_DIR / "存放同业及其他金融机构款项生成结果_中间表.xlsx",
        OUTPUT_DIR / "interbank_deposit_report_B260_B264.xlsx",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            df = pd.read_excel(path, dtype=object)
        except Exception:
            continue
        if "指标编码" not in df.columns:
            continue
        matched = df[df["指标编码"].astype(str).str.strip().str.upper() == "B0263"]
        if matched.empty:
            continue
        row = matched.iloc[0]
        return {
            "code": "B0263",
            "name": _clean_cell_text(row.get("指标名称")) or "存放同业及其他金融机构款项减值准备",
            "period": _clean_cell_text(row.get("期间")) or "20251231",
            "group_amount": row.get("生成金额-集团"),
            "parent_amount": row.get("生成金额-本行"),
            "source": path.name,
            "rule": _clean_cell_text(row.get("加工规则")),
            "note": _clean_cell_text(row.get("计算说明")),
        }
    return None


def _render_direct_interbank_impairment_answer(answer: dict) -> None:
    st.success(
        "存放同业及其他金融机构款项减值准备本期余额："
        f"{_format_indicator_amount(answer.get('group_amount'))} 千元（集团，{answer.get('period')}）。"
    )
    st.caption(
        f"指标编码：{answer.get('code')}；本行金额：{_format_indicator_amount(answer.get('parent_amount'))} 千元；"
        f"来源：{answer.get('source')}。"
    )
    if answer.get("rule"):
        st.caption(f"取数规则：{answer.get('rule')}")
    if answer.get("note"):
        st.caption(f"说明：{answer.get('note')}")


def render_smart_indicator_query() -> None:
    st.markdown("---")
    st.subheader("智能问数")
    st.caption("输入指标编码、指标名称或自然语言问题，系统会解析期间、集团/本行口径和业务维度，并返回指标结果、部门、加工规则和数据来源。")
    query = st.text_input(
        "请输入指标编码、指标名称或问题",
        placeholder="例如：A00002、B260、存放同业2025年的余额、存放同业境内本行余额",
        key="smart_indicator_query_text",
    )
    query = _clean_cell_text(query)
    if not query:
        return

    direct_answer = _direct_interbank_impairment_answer(query)
    if direct_answer is not None:
        _render_direct_interbank_impairment_answer(direct_answer)
        return

    matches = _indicator_search_results(query)
    if matches.empty:
        st.warning("未找到已加工指标。请确认该指标已经生成过报表，或换用指标编码查询。")
        return

    options = []
    for idx, row in matches.iterrows():
        period = _first_existing_value(row, ["期间"]) or "无期间"
        institution = _first_existing_value(row, ["机构", "机构口径"]) or "无机构"
        report_name = _first_existing_value(row, ["报表名称"]) or "无报表"
        options.append((idx, f"{row.get('指标编码')} | {row.get('指标名称')} | {period} | {institution} | {report_name}"))
    selected_idx = options[0][0]
    if len(options) > 1:
        selected_idx = st.selectbox(
            "匹配到多个指标，请选择",
            [idx for idx, _ in options],
            format_func=lambda value: next(label for idx, label in options if idx == value),
            key="smart_indicator_match_select",
        )
    row = matches.loc[selected_idx]
    metric_code = _clean_cell_text(row.get("指标编码")).upper()
    preferred_codes = _smart_query_preferred_codes(query)
    if preferred_codes and metric_code in preferred_codes:
        st.info(f"已将问题识别为指标 {metric_code}。")
    rule_index = _rule_indicator_index()
    rule_row = {}
    for code in _indicator_code_tokens(metric_code):
        if code in rule_index:
            rule_row = rule_index[code]
            break

    st.markdown("#### 指标结果")
    result_rows = [
        {
            "项目": "本次回答",
            "内容": _smart_answer_text(row, query),
        },
        {"项目": "指标编码", "内容": metric_code},
        {"项目": "指标名称", "内容": _clean_cell_text(row.get("指标名称"))},
        {"项目": "报表名称", "内容": _first_existing_value(row, ["报表名称"])},
        {"项目": "期间", "内容": _first_existing_value(row, ["期间"]) or "未标明"},
        {"项目": "机构", "内容": _display_institution(row, query)},
        {"项目": "生成金额-集团（千元）", "内容": _format_indicator_amount(row.get("生成金额-集团"))},
        {"项目": "生成金额-本行（千元）", "内容": _format_indicator_amount(row.get("生成金额-本行"))},
        {"项目": "计算状态", "内容": _first_existing_value(row, ["计算状态"])},
    ]
    st.dataframe(pd.DataFrame(result_rows), use_container_width=True, hide_index=True)

    st.markdown("#### 部门与规则")
    rule_text = _first_existing_value(row, ["加工规则"]) or _clean_cell_text(rule_row.get("指标加工规则")) or _first_existing_value(row, ["计算说明"])
    department_rows = [
        {"项目": "数据提供部门", "内容": _clean_cell_text(rule_row.get("数据提供部门")) or "未配置"},
        {"项目": "归口部门", "内容": _clean_cell_text(rule_row.get("归口管理部门")) or "未配置"},
        {"项目": "牵头部门", "内容": _clean_cell_text(rule_row.get("牵头管理部门")) or "未配置"},
        {"项目": "加工规则", "内容": rule_text or "未配置"},
        {"项目": "计算说明", "内容": _first_existing_value(row, ["计算说明"]) or "无"},
    ]
    st.dataframe(pd.DataFrame(department_rows), use_container_width=True, hide_index=True)

    st.markdown("#### 数据来源")
    source_rows = [
        {"项目": "中间表", "内容": _clean_cell_text(row.get("来源中间表"))},
        {"项目": "生成数据来源", "内容": _first_existing_value(row, ["数据来源"]) or "未标明"},
        {"项目": "规则数据来源", "内容": _clean_cell_text(rule_row.get("指标数据来源")) or "未配置"},
        {"项目": "对应文件", "内容": _clean_cell_text(rule_row.get("对应文件")) or "未配置"},
    ]
    st.dataframe(pd.DataFrame(source_rows), use_container_width=True, hide_index=True)

    trace_metric = metric_code if metric_code in {"B0260", "B0261", "B0262"} else ""
    if trace_metric:
        try:
            trace_bytes = build_interbank_metric_trace_workbook(trace_metric)
            st.download_button(
                f"下载 {trace_metric}_20251231 明细追溯.xlsx",
                data=trace_bytes,
                file_name=f"五2_{trace_metric}_20251231_明细追溯.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"smart_query_trace_{trace_metric.lower()}",
                use_container_width=True,
            )
        except Exception as exc:  # noqa: BLE001
            st.warning(f"{trace_metric} 明细追溯文件生成失败：{exc}")


_original_render_workflow_home = _app["render_workflow_home"]


def render_workflow_home() -> None:
    _original_render_workflow_home()
    render_smart_indicator_query()


_original_render_permission_assignment_page = _app["render_permission_assignment_page"]


def render_permission_assignment_page(access_control: dict, report_types: dict) -> None:
    _original_render_permission_assignment_page(access_control, report_types)
    render_file_upload_permission_admin(access_control)


_original_main = _app["main"]
_original_apply_global_styles = _app["apply_global_styles"]
_original_build_report_dataset = _app["build_report_dataset"]


def apply_global_styles() -> None:
    _original_apply_global_styles()
    apply_prd_styles()


def _run_with_upload_legacy_header_hidden(callback) -> None:
    original_set_page_config = st.set_page_config
    original_button = st.button
    original_caption = st.caption
    original_subheader = st.subheader

    def filtered_set_page_config(*args, **kwargs):
        return None

    def filtered_button(label, *args, **kwargs):
        if str(label) == "返回制作报表首页":
            return False
        return original_button(label, *args, **kwargs)

    def filtered_caption(body, *args, **kwargs):
        if str(body) == "上传文件":
            return None
        return original_caption(body, *args, **kwargs)

    def filtered_subheader(body, *args, **kwargs):
        if str(body) == "基础文件":
            return None
        return original_subheader(body, *args, **kwargs)

    st.set_page_config = filtered_set_page_config
    st.button = filtered_button
    st.caption = filtered_caption
    st.subheader = filtered_subheader
    try:
        callback()
    finally:
        st.set_page_config = original_set_page_config
        st.button = original_button
        st.caption = original_caption
        st.subheader = original_subheader


def main() -> None:
    st.set_page_config(page_title="财报智控平台", layout="wide", initial_sidebar_state="collapsed")
    access_control = _app["load_access_control"]()
    if not is_authenticated(access_control):
        render_login_page(access_control)
        return
    _run_with_upload_legacy_header_hidden(_original_main)


def build_report_dataset(rule_file_path, report_key, report_config, report_types, institution_context):
    if str(report_config.get("detail_generator") or "") == "central_bank_cash":
        from engine.central_bank_cash_report import build_central_bank_cash_report

        return build_central_bank_cash_report(
            UPLOAD_DIR,
            report_config,
            report_period=str((institution_context or {}).get("period") or ""),
        )
    if str(report_config.get("detail_generator") or "") == "interbank_deposits":
        from engine.interbank_deposit_report import build_interbank_deposit_report

        return build_interbank_deposit_report(
            UPLOAD_DIR,
            report_config,
            report_period=str((institution_context or {}).get("period") or ""),
        )
    return _original_build_report_dataset(rule_file_path, report_key, report_config, report_types, institution_context)


_app["apply_global_styles"] = apply_global_styles
_app["app_href"] = app_href
_app["render_product_header"] = render_product_header
_app["is_authenticated"] = is_authenticated
_app["handle_login_submit"] = handle_login_submit
_app["sync_remembered_login_token"] = sync_remembered_login_token
_app["render_login_page"] = render_login_page
_app["render_base_file_uploaders"] = render_base_file_uploaders
_app["render_permission_assignment_page"] = render_permission_assignment_page
_app["_worksheet_to_html"] = _worksheet_to_html
_app["render_published_workbook_view"] = render_published_workbook_view
_app["render_unified_navigation"] = render_unified_navigation
_app["render_top_user_bar"] = render_top_user_bar
_app["render_workflow_home"] = render_workflow_home
_app["build_report_dataset"] = build_report_dataset
_app["main"] = main

if __name__ == "__main__":
    main()
