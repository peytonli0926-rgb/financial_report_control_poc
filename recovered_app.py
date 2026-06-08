# decompiled by byteripper v1.0.0
# original file: __pycache__\app.cpython-314.pyc
# python version: unknown

def __annotate__(format):
    return {'return': None}

def apply_global_styles():
    ('unsafe_allow_html',)
    True
    '\n        <style>\n        :root {\n            --brand-950: #002b24;\n            --brand-900: #003a31;\n            --brand-800: #06483d;\n            --brand-700: #0b5a4c;\n            --brand-500: #6bbf1a;\n            --brand-400: #82ca2f;\n            --ink-900: #10231f;\n            --ink-700: #314541;\n            --ink-500: #63736f;\n            --line: #dfe8e5;\n            --soft-line: #edf2f0;\n            --surface: #ffffff;\n            --page: #f5f8f7;\n            --aqua: #00a7b5;\n        }\n        html, body, [class*="css"] {\n            font-size: 15px;\n            color: var(--ink-900);\n            font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;\n        }\n        .stApp {\n            font-size: 15px;\n            background:\n                radial-gradient(circle at 14% 10%, rgba(107, 191, 26, 0.10), transparent 26%),\n                linear-gradient(180deg, #f7faf9 0%, #eef4f2 100%);\n        }\n        [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"],\n        [data-testid="stHeader"], div[data-testid="stToolbar"] + div { display: none !important; }\n        .block-container {\n            max-width: none !important;\n            padding: 0.65rem 1rem 1.5rem !important;\n            margin-top: 0 !important;\n        }\n        [data-testid="column"] > div { gap: 0.7rem; }\n        h1, h2, h3 { color: var(--ink-900) !important; letter-spacing: -0.02em; }\n        h1 { font-size: 1.35rem !important; margin: 0 0 0.2rem !important; }\n        h2, h3 { font-size: 1.05rem !important; }\n        p, li, label, .stMarkdown, .stCaption, .stText, .stAlert { font-size: 0.94rem !important; }\n        div[data-testid="stCaptionContainer"] { color: var(--ink-500) !important; }\n\n        .product-title {\n            position: relative;\n            color: var(--ink-900) !important;\n            background: transparent;\n            font-weight: 800;\n            font-size: 1.12rem;\n            padding: 0.7rem 0.85rem 1.05rem 2rem;\n            margin: 0 -0.85rem 0.4rem;\n            border-bottom: 1px solid rgba(0, 58, 49, 0.14);\n        }\n        [data-testid="stSidebar"] .product-title {\n            color: var(--ink-900) !important;\n            border-bottom-color: rgba(0, 58, 49, 0.14);\n        }\n        .product-title::before {\n            content: "";\n            position: absolute;\n            left: 0;\n            top: 1.22rem;\n            left: 0.85rem;\n            width: 0.55rem;\n            height: 0.55rem;\n            background: var(--brand-500);\n            box-shadow: 0 0 0 3px rgba(107, 191, 26, 0.18);\n        }\n        div[data-testid="column"]:has(.product-title) > div {\n            background: linear-gradient(180deg, #002b24 0%, #00382f 48%, #002e27 100%);\n            border: 1px solid rgba(255, 255, 255, 0.08);\n            box-shadow: 0 16px 38px rgba(0, 38, 32, 0.16);\n            min-height: calc(100vh - 1.35rem);\n            padding: 0.95rem 0.85rem 1.2rem;\n        }\n        div[data-testid="column"]:has(.product-title) .stMarkdown,\n        div[data-testid="column"]:has(.product-title) p,\n        div[data-testid="column"]:has(.product-title) span,\n        div[data-testid="column"]:has(.product-title) label,\n        div[data-testid="column"]:has(.product-title) div[data-testid="stCaptionContainer"] {\n            color: rgba(255, 255, 255, 0.78) !important;\n        }\n        div[data-testid="column"]:has(.product-title) .stButton button {\n            justify-content: flex-start;\n            width: 100%;\n            min-height: 2.35rem !important;\n            color: rgba(255, 255, 255, 0.62) !important;\n            background: transparent !important;\n            border: 0 !important;\n            border-left: 3px solid transparent !important;\n            box-shadow: none !important;\n            padding: 0.45rem 0.65rem 0.45rem 1.1rem !important;\n            margin: 0 !important;\n            border-radius: 0 !important;\n        }\n        div[data-testid="column"]:has(.product-title) .stButton button p {\n            color: inherit !important;\n            font-size: 0.9rem !important;\n            line-height: 1.35 !important;\n        }\n        div[data-testid="column"]:has(.product-title) .stButton button[kind="primary"],\n        div[data-testid="column"]:has(.product-title) .stButton button:hover {\n            color: #ffffff !important;\n            background: rgba(0, 68, 58, 0.70) !important;\n            border-left-color: var(--brand-500) !important;\n        }\n        div[data-testid="column"]:has(.product-title) .stButton button[kind="primary"] p {\n            color: var(--brand-400) !important;\n            font-weight: 800 !important;\n        }\n        .menu-level-1 {\n            margin: 0.25rem -0.85rem 0;\n            padding: 0.68rem 0.85rem 0.68rem 1.1rem;\n            color: rgba(255,255,255,0.90);\n            background: rgba(0, 64, 54, 0.56);\n            font-size: 0.92rem;\n            font-weight: 800;\n        }\n        .menu-level-2 {\n            margin: 0 -0.85rem;\n            padding: 0.34rem 0.85rem 0.2rem 1.6rem;\n            color: rgba(255,255,255,0.35);\n            background: rgba(0, 24, 20, 0.28);\n            font-size: 0.78rem;\n            font-weight: 700;\n        }\n        .menu-level-3-label {\n            margin: 0 -0.85rem;\n            padding: 0.48rem 0.85rem 0.28rem 2.05rem;\n            color: rgba(255,255,255,0.40);\n            background: rgba(0, 20, 17, 0.22);\n            font-size: 0.82rem;\n            font-weight: 700;\n        }\n        div[data-testid="column"]:has(.product-title) .stButton {\n            margin: 0 -0.85rem !important;\n        }\n        div[data-testid="column"]:has(.product-title) .stButton + .stButton {\n            margin-top: 0 !important;\n        }\n        .menu-empty {\n            padding: 0.45rem 0.75rem;\n            color: rgba(255,255,255,0.52);\n            font-size: 0.84rem;\n        }\n        .side-menu {\n            margin: 0 -0.85rem;\n            padding-bottom: 0.8rem;\n        }\n        .side-menu a {\n            text-decoration: none !important;\n        }\n        .side-menu-primary {\n            display: flex;\n            align-items: center;\n            justify-content: space-between;\n            min-height: 2.55rem;\n            padding: 0 0.95rem;\n            color: rgba(255,255,255,0.88);\n            background: rgba(0, 63, 53, 0.48);\n            font-size: 0.92rem;\n            font-weight: 800;\n            border-left: 3px solid transparent;\n        }\n        .side-menu-primary.active {\n            color: #ffffff;\n            background: rgba(0, 72, 61, 0.86);\n            border-left-color: var(--brand-500);\n        }\n        .side-menu-primary:hover {\n            color: #ffffff;\n            background: rgba(0, 72, 61, 0.74);\n        }\n        .side-menu-children {\n            padding: 0.35rem 0 0.55rem;\n            background: rgba(0, 25, 21, 0.30);\n        }\n        .side-menu-secondary {\n            display: block;\n            padding: 0.42rem 0.75rem 0.42rem 2.05rem;\n            color: rgba(255,255,255,0.54);\n            font-size: 0.84rem;\n            line-height: 1.45;\n            border-left: 3px solid transparent;\n        }\n        .side-menu-secondary:hover {\n            color: rgba(255,255,255,0.86);\n            background: rgba(255,255,255,0.035);\n        }\n        .side-menu-secondary.active {\n            color: var(--brand-400);\n            font-weight: 800;\n            border-left-color: var(--brand-500);\n            background: rgba(0, 55, 47, 0.50);\n        }\n        .side-menu-group {\n            padding: 0.62rem 0.75rem 0.32rem 1.35rem;\n            color: rgba(255,255,255,0.70);\n            font-size: 0.86rem;\n            font-weight: 800;\n        }\n        .side-menu-tertiary {\n            display: block;\n            padding: 0.38rem 0.75rem 0.38rem 2.25rem;\n            color: rgba(255,255,255,0.48);\n            font-size: 0.82rem;\n            line-height: 1.42;\n            border-left: 3px solid transparent;\n        }\n        .side-menu-tertiary:hover {\n            color: rgba(255,255,255,0.82);\n            background: rgba(255,255,255,0.035);\n        }\n        .side-menu-tertiary.active {\n            color: var(--brand-400);\n            font-weight: 800;\n            border-left-color: var(--brand-500);\n            background: rgba(0, 55, 47, 0.50);\n        }\n        .side-menu-tertiary.disabled {\n            color: rgba(255,255,255,0.22);\n            pointer-events: none;\n        }\n        div[data-testid="stRadio"] > div { gap: 0.28rem; }\n        div[data-testid="stRadio"] label {\n            border-radius: 0;\n            padding: 0.64rem 0.75rem;\n            border-left: 3px solid transparent;\n            transition: all 120ms ease;\n        }\n        div[data-testid="stRadio"] label:hover {\n            background: rgba(255, 255, 255, 0.07);\n            border-left-color: rgba(130, 202, 47, 0.65);\n        }\n        div[data-testid="stRadio"] input:checked + div { color: var(--brand-900) !important; font-weight: 700; }\n        div[data-testid="stRadio"] label:has(input:checked) {\n            background: linear-gradient(90deg, rgba(107, 191, 26, 0.22), rgba(107, 191, 26, 0.04));\n            border-left-color: var(--brand-500);\n        }\n\n        .product-header {\n            display: flex;\n            align-items: center;\n            justify-content: space-between;\n            gap: 1rem;\n            background: linear-gradient(90deg, #ffffff 0%, #f7fbf8 65%, #eef8e7 100%);\n            border: 1px solid var(--line);\n            border-left: 5px solid var(--brand-500);\n            box-shadow: 0 10px 24px rgba(16, 35, 31, 0.06);\n            padding: 1rem 1.1rem;\n            margin-bottom: 1rem;\n        }\n        .product-header h1 { margin: 0 !important; font-size: 1.42rem !important; }\n        .product-header-subtitle { margin-top: 0.28rem; color: var(--ink-500); font-size: 0.9rem; }\n        .product-header-badge {\n            color: var(--brand-900);\n            background: #eaf6e4;\n            border: 1px solid #cde7bd;\n            padding: 0.42rem 0.72rem;\n            font-weight: 700;\n            white-space: nowrap;\n        }\n        .page-card, .workflow-hero, div[data-testid="stVerticalBlockBorderWrapper"] {\n            background: var(--surface) !important;\n            border: 1px solid var(--line) !important;\n            border-radius: 0 !important;\n            box-shadow: 0 10px 24px rgba(16, 35, 31, 0.05);\n        }\n        .page-card { padding: 1.05rem 1.15rem; margin-bottom: 1rem; }\n        .table-header {\n            background: #f4f8f6;\n            border-top: 1px solid var(--line);\n            border-bottom: 1px solid var(--line);\n            padding: 0.55rem 0;\n            font-weight: 700;\n            color: var(--ink-700);\n        }\n        .stButton button, .stDownloadButton button, .stFileUploader button {\n            min-height: 2.35rem;\n            border-radius: 0 !important;\n            font-size: 0.92rem !important;\n            font-weight: 700 !important;\n            border: 1px solid #cddbd6 !important;\n            box-shadow: none !important;\n        }\n        .stButton button[kind="primary"], .stDownloadButton button {\n            background: var(--brand-500) !important;\n            border-color: var(--brand-500) !important;\n            color: #ffffff !important;\n        }\n        .stButton button[kind="primary"]:hover, .stDownloadButton button:hover {\n            background: #5aa716 !important;\n            border-color: #5aa716 !important;\n        }\n        .stButton button:hover, .stFileUploader button:hover {\n            border-color: var(--brand-500) !important;\n            color: var(--brand-900) !important;\n        }\n        input, textarea, select, div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {\n            border-radius: 0 !important;\n            border-color: #cfdcd8 !important;\n        }\n        div[data-baseweb="select"] > div:hover, div[data-baseweb="input"] > div:hover { border-color: var(--brand-500) !important; }\n        .stFileUploader section {\n            border-radius: 0 !important;\n            border-color: #cfdcd8 !important;\n            background: #fbfdfc !important;\n        }\n        .stAlert { border-radius: 0 !important; border: 1px solid var(--line) !important; }\n\n        .workflow-hero {\n            padding: 0 !important;\n            background: transparent !important;\n            border: 0 !important;\n            box-shadow: none !important;\n        }\n        .dashboard-home {\n            display: grid;\n            gap: 0.9rem;\n        }\n        .dashboard-welcome {\n            position: relative;\n            overflow: hidden;\n            min-height: 132px;\n            border-radius: 10px;\n            padding: 1.15rem 1.35rem;\n            border: 1px solid #e6eef5;\n            background:\n                radial-gradient(circle at 88% 42%, rgba(42, 210, 142, .22), transparent 18%),\n                linear-gradient(105deg, #ffffff 0%, #f8fcff 50%, #eaf8f3 100%);\n            box-shadow: 0 12px 26px rgba(20, 70, 120, .06);\n        }\n        .dashboard-welcome::after {\n            content: "AI";\n            position: absolute;\n            right: 6.5rem;\n            top: 1.3rem;\n            width: 74px;\n            height: 74px;\n            border-radius: 24px;\n            display: grid;\n            place-items: center;\n            color: #ffffff;\n            font-weight: 950;\n            font-size: 1.65rem;\n            background: linear-gradient(145deg, #0fcf83, #45e6a8);\n            box-shadow: 0 18px 38px rgba(22, 195, 127, .28);\n            transform: rotate(-7deg);\n        }\n        .dashboard-welcome h2 {\n            margin: 0 0 .4rem !important;\n            font-size: 1.45rem !important;\n            color: #0f172a !important;\n            font-weight: 950;\n        }\n        .dashboard-welcome p {\n            margin: 0 0 .85rem !important;\n            max-width: 610px;\n            color: #64748b !important;\n            line-height: 1.65;\n        }\n        .dashboard-tags {\n            display: flex;\n            flex-wrap: wrap;\n            gap: .55rem;\n        }\n        .dashboard-tags span {\n            display: inline-flex;\n            align-items: center;\n            gap: .25rem;\n            color: #334155;\n            font-size: .78rem;\n            font-weight: 800;\n            padding: .25rem .55rem;\n            border-radius: 999px;\n            background: rgba(255,255,255,.72);\n            border: 1px solid rgba(203, 213, 225, .75);\n        }\n        .dashboard-metrics,\n        .dashboard-quick-grid {\n            display: grid;\n            grid-template-columns: repeat(4, minmax(0, 1fr));\n            gap: .8rem;\n        }\n        .dashboard-metric,\n        .dashboard-panel,\n        .dashboard-quick-card {\n            border: 1px solid #e7edf4;\n            border-radius: 10px;\n            background: rgba(255,255,255,.96);\n            box-shadow: 0 10px 24px rgba(21, 65, 110, .055);\n        }\n        .dashboard-metric {\n            display: flex;\n            align-items: center;\n            gap: .9rem;\n            padding: .85rem .95rem;\n            min-height: 74px;\n        }\n        .dashboard-icon {\n            width: 42px;\n            height: 42px;\n            border-radius: 12px;\n            display: grid;\n            place-items: center;\n            font-size: 1.2rem;\n            font-weight: 950;\n        }\n        .dashboard-icon.blue { color: #1677ff; background: #eaf3ff; }\n        .dashboard-icon.green { color: #18a058; background: #eaf8ef; }\n        .dashboard-icon.orange { color: #f97316; background: #fff3e7; }\n        .dashboard-icon.purple { color: #6d5dfc; background: #f0efff; }\n        .dashboard-metric-title { color: #64748b; font-size: .78rem; font-weight: 800; }\n        .dashboard-metric-value { color: #0f172a; font-size: 1.35rem; font-weight: 950; line-height: 1.15; }\n        .dashboard-metric-sub { color: #94a3b8; font-size: .72rem; }\n        .dashboard-section {\n            border: 1px solid #e7edf4;\n            border-radius: 10px;\n            background: rgba(255,255,255,.96);\n            padding: .95rem;\n            box-shadow: 0 10px 24px rgba(21, 65, 110, .055);\n        }\n        .dashboard-section-title {\n            display: flex;\n            align-items: center;\n            justify-content: space-between;\n            margin-bottom: .72rem;\n            color: #0f172a;\n            font-size: .98rem;\n            font-weight: 950;\n        }\n        .dashboard-section-title a {\n            color: #1677ff !important;\n            text-decoration: none !important;\n            font-size: .74rem;\n            font-weight: 800;\n        }\n        .dashboard-quick-card {\n            display: grid;\n            grid-template-columns: 44px 1fr 14px;\n            gap: .65rem;\n            align-items: center;\n            min-height: 84px;\n            padding: .72rem .75rem;\n            color: inherit !important;\n            text-decoration: none !important;\n            transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease;\n        }\n        .dashboard-quick-card:hover {\n            transform: translateY(-2px);\n            border-color: #bcd7ff;\n            box-shadow: 0 16px 28px rgba(28, 111, 230, .10);\n        }\n        .dashboard-quick-title { color: #0f172a; font-size: .86rem; font-weight: 950; margin-bottom: .18rem; }\n        .dashboard-quick-desc { color: #64748b; font-size: .72rem; line-height: 1.45; }\n        .dashboard-main-grid {\n            display: grid;\n            grid-template-columns: 1.35fr .95fr .72fr;\n            gap: .9rem;\n        }\n        .dashboard-flow {\n            display: grid;\n            grid-template-columns: repeat(4, minmax(0, 1fr));\n            gap: .65rem;\n            position: relative;\n        }\n        .dashboard-flow-card {\n            position: relative;\n            min-height: 150px;\n            padding: .72rem;\n            border: 1px solid #e7edf4;\n            border-radius: 10px;\n            background: linear-gradient(180deg, #ffffff, #fbfdff);\n            text-align: center;\n            text-decoration: none !important;\n            color: inherit !important;\n        }\n        .dashboard-flow-num {\n            width: 22px;\n            height: 22px;\n            border-radius: 50%;\n            margin: 0 auto .45rem;\n            display: grid;\n            place-items: center;\n            color: #fff;\n            font-size: .72rem;\n            font-weight: 900;\n            background: #0f9f72;\n        }\n        .dashboard-flow-card:nth-child(4) .dashboard-flow-num { background: #2f7eff; }\n        .dashboard-flow-card img { width: 50px; height: 42px; object-fit: contain; margin-bottom: .35rem; }\n        .dashboard-flow-title { color: #0f172a; font-weight: 950; font-size: .84rem; margin-bottom: .3rem; }\n        .dashboard-flow-desc { color: #64748b; font-size: .72rem; line-height: 1.45; }\n        .dashboard-list {\n            display: grid;\n            gap: .58rem;\n        }\n        .dashboard-list-row {\n            display: grid;\n            grid-template-columns: 1fr auto;\n            gap: .5rem;\n            align-items: center;\n            padding: .48rem .55rem;\n            border-radius: 8px;\n            background: #fbfdff;\n            border: 1px solid #eef3f8;\n        }\n        .dashboard-list-name { color: #334155; font-weight: 800; font-size: .78rem; }\n        .dashboard-list-meta { color: #94a3b8; font-size: .72rem; margin-top: .12rem; }\n        .dashboard-badge {\n            border-radius: 999px;\n            padding: .18rem .45rem;\n            font-size: .68rem;\n            font-weight: 900;\n            white-space: nowrap;\n            color: #0f9f72;\n            background: #eaf8ef;\n        }\n        .dashboard-badge.warn { color: #f97316; background: #fff3e7; }\n        .dashboard-focus-row {\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n            padding: .62rem .55rem;\n            border-bottom: 1px solid #eef3f8;\n            color: #334155;\n            font-size: .8rem;\n            font-weight: 850;\n        }\n        .dashboard-focus-row:last-child { border-bottom: 0; }\n        .dashboard-focus-row b { color: #f97316; font-size: 1rem; }\n        @media (max-width: 1200px) {\n            .dashboard-main-grid { grid-template-columns: 1fr; }\n            .dashboard-metrics, .dashboard-quick-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }\n        }\n        @media (max-width: 760px) {\n            .dashboard-metrics, .dashboard-quick-grid, .dashboard-flow { grid-template-columns: 1fr; }\n            .dashboard-welcome::after { display: none; }\n        }\n        [data-testid="stDataFrame"] {\n            border: 1px solid var(--line);\n            box-shadow: 0 8px 20px rgba(16, 35, 31, 0.04);\n        }\n        .report-viewer-toolbar {\n            background: #ffffff;\n            border: 1px solid var(--line);\n            border-left: 5px solid var(--brand-500);\n            padding: 0.95rem 1rem 0.9rem;\n            margin-bottom: 0.85rem;\n            box-shadow: 0 8px 18px rgba(16, 35, 31, 0.05);\n        }\n        .report-viewer-toolbar label {\n            color: var(--ink-700) !important;\n            font-weight: 700 !important;\n            font-size: 0.86rem !important;\n            margin-bottom: 0.25rem !important;\n        }\n        .report-viewer-toolbar .stButton button,\n        .report-viewer-toolbar .stDownloadButton button {\n            margin-top: 1.68rem;\n            height: 2.45rem;\n        }\n        .report-viewer-title { font-size: 1.28rem; font-weight: 800; margin-bottom: 0.3rem; color: var(--ink-900); }\n        .metric-card {\n            background: #ffffff;\n            border: 1px solid var(--line);\n            border-left: 4px solid var(--brand-500);\n            padding: 0.85rem 0.95rem;\n            box-shadow: 0 8px 18px rgba(16, 35, 31, 0.05);\n        }\n        .metric-label { color: var(--ink-500); font-size: 0.82rem; margin-bottom: 0.25rem; }\n        .metric-value { color: var(--brand-900); font-weight: 800; font-size: 1.15rem; }\n        .structure-page {\n            background: #f7faf8;\n            border: 1px solid var(--line);\n            box-shadow: 0 12px 28px rgba(16, 35, 31, 0.06);\n        }\n        .structure-toolbar {\n            display: flex;\n            align-items: center;\n            justify-content: space-between;\n            gap: 1rem;\n            padding: 1rem 1.15rem;\n            background: #ffffff;\n            border-bottom: 1px solid var(--line);\n        }\n        .structure-title {\n            color: var(--ink-900);\n            font-size: 1.18rem;\n            font-weight: 900;\n        }\n        .structure-source {\n            margin-top: 0.25rem;\n            color: var(--ink-500);\n            font-size: 0.82rem;\n        }\n        .structure-stats {\n            display: flex;\n            gap: 0.5rem;\n            white-space: nowrap;\n        }\n        .structure-stats span {\n            color: var(--brand-900);\n            background: #eaf6e4;\n            border: 1px solid #cde7bd;\n            padding: 0.32rem 0.55rem;\n            font-weight: 800;\n            font-size: 0.82rem;\n        }\n        .structure-tree {\n            overflow: auto;\n            padding: 1.1rem 1.15rem 1.4rem;\n            min-height: 560px;\n        }\n        .structure-node {\n            position: relative;\n            display: flex;\n            flex-direction: column;\n            align-items: center;\n            flex: 0 0 auto;\n            min-width: 250px;\n            margin: 0;\n        }\n        .structure-node::before {\n            content: "";\n            position: absolute;\n            top: -1.05rem;\n            left: 50%;\n            height: 1.05rem;\n            border-left: 1px solid #bfd1cc;\n        }\n        .structure-node:first-child::before,\n        .structure-tree > .structure-node::before {\n            display: none;\n        }\n        .structure-card {\n            display: flex;\n            align-items: center;\n            justify-content: center;\n            gap: 0.45rem;\n            width: 230px;\n            min-height: 3rem;\n            padding: 0.52rem 0.68rem;\n            background: #ffffff;\n            border: 1px solid #d9e6e1;\n            border-top: 4px solid var(--brand-500);\n            box-shadow: 0 6px 16px rgba(16, 35, 31, 0.05);\n        }\n        .structure-level {\n            flex: 0 0 auto;\n            color: var(--brand-900);\n            background: #eef8e7;\n            border: 1px solid #d5eacb;\n            padding: 0.16rem 0.34rem;\n            font-size: 0.72rem;\n            font-weight: 900;\n        }\n        .structure-name {\n            color: var(--ink-900);\n            font-size: 0.86rem;\n            font-weight: 800;\n            line-height: 1.35;\n            word-break: break-word;\n        }\n        .structure-ratio {\n            flex: 0 0 auto;\n            color: #c45b12;\n            background: #fff5ec;\n            border: 1px solid #f2d2b7;\n            padding: 0.16rem 0.35rem;\n            font-size: 0.72rem;\n            font-weight: 900;\n        }\n        .structure-children {\n            position: relative;\n            display: flex;\n            align-items: flex-start;\n            justify-content: center;\n            gap: 0.9rem;\n            margin-top: 1.75rem;\n            padding-top: 1.05rem;\n            min-width: max-content;\n        }\n        .structure-children::before {\n            content: "";\n            position: absolute;\n            top: 0;\n            left: 50%;\n            height: 1.05rem;\n            border-left: 1px solid #bfd1cc;\n        }\n        .structure-children::after {\n            content: "";\n            position: absolute;\n            top: 1.05rem;\n            left: 125px;\n            right: 125px;\n            border-top: 1px solid #bfd1cc;\n        }\n        .structure-children > .structure-node {\n            z-index: 1;\n        }\n        .structure-expand {\n            position: relative;\n            z-index: 1;\n            margin: 0;\n            min-width: 250px;\n            text-align: center;\n        }\n        .structure-expand::before {\n            content: "";\n            position: absolute;\n            top: -1.05rem;\n            left: 50%;\n            height: 1.05rem;\n            border-left: 1px solid #bfd1cc;\n        }\n        .structure-expand summary {\n            display: inline-flex;\n            align-items: center;\n            justify-content: center;\n            cursor: pointer;\n            color: #ffffff;\n            background: var(--brand-500);\n            border: 1px solid var(--brand-500);\n            width: 1.5rem;\n            height: 1.5rem;\n            font-weight: 900;\n            list-style: none;\n            box-shadow: 0 6px 14px rgba(91, 160, 22, 0.22);\n        }\n        .structure-expand summary::-webkit-details-marker {\n            display: none;\n        }\n        .structure-expand summary::before {\n            content: "+";\n            font-size: 1rem;\n            line-height: 1;\n        }\n        .structure-expand[open] summary::before {\n            content: "-";\n        }\n        .structure-hidden-children {\n            margin-top: 1.75rem;\n        }\n        .structure-root-card,\n        .structure-level-card {\n            background: #ffffff;\n            border: 1px solid #d9e6e1;\n            border-top: 4px solid var(--brand-500);\n            box-shadow: 0 6px 16px rgba(16, 35, 31, 0.05);\n            padding: 0.72rem 0.85rem;\n            min-height: 4.2rem;\n        }\n        .structure-root-card {\n            display: inline-flex;\n            align-items: center;\n            gap: 0.55rem;\n            margin: 1rem 1.15rem 0.3rem;\n            min-width: 340px;\n        }\n        .structure-section {\n            margin: 1rem 1.15rem;\n            padding: 0.9rem;\n            background: #fbfdfc;\n            border: 1px solid var(--line);\n        }\n        .structure-section-title {\n            display: flex;\n            align-items: center;\n            gap: 0.55rem;\n            margin-bottom: 0.85rem;\n            color: var(--ink-900);\n            font-weight: 900;\n            font-size: 1rem;\n        }\n        .structure-level-card .structure-name {\n            display: block;\n            min-height: 2.3rem;\n        }\n        .structure-child-count {\n            display: inline-block;\n            margin-top: 0.45rem;\n            color: var(--brand-900);\n            background: #eef8e7;\n            border: 1px solid #d5eacb;\n            padding: 0.15rem 0.38rem;\n            font-size: 0.72rem;\n            font-weight: 900;\n        }\n        .structure-chart-board {\n            overflow: auto;\n            padding: 1.2rem 1.15rem 1.6rem;\n            background: #fbfdfc;\n            border-top: 1px solid var(--line);\n        }\n        .structure-root-row {\n            display: flex;\n            justify-content: center;\n            min-width: max-content;\n        }\n        .structure-org-root {\n            display: inline-flex;\n            align-items: center;\n            gap: 0.5rem;\n            padding: 0.62rem 1rem;\n            color: var(--ink-900);\n            background: #ffffff;\n            border: 1px solid #f2c6a8;\n            border-radius: 8px;\n            font-weight: 900;\n            box-shadow: 0 8px 18px rgba(16, 35, 31, 0.06);\n        }\n        .structure-level-one-row {\n            position: relative;\n            display: flex;\n            align-items: flex-start;\n            gap: 1rem;\n            min-width: max-content;\n            margin-top: 2.2rem;\n            padding-top: 1.4rem;\n        }\n        .structure-level-one-row::before {\n            content: "";\n            position: absolute;\n            top: 0;\n            left: 4rem;\n            right: 4rem;\n            border-top: 1px solid #9fb0ad;\n        }\n        .structure-level-one-row::after {\n            content: "";\n            position: absolute;\n            top: -2.2rem;\n            left: 50%;\n            height: 2.2rem;\n            border-left: 1px solid #9fb0ad;\n        }\n        .structure-branch {\n            position: relative;\n            width: 150px;\n            flex: 0 0 150px;\n        }\n        .structure-branch::before {\n            content: "";\n            position: absolute;\n            top: -1.4rem;\n            left: 50%;\n            height: 1.4rem;\n            border-left: 1px solid #9fb0ad;\n        }\n        .structure-org-card {\n            position: relative;\n            display: flex;\n            flex-direction: column;\n            gap: 0.22rem;\n            min-height: 3.35rem;\n            padding: 0.48rem 0.52rem;\n            background: #ffffff;\n            border: 1px solid #dde7e4;\n            border-radius: 6px;\n            box-shadow: 0 8px 18px rgba(16, 35, 31, 0.05);\n        }\n        .structure-org-card.active {\n            border-color: #86b7ff;\n            box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.10), 0 8px 18px rgba(16, 35, 31, 0.05);\n        }\n        .structure-org-name {\n            color: var(--ink-900);\n            font-size: 0.78rem;\n            font-weight: 900;\n            line-height: 1.28;\n            word-break: break-word;\n        }\n        .structure-org-ratio {\n            align-self: flex-start;\n            color: #e35f10;\n            background: #fff7ef;\n            border: 1px solid #ffd7b8;\n            border-radius: 4px;\n            padding: 0.08rem 0.24rem;\n            font-size: 0.66rem;\n            font-weight: 900;\n        }\n        .structure-second-list {\n            position: relative;\n            margin-top: 1.2rem;\n            padding-top: 0.8rem;\n        }\n        .structure-second-list::before {\n            content: "";\n            position: absolute;\n            top: 0;\n            left: 50%;\n            height: 0.8rem;\n            border-left: 1px solid #b7c7c3;\n        }\n        .structure-second-card {\n            margin-top: 0.48rem;\n            min-height: 3rem;\n        }\n        .structure-descendant-list {\n            position: relative;\n            margin: 0.38rem 0 0.2rem 0.55rem;\n            padding-left: 0.58rem;\n            border-left: 1px solid #c9d8d4;\n        }\n        .structure-descendant-card {\n            margin-top: 0.34rem;\n            padding: 0.34rem 0.42rem;\n            background: #ffffff;\n            border: 1px solid #e0ebe7;\n            border-radius: 5px;\n        }\n        .structure-descendant-card .structure-org-name {\n            font-size: 0.72rem;\n            line-height: 1.25;\n        }\n        .structure-descendant-card .structure-org-ratio {\n            font-size: 0.62rem;\n        }\n        .structure-descendant-level {\n            display: inline-block;\n            margin-bottom: 0.18rem;\n            color: var(--brand-900);\n            background: #eef8e7;\n            border: 1px solid #d5eacb;\n            padding: 0.06rem 0.22rem;\n            font-size: 0.62rem;\n            font-weight: 900;\n        }\n        .structure-more-chip {\n            margin-top: 0.48rem;\n            padding: 0.36rem 0.5rem;\n            color: var(--ink-500);\n            background: #ffffff;\n            border: 1px dashed #c4d2ce;\n            border-radius: 6px;\n            text-align: center;\n            font-size: 0.78rem;\n            font-weight: 900;\n        }\n        .structure-drilldown {\n            margin: 0.9rem 1.15rem 1.2rem;\n        }\n        \n\n        /* Modern fintech cockpit overrides */\n        :root {\n            --fin-bg: #f4f7fb;\n            --fin-panel: rgba(255, 255, 255, .92);\n            --fin-panel-solid: #ffffff;\n            --fin-line: #e5edf6;\n            --fin-ink: #111827;\n            --fin-muted: #64748b;\n            --fin-blue: #1d63ff;\n            --fin-cyan: #11b7d7;\n            --fin-violet: #635bff;\n            --fin-gold: #d6a84f;\n            --fin-red: #e5484d;\n            --fin-green: #17a773;\n            --fin-orange: #f59e0b;\n            --fin-shadow: 0 18px 42px rgba(21, 45, 86, .08);\n        }\n        html, body, [class*="css"] {\n            font-family: "Microsoft YaHei", "PingFang SC", "HarmonyOS Sans SC", "Noto Sans CJK SC", sans-serif !important;\n        }\n        .stApp {\n            background:\n                radial-gradient(circle at 16% 8%, rgba(29, 99, 255, .10), transparent 28%),\n                radial-gradient(circle at 88% 0%, rgba(17, 183, 215, .14), transparent 24%),\n                linear-gradient(180deg, #f8fbff 0%, #f2f6fb 100%) !important;\n            color: var(--fin-ink) !important;\n        }\n        .block-container {\n            padding: .95rem 1.15rem 1.6rem !important;\n            max-width: 1440px !important;\n        }\n        div[data-testid="column"]:has(.product-title) > div {\n            min-height: calc(100vh - 1.9rem) !important;\n            border-radius: 24px !important;\n            padding: 1rem .78rem !important;\n            border: 1px solid rgba(255,255,255,.12) !important;\n            background:\n                radial-gradient(circle at 26% 12%, rgba(74, 222, 190, .20), transparent 25%),\n                linear-gradient(180deg, #071a32 0%, #081f3e 48%, #06162c 100%) !important;\n            box-shadow: 0 24px 54px rgba(7, 20, 42, .18) !important;\n            overflow: hidden;\n        }\n        .product-title {\n            margin: .2rem .1rem 1rem !important;\n            padding: .35rem .6rem .8rem 2.35rem !important;\n            color: #ffffff !important;\n            border-bottom: 1px solid rgba(255,255,255,.10) !important;\n            font-size: 1.08rem !important;\n            font-weight: 950 !important;\n            letter-spacing: .02em;\n        }\n        .product-title::before {\n            left: .55rem !important;\n            top: .35rem !important;\n            width: 1.28rem !important;\n            height: 1.28rem !important;\n            border-radius: .45rem !important;\n            background: linear-gradient(145deg, #20e3b2, #1d63ff) !important;\n            box-shadow: 0 0 0 4px rgba(32, 227, 178, .12), 0 12px 22px rgba(29, 99, 255, .22) !important;\n        }\n        .side-menu { margin: 0 !important; padding: 0 !important; }\n        .side-menu-section-label {\n            padding: .72rem .7rem .36rem;\n            color: rgba(226, 232, 240, .48);\n            font-size: .72rem;\n            font-weight: 900;\n            letter-spacing: .08em;\n        }\n        .side-menu-primary {\n            min-height: 2.7rem !important;\n            margin: .12rem 0 !important;\n            padding: 0 .78rem !important;\n            border: 1px solid transparent !important;\n            border-radius: 13px !important;\n            color: rgba(255, 255, 255, .92) !important;\n            background: transparent !important;\n            font-size: .9rem !important;\n            font-weight: 850 !important;\n            transition: all 160ms ease;\n        }\n        .side-menu-primary .nav-icon { width: 1.55rem; color: rgba(125, 211, 252, .88); }\n        .side-menu-primary span,\n        .side-menu-secondary,\n        .side-menu-tertiary {\n            color: rgba(255, 255, 255, .88) !important;\n            text-shadow: 0 1px 1px rgba(0, 0, 0, .18);\n        }\n        .side-menu-primary.active,\n        .side-menu-primary:hover {\n            color: #ffffff !important;\n            background: linear-gradient(90deg, rgba(29, 99, 255, .24), rgba(17, 183, 215, .12)) !important;\n            border-color: rgba(125, 211, 252, .22) !important;\n            box-shadow: inset 0 0 0 1px rgba(255,255,255,.04);\n        }\n        .side-menu-children {\n            margin: .1rem 0 .45rem !important;\n            padding: .35rem 0 .35rem .78rem !important;\n            border-left: 1px solid rgba(148, 163, 184, .18);\n            background: transparent !important;\n        }\n        .side-menu-secondary,\n        .side-menu-tertiary {\n            display: block;\n            padding: .42rem .7rem !important;\n            margin: .05rem 0 !important;\n            border-radius: 10px !important;\n            color: rgba(203, 213, 225, .62) !important;\n            border-left: 0 !important;\n            font-size: .78rem !important;\n            text-decoration: none !important;\n            transition: all 140ms ease;\n        }\n        .side-menu-secondary.active,\n        .side-menu-secondary:hover,\n        .side-menu-tertiary.active,\n        .side-menu-tertiary:hover {\n            color: #ffffff !important;\n            background: rgba(255,255,255,.07) !important;\n        }\n        .top-userbar {\n            position: sticky;\n            top: .75rem;\n            z-index: 30;\n            display: flex;\n            align-items: center;\n            justify-content: space-between;\n            min-height: 64px;\n            padding: .72rem .95rem;\n            margin-bottom: .95rem;\n            border: 1px solid rgba(226, 232, 240, .82);\n            border-radius: 22px;\n            background: rgba(255,255,255,.82);\n            backdrop-filter: blur(16px);\n            box-shadow: 0 14px 34px rgba(21, 45, 86, .07);\n        }\n        .top-bar-left { display: flex; align-items: center; gap: .78rem; }\n        .top-bar-mark {\n            width: 38px; height: 38px; border-radius: 13px;\n            display: grid; place-items: center;\n            color: #fff; font-weight: 950; font-size: .88rem;\n            background: linear-gradient(145deg, var(--fin-blue), var(--fin-cyan));\n            box-shadow: 0 14px 26px rgba(29, 99, 255, .22);\n        }\n        .top-bar-title { color: var(--fin-ink); font-size: .98rem; font-weight: 950; line-height: 1.2; }\n        .top-bar-title span { display: block; margin-top: .18rem; color: var(--fin-muted); font-size: .74rem; font-weight: 650; }\n        .top-bar-search {\n            min-width: 330px;\n            padding: .58rem .78rem;\n            border: 1px solid var(--fin-line);\n            border-radius: 999px;\n            color: #94a3b8;\n            background: #f8fafc;\n            font-size: .8rem;\n        }\n        .top-bar-right { display: flex; align-items: center; gap: .72rem; }\n        .top-icon-btn {\n            width: 36px; height: 36px; border-radius: 12px;\n            display: grid; place-items: center;\n            color: #475569; background: #f8fafc; border: 1px solid var(--fin-line);\n        }\n        .user-menu-wrap { position: relative; }\n        .user-menu-wrap details { position: relative; }\n        .user-menu-wrap summary { list-style: none; cursor: pointer; }\n        .user-menu-wrap summary::-webkit-details-marker { display: none; }\n        .top-user-pill {\n            display: flex; align-items: center; gap: .55rem;\n            padding: .34rem .48rem .34rem .38rem;\n            border-radius: 999px; background: #f8fafc; border: 1px solid var(--fin-line);\n        }\n        .top-user-avatar {\n            width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center;\n            color: #fff; font-weight: 950; background: linear-gradient(145deg, #111827, #365478);\n        }\n        .top-user-meta { color: var(--fin-ink); font-size: .8rem; font-weight: 900; line-height: 1.15; padding-right: .25rem; }\n        .top-user-meta span { display: block; color: var(--fin-muted); font-size: .68rem; font-weight: 650; margin-top: .14rem; }\n        .user-menu-panel {\n            position: absolute; right: 0; top: 46px; width: 178px;\n            padding: .48rem; border-radius: 16px; border: 1px solid var(--fin-line);\n            background: #fff; box-shadow: 0 22px 48px rgba(15, 23, 42, .14);\n        }\n        .user-menu-panel a {\n            display: block; padding: .58rem .7rem; border-radius: 10px;\n            color: #334155 !important; text-decoration: none !important; font-size: .82rem; font-weight: 800;\n        }\n        .user-menu-panel a:hover { background: #f1f5f9; color: var(--fin-blue) !important; }\n        .user-menu-panel .danger { color: #dc2626 !important; }\n        .fin-card, .dashboard-section, .dashboard-metric, .dashboard-quick-card, .dashboard-flow-card {\n            border-radius: 18px !important;\n            border: 1px solid var(--fin-line) !important;\n            box-shadow: var(--fin-shadow) !important;\n        }\n        .dashboard-home { animation: finFadeUp 280ms ease both; }\n        .dashboard-welcome {\n            min-height: 250px !important;\n            padding: 1.6rem 1.8rem !important;\n            border-radius: 24px !important;\n            border: 1px solid rgba(220, 230, 245, .92) !important;\n            background:\n                radial-gradient(circle at 78% 48%, rgba(29, 99, 255, .16), transparent 24%),\n                linear-gradient(115deg, #ffffff 0%, #f8fbff 42%, #eef7ff 100%) !important;\n            box-shadow: var(--fin-shadow) !important;\n        }\n        .dashboard-welcome::after {\n            content: "AI" !important;\n            right: 5.8rem !important;\n            top: 3.6rem !important;\n            width: 112px !important;\n            height: 112px !important;\n            border-radius: 34px !important;\n            background: linear-gradient(145deg, #1d63ff, #11b7d7) !important;\n            box-shadow: 0 24px 54px rgba(29, 99, 255, .22) !important;\n        }\n        .dashboard-welcome h2 { font-size: 1.85rem !important; letter-spacing: -.03em; }\n        .dashboard-welcome p { max-width: 720px !important; font-size: .95rem !important; }\n        .dashboard-metrics { grid-template-columns: repeat(5, minmax(0, 1fr)) !important; }\n        .dashboard-metric { min-height: 108px !important; align-items: flex-start !important; padding: 1rem !important; }\n        .dashboard-metric-value { font-size: 1.7rem !important; }\n        .dashboard-section { padding: 1.05rem !important; }\n        .dashboard-main-grid { grid-template-columns: 1.15fr .86fr .76fr !important; }\n        .status-done { color: var(--fin-green); background: #e8f8f1; }\n        .status-running { color: var(--fin-blue); background: #eaf2ff; }\n        .status-pending { color: var(--fin-orange); background: #fff7e6; }\n        .status-error { color: var(--fin-red); background: #fff0f0; }\n        .report-workbench { display: grid; gap: .9rem; animation: finFadeUp 260ms ease both; }\n        .report-top-card {\n            border-radius: 24px; padding: 1.25rem; border: 1px solid var(--fin-line);\n            background: linear-gradient(115deg, #ffffff, #f6faff 58%, #edf7ff);\n            box-shadow: var(--fin-shadow);\n        }\n        .report-meta-row { display: flex; flex-wrap: wrap; gap: .65rem; margin-top: .85rem; }\n        .report-meta-pill { padding: .42rem .65rem; border-radius: 999px; background: #fff; border: 1px solid var(--fin-line); color: #475569; font-size: .78rem; font-weight: 850; }\n        .report-stepper { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: .55rem; }\n        .report-step { position: relative; padding: .85rem .7rem; border-radius: 16px; border: 1px solid var(--fin-line); background: #fff; box-shadow: 0 10px 24px rgba(21,45,86,.045); }\n        .report-step.active { border-color: rgba(29,99,255,.35); background: linear-gradient(180deg, #fff, #f0f6ff); }\n        .report-step-num { width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; color: #fff; background: linear-gradient(145deg, var(--fin-blue), var(--fin-cyan)); font-size: .72rem; font-weight: 950; }\n        .report-step-title { margin-top: .48rem; color: var(--fin-ink); font-size: .8rem; font-weight: 950; }\n        .report-layout-grid { display: grid; grid-template-columns: 230px 1fr 285px; gap: .9rem; align-items: start; }\n        .report-tree, .report-side-panel { border-radius: 20px; border: 1px solid var(--fin-line); background: #fff; box-shadow: var(--fin-shadow); padding: 1rem; }\n        .report-tree-title, .report-side-title { color: var(--fin-ink); font-size: .92rem; font-weight: 950; margin-bottom: .75rem; }\n        .report-tree-item { padding: .55rem .65rem; border-radius: 12px; color: #475569; font-size: .8rem; font-weight: 800; margin-bottom: .18rem; }\n        .report-tree-item.active { color: var(--fin-blue); background: #edf4ff; }\n        .report-action-card { border-radius: 20px; border: 1px solid var(--fin-line); background: #fff; box-shadow: var(--fin-shadow); padding: 1rem; }\n        .report-button-row { display: flex; gap: .6rem; flex-wrap: wrap; margin-top: .85rem; }\n        .fin-primary-btn, .fin-secondary-btn { display: inline-flex; align-items: center; justify-content: center; min-height: 2.35rem; padding: 0 .9rem; border-radius: 12px; text-decoration: none !important; font-size: .82rem; font-weight: 900; }\n        .fin-primary-btn { color: #fff !important; background: linear-gradient(90deg, var(--fin-blue), var(--fin-cyan)); box-shadow: 0 14px 26px rgba(29,99,255,.18); }\n        .fin-secondary-btn { color: #334155 !important; background: #fff; border: 1px solid var(--fin-line); }\n        @keyframes finFadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }\n        /* Fintech SaaS polish: readability-first sidebar and cockpit cards */\n        :root {\n            --primary: #1677FF;\n            --primary-dark: #0F4C81;\n            --text-main: #0F172A;\n            --text-second: #52657A;\n            --text-muted: #8A9AAF;\n            --bg-page: #F3F7FC;\n            --bg-card: #FFFFFF;\n            --border-soft: #E3EBF5;\n            --success: #16A34A;\n            --warning: #F59E0B;\n            --danger: #EA580C;\n            --purple: #7C3AED;\n            --fin-shadow: 0 12px 30px rgba(30, 64, 120, 0.08);\n        }\n        .stApp {\n            background:\n                radial-gradient(circle at 12% 8%, rgba(22,119,255,0.10), transparent 30%),\n                radial-gradient(circle at 85% 12%, rgba(20,184,166,0.10), transparent 28%),\n                linear-gradient(180deg, #F6FAFF 0%, #EEF4FA 100%) !important;\n        }\n        div[data-testid="column"]:has(.product-title) > div {\n            background: linear-gradient(180deg, #EEF6FF 0%, #F7FBFF 45%, #FFFFFF 100%) !important;\n            border: 1px solid rgba(220, 230, 245, 0.86) !important;\n            box-shadow: 0 18px 46px rgba(38, 71, 120, 0.10) !important;\n        }\n        .product-title {\n            color: #1E2A3A !important;\n            border-bottom: 1px solid rgba(120, 150, 180, 0.18) !important;\n            text-shadow: none !important;\n        }\n        div[data-testid="column"]:has(.product-title) .stMarkdown,\n        div[data-testid="column"]:has(.product-title) p,\n        div[data-testid="column"]:has(.product-title) span,\n        div[data-testid="column"]:has(.product-title) label,\n        div[data-testid="column"]:has(.product-title) div[data-testid="stCaptionContainer"] {\n            color: #24364B !important;\n            text-shadow: none !important;\n        }\n        .side-menu-section-label {\n            padding: 1rem .9rem .42rem !important;\n            color: #9AA8B8 !important;\n            font-size: 11px !important;\n            line-height: 1 !important;\n            letter-spacing: 1.5px !important;\n            font-weight: 900 !important;\n            text-transform: uppercase;\n        }\n        .side-menu-primary {\n            min-height: 48px !important;\n            height: 48px !important;\n            padding: 0 14px !important;\n            margin: .18rem 0 !important;\n            border-radius: 14px !important;\n            color: #24364B !important;\n            font-weight: 650 !important;\n            border: 0 !important;\n            border-left: 3px solid transparent !important;\n            background: transparent !important;\n            transform: translateX(0);\n            transition: background 180ms ease, transform 180ms ease, color 180ms ease;\n        }\n        .side-menu-primary > span:first-child {\n            display: inline-flex;\n            align-items: center;\n            gap: 10px;\n            color: #24364B !important;\n        }\n        .side-menu-primary .nav-icon {\n            width: 18px !important;\n            color: #7B8FA8 !important;\n            font-weight: 900;\n        }\n        .side-menu-primary > span:last-child {\n            color: #9AA8B8 !important;\n            text-shadow: none !important;\n            transition: color 180ms ease;\n        }\n        .side-menu-primary span,\n        .side-menu-secondary,\n        .side-menu-tertiary {\n            color: #24364B !important;\n            text-shadow: none !important;\n        }\n        .side-menu-primary.active {\n            color: #102A43 !important;\n            font-weight: 700 !important;\n            border-left-color: #1677FF !important;\n            background: linear-gradient(90deg, rgba(22,119,255,0.16), rgba(22,119,255,0.06)) !important;\n        }\n        .side-menu-primary.active > span:first-child,\n        .side-menu-primary.active span {\n            color: #102A43 !important;\n            font-weight: 700 !important;\n        }\n        .side-menu-primary.active .nav-icon {\n            color: #1677FF !important;\n        }\n        .side-menu-primary:hover {\n            color: #102A43 !important;\n            background: rgba(22,119,255,0.08) !important;\n            transform: translateX(2px);\n            border-left-color: rgba(22,119,255,0.35) !important;\n        }\n        .side-menu-primary:hover > span:last-child {\n            color: #1677FF !important;\n        }\n        .side-menu-children {\n            border-left: 1px solid rgba(120, 150, 180, 0.18) !important;\n            margin: .2rem 0 .55rem .95rem !important;\n            padding: .25rem 0 .25rem .45rem !important;\n        }\n        .side-menu-group {\n            padding: .72rem .7rem .32rem !important;\n            color: #6B7C93 !important;\n            background: transparent !important;\n            font-size: 12px !important;\n            font-weight: 800 !important;\n            letter-spacing: .04em;\n        }\n        .side-menu-secondary,\n        .side-menu-tertiary {\n            color: #6B7C93 !important;\n            border-radius: 12px !important;\n            font-weight: 600 !important;\n        }\n        .side-menu-tertiary.disabled,\n        .side-menu-secondary.disabled {\n            color: #B6C2D0 !important;\n            pointer-events: none;\n            background: transparent !important;\n        }\n        .side-menu-secondary.active,\n        .side-menu-secondary:hover,\n        .side-menu-tertiary.active,\n        .side-menu-tertiary:hover {\n            color: #102A43 !important;\n            background: rgba(22,119,255,0.08) !important;\n        }\n        .top-userbar {\n            background: rgba(255,255,255,0.86) !important;\n            backdrop-filter: blur(18px);\n            border: 1px solid rgba(220,230,245,0.9) !important;\n            box-shadow: 0 12px 32px rgba(38, 71, 120, 0.08) !important;\n        }\n        .top-bar-mark {\n            box-shadow: 0 12px 24px rgba(22,119,255,0.16) !important;\n        }\n        .top-bar-title {\n            color: #0F172A !important;\n            font-size: 18px !important;\n            font-weight: 800 !important;\n        }\n        .top-bar-title span {\n            color: #6B7C93 !important;\n            font-size: 12px !important;\n        }\n        .top-bar-search {\n            background: #F8FAFD !important;\n            border-color: #DDE7F3 !important;\n            color: #8A9AAF !important;\n        }\n        .top-bar-search:hover {\n            border-color: #1677FF !important;\n            box-shadow: 0 0 0 3px rgba(22,119,255,0.12);\n        }\n        .dashboard-welcome {\n            background:\n                radial-gradient(circle at 80% 50%, rgba(22,119,255,0.18), transparent 24%),\n                radial-gradient(circle at 89% 28%, rgba(20,184,166,0.13), transparent 15%),\n                radial-gradient(circle at 72% 74%, rgba(124,58,237,0.08), transparent 18%),\n                linear-gradient(135deg, #FFFFFF 0%, #F7FBFF 45%, #EAF4FF 100%) !important;\n            border: 1px solid rgba(215,228,245,0.9) !important;\n            box-shadow: 0 20px 60px rgba(33, 80, 140, 0.10) !important;\n        }\n        .dashboard-welcome::before {\n            content: "";\n            position: absolute;\n            right: 2.6rem;\n            top: 1.35rem;\n            width: 310px;\n            height: 190px;\n            opacity: .46;\n            background-image:\n                radial-gradient(circle, rgba(22,119,255,.24) 1px, transparent 1.5px),\n                linear-gradient(120deg, transparent 0 42%, rgba(22,119,255,.14) 42% 43%, transparent 43% 100%);\n            background-size: 18px 18px, 100% 100%;\n            pointer-events: none;\n        }\n        .dashboard-welcome::after {\n            background: linear-gradient(145deg, #1677FF, #14B8A6) !important;\n            box-shadow:\n                0 22px 58px rgba(22,119,255,0.24),\n                -42px 20px 80px rgba(20,184,166,0.16),\n                38px -20px 70px rgba(124,58,237,0.10) !important;\n        }\n        .dashboard-welcome h2 {\n            color: #0F172A !important;\n        }\n        .dashboard-welcome p {\n            color: #52657A !important;\n        }\n        .dashboard-tags span {\n            background: #F3F7FC !important;\n            color: #24364B !important;\n            border: 1px solid #D8E4F0 !important;\n        }\n        .dashboard-metric {\n            min-height: 118px !important;\n            background: #FFFFFF !important;\n            border: 1px solid #E5ECF5 !important;\n            border-radius: 18px !important;\n            box-shadow: 0 12px 30px rgba(30, 64, 120, 0.08) !important;\n            transition: transform 180ms ease, box-shadow 180ms ease;\n        }\n        .dashboard-metric:hover {\n            transform: translateY(-3px);\n            box-shadow: 0 18px 40px rgba(30, 64, 120, 0.12) !important;\n        }\n        .dashboard-metric-title {\n            color: #52657A !important;\n            font-weight: 800 !important;\n        }\n        .dashboard-metric-value {\n            color: #0F172A !important;\n            font-size: 30px !important;\n            font-weight: 800 !important;\n        }\n        .dashboard-metric-value span {\n            font-size: 14px !important;\n            color: #0F172A !important;\n        }\n        .dashboard-metric-sub {\n            color: #7A8CA3 !important;\n        }\n        .dashboard-icon {\n            width: 50px !important;\n            height: 50px !important;\n            border-radius: 14px !important;\n        }\n        .dashboard-icon.blue { color: #1677FF !important; background: #EAF3FF !important; }\n        .dashboard-icon.green { color: #16A34A !important; background: #EAF8F1 !important; }\n        .dashboard-icon.orange { color: #F59E0B !important; background: #FFF4E5 !important; }\n        .dashboard-icon.purple { color: #7C3AED !important; background: #F1ECFF !important; }\n        .dashboard-icon.danger { color: #EA580C !important; background: #FFF0E8 !important; }\n        .dashboard-section {\n            background: #FFFFFF !important;\n            border: 1px solid #E3EBF5 !important;\n            border-radius: 20px !important;\n            box-shadow: 0 12px 30px rgba(30, 64, 120, 0.07) !important;\n        }\n        .dashboard-quick-card {\n            min-height: 98px !important;\n            background: linear-gradient(180deg, #FFFFFF 0%, #FAFCFF 100%) !important;\n            border: 1px solid #E3EBF5 !important;\n            border-radius: 16px !important;\n            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;\n        }\n        .dashboard-quick-card:hover {\n            border-color: rgba(22,119,255,0.35) !important;\n            box-shadow: 0 16px 32px rgba(22,119,255,0.10) !important;\n            transform: translateY(-2px);\n        }\n        .dashboard-quick-title {\n            color: #0F172A !important;\n            font-weight: 800 !important;\n        }\n        .dashboard-quick-desc {\n            color: #52657A !important;\n        }\n        @media (max-width: 1200px) {\n            .dashboard-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }\n            .dashboard-main-grid, .report-layout-grid { grid-template-columns: 1fr !important; }\n            .top-bar-search { display: none; }\n        }\n</style>\n        '
    st

def __annotate__(format):
    return {'title': str, 'subtitle': str, 'badge': str, 'return': None}

def render_product_header(title, subtitle, badge):
    subtitle_html = ''
    ('unsafe_allow_html',)
    True
    '</div>\n        </div>\n        '
    html.st(None)
    '\n            </div>\n            <div class="product-header-badge">'
    '</h1>\n                '
    html.st(None)
    '\n        <div class="product-header">\n            <div>\n                <h1>'
    '</div>'
    html.st(None)
    '<div class="product-header-subtitle">'

def __annotate__(format):
    return {'password': str, 'return': str}

def password_hash(password):
    payload = 'financial_report_control_poc:'.hashlib('utf-8')
    return sha256(None)()

def __annotate__(format):
    return 'return'
    str
    'stored_hash'
    str
    'password'

def verify_password(password, stored_hash):
    stored_hash
    if return str == stored_hash(''):
        pass

def __annotate__(format):
    return 'return' / (dict, Any)

def default_access_control():
    return {'admin': ['admin']}
    'user_roles'
    {'admin': ['*']}
    'role_permissions'
    [{'role_key': 'admin', 'role_name': '系统管理员', 'active': True, 'description': '拥有全部页面权限'}]
    'roles'
    [{'users': 'username', 'admin': 'name', '管理员': 'department', '系统管理': 'active', True: 'is_admin', True: 'password_hash'('admin123')}]

def __annotate__(format):
    return 'return' / (dict, Any)

def load_access_control():
    config = loads()
    ACCESS_CONTROL_PATH.save_access_control()(JSONDecodeError)
    return
    config = 'utf-8'(('encoding',))
    migrate_access_control.insert(JSONDecodeError)
    (None / 'users')()(True, False((None / 'users')()) / 'users' / (loads() / 'users'))
    [] / (loads() / 'roles')
    ['*']('role_permissions', {})['admin'] = 'roles'
    'admin'(JSONDecodeError)
    return ['admin']('user_roles', {})
    migrate_access_control
    config = loads()

def __annotate__(format):
    return 'return' / (dict, Any)
    'config' / (dict, Any)

def migrate_access_control(config):
    default_config = isinstance()
    (str / 'users')['users'] = list.password_hash('users')
    user = 'users'
    'name'.password_hash('display_name')
    'name'.pop('department', '')
    'name'.password_hash('display_name').password_hash('username').pop('active', True)
    False
    if 'admin123'('123456')['password_hash'] = any(insert.password_hash('username')) == 'admin':
        pass
    {}['role_permissions'] = ('is_admin'.password_hash('password_hash')(list.password_hash('roles'), str) / 'roles')()('roles', list.password_hash('role_permissions'))
    {}['user_roles'] = list.password_hash('user_roles')
    username = list()(insert)
    if page = 'permissions' == ['*']:
        pass
    page = '*'
    'legacy_'
    True({False((None / 'roles')()) / 'roles': 'role_key', 'role_name': '历史权限', 'active': True, 'description': '由旧版用户页面权限自动迁移'})
    page = ['admin'].pop('user_roles', {})
    page = (None / 'roles')()
    [[](insert) / 'role_permissions'] / 'user_roles'
    [](insert)((None / 'roles')(), True / (False((None / 'roles')()) / 'roles' / 'roles'))
    'admin'.pop('user_roles', {}).pop('admin', ['admin'])
    return ['*'].pop('role_permissions', {})

def __annotate__(format):
    'return'
    'config' / (dict, Any)

def save_access_control(config):
    ('parents', 'exist_ok')
    ('encoding',)
    'utf-8'
    ('ensure_ascii', 'indent')
    False
    ACCESS_CONTROL_PATH
    True
    True
    ACCESS_CONTROL_PATH.mkdir.dumps

def __annotate__(format):
    return 'access_control' / (dict, Any) / ('return' / (dict, Any))

def active_users(access_control):
    user = []
    return 'users'('active', True)
    []

def __annotate__(format):
    return 'return' / (dict, Any)
    'access_control' / (dict, Any)

def current_user(access_control):
    users = st(session_state.next('authenticated_username', ''))('users', [])
    return {}

def __annotate__(format):
    return (('return' / (dict, Any)) + None)
    Any
    'password'
    Any
    'username'
    ('access_control' / (dict, Any))

def authenticate_user(access_control, username, password):
    return None.str('users', [])().str('active', True).str('password_hash', '')

def __annotate__(format):
    return Any
    'return'
    'user' / (dict, Any)

def user_auth_token(user):
    payload = ':financial_report_control_poc'.sha256('utf-8')
    return hexdigest(None)()
    ':'.encode('password_hash')
    'username'

def __annotate__(format):
    return (('return' / (dict, Any)) + None)
    Any
    'token'
    ('access_control' / (dict, Any))

def authenticated_user_from_token(access_control, token):
    user = user_auth_token
    return

def __annotate__(format):
    return 'return'
    'access_control' / (dict, Any)

def is_authenticated(access_control):
    user = get
    return True
    token = authenticated_user_from_token(session_state.st('auth_token', ''))
    token_user = True
    return False
    session_state['authenticated_username'] = 'active'(authenticated_user_from_token.st('username'))
    return True

def __annotate__(format):
    return {'params': str, 'return': str}

def app_href():
    query_params = {}
    query_params.session_state('auth_token')
    token = query_params('auth_token')
    return 'auth_token' + '?'(None.st()())
    query_params.session_state('auth_token')

def __annotate__(format):
    'return'
    'access_control' / (dict, Any)

def render_login_page(access_control):
    import base64
    base64 = base64
    visual_path = exists / 'assets' / 'login_left_visual.png'
    visual_data_uri = ''
    visual_data_uri = None.decode()('data:image/png;base64,'.markdown.form()).form_submit_button('ascii')
    ('unsafe_allow_html',)
    left()
    ('unsafe_allow_html',)
    ('unsafe_allow_html',)
    True(None, None, None)
    right()
    ('unsafe_allow_html',)
    ('clear_on_submit',)()
    username = ('placeholder', 'label_visibility')
    password = ('type', 'placeholder', 'label_visibility')
    ('unsafe_allow_html',)
    submitted = ('type', 'use_container_width')
    True(None, None, None)
    ('unsafe_allow_html',)
    user = authenticate_user.error(None, '<div class="login-browser"><span class="chrome-dot"></span><span>推荐使用 Chrome / Edge 最新版本浏览器</span></div>', True())
    '用户名或密码错误，或用户已停用。'
    authenticate_user(None, None, None)
    token = '登录系统'('primary')
    authenticate_user['authenticated_username'] = authenticate_user(None('username'))
    authenticate_user['auth_token'] = True
    authenticate_user['auth_token'] = '<div class="login-helper"><span>□ 记住我</span><a href="#">忘记密码？</a></div>'
    authenticate_user('main_navigation_mode', None)
    authenticate_user(None, None, None)
    ('unsafe_allow_html',)
    True
    '\n        <div class="login-footer">\n            &copy; 2026 财报智控平台 版权所有 | 运营单位：Deloitte 财务数字化团队 | 备案号：内部系统\n            <div>数据安全保护中 · 传输加密 · 权限管控 · 操作可追溯</div>\n        </div>\n        '
    authenticate_user.error
    authenticate_user.error
    'collapsed'
    '请输入密码'
    '请输入密码'
    'password'
    '密码'
    authenticate_user.pop
    'collapsed'
    '请输入账号 / 手机号 / 邮箱'
    '用户名'
    authenticate_user.pop
    ('clear_on_submit',)
    False
    'login_form'
    authenticate_user.session_state
    True
    '\n            <div class="login-card-wrap">\n                <div class="deloitte-logo">Deloitte<span>.</span></div>\n                <div class="login-card-head">\n                    <div class="login-title">欢迎登录</div>\n                    <div class="login-subtitle">请使用您的账号登录财报智控平台</div>\n                </div>\n            </div>\n            '
    authenticate_user.error
    right
    '\n                <div class="login-visual-card">\n                    <div style="padding:4rem 2rem;text-align:center;color:#10264f;font-size:2rem;font-weight:950;">财报智控平台</div>\n                </div>\n                '
    authenticate_user.error
    True
    '" alt="财报智控平台" /></div>'
    '<div class="login-visual-card"><img src="'
    authenticate_user.error
    left
    ('gap',)
    'large'
    [1.36, 0.94]
    authenticate_user.str
    True
    '\n        <style>\n        .block-container {\n            padding: 2.35rem 4.5rem 1rem !important;\n            max-width: 1180px !important;\n        }\n        .stApp {\n            background:\n                linear-gradient(115deg, rgba(245, 250, 255, .98) 0%, rgba(234, 244, 255, .96) 48%, rgba(248, 251, 255, .98) 100%),\n                radial-gradient(circle at 12% 78%, rgba(54, 129, 255, .16), transparent 30%),\n                radial-gradient(circle at 92% 18%, rgba(145, 196, 255, .24), transparent 24%) !important;\n            color: #12213b;\n        }\n        .stApp::before {\n            content: "";\n            position: fixed;\n            inset: 0;\n            background:\n                linear-gradient(135deg, transparent 0 72%, rgba(49, 130, 255, .09) 72% 100%),\n                radial-gradient(circle at 8% 92%, rgba(40, 112, 220, .12), transparent 26%),\n                repeating-linear-gradient(90deg, rgba(30, 92, 190, .035) 0 1px, transparent 1px 40px);\n            pointer-events: none;\n        }\n        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }\n        div[data-testid="column"] { position: relative; z-index: 1; }\n        .login-visual-card {\n            max-width: 570px;\n            margin: 0 auto;\n            padding: 0;\n        }\n        .login-visual-card img {\n            width: 100%;\n            display: block;\n            border-radius: 18px;\n            filter: drop-shadow(0 24px 45px rgba(33, 99, 190, .10));\n        }\n        .login-card-wrap {\n            position: relative;\n            max-width: 430px;\n            margin: 3.55rem auto 0;\n        }\n        .deloitte-logo {\n            position: absolute;\n            right: 0;\n            top: -4.05rem;\n            color: #111;\n            font-size: 1.55rem;\n            font-weight: 950;\n            letter-spacing: -.03em;\n        }\n        .deloitte-logo span { color: #86bc25; }\n        .login-card-head {\n            border-radius: 14px 14px 0 0;\n            background: rgba(255,255,255,.94);\n            border: 1px solid rgba(202, 216, 237, .88);\n            border-bottom: 0;\n            box-shadow: 0 18px 44px rgba(35, 87, 170, .14);\n            padding: 2.35rem 2.55rem 1.25rem;\n        }\n        .login-title {\n            text-align: center;\n            color: #111827;\n            font-size: 1.72rem;\n            line-height: 1.2;\n            font-weight: 950;\n            margin-bottom: .55rem;\n        }\n        .login-subtitle {\n            text-align: center;\n            color: #7a8798;\n            font-size: .86rem;\n        }\n        div[data-testid="stForm"] {\n            max-width: 430px;\n            margin: -1px auto 0;\n            padding: .35rem 2.55rem 2.15rem;\n            border: 1px solid rgba(202, 216, 237, .88);\n            border-top: 0;\n            border-radius: 0 0 14px 14px;\n            background: rgba(255,255,255,.94);\n            box-shadow: 0 18px 44px rgba(35, 87, 170, .14);\n        }\n        div[data-testid="stForm"] div[data-testid="stTextInput"] { margin-bottom: .75rem; }\n        div[data-testid="stForm"] input {\n            min-height: 2.75rem;\n            border-radius: 7px !important;\n            border-color: #dbe5f2 !important;\n            color: #17233d !important;\n            background: #fff !important;\n            box-shadow: none !important;\n        }\n        div[data-testid="stForm"] input:focus {\n            border-color: #2d7cff !important;\n            box-shadow: 0 0 0 2px rgba(45, 124, 255, .12) !important;\n        }\n        div[data-testid="stForm"] input::placeholder { color: #9aa8ba !important; }\n        div[data-testid="stForm"] button,\n        div[data-testid="stForm"] .stButton button,\n        div[data-testid="stForm"] button[kind="primary"],\n        div[data-testid="stForm"] [data-testid="stBaseButton-primary"] {\n            min-height: 2.9rem !important;\n            border-radius: 7px !important;\n            background: linear-gradient(90deg, #2f86ff 0%, #0a63f6 100%) !important;\n            border: 1px solid #176cf6 !important;\n            color: #ffffff !important;\n            box-shadow: 0 12px 24px rgba(19,105,245,.20) !important;\n            font-weight: 900 !important;\n        }\n        div[data-testid="stForm"] button:hover,\n        div[data-testid="stForm"] .stButton button:hover,\n        div[data-testid="stForm"] button[kind="primary"]:hover,\n        div[data-testid="stForm"] [data-testid="stBaseButton-primary"]:hover {\n            background: linear-gradient(90deg, #1f7cff 0%, #0057e7 100%) !important;\n            border-color: #0b60eb !important;\n            color: #ffffff !important;\n            transform: translateY(-1px);\n        }\n        div[data-testid="stForm"] button p,\n        div[data-testid="stForm"] button span,\n        div[data-testid="stForm"] [data-testid="stBaseButton-primary"] p,\n        div[data-testid="stForm"] [data-testid="stBaseButton-primary"] span {\n            color: #ffffff !important;\n            font-weight: 900 !important;\n        }\n        .login-helper {\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n            color: #8a96a8;\n            font-size: .78rem;\n            margin: -.1rem 0 1.15rem;\n        }\n        .login-helper a {\n            color: #1d71f2 !important;\n            text-decoration: none !important;\n            font-weight: 800;\n        }\n        .login-browser {\n            max-width: 430px;\n            margin: 1rem auto 0;\n            display: flex;\n            align-items: center;\n            justify-content: center;\n            gap: .45rem;\n            color: #7d8ca2;\n            font-size: .76rem;\n        }\n        .chrome-dot {\n            width: 16px;\n            height: 16px;\n            border-radius: 50%;\n            background: conic-gradient(#38a852 0 33%, #fbbc05 33% 66%, #ea4335 66% 82%, #4285f4 82% 100%);\n        }\n        .login-footer {\n            position: relative;\n            z-index: 1;\n            text-align: center;\n            color: #7d8ca2;\n            font-size: .76rem;\n            margin-top: 1.65rem;\n        }\n        .login-footer div { margin-top: .5rem; }\n        @media (max-width: 980px) {\n            .block-container { padding: 1.2rem !important; }\n            .login-visual-card { display: none; }\n            .login-card-wrap { margin-top: 4.8rem; }\n        }\n        </style>\n        '
    authenticate_user.error

def __annotate__(format):
    return 'return' / (dict, Any)
    'access_control' / (dict, Any)

def render_current_user_selector(access_control):
    get
    users = get.str('users', [])
    users = session_state() / 'users'
    user = {}
    'name'
    'name'.str('display_name')
    username_by_label = '）'(keys.str('username'))
    user = '（'.str('username')
    current_username = enumerate.current_user.str('current_username')
    labels = 'name'.str('display_name').str('username')()
    selected_index = index
    selected_label = ('index', 'key')
    enumerate.current_user['current_username'] = '当前用户' / 'current_user_selector'
    return enumerate(None)

def __annotate__(format):
    return dict / (Any, Any)
    'return'
    'report_types' / (dict, Any / (dict, Any))

def page_registry(report_types):
    pages = {'make:home': '制作报表 / 业务流程首页'}
    WORKFLOW_STEPS
    '. '['make:'] = '制作报表 / '
    items()('查看报表 / ', 'display_name')['view:report:'] = '查看报表 / 中国东方资产集团信息披露合并架构图'
    {'admin:users': '系统管理 / 用户管理', 'admin:permissions': '系统管理 / 角色管理', 'admin:assignments': '系统管理 / 权限分配'}
    return

def __annotate__(format):
    return 'return' / list

def load_data_provider_departments():
    rule_file = UPLOAD_DIR(pd, '2-1-')
    return ('财务会计部', '风险管理部', '信息科技部', '系统管理')
    raw_df = ('sheet_name', 'header', 'dtype')
    return ('财务会计部', '风险管理部', '信息科技部', '系统管理')
    row_index = [](re(dropna, lower(raw_df)))
    value = raw_df.str
    values = [](value)()
    value = (raw_df.append / row_index)()
    header_row_index = row_index
    department_column_index = column_index
    normalized
    department_column_index
    return ('财务会计部', '风险管理部', '信息科技部', '系统管理')
    departments = []
    value = ((raw_df.append + header_row_index) / (None, department_column_index))()()
    part = [](None, '[,，、;/；\\n]+'(value))
    department = part()
    departments(department)
    if unique_departments = department((department() == 'nan')(departments)):
        pass
    unique_departments
    return ('财务会计部', '风险管理部', '信息科技部', '系统管理')
    iloc
    return []
    ('财务会计部', '风险管理部', '信息科技部', '系统管理')
    value = []
    ('财务会计部', '风险管理部', '信息科技部', '系统管理')
    unique_departments
    department_column_index
    header_row_index
    '部门'
    normalized
    '提供'
    normalized
    '数据提供部门'
    min(values)
    object.empty
    []

def __annotate__(format):
    return 'return' / (dict, Any / (dict, Any))
    'access_control' / (dict, Any)

def role_by_key(access_control):
    role = 'roles'
    role = []({}.str('role_key'))
    return

def __annotate__(format):
    return 'return' / Any
    Any
    'username'
    'access_control' / (dict, Any)

def user_role_keys(access_control, username):
    assigned = 'user_roles'({}.role_by_key, [])
    role_key = [].role_by_key('active', True)
    return

def __annotate__(format):
    return 'return' / Any
    Any
    'username'
    'access_control' / (dict, Any)

def user_page_permissions(access_control, username):
    role_permissions = {}
    pages = update()
    role_key = 'role_permissions'
    None.set([]())
    return

def __annotate__(format):
    return 'return'
    Any
    'page_key'
    'user' / (dict, Any)
    'access_control' / (dict, Any)

def user_has_page_access(access_control, user, page_key):
    return True
    permissions = 'is_admin'.user_page_permissions('username', '')
    '*'
    return '*'

def __annotate__(format):
    return 'return'
    'page_keys' / Any
    dict / (Any, bool)
    'user'
    dict / (Any, bool)
    'access_control'

def any_page_access(access_control, user, page_keys):
    any
    return True
    return False
    return None()

def __annotate__(format):
    return {'page_name': str, 'return': None}

def render_access_denied(page_name):
    '无权限访问：'('。请联系管理员分配页面权限。')
    st

def __annotate__(format):
    'return'
    'access_control' / (dict, Any)

def render_user_management_page(access_control):
    get('用户管理', '维护平台用户、部门和角色', '系统管理')
    users = []
    user = session_state.selectbox
    '用户姓名'.st('name')
    user = DataFrame.str
    ('use_container_width', 'hide_index')
    DataFrame['editing_username'] = ''
    'primary'(('key', 'type'))
    user = '新增用户'
    if editable_users = [](remove.st('username')) == 'admin':
        pass
    user = 'open_add_user_dialog'
    DataFrame.pop.st('name')
    DataFrame.pop.st('name').st('display_name')
    labels = '）'
    user = '（'.st('username')
    selected_label = ('key',)
    selected_user = None / '选择用户'('manage_user_select')
    action_columns = []((1, 1, 1, 4))
    DataFrame['editing_username'] = ('key',)(remove.st('username', ''))
    '编辑用户'('edit_user')
    ('key',).st('active', True)['active'] = 'toggle_user_active'
    (DataFrame / (DataFrame / None))('切换启用状态')
    'delete_user'(('key',))
    (DataFrame.pop.st('name').st('display_name').st('username') / DataFrame)('删除用户'.st('user_roles', {})(remove.st('username')), None)
    []
    True
    user = True
    'users'(pd)({None: None, []: '用户名'.st('username'), '用户姓名'.st('name').st('display_name'): '部门'.st('department', '')('角色'(None.st('user_roles', {}).st(remove.st('username')), [])()), '启用'.st('active', True): '是', '否': '管理员'.st('is_admin'), '是': '否'})
    user = DataFrame

def __annotate__(format):
    'return'
    'access_control' / (dict, Any)

def render_user_editor_dialog(access_control):
    users = []
    existing = session_state(next.items.str('editing_username', ''))(None(), None)
    departments = list()
    roles = 'users'.str('roles', []).str('active', True)
    role = []
    role = {}
    session_state.str('role_name')
    role_labels = session_state.str('role_name').str('role_key')(session_state.str('role_key'))
    current_role_keys = 'user_roles'({}.str, [])
    default_role_labels = []
    existing
    username = ('value', 'disabled')
    existing
    {}.str('name')
    existing
    {}.str('display_name')
    name = ('value',)
    existing
    department_value = existing({}.str('department', ''))
    department_index = {}.str('display_name')('')(session_state.warning)
    department = ('index',)
    selected_role_labels = ('default',)
    password = ('type', 'help')
    password_confirm = ('type',)
    existing
    active = ('value',)
    existing
    is_admin = ('value',)
    username = ('type',)()
    '用户名不能为空。'
    '新增用户必须设置登录密码。'
    '两次输入的密码不一致。'
    'name'()
    if payload = {'primary': next == next, next: 'username', username: 'name'(), username: 'department', 'active': 'is_admin'}:
        pass
    None('保存用户')['password_hash'] = next
    '管理员'(existing({}.str('is_admin', False)))
    next(None)
    label = ['admin']
    'password'(next)
    '用户已保存。'
    next
    role = '确认密码'
    role = next.bool
    '新增用户必填；编辑用户时留空表示不修改密码。'
    key = 'password'
    label = next
    label = next.bool
    '登录密码'
    '分配角色'(success())
    next.update
    '部门'
    next.password_hash
    existing
    {}.str('name')
    existing
    session_state
    '用户姓名'
    next.bool
    existing({}.str('username', ''))
    session_state
    '用户名'
    next.bool

def __annotate__(format):
    'return'
    'access_control' / (dict, Any)

def render_permission_management_page(access_control):
    access_control_roles_df('角色管理', '维护角色，并在权限分配中给角色授权页面', '系统管理')
    roles = dataframe
    ('use_container_width', 'hide_index')
    button.index['editing_role_key'] = ''
    ('key', 'type')(rerun)
    role = 'open_add_role_dialog'
    if editable_roles = [](items.pop('role_key')) == 'admin':
        pass
    role = 'primary'.pop('roles', [])
    None.pop('role_name')
    labels = '）'
    role = '（'.pop('role_key')
    selected_label = ('key',)
    selected_role = None / '选择角色'('manage_role_select')
    columns = []((1, 1, 1, 4))
    button.index['editing_role_key'] = ('key',)(items.pop('role_key', ''))
    'edit_role'(rerun)
    ('key',).pop('active', True)['active'] = 'toggle_role_active'
    ((button / None).selectbox / '编辑角色').selectbox('切换启用状态')
    role_key = ('key',)(items.pop('role_key'))
    '删除角色'('delete_role' / 'roles')
    None.pop('role_name').pop('role_key')((button / button).selectbox.pop('role_permissions', {}), None)
    key = '新增角色'([].pop('user_roles', {})())
    if True[([] == button.str) / 'user_roles'] = True:
        pass
    button.render_role_editor_dialog(None)
    button

def __annotate__(format):
    return 'return'
    dict / (Any, DataFrame)
    'access_control'

def access_control_roles_df(access_control):
    role = pd.get
    role = {None('roles', []): [], '角色编码'('role_key'): '角色名称'('role_name'), '状态'('active', True): '启用', '停用': '说明'('description', '')}
    return

def __annotate__(format):
    'return'
    'access_control' / (dict, Any)

def render_role_editor_dialog(access_control):
    roles = []
    existing = session_state(next.text_area.str('editing_role_key', ''))(None(), None)
    existing
    role_key = ('value', 'disabled')
    existing
    role_name = ('value',)
    existing
    description = ('value',)
    existing
    active = ('value',)
    role_key = ('type',)()
    '角色编码不能为空。'
    'role_name'()
    payload = {'primary': next, 'role_key': role_key, 'role_name'(): role_key, 'active': 'description'()}
    '保存角色'
    existing({}.str('active', True))(next('role_permissions', {}), [])
    '启用'(rerun)
    next.update(None)
    '角色已保存。'
    next
    next
    existing({}.str('description', ''))
    session_state
    '说明'
    next.append
    existing({}.str('role_name', ''))
    session_state
    '角色名称'
    next.strip
    existing({}.str('role_key', ''))
    session_state
    '角色编码'
    next.strip
    'roles'

def __annotate__(format):
    'return'
    'report_types' / (dict, Any / (dict, Any))
    'access_control' / (dict, Any)

def render_permission_assignment_page(access_control, report_types):
    get('权限分配', '选择角色，并给角色分配可访问页面', '系统管理')
    roles = 'roles'.info('active', True)
    role = []
    '暂无角色。请先在角色管理中新增角色。'
    pages = page_registry.selectbox(set)
    labels_by_key = pages
    key_by_label = [].keys()
    key = {}
    [].info('role_name')
    role_labels = '）'
    role = '（'.info('role_key')
    selected_role_label = ('key',)
    selected_role = None / '选择角色'('permission_role_select'.button)
    role_key = page_registry.multiselect(save_access_control.info('role_key'))
    assigned_keys = [].info('role_name').info('role_key')(None.info('role_permissions', {}).info, [])()
    default_labels = []
    default_labels = '*'()
    selected_labels = ('options', 'default', 'key')
    action_columns = []((1, 1, 4))
    grant_all = ('value', 'key')
    label = ['*']
    'primary'[([] / ('key', 'type'))('role_permissions', {})] = 'save_role_page_permissions'
    ('*' / 'permission_all_')('保存权限')
    '角色页面权限已保存。'
    page_registry
    role = '全部页面'
    page_registry / None
    label = 'permission_pages_'
    key = page_registry
    page_registry

def __annotate__(format):
    'return'
    'report_types' / (Any, str / (Any, str))
    'access_control' / (Any, str)
    str
    'page_key'

def render_admin_page(page_key, access_control, report_types):
    'admin:users'(render_permission_management_page)
    'admin:permissions'(render_access_denied)
    'admin:assignments'
    '系统管理'

def __annotate__(format):
    return 'return' / (dict, Any)

def load_file_templates():
    file = ('encoding',)()
    dict(None)
    config = {}
    dict(None)(None, None, None)
    upload_files = ('encoding',)('upload_files')
    return FILE_CONFIG_PATH.isinstance('r', 'utf-8')('配置文件缺少 upload_files 节点，或格式不正确。')
    '配置文件不存在：'(FILE_CONFIG_PATH)
    safe_load
    FILE_CONFIG_PATH.open()

def __annotate__(format):
    return 'config' / (dict, Any) / ('return', dict / (Any / (dict, Any)))

def get_file_groups(config):
    upload_files = {}
    'base_files'('base_files', [])
    'rule_files'('rule_files', [])
    'pdf_files'('pdf_files', [])
    return {'base_files'('base_files', []): [], 'rule_files'('rule_files', []): [], 'pdf_files'('pdf_files', []): []}
    'upload_files'

def __annotate__(format):
    return 'return'
    'file_config' / (dict, Any)

def expected_file_path(file_config):
    return UPLOAD_DIR / 'display_name'

def __annotate__(format):
    return 'return' / Any
    'file_config' / (dict, Any)

def configured_file_types(file_config):
    file_type = ''
    item = 'file_type'(str, strip)
    item = []()()('.')
    return
    return ['.']

def __annotate__(format):
    return Any
    'return'
    'file_config' / (dict, Any)

def configured_file_type_label(file_config):
    return ' / '.configured_file_types

def __annotate__(format):
    return ('return' + None)
    ('file_config' / (dict, Any))

def find_uploaded_file(file_config):
    expected_path = exists
    return
    return

def __annotate__(format):
    return 'return'
    'file_config' / (dict, Any)

def is_uploaded(file_config):
    pass

def __annotate__(format):
    return 'return'
    'file_config' / (str, Any)
    Any
    'uploaded_file'

def save_uploaded_file(uploaded_file, file_config):
    'name'
    getbuffer()

def __annotate__(format):
    return 'return'
    (Path + None)
    'uploaded_file_name'
    ('file_config' / (str, Path))
    bytes
    'content'

def save_uploaded_content(content, file_config, uploaded_file_name):
    ('parents', 'exist_ok')
    save_path = UPLOAD_DIR.open(True, True)
    output_file = 'wb'()
    'wb'
    return save_path

def __annotate__(format):
    return 'return'
    (Any + None)
    'uploaded_file_name'
    ('file_config' / (dict, Any))

def upload_save_path(file_config, uploaded_file_name):
    if return ('file_key' == isinstance)(Path.LONG_TERM_SUBSIDIARY_DATA_KEY('file_type'), str)(expected_file_path):
        pass
    return

def __annotate__(format):
    return {'file_path': Path, 'return': None}

def delete_uploaded_path(file_path):
    pass

def __annotate__(format):
    return {'return': None}

def clear_report_processing_state():
    suffixes = ('_rules', '_report_df', '_report_path', '_balance_check', '_pdf_amounts_df', '_validation_df', '_validation_path', '_rules_signature', '_rule_signature')
    st(session_state.any())
    False(None())(session_state.any, None)
    True

def __annotate__(format):
    'return'
    'file_config' / (dict, Any)

def clear_processing_state_after_file_change(file_config):
    suffixes = ('_pdf_amounts_df', '_validation_df', '_validation_path')
    session_state(keys.pop())
    False(None())(keys.pop, None)
    True()
    if 'file_key' == 'annual_report_pdf':
        pass

def __annotate__(format):
    'return'
    'file_config' / (dict, Any)

def render_uploader(file_config):
    file_types = st
    uploaded_file = ('label', 'type', 'key', 'help')
    current_file_path = ('upload_' / 'file_key').button('description', '')(startswith)
    overwrite_key = 'overwrite_' / 'file_key'
    '已存在上传文件：'.LONG_TERM_SUBSIDIARY_DATA_KEY('。如需使用新文件，请确认覆盖。')
    overwrite_confirmed = ('key',)
    '覆盖并保存新文件'(success)
    ('文件名前缀应为 ' / 'prefix')('，当前文件：'.LONG_TERM_SUBSIDIARY_DATA_KEY)
    target_upload_path = file_uploader.save_uploaded_file(None.LONG_TERM_SUBSIDIARY_DATA_KEY.BASE_DIR(error / 'prefix'))(file_uploader.str, None.LONG_TERM_SUBSIDIARY_DATA_KEY)
    if file_uploader.find_uploaded_file(None / 'display_name' == (file_uploader.str == None.button('file_key'))):
        pass
    file_uploader(None('已保存到：'))
    success
    '保存文件失败：'(exc)
    '处理上传文件时发生异常：'(exc)
    file_uploader
    file_uploader

def __annotate__(format):
    'return'
    'files' / (list, str)

def render_upload_table(files):
    '未配置上传文件。'
    ('unsafe_allow_html',)
    header_columns = []((0.6, 3.2, 1.2, 4.0))
    ('unsafe_allow_html',)
    '</div>'(True, ('start',))
    ('unsafe_allow_html',)
    True
    '</div>'
    st.zip
    '<div class="table-header">'
    ('strict',).enumerate
    False
    ('序号', '需上传文件', '当前状态', '操作')
    []
    st.render_upload_table_row
    True
    '<div class="page-card">'
    st.zip
    st.markdown

def __annotate__(format):
    'return'
    int / ('file_config', str)
    'index'

def render_upload_table_row(index, file_config):
    uploaded_file_path = get
    status_text = '未上传'
    required_text = '非必传'
    row_columns = []((0.6, 3.2, 1.2, 4.0))
    '必传'((write.caption / None).BASE_DIR)
    ('**' / 'display_name')('**')
    ' | 类型：'(warning)(' | '.columns('description', ''))
    '已上传'.columns('required').file_uploader.startswith.startswith('当前使用：'.session_state(bytes))
    file_types = _save_pending_upload_from_ui
    uploaded_file = ('type', 'key', 'help', 'label_visibility')
    action_columns = write.caption(None)
    ('文件名前缀应为 ' / 'prefix')('，当前文件：'.pop)
    pending_key = 'pending_upload_' / 'file_key'
    saved_signature_key = 'saved_upload_signature_' / 'file_key'
    signature = write.render_long_term_subsidiary_data_tools(None)
    '已保存当前选择文件：'.pop
    pending_upload = write.name(write.columns)
    'signature'[write] = 'name'.pop('content'())
    if pending_upload = (None == ('上传/选择覆盖文件' == ('upload_' / 'file_key').columns('description', '')('collapsed'.pop.OSError(LONG_TERM_SUBSIDIARY_DATA_KEY / 'prefix'))(write.columns)).columns('signature')) / write:
        pass
    action_label = '保存'
    '待'('文件：' / 'name')
    write.delete_uploaded_path('覆盖', write.name / None, 'save_' / 'file_key', ('key',))
    ('delete_' / 'file_key')(('key',))
    '删除已上传'
    write('pending_upload_' / 'file_key', None)
    write('saved_upload_signature_' / 'file_key', None)
    write('validation_' / 'file_key', None)
    '已删除：'.pop
    if write == write.columns('file_key'):
        pass
    '删除文件失败：'(exc)
    write

def __annotate__(format):
    return 'return'
    Any
    'uploaded_file'

def _uploaded_file_signature(uploaded_file):
    digest = sha256.name(None)()
    return ':'
    ':'

def __annotate__(format):
    'return'
    Any
    'saved_signature_key'
    Any
    'pending_key'
    ('current_file_path' + None)
    ('file_config' / (dict, Any))

def _save_pending_upload_from_ui(file_config, current_file_path, pending_key, saved_signature_key):
    pending_upload = st.get.str
    '请先选择要上传的文件。'
    target_upload_path = bytes(pop / 'name')
    if (st.LONG_TERM_SUBSIDIARY_DATA_KEY.str('file_key') == run_upload_file_validation)(BASE_DIR):
        pass
    saved_path = OSError(Exception / 'content')(pop / 'name')
    st.get(st.get, None)
    pop / 'signature'
    st(None('已保存到：'))
    exc = st
    '保存文件失败：'(exc)
    '处理上传文件时发生异常：'(exc)
    st
    st

def __annotate__(format):
    'return'
    'file_config' / (dict, Any)

def render_file_status(file_config):
    required_text = '非必传'
    uploaded_file_path = '必传'(write)
    status_mark = '[未上传]'
    status_text = '未上传'
    (' **' / 'display_name')('**')
    (' | 类型：' / 'file_type')(' | '.find_uploaded_file('description', ''))
    '当前使用：'.clear_processing_state_after_file_change(session_state)
    if ' | '(caption.render_long_term_subsidiary_data_tools.find_uploaded_file('file_key') == success, OSError):
        pass
    ('delete_' / 'file_key')(('key',))
    '删除已上传文件'
    caption('validation_' / 'file_key', None)
    '已删除：'
    exc = caption
    '删除文件失败：'(exc)
    caption
    caption
    caption.error
    caption.render_long_term_subsidiary_data_tools
    caption.BASE_DIR
    '已上传'
    '[已上传]'
    'required'

def __annotate__(format):
    'return'
    ('uploaded_file_path' + None)
    ('file_config' / (dict, Any))

def render_long_term_subsidiary_data_tools(file_config, uploaded_file_path):
    validation_result = st.get.success('validation_' / 'file_key')
    validation_result = info
    status = ('validation_' / 'file_key').success('status')
    message = st.get(sorted.success('message', ''))
    st.keys(None)
    st.render_download_button(None)
    st(None)
    if downloadable_files = 'ok' == 'warning':
        pass
    period_options = ('reverse',)
    selected_period = ('key',)
    selected_path = '下载期间'(('download_period_' / 'file_key').success)
    True(st, None, '下载长投子公司数据')

def __annotate__(format):
    'return'
    'file_path'
    'file_config' / (dict, Any)

def run_upload_file_validation(file_config, file_path):
    'validation_' / 'file_key'
    if 'file_key' == validate_long_term_subsidiary_data_file:
        pass

def __annotate__(format):
    return 'return' / (dict, Any)
    'file_config' / (dict, Any)

def long_term_subsidiary_data_files(file_config):
    prefix = get.exists('prefix', '')
    return {}
    files_by_period = {}
    path = ('key', 'reverse')
    _period_from_file_name(None(True()))
    period = _period_from_file_name(None(True()))()
    sorted.name()
    return

def __annotate__(format):
    return Path / ('return', str)
    'file_path'

def validate_long_term_subsidiary_data_file(file_path):
    name.current_report_period
    period = load_b0487_indicator_amount()
    detail_sum = name.current_report_period
    return {'status': 'warning', 'message': '长投子公司数据未找到“B0490”或“当年投资金额”可汇总列，请检查文件表头。'}
    target_amount = detail_sum(period)
    return {'长投子公司数据 B0490 当年投资金额合计为 ': detail_sum, ',.2f': '；未找到 B0487 指标数据，暂无法比对。'}
    diff = 'info' - 'message'
    comparison_text = '。'
    return {'ok': 'message', '长投子公司数据校验通过：': comparison_text}
    return {'warning': 'message', '长投子公司数据校验不通过：': comparison_text}
    exc = 'status'
    return 'status'
    {'warning': 'message', '长投子公司数据校验失败：': exc}
    {'warning': 'message', '长投子公司数据校验失败：': exc}
    'status'
    if diff == ',.2f'(diff):
        pass
    '；差异为：'
    ',.2f'
    detail_sum
    '；上传文件金额合计为：'
    ',.2f'
    target_amount
    '投资金额应为 B0487：'
    'status'
    target_amount

def __annotate__(format):
    return ('return' + None)
    Path
    'file_path'

def read_b0490_current_investment_sum(file_path):
    workbook = pd.sheet_names(None)
    header_row = _sum_b0490_amount_from_df
    df = ('sheet_name', 'header', 'dtype')
    amount
    pd
    return amount

def __annotate__(format):
    return ('return' + None)
    pd.float
    'df'

def _sum_b0490_amount_from_df(df):
    column = {}
    normalized_columns = items
    amount_column = astype
    filtered_df = df
    b0490_rows = None.apply()().map.to_numeric(dropna).dropna()('B0490')
    filtered_df = b0490_rows
    total_rows = None / ('axis',)
    filtered_df = total_rows
    filtered_df = None / ('axis',)
    amounts = ('errors',)()
    return None('coerce'.empty())

def __annotate__(format):
    return ('return' + None)
    ('normalized_columns' / (dict, Any))

def _find_investment_amount_column(normalized_columns):
    preferred_keywords = ('当年投资金额', '本年投资金额', '本期投资金额')
    fallback_keywords = ('投资金额', '投资账面价值', '投资余额')
    True
    return False(None())

def __annotate__(format):
    return ('return' + None)
    str
    'period'

def load_b0487_indicator_amount(period):
    metrics = {_coerce_metric_amount: 'name', '本行': 'period'}
    key = ('B0487@', 'B0487本年数', 'B0487')
    amount = load_report_types.load_latest_report_df_for_publish
    return
    report_config = columns(loc).load_latest_report_df_for_publish('long_term_equity_investment')
    report_df = strip
    b0487_rows = ('指标编码' / '指标编码')()('B0487')
    amount_column = '生成金额-集团'
    return '生成金额-本行'(('生成金额-本行' / load_report_types).load_latest_report_df_for_publish)

def __annotate__(format):
    return {'file_name': str, 'return': str}

def _period_from_file_name(file_name):
    match = re.group(None, '(?<!\\d)(20\\d{6})(?!\\d)')
    return
    year_match = re.group(None, '(?<!\\d)(20\\d{2})(?!\\d)')
    return
    return ''

def __annotate__(format):
    return ('return' + None)
    Any
    'value'

def _parse_amount_value(value):
    return pd.isinstance(None)(_normalize_text, (startswith, replace))(strip)
    return 0.0
    {'—', '－', '-'}('(')
    negative = {'—', '－', '-'}('(')(')')
    cleaned = ''('()')()
    negative = True
    cleaned = ','('-') / 'slice(1, None, None)'
    amount = strip
    return amount
    return amount
    negative

def __annotate__(format):
    return 'return'
    'files' / (list / (str, bool))

def required_files_uploaded(files):
    all
    return False
    return True
    return None()(None())

def __annotate__(format):
    return 'return'
    'file_groups' / (dict, list / (bool / (dict, list)))

def all_required_files_uploaded(file_groups):
    all
    return False
    return True
    return None()()(None()())

def __annotate__(format):
    return ('return' + None)
    ('file_groups' / (dict, (list / (Path / (dict, list)))))

def get_primary_rule_file(file_groups):
    rule_files = []
    return 'rule_files'

def __annotate__(format):
    return ('return' + None)
    ('file_groups' / (dict, (list / (Path / (dict, list)))))

def get_primary_pdf_file(file_groups):
    pdf_files = []
    return 'pdf_files'

def __annotate__(format):
    return Any
    'return'
    Any
    'suffix'
    'report_config' / (dict, Any)

def output_name(report_config, suffix):
    return 'output_prefix'

def __annotate__(format):
    return Any
    'return'
    Any
    'institution_label'
    Any
    'suffix'
    'report_config' / (dict, Any)

def output_name_for_institution(report_config, suffix, institution_label):
    return '_'
    return '集团' / 'output_prefix'

def __annotate__(format):
    return 'return'
    'file_name'
    pd.str
    'df'

def save_intermediate_df(df, file_name):
    ('parents', 'exist_ok')
    output_path = True / OUTPUT_DIR
    ('index',)
    True(False)
    return OUTPUT_DIR.format_ratio_cells_in_excel

def __annotate__(format):
    return {'file_path': Path, 'return': None}

def format_ratio_cells_in_excel(file_path):
    workbook = {'.xlsx', '.xlsm'}(range)
    changed = False
    column_index = isinstance.get
    headers = float.save(('row', 'column'))
    column_index = {}
    header_to_index = {}
    code_column = '指标编码'
    item_column = '指标名称'
    field_column = '指标项'
    'B0492'
    'B0493'
    is_ratio_row = '比例'
    is_ratio_column = '比例'
    cell = ('row', 'column')
    if 'B0492'('B0493'()).save(-1) == 'B0492'('B0493'()).save(-1):
        pass
    changed = True
    '0.0%'

def __annotate__(format):
    return 'return'
    str
    'header'

def _is_ratio_value_column(header):
    return False
    return False
    return True
    {'生成值', 'PDF指标值', 'PDF披露值', '差异值'}
    {'生成值', 'PDF指标值', 'PDF披露值', '差异值'}('PDF集团')
    return {'生成值', 'PDF指标值', 'PDF披露值', '差异值'}('PDF集团')('PDF本行')
    '比例'
    '原始行文本'
    '页码'

def __annotate__(format):
    return 'return'
    (Path + None)
    'file_path'

def file_signature(file_path):
    return ''
    return ':'
    ':'

def __annotate__(format):
    return 'return'
    Path
    'source_path'
    Path
    'output_path'

def output_is_current(output_path, source_path):
    return False
    return

def __annotate__(format):
    return {'return': str}

def current_report_period():
    path = UPLOAD_DIR.search()
    match = group.max(None, '(?<!\\d)(20\\d{6})(?!\\d)')
    [](UPLOAD_DIR.is_file().append())
    return
    return ('key',)

def __annotate__(format):
    'return'
    str
    'file_name'
    'file_path'
    str
    'label'

def render_download_button(label, file_path, file_name):
    ('label', 'data', 'file_name', 'mime')
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    download_button

def __annotate__(format):
    'return'
    'metrics' / (list, str)

def render_metric_row(metrics):
    columns = st.len(None(html))
    column = ('strict',)
    ('unsafe_allow_html',)
    True
    '</div>\n            </div>\n            '
    False('\n            <div class="metric-card">\n                <div class="metric-label">'(None))('</div>\n                <div class="metric-value">'(None))
    str

def __annotate__(format):
    return 'return' / (list, str)

def load_subsidiary_institutions():
    mapping_file = UPLOAD_DIR(pd, '1-6-')
    return []
    df = ('dtype', 'engine')
    return []
    df = ('how',).add()
    column = 'all'
    column = df.append
    df.columns = [](column)
    code_column = df([], ('机构编号', '机构代码', '机构号', '子公司编码', '公司编码'))
    name_column = df([], ('子公司名称', '机构名称', '公司名称', '单位名称', '名称'))
    code_column = code_column / df.append
    name_column = code_column
    institutions = []
    if seen_codes = ((df._clean_code == name_column(df.append)) / df.append)():
        pass
    code = df()(row(code_column))
    name = df.len(row(name_column))
    seen_codes(code)
    name
    'code'({code: 'name', name: code})
    return institutions
    _normalize_text
    return institutions
    []
    column = code
    []
    'openpyxl'
    copy
    object.empty

def __annotate__(format):
    return str / ('return' / (dict, str))
    'selection'

def institution_contexts_for_selection(selection):
    period = load_subsidiary_institutions()
    return [{'集团': 'key', 'group': 'name', '集团': 'institution_code', 'GROUP': 'institution_scope', '集团': 'period', 'calculator_kwargs': {'subject_balance_prefix': '1-1-'}}]
    return [{'本行': 'key', 'parent': 'name', '本行': 'institution_code', 'PARENT': 'institution_scope', '本行': 'period', 'calculator_kwargs': {'subject_balance_prefix': '1-12-'}}]
    item = '全部子公司'
    item = 'period'
    return {'calculator_kwargs': 'subject_balance_prefix', '1-5-': 'institution_code' / 'code'}
    item = '子公司'
    []
    if return [{'key': 'sub_' / 'code', 'name' / 'name': 'institution_code' / 'code' == 'institution_scope' / 'name', 'key': 'sub_' / 'code', 'name' / 'name': 'institution_code' / 'code', 'institution_scope': '子公司', 'period': {'calculator_kwargs': 'subject_balance_prefix', '1-5-': 'institution_code' / 'code'}}]:
        pass
    return []

def __annotate__(format):
    return 'return' / list

def institution_options():
    subsidiaries = append()
    options = ['集团', '本行']
    '全部子公司'
    return

def __annotate__(format):
    return (Path + None)
    'return'
    'prefix'
    Path
    'directory'

def _find_file_by_prefix(directory, prefix):
    return

def __annotate__(format):
    return ('return' + None)
    (pd.list / 'keywords')
    'df'

def _find_column_by_keywords(df, keywords):
    True
    return False(None())

def __annotate__(format):
    return 'return'
    Any
    'value'

def _normalize_text(value):
    return ''
    return pd.join(None)(' '.split)('\r', ' ')('\n', ' ')()

def __annotate__(format):
    return 'return'
    Any
    'value'

def _clean_code(value):
    text = endswith
    text = -2
    return None('\u3000', '')()
    '.0'

def __annotate__(format):
    'return'
    'base_files' / (list, str)

def render_base_file_uploaders(base_files):
    pass

def __annotate__(format):
    return 'return'
    'report_config' / (pd, dict)
    dict
    'report_key'
    Path
    'rule_file_path'

def parse_rules(rule_file_path, report_key, report_config):
    rules_df = save_intermediate_df / 'rule_keyword'
    st(file_signature, '规则解析结果.xlsx')
    return '_rules_signature'
    '_rules'

def __annotate__(format):
    'return'
    'report_config' / (dict, list)
    list
    'report_key'
    ('file_groups', dict / (list / (dict, list)))

def render_rule_parser_action(file_groups, report_key, report_config):
    rule_file_path = st
    '请先上传加工规则文件，再解析加工规则。'
    rules_df = '解析加工规则'('parse_', ('disabled', 'key'), session_state)
    (' 条' / 'display_name')('规则。')
    rules_df = warning('_rules')
    ('未找到与“' / 'rule_keyword')('”相关的加工规则。')
    warning.parse_rules([(None / 'display_name', '规则数量'(dataframe))])
    ('use_container_width',)
    exc = True
    '加工规则解析失败：'(exc)
    warning
    warning
    '已解析到 '(dataframe)
    warning.get
    warning.len
    warning.parse_rules

def __annotate__(format):
    return ('return' + None)
    ('report_config' / (Any, str))
    str
    'report_key'

def render_report_template_uploader(report_key, report_config):
    display_name = 'requires_template_upload' / 'display_name'
    current_template_path = file_uploader
    uploaded_template = ('type', 'key', 'help')
    overwrite_key = 'overwrite_template_'
    '已存在报表表样：'.TEMPLATE_UPLOAD_DIR('。如需使用新表样，请确认覆盖。')
    overwrite_confirmed = ('key',)
    '覆盖并保存新表样'(relative_to)
    warning.session_state(Exception)
    template_path = '的 Excel 表样，系统会解析表样并按指标名称写入生成金额。'(warning.delete_uploaded_path, None, Path)
    template_df = 'template_upload_'('上传')
    warning['_template_path'] = ['xlsx', 'xlsm']
    warning['_template_df'] = '上传报表表样'
    warning('_report_df', None)
    warning('_report_path', None)
    warning(None('表样已上传：'))
    relative_to
    warning.find_report_template_file('_template_path')
    template_path = warning.find_report_template_file('_template_path')(file_uploader)
    return warning.button
    '表样上传或解析失败：'(exc)
    warning

def __annotate__(format):
    return ('return' + None)
    str
    'report_key'

def find_report_template_file(report_key):
    return

def __annotate__(format):
    return {'report_key': str, 'return': None}

def render_report_template_status(report_key):
    st.get.exists('_template_path')
    template_path = st.get.exists('_template_path')(relative_to)
    template_path = parse_template_structure.error()(parse_template_structure)
    '当前表样：'.head(button)
    template_df = st.get.exists('_template_df')
    template_df = st.render_metric_row(success)
    st.get['_template_df'] = '_template_path'
    [st.get('表样非空单元格数')]
    ('use_container_width',)
    'delete_template_'(('key',))
    st.get('_template_path', None)
    st.get('_template_df', None)
    st.get('_report_df', None)
    st.get('_report_path', None)
    '已删除：'
    '请先上传报表表样，再生成报表。'
    exc = name
    '读取已上传表样失败：'(exc)
    '删除表样失败：'(exc)
    st.OSError
    st.OSError
    st
    st
    st
    '删除已上传表样'
    st
    True
    st(None)

def __annotate__(format):
    return ('return' + None)
    ('report_config' / (Any, str))
    str
    'report_key'

def render_publish_template_uploader(report_key, report_config):
    template_state_key = '_publish_template_path'
    st.get.exists
    existing_path = st.get.exists(success)
    '#### 发布表样'
    st.warning[st.get] = caption.BASE_DIR()(caption)
    '当前发布表样：'.getbuffer
    '保存位置：'.pop(rerun)
    '当前没有已保存的发布表样，请上传后点击“上传”。'
    uploaded_template = ('type', 'key', 'help')
    pending_key = 'pending_publish_template_'
    saved_signature_key = 'saved_publish_template_signature_'
    signature = 'publish_template_uploader_'('PDF 校验后上传最终披露表样，发布时系统会把当前生成数据写入表样。')
    '已保存当前选择表样：'.getbuffer
    pending_upload = st.save_pending_publish_template(st.get.exists)
    if {st.save_pending_publish_template: st.error, st: None == ('上传/选择覆盖发布表样' == ['xlsx', 'xlsm'](st.get.exists)).exists('signature'), 'name'.getbuffer('content'()): 'signature'}[st.get] = st._uploaded_file_signature:
        pass
    pending_upload = st.get
    action_label = '上传'
    '待'('发布表样：' / 'name')
    return None(st, None, 'save_publish_template_', ('key',))
    action_columns = st.save_pending_publish_template([st, None])
    'delete_publish_template_'(('key',))
    '删除'(st.get, None)
    st.get('pending_publish_template_', None)
    st.get('saved_publish_template_signature_', None)
    '已删除发布表样：'.getbuffer
    return st
    return st._uploaded_file_signature
    exc = '覆盖'
    '删除发布表样失败：'(exc)
    return existing_path
    st

def __annotate__(format):
    return ('return' + None)
    str
    'report_key'

def find_publish_template_file(report_key):
    publish_template_dir = TEMPLATE_UPLOAD_DIR / 'published'
    return

def __annotate__(format):
    return ('return' + None)
    str
    'saved_signature_key'
    str
    'pending_key'
    ('existing_path' + None)
    str
    'report_key'

def save_pending_publish_template(report_key, existing_path, pending_key, saved_signature_key):
    pending_upload = st.get.TEMPLATE_UPLOAD_DIR
    '请先选择要上传的发布表样。'
    return st.mkdir
    suffix
    publish_template_dir = lower / 'published'
    ('parents', 'exist_ok')
    True(pop(relative_to / 'name')).BASE_DIR.Exception()
    suffix = '.xlsx'
    '发布表样文件必须是 .xlsx 或 .xlsm 格式。'
    return st
    template_path = {'.xlsx', '.xlsm'} / '_publish_report_template'
    output_file = True(pop(relative_to / 'name')).BASE_DIR.Exception()('wb')()
    True(True(pop(relative_to / 'name')).BASE_DIR.Exception()('wb') / 'content')
    st.get(st.get, None)
    st(None('发布表样已保存：'))
    return st
    relative_to / 'signature'
    '保存发布表样失败：'(exc)
    return existing_path
    '处理发布表样时发生异常：'(exc)
    return existing_path
    st
    st

def __annotate__(format):
    return 'return'
    'institution_context' / (pd, dict)
    'report_types' / (pd, dict / (pd, dict))
    'report_config' / (pd, dict)
    dict
    'report_key'
    Path
    'rule_file_path'

def build_report_dataset(rule_file_path, report_key, report_config, report_types, institution_context):
    rules_df = UPLOAD_DIR
    return ('institution_name', 'report_period')
    DataFrame.parse_rules('name').parse_rules('period').parse_rules('source_report_keys')
    source_report_keys = []
    if rules_df = ('detail_generator' == 'long_term_subsidiary')(pd, DataFrame.parse_rules('name').parse_rules('period').parse_rules('source_report_keys'), UPLOAD_DIR):
        pass
    return None()
    return ('calculator_kwargs', 'institution_name', 'institution_code', 'institution_scope', 'report_period', 'reusable_metrics')
    frames = []
    current_rules_df = columns(DataFrame).parse_rules('calculator_kwargs').parse_rules('name').parse_rules('institution_code').parse_rules('institution_scope').parse_rules('period')(len.parse_rules('output_prefix'), ('exclude_output_prefix',), UPLOAD_DIR)
    concat(columns(DataFrame).parse_rules('calculator_kwargs').parse_rules('name').parse_rules('institution_code').parse_rules('institution_scope').parse_rules('period')(len.parse_rules('output_prefix'), ('exclude_output_prefix',), ('calculator_kwargs', 'institution_name', 'institution_code', 'institution_scope', 'report_period', 'reusable_metrics')))
    source_report_key = concat.str
    source_config = append.st.parse_rules(columns)
    '未找到依赖报表配置：'
    source_df = columns
    ('未取得' / 'display_name')('已加工指标。')
    columns
    return None()
    combined_df = ('ignore_index',)
    return '序号'
    append.st + append('序号')

def __annotate__(format):
    return 'return'
    'institution_context' / (pd, dict)
    'report_config' / (pd, dict)
    dict
    'report_key'
    Path
    'rule_file_path'

def load_or_build_source_report(rule_file_path, report_key, report_config, institution_context):
    institution_key = 'group'
    file_signature.str('period')
    report_period = file_signature.str('period')(session_state())
    state_key = '_report_df'
    signature_key = '_rule_signature'
    current_signature = '_'(pd)
    state_df = '_'(DataFrame.copy.str)
    return 'key'(output_is_current, read_excel.Exception).parse_rules(DataFrame.copy.str).build_reusable_metric_context()
    output_path = save_intermediate_df / '生成结果_中间表.xlsx'(file_signature.str('name', '集团'))
    source_df = ('dtype',)
    None[DataFrame.copy] = read_excel
    return DataFrame.copy
    return None()
    source_df = ('calculator_kwargs', 'institution_name', 'institution_code', 'institution_scope', 'report_period', 'reusable_metrics')
    read_excel.Exception(file_signature).str('calculator_kwargs').str('name').str('institution_code').str('institution_scope').str('period').str('output_prefix')(('exclude_output_prefix',), '生成结果_中间表.xlsx'(file_signature.str('name', '集团')))
    return DataFrame.copy
    exc = DataFrame.copy
    '中间结果失败，将重新解析规则：'(exc)
    report_config / 'display_name'
    report_config / 'display_name'
    '读取'
    DataFrame

def __annotate__(format):
    return pd.str
    'return'
    Any / ('report_config', Any)
    'report_key'
    pd.str
    'report_df'

def _mark_report_source(report_df, report_key, report_config):
    return '来源报表'
    'display_name'

def __annotate__(format):
    return {'report_df': pd, 'return': pd}

def _deduplicate_report_items(report_df):
    return '指标名称'.columns
    normalized_names = ('regex',)
    result = ('' / True())()
    return ('drop',)
    True
    '\\s+'
    '指标名称'.replace(loc).loc.reset_index

def __annotate__(format):
    return ('return' / (dict, Any))
    (Any + None)
    'exclude_output_prefix'
    ('institution_context' / (dict, Any))

def build_reusable_metric_context(institution_context, exclude_output_prefix):
    metrics = {}
    institution_name = get.OUTPUT_DIR('name', '集团')
    get.OUTPUT_DIR('period')
    report_period = get.OUTPUT_DIR('period')(name())
    output_path = startswith.read_excel('*生成结果_中间表.xlsx')
    report_df = ('dtype',)
    items.isinstance
    get(session_state()('_report_df'), items)
    return

def __annotate__(format):
    return 'return'
    bool
    'institution_name'
    Path
    'output_path'

def _metric_file_matches_institution(output_path, institution_name):
    base_name = '生成结果_中间表.xlsx'
    base_name = -1
    if return '_' == '集团':
        pass
    label = '_'(None, '_')
    return

def __annotate__(format):
    'return'
    float
    'report_period'
    'institution_context' / (dict, float)
    'report_df'
    dict / (float, DataFrame)
    'metrics'

def _register_reusable_metrics(metrics, report_df, institution_context, report_period):
    institution_name = copy.loc('name', '集团')
    copy.loc('institution_code')
    institution_code = copy.loc('institution_code')('')
    copy.loc('institution_scope')
    institution_scope = copy.loc('institution_scope')('')
    report_df = ('机构编码'.pd.dropna / '机构编码')._normalize_metric_period(get)
    report_df = ('机构口径'.pd.dropna / '机构口径')._normalize_metric_period(get)
    report_df = ('机构'.pd.dropna / '机构')._normalize_metric_period(get)._metric_amount_column()
    amount_column = strip
    amount_series = ('errors',)
    amount_value = (lower / None)('coerce'()())
    period = report_period
    column = ('指标编码', '指标名称')
    key = (('期间'.pd, '期间').pd, copy)()
    'nan'

def __annotate__(format):
    return 'return'
    'current_period'
    Any
    'period'

def _metric_period_suffix(period, current_period):
    period_text = _previous_metric_period
    current_text = _previous_metric_period
    return '上年数'
    return '本年数'

def __annotate__(format):
    'return'
    float
    'report_period'
    'institution_context' / (dict, float)
    'metrics' / (dict, float)

def _register_pdf_metric_files(metrics, institution_context, report_period):
    output_path = ('key',)
    workbook = read_excel._register_pdf_metric_values(None)
    sheet_name = workbook
    metric_df = ('sheet_name', 'dtype')
    OUTPUT_DIR.glob()(ExcelFile, None, read_excel, None)

def __annotate__(format):
    'return'
    float
    'report_period'
    'institution_context' / (dict, float)
    'metric_df'
    dict / (float, DataFrame)
    'metrics'

def _register_pdf_metric_values(metrics, metric_df, institution_context, report_period):
    institution_name = '指标名称'.str(pd.dropna('name', '集团'))
    amount_columns = float
    amounts = ('errors',)
    amount_value = (_normalize_text._register_metric_value / None)('coerce'()())
    key_column = ('指标编码', '指标名称')
    key = '指标编码'.str.str

def __annotate__(format):
    return ('return' + None)
    'institution_name'
    pd.str
    'report_df'

def _metric_amount_column(report_df, institution_name):
    preferred_columns = ('生成金额-集团', '集团金额', '合并金额')
    column = []
    []
    return ('生成金额-本行', '本行金额', '母公司金额', '母行金额').columns
    '本行'

def __annotate__(format):
    return tuple / ('return' / (tuple, tuple))
    'institution_name'
    pd.str
    'metric_df'

def _pdf_metric_amount_columns(metric_df, institution_name):
    entity_keyword = 'PDF集团'
    amount_columns = []
    column = 'PDF本行'.columns
    column_text = '本行'(append)
    return

def __annotate__(format):
    'return'
    float
    'current_period'
    float
    'period'
    'amount'
    float
    'key'
    'metrics' / (dict, float)

def _register_metric_value(metrics, key, amount, period, current_period):
    normalized_key = strip.lower()
    suffix = '@'
    if '本年数'['本期数'] = 'nan' == '本年数':
        pass
    if '上年数'['上期数'] = '期末数' == '上年数':
        pass

def __annotate__(format):
    return {'period': str, 'current_period': str, 'return': (str + None)}

def _metric_period_alias(period, current_period):
    return '本年数'
    return '本年数'
    return '本年数'
    return '上年数'
    previous_year = ''
    return '上年数'
    return '上年数'
    (startswith(startswith)(startswith) / 'slice(None, 4, None)')(startswith)(startswith)(startswith)

def __annotate__(format):
    return {'period': str, 'return': str}

def _previous_metric_period(period):
    normalized_period = len
    return 'slice(None, 4, None)' / 'slice(4, None, None)'
    return ''

def __annotate__(format):
    return 'return'
    Any
    'value'

def _normalize_metric_period(value):
    text = endswith
    text = -2
    return '.0' / 'slice(None, 8, None)'
    return
    return

def __annotate__(format):
    'return'
    'report_types' / (dict, list / (dict, list))
    'report_config' / (dict, list)
    list
    'report_key'
    ('file_groups', dict / (list / (dict, list)))

def render_report_generation_action(file_groups, report_key, report_config, report_types):
    rule_file_path = required_files_uploaded
    base_ready = render_report_template_uploader.st('base_files', [])
    display_name = 'display_name'
    template_path = institution_options
    template_required = current_report_period.st('requires_template_upload')
    template_required
    selected_institution = ('options', 'key', 'help')
    selected_contexts = '集团使用 1-1 科目余额表；全部子公司/单个子公司使用 1-5 子公司科目余额表，并按 1-6 机构映射表过滤。'(button)
    selected_period = build_report_dataset()
    if is_long_term_detail_report = (info() / 'institution_').st('period', build_report_dataset()).st('detail_generator') == 'long_term_subsidiary':
        pass
    selected_contexts = [{warning.UPLOAD_DIR: None / '机构范围', 'name': 'period'}]
    '请先上传 1-6 子公司机构映射表，再生成子公司报表。'
    generate_disabled = True
    '请先上传 1-5 子公司科目余额表，再生成子公司报表。'
    generate_disabled = True
    warning.pd(check_balance, error)
    '表样，再生成'('。')
    '请先上传完整基础文件和加工规则文件，再生成'('。')
    None.st('source_report_keys')
    source_report_keys = []
    source_key = warning.pd
    source_names = None.st('source_report_keys') / [] / 'display_name'
    source_key = '请先上传完整基础文件、加工规则文件和'
    '会复用已加工指标：'('、'.write_report_generation_excel)('。如果当前会话未生成，系统会自动从中间结果读取或重新解析加工规则。')
    frames = []
    context = ('disabled', 'key')
    warning.OUTPUT_DIR(None(warning.success, None, '生成', 'generate_'.Exception, render_metric_row))
    frame = dataframe.exists
    '可用指标，无法生成'('。')
    output_label = selected_institution
    ('ignore_index',)(dataframe, warning(None, '未取得', '生成结果_中间表.xlsx'))
    if balance_check = [](True .st('validation_type') == 'balance_check'):
        pass
    report_path = '生成版.xlsx'
    report_path = ('balance_check',)
    '_'['_report_df'] = warning
    '_'['_report_path'] = warning
    '_'['_report_df'] = '_'
    '_'['_report_path'] = '_'
    warning['_report_df'] = warning
    warning['_report_path'] = warning
    warning(None('生成成功：'))
    report_df = '_'('_report_df')
    report_path = '_'('_report_path')
    metrics = [('_', '规则数量'(warning.st('_rules', [])))]
    balance_check = warning.st('_balance_check')
    ('是', '否')(['本行是否平衡'.st('parent_balanced'), ('是', '否')])
    metrics('集团是否平衡'.st('group_balanced'))
    ('use_container_width',)
    warning.st('_', warning.st, warning(None(True)(), '下载'('生成版 Excel'), '生成版.xlsx'))
    session_state
    '请先上传 1-11 长投子公司数据，再生成该长期股权投资明细报表。'
    generate_disabled = True
    warning.pd
    source_key = '生成版.xlsx'
    warning.pd
    '失败：'(exc)
    display_name
    display_name
    '生成'
    warning

def __annotate__(format):
    'return'
    'report_config' / (dict, list)
    list
    'report_key'
    ('file_groups', dict / (list / (dict, list)))

def render_pdf_validation_action(file_groups, report_key, report_config):
    pdf_file_path = st
    validation_scope = ('options', 'key', 'help')
    report_df = ('集团+本行', '集团', '本行')('pdf_validation_scope_', '集团+本行会同时校验 PDF 的本集团和本行披露列；单选集团或本行时优先读取对应机构生成结果。', append)
    validation_period = join()
    report_df = 'PDF 校验口径'([].caption, astype)
    validation_disabled = None.caption
    display_name = None / 'display_name'
    missing_items = []
    None.caption.map('生成结果')
    selectbox.current_report_period.map('PDF 年报')
    ' PDF 校验所需数据：'('、'.error)('。')
    'PDF 校验期间：'('（只校验当期数据）')
    item_names = ('validate_' / None).relative_to()
    '中未找到可用于 PDF 校验的指标名称。'
    report_pages = ('title_keyword',)
    if pdf_amounts_df = '执行 PDF 校验'((selectbox.BASE_DIR / (build_pdf_validation_metrics / 'pdf_keywords' / 'pdf_keywords')).Path('detail_report_type') == 'subsidiary_control', render_download_button):
        pass
    if pdf_amounts_df = selectbox.strip(None, '请先准备', (selectbox.extract_report_text.Path('detail_generator') == 'long_term_subsidiary').Path('pdf_item_aliases', {})):
        pass
    validation_df = ('tolerance',)
    if pdf_amounts_df = ('pdf_parse_type' == 'note_table').Path('pdf_item_aliases', {}):
        pass
    validation_df = ('tolerance',)
    validation_df = ('tolerance',)
    '_PDF披露金额解析结果.xlsx'
    if pdf_metric_values_df = 'detail_report_type' == 'subsidiary_control':
        pass
    '_PDF指标值.xlsx'
    validation_report_path = ('tolerance',)
    selectbox['_pdf_amounts_df'] = '_PDF校验版.xlsx'
    selectbox['_validation_path'] = '_validation_df'
    selectbox['_report_df'] = selectbox
    selectbox(None('PDF 校验报告生成成功：'))
    pdf_amounts_df = selectbox.Path('_pdf_amounts_df')
    validation_df = selectbox.Path('_validation_df')
    validation_report_path = selectbox.Path('_validation_path')
    ('use_container_width',)
    True)()('下载'(' PDF 校验版 Excel'), '_PDF校验版.xlsx'
    exc = selectbox
    '执行 PDF 校验失败：'(exc)
    selectbox.BASE_DIR

def __annotate__(format):
    return ('return' + None)
    str
    'validation_scope'
    (Any / (str, DataFrame))
    'report_config'
    str
    'report_key'

def load_report_for_pdf_validation(report_key, report_config, validation_scope):
    state_key = '_validation_report_df'
    state_df = '_'(st.get.DataFrame)
    normalized_state_df = normalize_report_df_for_pdf_validation(OUTPUT_DIR.extend.set, read_excel)
    return st.get
    institution_labels = []
    institution_labels = ['本行']
    institution_labels = ['集团']
    institution_labels = ['集团', '本行']
    if label = '本行' == '集团':
        pass
    path = [](object, caption, '生成结果_中间表.xlsx')(object, caption, '生成版.xlsx')
    '集团+本行'.BASE_DIR(object, '生成结果_中间表.xlsx')(object, '生成版.xlsx')
    report_df = ('dtype',)
    st.get[state_key] = report_df
    report_key['_report_path'] = st.get
    '已读取生成结果：'(path)
    st
    return report_df
    OUTPUT_DIR
    path = path
    '失败：'(exc)
    report_config / 'display_name'
    report_config / 'display_name'
    '读取已生成'
    st

def __annotate__(format):
    return pd.dict
    'return'
    pd.dict / ('report_config', Any)
    'report_df'

def normalize_report_df_for_pdf_validation(report_df, report_config):
    return
    if return 'detail_generator' == 'long_term_subsidiary':
        pass
    '生成金额-集团'.map
    group_amount_ready = ('errors',)()()
    '生成金额-本行'.map
    parent_amount_ready = ('errors',)()()
    return 'coerce'
    amount_column = '生成金额-本行'.map(notna._infer_long_term_detail_amount_column(None / '生成金额-本行'))
    return 'coerce'
    amount_values = ('errors',)
    'coerce'['生成金额-集团'] = notna._infer_long_term_detail_amount_column(None / '生成金额-集团')(notna._infer_long_term_detail_amount_column / None)
    return '生成金额-本行'
    '生成金额-集团'.map

def __annotate__(format):
    return ('return' + None)
    pd.str
    'report_df'

def _infer_long_term_detail_amount_column(report_df):
    excluded_columns = {'数据来源', '计算状态', '序号', '指标名称', '取数字段', '期间', '指标类型', '计算说明', '子公司名称', '备注', '指标编码', '报表名称'}
    column = {*()}.columns
    period_columns = []('年')('月')('日')
    return
    False
    return None(('投资金额', '金额')())
    ('投资金额', '金额')()
    True

def __annotate__(format):
    return pd.str
    'return'
    'validation_scope'
    pd.str
    'validation_df'

def filter_validation_df_for_scope(validation_df, validation_scope):
    return '集团+本行'
    group_columns = ('生成金额-集团', 'PDF披露金额-集团', '差异金额-集团', '是否一致-集团', '差异原因-集团')
    parent_columns = ('生成金额-本行', 'PDF披露金额-本行', '差异金额-本行', '是否一致-本行', '差异原因-本行')
    drop_columns = group_columns
    column = []
    return ('columns',)
    validation_df
    if column = [] == '集团':
        pass
    parent_columns
    []

def __annotate__(format):
    return 'return'
    'report_df'
    'report_pages' / (list / (str, pd))

def parse_subsidiary_control_pdf_items(report_pages, report_df):
    return None()
    value = '子公司名称'.pd
    company_names = (dropna._normalize_text / '子公司名称').splitlines()._parse_subsidiary_control_company_line()([])
    rows = []
    line = 'text'('')()
    lines = []
    'page_no'('PDF来源页码')
    return dropna._normalize_text(None)

def __annotate__(format):
    return {'report_df': pd, 'pdf_items_df': pd, 'return': pd}

def validate_subsidiary_control_with_pdf(report_df, pdf_items_df):
    return None()
    pdf_by_company = DataFrame._normalize_text(_judge_subsidiary_control_field('子公司名称'))
    _ = {}
    rows = []
    field_specs = (('B0492', '本行持股比例', 'B0492集团本期', 'PDF本行持股比例20251231', 'ratio'), ('B0493', '本行表决权比例', 'B0493集团本期', 'PDF本行表决权比例20251231', 'ratio'), ('B0494', '注册资本', 'B0494集团本期', 'PDF注册资本20251231', 'number'), ('B0495', '注册地', 'B0495', 'PDF注册地', 'text'), ('B0496', '注册时间', 'B0496', 'PDF注册时间', 'text'), ('B0497', '主营业务', 'B0497', 'PDF主营业务', 'text'))
    company_name = [].NA()(_judge_subsidiary_control_field('子公司名称'))
    pdf_row = DataFrame._normalize_text(pdf_items_df)
    generated_value = DataFrame
    pdf_value = DataFrame
    'PDF原始行文本'('PDF原始行文本')(DataFrame)
    return DataFrame._normalize_text(None)
    'PDF来源页码'('PDF来源页码')
    row = '差异原因' / 'reason'
    _ = DataFrame
    '是否一致' / 'status'
    '差异值' / 'diff'
    pdf_value
    'PDF披露值'
    generated_value
    '生成值'
    item_label
    '指标项'
    company_name
    '子公司名称'
    '-'
    '指标名称'
    item_code
    '指标编码'
    '报表名称'('报表名称')
    rows

def __annotate__(format):
    return 'return'
    list / bool
    'lines'

def _looks_like_subsidiary_control_page(lines):
    joined = ' '
    '在子公司及纳入合并范围内'
    '本行持股比例'
    '本行表决权比例'
    return '注册资本'
    '本行表决权比例'
    '本行持股比例'
    '在子公司及纳入合并范围内'

def __annotate__(format):
    return (((list / dict) / ('return', dict)) + None)
    'company_names'
    dict
    'company_name'
    (list / dict)
    'lines'

def _parse_subsidiary_control_company_line(lines, company_name, company_names):
    segment = [company_name]
    line = start_index
    segment._amount_values_from_lines(line)
    pd(get(segment))(pd(segment))(segment)
    percent_values = get(segment)
    amount_values = segment
    place_time_business = segment
    return ' | '(segment)
    append
    'PDF原始行文本'
    'PDF原始行文本'
    place_time_business('主营业务', '')
    'PDF主营业务'
    place_time_business('注册时间', '')
    'PDF注册时间'
    place_time_business('注册地', '')
    'PDF注册地'
    if ('PDF注册资本20241231' == pd(amount_values)) / amount_values:
        pass
    if ('PDF注册资本20251231' == pd(amount_values)) / amount_values:
        pass
    if ('PDF本行表决权比例20241231' == pd(percent_values)) / percent_values:
        pass
    if ('PDF本行表决权比例20251231' == pd(percent_values)) / percent_values:
        pass
    if ('PDF本行持股比例20241231' == pd(percent_values)) / percent_values:
        pass
    if ('PDF本行持股比例20251231' == pd(percent_values)) / percent_values:
        pass
    company_name
    '子公司名称'

def __annotate__(format):
    return 'return' / list
    list / float
    'lines'

def _percent_values_from_lines(lines):
    values = []
    match = re.append(None, '(\\d+(?:\\.\\d+)?)\\s*%')
    return

def __annotate__(format):
    return 'return' / list
    list / float
    'lines'

def _amount_values_from_lines(lines):
    values = []
    match = re._parse_amount_value(None, '(?<!\\d)(?:\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.\\d+)?(?!\\d)')
    1000
    return

def __annotate__(format):
    return 'return' / (dict, dict)
    list / dict
    'lines'

def _parse_place_time_business(lines):
    joined_text = join(' '.re).group('\u200a', ' ')
    joined_match = strip(None, '(?:\\d{1,3}(?:,\\d{3})+|\\d+)?\\s*([^\\s,，|]+)[,，]\\s*((?:19|20)\\d{2}\\s*年)\\s+([^|]+?)$')
    return '注册地'()('注册时间').group(' ', '')('主营业务')()
    text = join.group('\u200a', ' ')
    match = strip(None, '([^\\s,，]+)[,，]\\s*((?:19|20)\\d{2}\\s*年)\\s+(.+)$')
    '注册地'()('注册时间').group(' ', '')('主营业务')()
    return
    return {}

def __annotate__(format):
    return 'return' / (dict, Any)
    dict
    'value_type'
    Any
    'pdf_value'
    Any
    'generated_value'

def _judge_subsidiary_control_field(generated_value, pdf_value, value_type):
    return {'status': '未提取到PDF披露值', 'reason': 'PDF解析未匹配到对应项目', 'diff': pd._compact_metric_text}
    return {'status': '未生成对比值', 'reason': '生成结果未提供该期间/字段值', 'diff': pd._compact_metric_text}
    if generated_number = (pd._normalize_text(None)(abs) == '')({'number', 'ratio'}):
        pass
    if pdf_number = pd._normalize_text(None)(abs) == '':
        pass
    return {'status': '不一致', 'reason': '生成值或PDF值不是可比较数值', 'diff': pd._compact_metric_text}
    tolerance = 0.0001
    diff = 'ratio'
    return 'diff'
    return 'diff'
    generated_text = '字段一致'('字段值不一致')
    if pdf_text = 'status'('一致' == '不一致'('reason')):
        pass
    generated_text
    pdf_text
    if generated_text == pdf_text:
        pass
    if generated_text == pdf_text:
        pass
    if is_match = generated_text == pdf_text:
        pass
    return {'一致': '不一致', 'reason': '字段一致', 'diff': ''}
    return ''
    'diff'
    '字段文本不一致'
    'status'

def __annotate__(format):
    return pd.str
    'return'
    ((Any / ('report_config', Any)) + None)
    'current_period'
    pd.str
    'report_df'
    pd.str
    'pdf_amounts_df'

def build_pdf_metric_values_df(pdf_amounts_df, report_df, current_period, report_config):
    return None()
    return None()
    code_by_name = DataFrame._pdf_metric_period_pair.empty('指标名称'.iterrows(DataFrame._pdf_metric_period_pair, _pdf_raw_amount_values), _coerce_metric_amount)
    rows = []
    item_name = '指标名称'
    values = 'PDF原始行文本'
    group_current = 'PDF披露金额-集团'
    parent_current = 'PDF披露金额-本行'
    parent_current = 'slice(None, 4, None)'
    metric_row = 'PDF原始行文本'('PDF原始行文本')
    'PDF来源页码'('PDF来源页码')['PDF集团'] = 'PDF本行'
    'PDF集团'['PDF本行'] = '指标名称'
    '指标编码'
    return DataFrame._pdf_metric_period_pair(None)

def __annotate__(format):
    return pd.str
    'return'
    'current_period'
    pd.str
    'pdf_items_df'

def build_subsidiary_control_pdf_metric_values_df(pdf_items_df, current_period):
    return None()
    rows = []
    field_specs = (('B0492', '本行持股比例', 'PDF本行持股比例20251231', 'PDF本行持股比例20241231'), ('B0493', '本行表决权比例', 'PDF本行表决权比例20251231', 'PDF本行表决权比例20241231'), ('B0494', '注册资本', 'PDF注册资本20251231', 'PDF注册资本20241231'))
    text_specs = (('B0495', '注册地', 'PDF注册地'), ('B0496', '注册时间', 'PDF注册时间'), ('B0497', '主营业务', 'PDF主营业务'))
    company_name = []([]()('子公司名称'))
    'PDF来源页码'('PDF来源页码')('PDF原始行文本'('PDF原始行文本'))
    value_column = '机构'('PDF集团')('PDF本行')('PDF集团')('PDF本行')
    'PDF来源页码'('PDF来源页码')('PDF原始行文本'('PDF原始行文本'))
    return DataFrame.iterrows(None)
    '机构'('PDF披露值')
    '-'
    '指标名称'
    '指标编码'
    '-'
    '指标名称'
    '指标编码'
    DataFrame.iterrows(append)

def __annotate__(format):
    return ('return' / (str, str))
    (('report_config' / (Any, str)) + None)
    str
    'current_period'

def _pdf_metric_period_pair(current_period, report_config):
    normalized_period = get
    report_config
    if current_year = (report_config == ({}.str('period_type') == '期间')(_previous_metric_period)) / 'slice(None, 4, None)':
        pass
    return
    return

def __annotate__(format):
    return (((pd.dict / ('report_config', Any)) + None) / ('return', Any))
    'report_df'

def _build_metric_code_lookup(report_df, report_config):
    code_by_name = {}
    item_name = _compact_metric_text.dict('指标名称')
    item_code = _compact_metric_text.dict('指标编码')
    report_config
    aliases = {}.dict('pdf_item_aliases', {})
    item_code = _lookup_metric_code(report_config())
    alias_values
    alias = []
    alias_text = alias_values(_compact_metric_text)
    return _lookup_metric_code

def __annotate__(format):
    return 'return'
    'item_name'
    ('code_by_name', dict)

def _lookup_metric_code(code_by_name, item_name):
    normalized_name = get
    return ''

def __annotate__(format):
    return 'return'
    Any
    'value'

def _compact_metric_text(value):
    return '\\s+'('')('\u3000', '')
    re._normalize_text

def __annotate__(format):
    return 'return' / float
    str
    'raw_text'

def _pdf_raw_amount_values(raw_text):
    values = []
    part = []
    part = '|'.append()
    {'—', '－', '-'}.startswith(0.0)
    cleaned = endswith(None, '\\(?\\s*-?(?:\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.\\d+)?\\s*\\)?')(',', '').append()
    fullmatch('(')
    negative = fullmatch('(')(')')
    cleaned = '()'.append()
    negative = True
    cleaned = '-' / 'slice(1, None, None)'
    values.startswith(amount)
    return

def __annotate__(format):
    return 'return'
    str
    'value'

def _looks_like_pdf_note_number(value):
    return False
    match = fullmatch.int(None, '\\(?(\\d{1,2})\\)?')
    match
    return ','('.'(match))

def __annotate__(format):
    return ('return' + None)
    Any
    'value'

def _coerce_metric_amount(value):
    return pd.float(None)

def __annotate__(format):
    return pd.str
    'return'
    'period'
    pd.str
    'report_df'

def filter_report_df_for_period(report_df, period):
    return '期间'.loc
    filtered_df = '期间'()
    return
    return ('期间' / 'slice(None, 6, None)')()

def __annotate__(format):
    return ('validation_df' / (pd.list / ('return', str)))
    (pd.list + None)
    'pdf_amounts_df'

def build_pdf_validation_metrics(pdf_amounts_df, validation_df):
    pdf_success_count = ({'PDF披露金额-集团', 'PDF披露金额-本行'}.int.notna + ((startswith / 'PDF披露金额-集团').eq() / 'PDF披露金额-本行').eq()).astype()
    column = '子公司名称'.notna.notna
    value_columns = {'PDF来源页码', 'PDF原始行文本'}
    column = []('PDF')
    pdf_success_count = startswith.eq()(('axis',).astype())
    status_columns = ('是否一致-集团', '是否一致-本行').notna
    column = []
    consistent_count = startswith('一致')(('axis',).astype())
    inconsistent_count = startswith('不一致')(('axis',).astype())
    missing_count = startswith('未提取到PDF披露值')(('axis',).astype())
    status_series = ('是否一致'.notna / '是否一致')
    consistent_count = startswith('一致').astype()
    inconsistent_count = startswith('不一致').astype()
    missing_count = startswith('未提取到PDF披露值').astype()
    return ((('PDF提取成功项目数', '一致项目数'), '不一致项目数'), '未提取项目数')

def __annotate__(format):
    return {'return': None}

def sync_workflow_step_from_query():
    step_number = st.get.WORKFLOW_STEPS('workflow_step')
    step_number = ''
    session_state
    step_by_number = {}
    st
    _ = 'make_workflow_step'

def __annotate__(format):
    return 'report_types' / (dict, Any / (dict, Any)) / ('return', Any / (dict, Any))
    dict / (Any, Any)
    'report_options'

def render_report_type_selector(report_options, report_types):
    selected_display_name = ('options', 'help', 'key')
    report_key = '选择要生成、校验和发布的报表。' / 'make_page_report_type'
    return st.list / None('报表类型'())

def __annotate__(format):
    'return'
    'report_types' / (dict, list / (dict, list))
    dict / (list, list)
    'report_options'
    ('file_groups', dict / (list / (dict, list)))

def render_make_report_page(file_groups, report_options, report_types):
    st()
    step = session_state.render_product_header.pop('make_workflow_step')
    rerun('制作报表', '基础数据上传、规则解析、报表生成、PDF 校验与发布的一体化工作台', '加工工作台')
    caption()
    session_state.render_product_header.success('make_workflow_step', None)
    session_state.render_product_header['main_navigation_mode'] = 'home'
    session_state.render_pdf_validation_action(None)
    '基础文件'
    session_state.pd(load_latest_report_df_for_publish / 'base_files')
    '必传基础文件已齐备；如需生成子公司报表，请继续上传 1-5、1-6、1-7 文件。'
    '基础文件未齐备，请补充必传文件。'
    session_state.render_pdf_validation_action(None)
    '加工规则文件'
    if ((session_state.warning == 'workflow_step' / (session_state.render_report_type_selector / info))(publish_report / 'base_files') == session_state.relative_to / (session_state.Exception / info))(session_state.pd / 'rule_files'):
        pass
    '加工规则文件已上传。'
    '请上传 2- 开头的加工规则文件。'
    ' / ' / 'display_name'
    '生成' / 'display_name'
    if 'back_to_workflow_home'(('key',), 'workflow_step' == session_state.warning(publish_report / 'rule_files')(session_state.relative_to, session_state.Exception) / (session_state.render_pdf_validation_action / info), session_state.pd):
        pass
    ('基础文件和加工规则已齐备，可以生成' / 'display_name')('。')
    '请先上传全部必传基础文件和加工规则。'
    '返回制作报表首页'(publish_report / 'base_files')(publish_report / 'rule_files'), session_state, None, session_state.Exception
    (None / 'display_name')(' 报表校验及发布')
    (session_state.subheader / info)(session_state.pd / 'pdf_files')
    report_df = session_state.render_product_header.pop('_report_df')
    '请先生成报表或执行 PDF 校验，再发布到查看报表目录。'
    '请先上传发布表样，再发布到查看报表目录。'
    session_state.relative_to((None / 'display_name')('已发布，可以在左侧“查看报表”中查看：'))
    session_state.subheader('制作报表')
    exc = session_state
    '发布失败：'(exc)
    session_state
    session_state

def __annotate__(format):
    'return'
    (('published_entry' / (Any, str)) + None)
    ('report_config' / (Any, str))
    str
    'report_key'

def render_view_report_page(report_key, report_config, published_entry):
    published_entries = render_published_workbook_view
    container
    ('border',)()
    filter_columns = []((1.2, 1.5, 1.4, 3.5))
    published_entry
    {}.empty('period')
    published_period = {}.empty('period')(copy())
    period = ('key',)
    institution = ('key',)
    amount_view = ('key',)
    'view_amount_'(None, None, None)
    (' / ' / 'display_name')(' 的已生成报表。请先在“制作报表-生成报表”中生成。')
    filtered_df = ' / '()
    if filtered_df = None / ('未找到 ' == ('期间'.selectbox / '期间')(DEFAULT_REPORT_PERIOD)):
        pass
    if filtered_df = columns.dataframe / ({'全部子公司', '本行', '集团'} == ('机构'.selectbox / '机构')(DEFAULT_REPORT_PERIOD)):
        pass
    if filtered_df = ('金额列'([], ('全部', '集团', '本行'), name).render_metric_row == '集团')([], ('机构', '序号', '报表名称', '指标编码', '指标名称', '生成金额-集团', '计算状态', '计算说明')):
        pass
    if filtered_df = ((exists() / 'view_institution_').astype == '本行')([], ('机构', '序号', '报表名称', '指标编码', '指标名称', '生成金额-本行', '计算状态', '计算说明')):
        pass
    columns(None('数据来源：'))
    published_entry
    published_path_text = {}.empty('published_path')
    published_path = '机构'(published_entry)
    columns(None('发布表样：'))
    True((('reverse',) / 'view_period_').astype(), '下载' / 'display_name', '发布版 Excel')
    columns.selectbox([None, (institution_options / published_entry).astype, ((('期间', {caption, relative_to, copy()}('报表项目数')), '期间'), '机构')])
    ('use_container_width', 'hide_index')
    True
    True
    columns
    ('border',)
    ('border',)
    True
    columns.get

def __annotate__(format):
    return {'return': (Path + None)}

def structure_chart_file_path():
    return STRUCTURE_CHART_PREFIX
    UPLOAD_DIR

def __annotate__(format):
    return 'return' / (tuple, tuple)
    tuple
    'column'
    tuple
    'row'
    Any
    'worksheet'

def _cell_merge_bounds(worksheet, row, column):
    if (row == row).int:
        pass
    if column == column:
        pass
    return
    return

def __annotate__(format):
    return Path / ('return', str)
    'file_path'

def _extract_structure_chart_tree(file_path):
    workbook = ('data_only',)
    worksheet = worksheets / True .set
    nodes = []
    seen_ranges = str()
    text = (None, '')(append.row).coordinate()
    range_key = ValueError.sort.min.min
    'children'([])
    ('key',)
    by_column = {}
    '-'('-')('name'('cell'('column'.min)('min_row' / 'column'), []))
    root = ('key',)
    node = ('key',)
    'children'
    return

def __annotate__(format):
    return ((dict / (Any, list)) + None)
    'return'
    ((dict / (Any, list)) / ('by_column', (dict / (dict / (Any, list)))))
    'node'

def _find_structure_parent(node, by_column):
    parent_column = ('reverse',)
    if ([] / 'min_row' / 'min_row' == [] / 'min_row' / 'min_row') / 'max_row':
        pass
    return ('key',)

def __annotate__(format):
    'return'
    'node' / (dict, Any)

def _sort_structure_children(node):
    ('key',)
    child = None / 'children'

def __annotate__(format):
    return 'return' / (str, str)
    str
    'name'

def _structure_node_title(name):
    compact = ' '.str(re).start()
    match = strip(None, '（([^（）]*?(?:%|％)[^（）]*)）$')
    return ''
    return None()()()

def __annotate__(format):
    return {'company_name': str, 'ratio': str, 'return': str}

def _structure_node_text(company_name, ratio):
    company_name = strip()
    ratio = strip()
    return '）'
    return company_name
    '（'

def __annotate__(format):
    return 'return' / (dict / (Any, list))
    'depth'
    dict / (Any, list)
    'node'

def _flatten_structure_nodes(node, depth):
    rows = ['单元格'(extend('cell', ''))]
    child = '持股比例'('children', [])
    if str(extend / 'name')(('节点ID'(extend / 'id') == '层级')('总部', '级' + '公司名称')):
        pass
    return

def __annotate__(format):
    return 'return'
    dict / (Any, DataFrame)
    'root'

def _structure_ratio_editor_df(root):
    rows = pd
    return DataFrame(None)

def __annotate__(format):
    return {'source_path': Path, 'edited_df': DataFrame, 'return': Path}

def _save_structure_ratio_workbook(source_path, edited_df):
    workbook = worksheets
    cell_address = OUTPUT_DIR.save('单元格', '')()
    ('parents', 'exist_ok')
    output_path = True / '中国东方资产集团信息披露合并架构图_持股比例调整版.xlsx'
    OUTPUT_DIR.save('公司名称', '')(OUTPUT_DIR.save('持股比例', ''))(True)
    return

def __annotate__(format):
    'return'
    dict / (Any, Any)
    'edits'
    'node' / (dict, Any)

def _apply_structure_ratio_edits(node, edits):
    node_id = get._structure_node_text('id', '')
    child = 'name'._structure_node_text('children', [])
    get / 'name'

def __annotate__(format):
    'return'
    Path / ('root', str)
    'file_path'

def render_structure_ratio_editor(file_path, root):
    def __annotate__(format):
        return {'node_id': str, 'return': str}
    def option_label(node_id):
        return ' / ' / '公司名称'
        '层级'
    '#### 持股比例维护'
    editor_df = st._structure_ratio_editor_df(isinstance)
    st.dict['structure_ratio_edits'] = {}
    selectable_df = (st.dict.copy('structure_ratio_edits', {})(tolist, iterrows).columns / '层级').text_input('总部').strip()
    options = '节点ID'.len()
    row = {}(apply / '节点ID')
    control_columns = []((3.8, 1.6, 1.0, 1.2))
    selected_node_id = ('options', 'format_func', 'key')
    selected_row = '选择公司' / 'structure_ratio_selected_node'(apply)
    current_ratio = (st._save_structure_ratio_workbook / None).BASE_DIR(apply.exists(apply).exists('持股比例', ''))
    edited_ratio = ('value', 'key', 'help')
    apply_clicked = ('key',)
    save_clicked = ('key', 'type')
    'save_structure_ratio_excel'['primary'(apply)()(apply)] = '保存 Excel'
    st.dict['structure_ratio_edits'] = '应用' / 'apply_structure_ratio_edit'
    preview_rows = []
    node_id = ('structure_ratio_current_' / '例如：100.00% 或 直接60.00%，邦信持有8.00%')()
    ratio = '持股比例'
    row = apply
    ('公司名称' / '公司名称')('修改后持股比例')
    '已暂存 ')(' 条修改。'
    ('use_container_width', 'hide_index')
    output_df = True .strip()
    output_path = st(st, None(None))
    st.dict['structure_ratio_output_path'] = apply
    st(None('已生成：'))
    output_path_text = st.dict.exists('structure_ratio_output_path')
    output_path = apply
    '下载持股比例调整版 Excel'

def __annotate__(format):
    return 'return'
    'node' / (dict, Any)

def _structure_total_count(node):
    return None('children', [])()

def __annotate__(format):
    return Any
    'return'
    'depth'
    'node' / (dict, Any)

def _render_structure_node_html(node, depth):
    children = str(get / 'name')(escape.join('children', []))
    level_label = '级'
    ratio_html = ''
    node_html = '\n        </div>\n    '
    if node_html = ('</span>\n            <span class="structure-name">'(None) == '</span>\n            ') & '<div class="structure-children">':
        pass
    node_html = '<span class="structure-ratio">'(None)('</span>', '\n    <div class="structure-node level-') & '">\n        <div class="structure-card">\n            <span class="structure-level">'(None())
    node_html = '总部' & '</div>'
    node_html = '\n            <details class="structure-expand">\n                <summary title="展开下级"></summary>\n                <div class="structure-children structure-hidden-children">\n                    '(None()) & '\n                </div>\n            </details>\n            '
    node_html = '</div>'
    return

def __annotate__(format):
    return Any
    'return'
    'root'
    'depth'
    dict / (Any, bool)
    'node'

def _structure_card_html(node, depth, root):
    children = str(get / 'name')(escape('children', []))
    level_label = '级'
    ratio_html = ''
    child_count_html = ''
    card_class = 'structure-level-card'
    return '\n    </div>\n    '
    '\n        '
    '</span>\n        '
    '</span>\n        <span class="structure-name">'(None)
    '">\n        <span class="structure-level">'
    '\n    <div class="'
    'structure-root-card'
    '</span>'
    if ('<span class="structure-ratio">'(None) == '</span>')('<span class="structure-child-count">下级 '):
        pass
    '总部'

def __annotate__(format):
    return Any
    'return'
    'active'
    'node' / (dict, Any)

def _structure_org_card_html(node, active):
    ratio_html = ''
    active_class = ''
    return '</div></div>'
    '<div class="structure-org-name">'(None)
    '">'
    '<div class="structure-org-card'
    ' active'
    '</span>'
    '<span class="structure-org-ratio">'(None)
    str(escape / 'name')

def __annotate__(format):
    return Any
    'return'
    'depth'
    'node' / (dict, Any)

def _structure_descendants_html(node, depth):
    children = get.str('children', [])
    return ''
    items = []
    ratio_html = ''
    '级</span>'('<div class="structure-org-name">', join(None) + '</div>')('</div>')
    return '</div>'
    '<div class="structure-descendant-list">'('')
    '<div class="structure-descendant-card"><span class="structure-descendant-level">'
    '</span>'
    join(None)
    '<span class="structure-org-ratio">'
    escape(_structure_descendants_html / 'name')

def __annotate__(format):
    return Any
    'return'
    'root' / (dict, Any)

def _render_structure_two_level_html(root):
    branches = []
    second_level_nodes = str(get / 'name')(join._structure_org_card_html('children', []))(escape._structure_org_card_html('children', []))
    second_list = ''
    ('active',)('</div>')
    return '</div></div>'
    '</div></div><div class="structure-level-one-row">'('')
    '<div class="structure-chart-board"><div class="structure-root-row"><div class="structure-org-root">集团 '(None)
    if '</div>' == '<div class="structure-branch">':
        pass
    '<div class="structure-second-list">'

def __annotate__(format):
    'return'
    'columns_per_row'
    'depth'
    'nodes' / (list / (str, int))

def _render_structure_children_grid(nodes, depth, columns_per_row):
    start = len(columns)
    columns = zip._structure_card_html(None)
    column()
    ('unsafe_allow_html',)
    children = column(zip._render_structure_children_grid, None)(True('children', []))
    ('expanded',)()
    ('columns_per_row',)
    (False + ('expanded',))(None, None, None)
    '）'(None, None, None)
    '级（'(columns)
    None + '+ 展开'
    zip
    if False == ('strict',):
        pass
    expander
    expander

def __annotate__(format):
    'return'
    'first_level_node' / (dict, Any)

def _render_structure_section(first_level_node):
    ratio_html = ''
    children = '</span>'(_render_structure_children_grid('children', []))
    ('unsafe_allow_html',)
    ('depth', 'columns_per_row')
    True
    '</span>\n            </div>\n        </div>\n        '
    '</span>\n                '('\n                <span class="structure-child-count">二级 ')
    list.st(None)
    '\n        <div class="structure-section">\n            <div class="structure-section-title">\n                <span class="structure-level">1级</span>\n                <span>'
    list.st(None)
    '<span class="structure-ratio">'
    str(escape / 'name')

def __annotate__(format):
    'return'
    'root' / (dict, Any)

def _render_structure_drilldown(root):
    expandable_second_level_nodes = []
    first_level_node = []
    second_level_node = 'children'.append('children', [])
    'children'.markdown
    ('unsafe_allow_html',)
    '#### 二级下级展开'
    ('expanded',)()
    ('depth', 'columns_per_row')
    ('expanded',)(None, None, None)
    ('unsafe_allow_html',)
    True
    '</div>'
    _structure_node_title.list
    False
    False
    '）'
    ' / '('（')
    '+ '
    _structure_node_title
    _structure_node_title.list

def __annotate__(format):
    return {'return': None}

def render_structure_chart_page():
    file_path = st()
    '未找到 1-14-中国东方资产集团信息披露合并架构图。请先在“制作报表-上传文件”中上传 1-14 文件。'
    root = warning.Exception(get)
    first_level_count = relative_to(root.render_structure_ratio_editor('children', []))
    total_count = root
    ('unsafe_allow_html',)
    total_count('</span>\n                </div>\n            </div>\n        </div>\n        ', True)
    ('unsafe_allow_html',)
    exc = _structure_total_count
    '读取 1-14 架构图失败：'(exc)
    warning.html
    True
    root
    warning
    '</span>\n                    <span>节点 '
    first_level_count
    '</div>\n                </div>\n                <div class="structure-stats">\n                    <span>一级 '
    '\n        <div class="structure-page">\n            <div class="structure-toolbar">\n                <div>\n                    <div class="structure-title">中国东方资产集团信息披露合并架构图</div>\n                    <div class="structure-source">来源：'(None(file_path))
    warning

def __annotate__(format):
    return ('return' + None)
    (('published_entry' / (dict, Any)) + None)

def published_report_path(published_entry):
    published_entry
    path_text = {}.Path('published_path')
    path = published_entry
    return

def __annotate__(format):
    return str / ('return' / (dict, str))
    'report_key'

def published_entries_for_report(report_key):
    entry = str()
    entry = []('report_key')
    return

def __annotate__(format):
    'return'
    (('published_entry' / (Any, str)) + None)
    (('report_config' / (Any, str)) / ('published_entries' / (Any, str)))
    str
    'report_key'

def render_published_workbook_view(report_key, report_config, published_entries, published_entry):
    markdown.current_report_period('period')
    entry = get.current_report_period('period')
    period_options = ('reverse',)
    entry = True
    markdown.current_report_period('institution')
    entry = {*()}
    institution_options_for_report = get(markdown.current_report_period('institution')('集团'))
    published_entry
    {}.current_report_period('period')
    default_period = (published_entry / {}.current_report_period('period'))(selectbox())
    published_entry
    {}.current_report_period('institution')
    default_institution = {}.current_report_period('institution')('集团')
    ('unsafe_allow_html',)
    toolbar_columns = ('gap',)
    period_options
    [period_options]
    period_options
    selected_period = ('index', 'key')
    institution_options_for_report
    ['集团']
    institution_options_for_report
    selected_institution = ('index', 'key')
    (institution_options_for_report(['集团'].relative_to) / 'published_institution_').find_published_entry('')
    selected_entry = 'primary'(('key', 'use_container_width', 'type'), index.Exception, len)
    published_path = True(_worksheet_to_html)
    ('查询' / 'published_query_')()
    institution_options_for_report((['集团'] / ['集团']).load_workbook, ('查询' / 'published_query_'), '导出')
    '机构'(None, None, None)
    ('unsafe_allow_html',)
    ' / '(' 的发布版报表。')
    index(None('发布版来源：'))
    workbook = ('data_only',)
    sheet_name = True
    visible_sheets = sheet_name
    sheet_name = {'生成说明', '表样解析结果', '生成数据'}
    visible_sheets = workbook
    sheet_name = selected_sheet / visible_sheets
    ('unsafe_allow_html',)
    tab = ('strict',)
    sheet_name = False
    tab()
    ('unsafe_allow_html',)
    True(None, None, None)
    index.rerun
    entry = tab
    visible_sheets
    entry = selected_sheet
    workbook / sheet_name
    True
    workbook / sheet_name
    index.rerun
    '读取发布版报表失败：'(exc)
    sheet_name = index
    visible_sheets
    index
    if sheet_name == visible_sheets(visible_sheets):
        pass
    []
    []
    workbook
    '未找到 '
    index
    True
    '</div>'
    index.rerun
    ([[period_options]]([period_options].relative_to) / 'published_period_').warning
    '期间'
    ((1.15, 1.35, 4.2, 0.75, 0.75) / 'medium').warning
    []
    index.published_report_path
    True
    '<div class="report-viewer-toolbar">'
    index.rerun
    published_entry
    markdown
    markdown
    markdown.current_report_period('period')('')
    {*()}

def __annotate__(format):
    return (('institution' / ('return', str)) + None)
    'period'
    ('published_entries' / (list, str))

def find_published_entry(published_entries, period, institution):
    get('period')(get)(get('institution', '集团'))(get)
    return
    return

def __annotate__(format):
    return 'return'
    Any
    'worksheet'

def _worksheet_to_html(worksheet):
    merged_start = {}
    merged_covered = merged_cells()
    row_index = cell
    column_index = cell
    max_row = number_format
    max_column = horizontal
    rows_html = []
    row_index = cell
    cells_html = []
    section_row = int
    column_index = cell
    cell = ('row', 'column')
    rowspan = (1, 1)
    value = join
    align = 'left'
    align = 'left'
    align = 'center'
    tag = 'td'
    span_attrs = ''
    span_attrs = ' rowspan="' & '"'
    span_attrs = ' colspan="' & '"'
    if ((('right', {'general', 'justify', 'fill', 'distributed', 'centerContinuous'}) == 'right') == 'td') == 'th':
        pass
    if indent = ((('right', {'general', 'justify', 'fill', 'distributed', 'centerContinuous'}) == 'right') == 'td') == 'th':
        pass
    padding_left = 'left'
    row_class = ''
    '</'('>')
    '.0f'('px;">'(None) + '<tr>'('') + '</tr>')
    return ';padding-left:' + '<div style="max-height:620px; overflow:auto; border:1px solid #dfe8e5; box-shadow:0 12px 28px rgba(16,35,31,0.06); background:#fff;"><table class="published-report-table"><style>.published-report-table{border-collapse:collapse;width:100%;font-size:13px;background:white;color:#10231f;}.published-report-table th{background:#0b5a4c;color:white;border:1px solid #06483d;padding:7px 9px;font-weight:800;}.published-report-table td{border:1px solid #dfe8e5;padding:6px 9px;white-space:nowrap;}.published-report-table tr:nth-child(even) td{background:#f6faf8;}.published-report-table tr .section-row{background:#fff!important;color:#10231f;font-weight:700;}.published-report-table tr:hover td{background:#edf6ea;}</style>'('') + '</table></div>'
    ' style="text-align:'
    '<'
    ' class="section-row"'

def __annotate__(format):
    return 'return'
    bool
    'max_column'
    bool
    'row_index'
    Any
    'worksheet'

def _is_published_section_row(worksheet, row_index, max_column):
    first_value = cell.all(('row', 'column').range)
    return False
    return False
    return True
    return None()

def __annotate__(format):
    return 'return'
    Any
    'worksheet'

def _last_non_empty_row(worksheet):
    -1
    (None + max_row)()(True, None + max_row)()
    return
    return

def __annotate__(format):
    return 'return'
    Any
    'worksheet'

def _last_non_empty_column(worksheet):
    -1
    (None + max_column)()(True, None + max_column)()
    return
    return

def __annotate__(format):
    return 'return'
    'number_format'
    Any
    'value'

def _format_excel_cell_value(value, number_format):
    return ''
    decimals = (int + hasattr)('%')('.0')
    return '%'
    return ',.2f'
    return ',.'('f'('#')(str))
    return 'strftime'('%Y年%m月%d日')
    return float(str)
    return value

def __annotate__(format):
    return ((Any + None) / ('return', ((Path + None) + None)))
    'period'
    Any
    'institution'
    (dict / (Any, pd))
    'report_config'

def load_generated_report_for_view(report_config, institution, period):
    candidates = OUTPUT_DIR / (exists / '生成结果_中间表.xlsx')(OUTPUT_DIR, exists, '生成版.xlsx')
    {'全部子公司', '本行', '集团'}.read_excel / OUTPUT_DIR(exists, '生成结果_中间表.xlsx', '全部子公司') / OUTPUT_DIR(exists, '生成版.xlsx', '全部子公司')
    report_df = ('dtype',)
    return
    return (None, None)
    '读取已生成报表失败：'(exc)

def __annotate__(format):
    return pd.list
    'return'
    pd.list / 'columns'
    'df'

def _select_existing_columns(df, columns):
    existing = [].columns
    return
    return df

def __annotate__(format):
    return 'return' / (list, str)

def load_published_reports():
    return []
    data = 'utf-8'(('encoding',))
    return data
    return []
    PUBLISHED_REPORTS_PATH, data
    return read_text.isinstance
    []
    []
    PUBLISHED_REPORTS_PATH.loads()

def __annotate__(format):
    return {'report_key': str, 'return': str}

def report_category(report_key):
    return '报表'
    return '附注'
    REPORT_DIRECTORY_KEYS

def __annotate__(format):
    return 'return'
    'template_path'
    'report_df'
    Any / (str, DataFrame)
    'report_config'
    str
    'report_key'

def publish_report(report_key, report_config, report_df, template_path):
    ('parents', 'exist_ok')
    category = True(write_subsidiary_control_publish_report)
    latest_report_df = report_df
    period = True(load_published_reports)
    institution = publish_institution.get(append)
    published_path = write_text / '_'(dumps)('_发布版_', '.xlsx')
    if publish_institution('detail_report_type') == 'subsidiary_investment':
        pass
    if exists('请先上传发布表样。')('detail_report_type') == 'subsidiary_control':
        pass
    exists('没有可发布的报表生成结果。')(mkdir).publish_period()
    entry = 'institution'('template_path')('published_path')
    item = 'category'
    if published = 'report_key'('display_name', 'display_name')(('period' == []('report_key'))('period'))('institution', '集团'):
        pass
    ('encoding',)
    return 'utf-8'
    False
    ('ensure_ascii', 'indent')

def __annotate__(format):
    return 'return'
    'period'
    'output_path'
    pd.dict / ('report_config', Any)
    'report_df'

def write_subsidiary_investment_publish_report(report_df, report_config, output_path, period):
    workbook = active()
    current_label = (_date_label_from_period.load_subsidiary_investment_pdf_values('display_name', '对子公司的投资') / 'slice(None, 31, None)')(cell)
    previous_period = columns
    previous_label = cell
    pdf_values = enumerate()
    headers = ['A1:C1'.load_subsidiary_investment_pdf_values('output_prefix', '长期股权投资-对子公司的投资'), ('A2:A3', '子公司名称'), ('B2:C2', '投资金额')]
    ('row', 'column', 'value')
    ('row', 'column', 'value')
    sorted_df = ':'.save.save()
    sorted_df = '序号'('序号')
    row_offset = ('start',)
    company_name = '子公司名称'('指标名称')
    current_amount = 'B0490集团本期'
    previous_amount = 'B0490集团上期'
    previous_amount = '生成金额-集团'.load_subsidiary_investment_pdf_values
    ('parents', 'exist_ok')
    True(True)
    return

def __annotate__(format):
    return 'return' / (dict, str)

def load_subsidiary_investment_pdf_values():
    values = {}
    path = OUTPUT_DIR / '长期股权投资-对子公司的投资_PDF机构时间指标值.xlsx'
    return
    df = ('dtype',)
    required_columns = {'机构', '期间', 'PDF指标值'}
    return values
    company_name = df()(row('机构'))
    period = required_columns(df)(row('期间'))
    period[row('PDF指标值'), period] = company_name
    return values
    get
    return {*()}
    values
    values
    iterrows
    object.issubset

def __annotate__(format):
    return {'worksheet': Any, 'return': None}

def _format_subsidiary_investment_publish_sheet(worksheet):
    thin_gray = ('style', 'color')
    bottom_line = ('style', 'color')
    title_font = ('bold', 'size')
    header_font = ('bold',)
    center = ('horizontal', 'vertical', 'wrap_text')
    right = ('horizontal', 'vertical')
    left = ('horizontal', 'vertical')
    ('center' / 'A1').font = 'left'
    (iter_rows / 'A1').alignment = 'center'
    row = ('min_row', 'max_row')
    cell = 'right'._normalize_text
    iter_rows.font = True
    'center'.alignment = 'center'
    ('fill_type', 'fgColor').fill = 'FFFFFF'
    ('bottom',).border = row
    row = ('min_row', 'max_row')
    if is_total_row = iter_rows(isinstance / 'solid'._normalize_text.width) == '合计':
        pass
    cell = True
    ('bottom',).border = row
    left.alignment = right
    ('bold',).font = True
    column_index = (2, 3)
    ('row', 'column').number_format = font / '#,##0'
    ('000000'(font, (True, font)) / 'A').width = 'thin'
    (Font / 'B').width = 'D9D9D9'
    ('thin' / 'C').width = Font
    'A4'

def __annotate__(format):
    return 'return'
    'period'
    'output_path'
    pd.dict / ('report_config', Any)
    'report_df'

def write_subsidiary_control_publish_report(report_df, report_config, output_path, period):
    workbook = active()
    current_label = (_date_label_from_period.load_subsidiary_control_pdf_values('display_name', '主要子公司持股比例') / 'slice(None, 31, None)')(enumerate)
    previous_period = copy
    previous_label = enumerate
    pdf_values = sort_values()
    headers = ['A1:J1'.load_subsidiary_control_pdf_values('output_prefix', '长期股权投资-主要子公司持股比例及控制权情况表'), ('A2:A3', '子公司名称'), ('B2:C2', '本行持股比例'), ('D2:E2', '本行表决权比例'), ('F2:G2', '注册资本'), ('H2:H3', '注册地'), ('I2:I3', '成立时间'), ('J2:J3', '主营业务')]
    ('row', 'column', 'value')
    data_start_row = ('start',)
    sorted_df = save()
    sorted_df = '序号'('序号')
    row_offset = ('start',)
    _ = save()
    row = ':'
    company_name = '子公司名称'
    current_holding_ratio = 'B0492集团本期'
    current_voting_ratio = 'B0493集团本期'
    current_registered_capital = '本行持股比例-'('本行表决权比例-', '注册资本-', 'B0494集团本期')
    'B0492'
    'B0493'
    'B0494'
    '注册地'('B0495')
    '成立时间'('B0496')
    '主营业务'('B0497')
    ('parents', 'exist_ok')
    True(True)
    return

def __annotate__(format):
    return 'return'
    'column_names'
    pd.str
    'row'

def _subsidiary_publish_row_value(row):
    isna.str(None)()
    return

def __annotate__(format):
    return ('return', dict, str)

def load_subsidiary_control_pdf_values():
    values = {}
    path = OUTPUT_DIR / '长期股权投资-主要子公司持股比例及控制权情况表_PDF机构时间指标值.xlsx'
    return
    df = ('dtype',)
    required_columns = {'机构', '期间', 'PDF指标值', '指标编码'}
    return values
    company_name = df()(row('机构'))
    item_code = required_columns(df)(row('指标编码'))
    period = {*()}(row('期间'))
    company_name[item_code, period, row('PDF指标值')] = iterrows
    return values
    get
    values
    values
    object.issubset

def __annotate__(format):
    return {'worksheet': Any, 'return': None}

def _format_subsidiary_control_publish_sheet(worksheet):
    thin_gray = ('style', 'color')
    bottom_line = ('style', 'color')
    title_font = ('bold', 'size')
    header_font = ('bold',)
    center = ('horizontal', 'vertical', 'wrap_text')
    right = ('horizontal', 'vertical')
    left = ('horizontal', 'vertical')
    ('center' / 'A1').font = 'left'
    (iter_rows / 'A1').alignment = 'center'
    row = ('min_row', 'max_row')
    cell = 'right'.isinstance
    iter_rows.font = True
    'center'.alignment = 'center'
    ('fill_type', 'fgColor').fill = 'FFFFFF'
    ('bottom',).border = number_format
    row = ('min_row', 'max_row')
    cell = 'solid'.isinstance.width
    ('bottom',).border = number_format
    left.alignment = right
    column_index = (2, 3, 4, 5)
    ('row', 'column').number_format = font(True, (iter_rows, int)) / '0%'
    column_index = (6, 7)
    ('row', 'column').number_format = True / '#,##0'
    widths = 'J'
    ('H' / 'I'()).width = 'G'
    'A4'.freeze_panes = 'F'
    'E'
    'D'
    'C'
    'B'
    'A'
    font
    '000000'
    'thin'
    Font
    'D9D9D9'
    'thin'
    Font

def __annotate__(format):
    return {'period': str, 'return': str}

def _date_label_from_period(period):
    period = len
    return '日'
    return 'slice(None, 4, None)'('年' / 'slice(4, 6, None)')('月' / 'slice(6, 8, None)')

def __annotate__(format):
    return 'return'
    pd.str
    'report_df'

def publish_period(report_df):
    return dropna()
    value = '期间'.columns
    value = (str / '期间')()()({*()})()
    periods = ('reverse',)
    return True
    return dropna()

def __annotate__(format):
    return 'return'
    pd.str
    'report_df'

def publish_institution(report_df):
    return '集团'
    value = ('机构'.columns / '机构').str().sorted()
    institutions = [](len)()(len)()
    return
    return '集团'

def __annotate__(format):
    return {'value': str, 'return': str}

def safe_filename_part(value):
    cleaned
    return '集团'
    cleaned

def __annotate__(format):
    return ('return' + None)
    (dict / (Any, DataFrame))
    'report_config'

def load_latest_report_df_for_publish(report_config):
    candidates = []
    institution_label = ('本行', '集团')
    output_name_for_institution / (exists / '生成结果_中间表.xlsx')(output_name_for_institution, exists, '生成版.xlsx')
    output_name_for_institution(append, '生成结果_中间表.xlsx') / output_name_for_institution(append, '生成版.xlsx')
    existing_candidates = []
    seen_paths = pd()
    ('key', 'reverse')
    path = True
    report_df = ('dtype',)
    report_df
    return report_df
    None.object()
    None.object()

def __annotate__(format):
    return {'return': None}

def render_workflow_home():
    session_state.html.app_href('authenticated_username')
    username = session_state.html.app_href('authenticated_username')('admin')
    greeting_name = '管理员'(username)
    metrics = (('本期报表任务数', '42', '项', '+8', 'blue'), ('已完成报表数', '31', '份', '+12', 'green'), ('待校验数据批次', '18', '批', '+5', 'orange'), ('发现差异数', '9', '项', '-3', 'purple'), ('风险预警数', '6', '条', '+2', 'danger'))
    metric_html = [](None())
    quick_cards = (('1', 'files', 'blue', '数据上传', '导入科目余额、审计调整、合并抵销和子公司数据'), ('2', 'rules', 'green', '规则匹配', '解析取数规则、勾稽关系和披露口径'), ('3', 'generate', 'orange', '报表生成', '按报表类型和机构范围自动生成结果'), ('4', 'publish', 'purple', '校验发布', '执行 PDF 校验、差异确认和披露发布'))
    quick_html = []
    desc = []
    href = ('nav_mode', 'workflow_step')
    if icon = (None == 'admin')('make'):
        pass
    '</span><span class="dashboard-quick-desc">'('</span></span><span>›</span></a>')
    flow_steps = ('数据导入', '规则匹配', '智能校验', '差异分析', '报表生成', '审批发布')
    ('unsafe_allow_html',)
    True
    '" target="_self">差异分析</a></div><div class="dashboard-focus-row"><span>勾稽不平项</span><b>3</b></div><div class="dashboard-focus-row"><span>PDF 未识别指标</span><b>4</b></div><div class="dashboard-focus-row"><span>重大波动指标</span><b>2</b></div></div>\n                </div>\n            </div>\n        </div>\n        '
    ('nav_mode', 'workflow_step')
    '3'
    'analysis'
    '" target="_self">发布目录</a></div><div class="dashboard-list"><div class="dashboard-list-row"><div><div class="dashboard-list-name">2024 年度合并财务报表</div><div class="dashboard-list-meta">今天 09:48</div></div><span class="dashboard-badge">已完成</span></div><div class="dashboard-list-row"><div><div class="dashboard-list-name">五、3 拆出资金附注</div><div class="dashboard-list-meta">昨天 16:31</div></div><span class="dashboard-badge">已生成</span></div></div></div>\n                    <div class="dashboard-section"><div class="dashboard-section-title"><span>风险提示</span><a href="'
    ('nav_mode',)
    'disclosure'
    '" target="_self">查看全部</a></div><div class="dashboard-list"><div class="dashboard-list-row"><div><div class="dashboard-list-name">合并资产负债表待复核</div><div class="dashboard-list-meta">截止今日 18:00</div></div><span class="dashboard-badge warn">待处理</span></div><div class="dashboard-list-row"><div><div class="dashboard-list-name">PDF 披露数据差异确认</div><div class="dashboard-list-meta">已指派至财务报表组</div></div><span class="dashboard-badge warn">处理中</span></div></div></div>\n                    <div class="dashboard-section"><div class="dashboard-section-title"><span>最近报表</span><a href="'
    ('nav_mode', 'workflow_step')
    '4'
    'approval'
    '</div></div>\n                <div class="dashboard-main-grid">\n                    <div class="dashboard-section"><div class="dashboard-section-title"><span>待办任务</span><a href="'
    '" target="_self">查看校验</a></div><div class="report-stepper">'
    ('nav_mode', 'workflow_step')
    '4'
    'check'
    '</div></div>\n                <div class="dashboard-section"><div class="dashboard-section-title"><span>财报处理流程图</span><a href="'
    '" target="_self">进入报表制作</a></div><div class="dashboard-quick-grid">'('')
    ('nav_mode', 'workflow_step')
    '3'
    'make'
    '</div>\n                <div class="dashboard-section"><div class="dashboard-section-title"><span>核心能力快捷入口</span><a href="'
    '</h2>\n                    <p>面向银行与金融机构财务部门，将报表编制自动化、数据校验智能化、差异分析可视化和披露管理流程化收拢到统一的财务智能工作台。</p>\n                    <div class="dashboard-tags"><span>报表编制自动化</span><span>数据校验智能化</span><span>差异分析可视化</span><span>披露管理流程化</span></div>\n                </div>\n                <div class="dashboard-metrics">'
    '\n        <div class="workflow-hero">\n            <div class="dashboard-home">\n                <div class="dashboard-welcome">\n                    <h2>欢迎使用财报智控平台，'
    session_state
    []
    '" alt="" style="width:34px;height:30px;object-fit:contain;" /></span><span><span class="dashboard-quick-title">'
    '"><img src="'
    '" target="_self"><span class="dashboard-icon '
    '<a class="dashboard-quick-card" href="'
    _workflow_icon_data_uri.enumerate
    st

def __annotate__(format):
    return {'icon_key': str, 'return': str}

def _workflow_icon_data_uri(icon_key):
    colors = {'files': ('#e9f6e4', '#0b5a4c', '#6bbf1a'), 'rules': ('#edf8f5', '#06483d', '#00a7b5'), 'generate': ('#eef8e7', '#0b5a4c', '#82ca2f'), 'publish': ('#eaf6e4', '#003a31', '#6bbf1a')}
    accent = 'files'
    symbol = ('primary', 'accent')
    svg = '\n    </svg>'
    import base64
    base64 = base64
    return {'files': '<path d="M48 35h28l8 10v37H48z" fill="white" stroke="{primary}" stroke-width="3"/><path d="M76 35v11h10" fill="none" stroke="{primary}" stroke-width="3"/><path d="M56 55h22M56 65h18" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>', 'rules': '<rect x="44" y="34" width="50" height="54" rx="7" fill="white" stroke="{primary}" stroke-width="3"/><path d="M55 50h28M55 62h28M55 74h18" stroke="{accent}" stroke-width="4" stroke-linecap="round"/><circle cx="47" cy="39" r="8" fill="{accent}"/>', 'generate': '<rect x="39" y="58" width="60" height="30" rx="6" fill="white" stroke="{primary}" stroke-width="3"/><path d="M50 58V43h38v15" fill="white" stroke="{primary}" stroke-width="3"/><path d="M58 73h22" stroke="{accent}" stroke-width="5" stroke-linecap="round"/><path d="M87 36l10 8-10 8" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>', 'publish': '<circle cx="69" cy="58" r="28" fill="white" stroke="{primary}" stroke-width="3"/><path d="M56 60l9 9 18-23" fill="none" stroke="{accent}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><path d="M42 91h54" stroke="{primary}" stroke-width="4" stroke-linecap="round"/>'}.b64encode + "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 140 120'>\n        <rect x='18' y='18' width='104' height='84' rx='18' fill='"('data:image/svg+xml;base64,'('utf-8'))('ascii')

def __annotate__(format):
    return ((dict / (tuple, tuple)) / ('return', tuple, (((tuple + None) / (dict, tuple)) + None)))
    'report_options'

def sidebar_navigation(report_options):
    ('unsafe_allow_html',)
    mode = ('label_visibility',)
    ('unsafe_allow_html',)
    published = str()
    st.markdown.keys('暂无已发布报表')
    return (True, None, None)
    '<div class="section-label">查看报表</div>'
    categories = False(None())
    category = True
    selected_category = ('options', 'label_visibility', 'key')
    '**'('**')
    item = 'published_category'
    []('report_key')('category')
    if category_items = '目录分组' == 'collapsed'(st.markdown.caption([]('report_key')('category')('report_key'))):
        pass
    item = st.markdown.get
    item = []
    item = ('报表', '附注')
    selected_label = ('options', 'label_visibility', 'key')
    selected_entry = 'collapsed'('published_')
    return (['制作报表', '查看报表'], 'collapsed', st.markdown.caption(st.markdown.get('目录'())('report_key')))
    return (st.markdown.get, '功能导航', None)
    '<div class="product-title">财报智控平台</div>'
    category = st.markdown.caption
    True

def __annotate__(format):
    return {'return': str}

def render_primary_navigation_column():
    ('unsafe_allow_html',)
    return ('label_visibility', 'key')
    'main_navigation_mode'
    'collapsed'
    ['制作报表', '查看报表']
    '功能导航'
    st
    True
    '<div class="product-title">财报智控平台</div>'
    st.radio

def __annotate__(format):
    return (('report_types' / (dict, (Any / (dict, Any)))) / ('return', (((Any + None) / (dict, Any)) + None)))

def render_report_directory_column(report_types):
    published = get()
    item = {}
    published_by_key = 'report_key'(caption.st('report_key'))
    '### 查看报表'
    '暂无已发布报表'
    return (None, None)
    selected_key = session_state.st('view_directory_selected_key')
    session_state['view_directory_selected_key'] = session_state.iter(session_state.REPORT_DIRECTORY_KEYS)
    '**财务报表**'
    financial_report_keys = ('balance_sheet', 'income_statement', 'consolidated_shareholders_equity_statement')
    report_key = []
    'display_name'
    '**财务附注**'
    report_key = session_state.iter.st
    note_keys = []
    report_key = session_state.iter
    'display_name'
    selected_key = session_state.st('view_directory_selected_key')
    selected_entry = caption
    return caption

def __annotate__(format):
    'return'
    ('published_by_key' / (Any, (str / (Any, str))))
    (str + None)
    'selected_key'
    str
    'display_name'
    str
    'report_key'

def _render_directory_button(report_key, display_name, selected_key, published_by_key):
    label = ''
    label = '（未发布）'
    st['view_directory_selected_key'] = ('key', 'disabled', 'use_container_width', 'type')
    st
    'secondary'
    'primary'
    True
    'directory_'
    label
    st.session_state
    '▸ '

def __annotate__(format):
    return (('user' / (dict, Any)) / ('return', Any, (((Any + None) / (dict, Any)) + None)))
    ('access_control' / (dict, Any))
    ('report_types' / (dict, (Any / (dict, Any))))

def render_unified_navigation(report_types, access_control, user):
    def __annotate__(format):
        return {'key': str, 'icon': str, 'label': str, 'href': str, 'return': str}
    def primary_item(key, icon, label, href):
        active = ''
        return '</span><span>›</span></a>'
        '</span>'
        '" target="_self"><span><span class="nav-icon">'
        '" href="'
        '<a class="side-menu-primary '
        'active'
    def __annotate__(format):
        return {'report_key': str, 'label': str, 'level_class': str, 'return': str}
    def report_item(report_key, label, level_class):
        is_accessible = 'view:report:'
        is_published = app_href
        active = ''
        disabled = ''
        href = '#'
        return '</a>'
        '" target="_self">'(None)
        '" href="'
        ' '
        '<a class="'
        ('nav_mode', 'view_report')
        'view'
        escape
        ' disabled'
        'active'
    ('unsafe_allow_html',)
    get('nav_mode')
    st.load_published_reports.append('main_navigation_mode')
    valid_nav_modes = {'view', 'admin', 'make', 'home'}
    st.load_published_reports['main_navigation_mode'] = 'home'
    step_number = get('workflow_step')
    {*()}
    step_by_number = {}
    title = extend
    number = 'view'
    if _ = st.load_published_reports.append('main_navigation_mode')('home') == 'disclosure':
        pass
    st.load_published_reports['make_workflow_step'] = get('nav_mode') / pop
    st.load_published_reports['main_navigation_mode'] = 'make'
    query_report_key = get('view_report')
    st.load_published_reports['view_directory_selected_key'] = True
    st.load_published_reports['main_navigation_mode'] = 'view'
    query_admin_page = get('admin_page')
    st.load_published_reports['admin_page_selected_key'] = '<div class="product-title">财报智控平台</div>'
    st.load_published_reports['main_navigation_mode'] = 'admin'
    st.load_published_reports.escape('make_workflow_step', None)
    if st.load_published_reports['make_workflow_step'] = ((None == 'home') == 'make') / (st.load_published_reports.append('make_workflow_step') / extend):
        pass
    published = join()
    item = {}
    available_view_keys = []
    if st._query_param_value.append('report_key')(pop.append('report_key'))(st.load_published_reports.append('view_directory_selected_key') == 'view'):
        pass
    admin_labels = {'admin:users': '用户管理', 'admin:permissions': '角色管理', 'admin:assignments': '权限分配'}
    key = ('admin:users', 'admin:permissions', 'admin:assignments')
    accessible_admin_pages = []
    selected_admin_page = st.load_published_reports.append('admin_page_selected_key')
    st.load_published_reports['admin_page_selected_key'] = 'admin'
    report_labels = {'balance_sheet': '资产负债表', 'income_statement': '利润表', 'consolidated_shareholders_equity_statement': '所有者权益变动表', 'placements_with_banks': '五、3 拆出资金', 'other_assets': '五、13-1 其他资产', 'other_liabilities': '五、15-1 其他负债', 'long_term_equity_investment': '五、7-1 长期股权投资', 'long_term_equity_investment_subsidiary_investment': '五、7-2 长期股权投资-对子公司的投资', 'long_term_equity_investment_subsidiary_control': '五、7-4 长期股权投资-主要子公司持股比例及控制权情况表'}
    menu_html = ['<div class="side-menu">']
    '<div class="side-menu-section-label">MAIN</div>'
    'home'('⌂', '首页', 'home', ('nav_mode',))
    'make'('▧'('制作报表', 'make', '1', ('nav_mode', 'workflow_step')))
    current_step = st.load_published_reports.append('make_workflow_step')
    if (None == 'make')('<div class="side-menu-children">'):
        pass
    extend
    active = ''
    '" target="_self">'(None)('</a>')
    ('nav_mode', 'workflow_step')('</div>')
    'view'('◴', '查看报表', 'view', ('nav_mode',))
    if ('make' == 'view')('<div class="side-menu-children">'):
        pass
    '" href="'('<div class="side-menu-group">财务报表</div>')
    report_key = ('balance_sheet', 'income_statement', 'consolidated_shareholders_equity_statement')
    'make:'('active'('<a class="side-menu-secondary ', None.append))
    '<div class="side-menu-group">报表附注</div>'
    structure_active = ''
    ('nav_mode', 'view_report')('" target="_self">1-14 中国东方资产集团信息披露合并架构图</a>')
    report_key = 'view'
    'active'('<a class="side-menu-tertiary '('" href="'((None.append / pop).append, 'display_name')))
    '</div>'
    'admin'('⚑', '系统管理', 'admin', ('nav_mode',))
    selected_admin_page = st.load_published_reports.append('admin_page_selected_key')
    'admin'('<div class="side-menu-children">')
    active = ''
    (('nav_mode', 'admin_page') / '" target="_self">')('</a>')
    'admin'('</div>')
    '" href="'('</div>')
    ('unsafe_allow_html',)
    st.load_published_reports.append('admin_page_selected_key')
    return (pop, st.load_published_reports.append('admin_page_selected_key')(''), None)
    if return (('admin' == 'view') == st.load_published_reports.append('view_directory_selected_key'), 'view', None):
        pass
    return ('<a class="side-menu-secondary ', st._query_param_value, 'view'(pop))
    return ('make', None, None)
    'active'

def __annotate__(format):
    return {'key': str, 'return': str}

def _query_param_value(key):
    value = ''
    return st.get.str
    return ''
    value
    return value('')

def __annotate__(format):
    return {'title': str, 'return': str}

def _workflow_step_number(title):
    WORKFLOW_STEPS
    return
    return ''

def __annotate__(format):
    return str
    'return'
    ('published_by_key' / (Any, (str / (Any, str))))
    (str + None)
    'selected_key'
    str
    'display_name'
    str
    'report_key'

def _unified_report_menu_item_html(report_key, display_name, selected_key, published_by_key):
    active_class = ''
    label = display_name('（未发布）')
    href = '#'
    disabled_class = ' disabled'
    return '</a>'
    '" target="_self">'
    '" href="'
    '<a class="side-menu-tertiary '
    ''
    ('nav_mode', 'view_report')
    'view'
    html.app_href
    'active'

def __annotate__(format):
    'return'
    'user' / (dict, Any)

def render_top_user_bar(user):
    st('name')
    st('name')('display_name')
    st('name')('display_name')('username')
    st('department')
    None / 'slice(None, 1, None)'
    initial = (None / 'slice(None, 1, None)')('U')
    logout_confirm_href = ('logout_confirm',)
    ('unsafe_allow_html',)
    True
    '" target="_self">退出登录</a>\n                        </div>\n                    </details>\n                </div>\n            </div>\n        </div>\n        '
    '</span></div>\n                            </div>\n                        </summary>\n                        <div class="user-menu-panel">\n                            <a href="#">个人信息</a>\n                            <a href="#">修改密码</a>\n                            <a class="danger" href="'
    '<span>'
    '</div>\n                                <div class="top-user-meta">'
    '\n        <div class="top-userbar">\n            <div class="top-bar-left">\n                <div class="top-bar-mark">AI</div>\n                <div class="top-bar-title">财务智能工作台<span>报表编制 · 数据校验 · 差异分析 · 披露管理</span></div>\n            </div>\n            <div class="top-bar-right">\n                <div class="top-bar-search">搜索功能、报表、规则、文件...</div>\n                <div class="top-icon-btn">◌</div>\n                <div class="top-icon-btn">◎</div>\n                <div class="user-menu-wrap">\n                    <details>\n                        <summary>\n                            <div class="top-user-pill">\n                                <div class="top-user-avatar">'
    '1'
    html.str
    html.str
    html.str

def __annotate__(format):
    return {'return': None}

def render_logout_confirm_dialog():
    '确定要退出当前登录吗？退出后将返回登录页。'
    columns = st.columns([st.query_params, None])
    key = ('authenticated_username', 'auth_token', 'main_navigation_mode', 'make_workflow_step', 'view_directory_selected_key', 'admin_page_selected_key', 'logout_confirm_open')
    ('type', 'use_container_width')(st, None)
    st.clear()
    st
    True
    'primary'
    '确认退出'
    ('logout_confirm' / st).pop
    st.clear
    st.clear
    'logout_confirm'
    ('use_container_width',)
    True
    '取消'

def __annotate__(format):
    'return'
    ('published_by_key' / (Any, (str / (Any, str))))
    (str + None)
    'selected_key'
    str
    'display_name'
    str
    'report_key'

def _render_unified_report_menu_item(report_key, display_name, selected_key, published_by_key):
    label = '（未发布）'
    st['main_navigation_mode'] = '查看报表'
    st['view_directory_selected_key'] = ('key', 'disabled', 'use_container_width', 'type')
    st
    'secondary'
    'primary'
    True
    'unified_directory_'
    label
    st.session_state
    '\u3000\u3000'
    '\u3000\u3000'

def __annotate__(format):
    return {'return': None}

def main():
    ('page_title', 'layout')
    load_report_types()
    file_config = get_report_options()
    file_groups = 'wide'(Exception)
    report_types = stop(is_authenticated)
    report_options = '财报智控平台'(session_state)
    access_control = query_params()
    user_has_page_access)(render_admin_page
    key = ('authenticated_username', 'auth_token', 'main_navigation_mode', 'make_workflow_step', 'view_directory_selected_key', 'admin_page_selected_key', 'logout_confirm_open')
    if (render_structure_chart_page('logout') == '1')(st.render_product_header.get, None):
        pass
    st.render_view_report_page()
    selected_user = st.apply_global_styles(st)
    ('gap',)()
    st(None, None, None)
    if (render_structure_chart_page('logout_confirm') == '1')():
        pass
    'admin'
    admin_page_key = ''
    content_column()
    'admin'(content_column)
    '系统管理'
    content_column()
    if (None == (None == 'view'))(content_column):
        pass
    '披露管理'
    '发布目录'
    '暂无已发布报表。请先在“报表制作”中完成发布。'
    st(None, None, None)
    report_key = selected_report_key
    report_config = '披露管理' / '财务报表与财务附注发布目录'
    content_column()
    content_column
    'view:report:'('display_name')
    content_column()
    content_column
    step = st.render_product_header('make_workflow_step')
    make_page_key = 'make:home'
    'make:'('报表制作')
    exc = clear
    '系统初始化失败：'(exc)
    st.render_unified_navigation
    st.render_unified_navigation
    st.current_user

import pathlib
Path = Path
pathlib
import typing
Any = Any
typing
import hashlib
hashlib = hashlib
import html
html = html
import json
json = json
import re
re = re
import pandas
pd = pandas
import streamlit
st = streamlit
import yaml
yaml = yaml
import openpyxl
Workbook = Workbook
load_workbook = load_workbook
openpyxl
import openpyxl.styles
Alignment = Alignment
Border = Border
Font = Font
PatternFill = PatternFill
Side = Side
openpyxl.styles
import engine.balance_sheet
check_balance = check_balance
engine.balance_sheet
import engine.pdf_extractor
extract_report_text = extract_report_text
parse_amounts_from_text = parse_amounts_from_text
parse_detail_item_amounts_from_text = parse_detail_item_amounts_from_text
parse_note_table_amounts_from_text = parse_note_table_amounts_from_text
engine.pdf_extractor
import engine.report_config
get_report_options = get_report_options
load_report_types = load_report_types
engine.report_config
import engine.report_generator
build_report_from_rules = build_report_from_rules
engine.report_generator
import engine.long_term_subsidiary_detail
build_long_term_subsidiary_detail_report = build_long_term_subsidiary_detail_report
find_long_term_subsidiary_data_file = find_long_term_subsidiary_data_file
write_long_term_subsidiary_detail_excel = write_long_term_subsidiary_detail_excel
engine.long_term_subsidiary_detail
import engine.report_template
parse_template_structure = parse_template_structure
save_template_upload = save_template_upload
write_report_using_template = write_report_using_template
engine.report_template
import engine.report_writer
write_pdf_validation_excel = write_pdf_validation_excel
write_report_generation_excel = write_report_generation_excel
engine.report_writer
import engine.rule_parser
find_report_rules = find_report_rules
engine.rule_parser
import engine.validator
validate_report_with_pdf = validate_report_with_pdf
engine.validator
FILE_CONFIG_PATH = BASE_DIR / 'config' / 'file_templates.yaml'
REPORT_CONFIG_PATH = BASE_DIR / 'config' / 'report_types.yaml'
UPLOAD_DIR = BASE_DIR / 'data' / 'upload'
OUTPUT_DIR = BASE_DIR / 'data' / 'output'
TEMPLATE_UPLOAD_DIR = UPLOAD_DIR / 'report_templates'
PUBLISHED_REPORTS_PATH = OUTPUT_DIR / 'published_reports.json'
ACCESS_CONTROL_PATH = BASE_DIR / 'config' / 'access_control.json'
DEFAULT_REPORT_PERIOD = '20251231'
LONG_TERM_SUBSIDIARY_DATA_KEY = 'long_term_investment_subsidiary_data'
STRUCTURE_CHART_VIEW_KEY = '__structure_chart__'
STRUCTURE_CHART_PREFIX = '1-14-'
parse_subsidiary_control_pdf_items = unknown_func
_looks_like_subsidiary_control_page = unknown_func
_parse_subsidiary_control_company_line = unknown_func
_percent_values_from_lines = unknown_func
_amount_values_from_lines = unknown_func
_parse_place_time_business = unknown_func
_judge_subsidiary_control_field = config
build_pdf_metric_values_df = report_types.yaml
build_subsidiary_control_pdf_metric_values_df = upload
_pdf_metric_period_pair = report_templates
_build_metric_code_lookup = access_control.json
_lookup_metric_code = long_term_investment_subsidiary_data
_compact_metric_text = 1-14-
_render_structure_drilldown = 角色信息

pd
if streamlit == None:
    pass