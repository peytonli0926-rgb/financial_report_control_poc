from pathlib import Path
from typing import Any

import yaml


ReportConfig = dict[str, Any]


def load_report_types(config_path: str | Path) -> dict[str, ReportConfig]:
    """Load report type definitions from config/report_types.yaml."""
    path = Path(config_path)

    try:
        if not path.exists():
            raise FileNotFoundError(f"报表类型配置文件不存在：{path}")
        if not path.is_file():
            raise ValueError(f"报表类型配置路径不是文件：{path}")

        with path.open("r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file) or {}

        report_types = config.get("report_types")
        if not isinstance(report_types, dict) or not report_types:
            raise ValueError("配置文件缺少 report_types 节点，或格式不正确。")

        for report_key, report_config in report_types.items():
            _validate_report_config(report_key, report_config)

        return report_types
    except yaml.YAMLError as exc:
        raise ValueError(f"报表类型 YAML 配置解析失败：{exc}") from exc
    except OSError as exc:
        raise OSError(f"读取报表类型配置失败：{exc}") from exc


def get_report_options(report_types: dict[str, ReportConfig]) -> dict[str, str]:
    """Return display-name to report-key mapping for UI selectors."""
    return {
        str(report_config["display_name"]): report_key
        for report_key, report_config in report_types.items()
    }


def _validate_report_config(report_key: str, report_config: Any) -> None:
    if not isinstance(report_config, dict):
        raise ValueError(f"报表类型 {report_key} 必须是字典结构。")

    required_fields = [
        "display_name",
        "rule_keyword",
        "pdf_keywords",
        "output_prefix",
        "period_type",
        "validation_type",
        "key_items",
    ]
    missing_fields = [
        field for field in required_fields if field not in report_config
    ]
    if missing_fields:
        raise ValueError(
            f"报表类型 {report_key} 缺少必要字段：{', '.join(missing_fields)}"
        )

    if not isinstance(report_config["pdf_keywords"], list):
        raise ValueError(f"报表类型 {report_key} 的 pdf_keywords 必须是列表。")
    if not isinstance(report_config["key_items"], list):
        raise ValueError(f"报表类型 {report_key} 的 key_items 必须是列表。")
