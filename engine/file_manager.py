from pathlib import Path
from typing import Any, BinaryIO

import yaml


FileConfig = dict[str, Any]
RequiredFileStatus = dict[str, Any]


def load_file_config(config_path: str | Path) -> FileConfig:
    """Read YAML upload configuration from disk."""
    path = Path(config_path)

    try:
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在：{path}")
        if not path.is_file():
            raise ValueError(f"配置路径不是文件：{path}")

        with path.open("r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file) or {}

        if not isinstance(config, dict):
            raise ValueError("配置文件内容必须是 YAML 字典结构。")
        if not isinstance(config.get("upload_files"), dict):
            raise ValueError("配置文件缺少 upload_files 节点，或格式不正确。")

        return config
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML 配置解析失败：{exc}") from exc
    except OSError as exc:
        raise OSError(f"读取配置文件失败：{exc}") from exc


def save_uploaded_file(uploaded_file: Any, upload_dir: str | Path) -> Path:
    """Save a Streamlit uploaded file object to the local upload directory."""
    if uploaded_file is None:
        raise ValueError("上传文件不能为空。")

    file_name = getattr(uploaded_file, "name", None)
    if not file_name:
        raise ValueError("上传文件缺少 name 属性，无法确定保存文件名。")

    target_dir = Path(upload_dir)
    save_path = target_dir / Path(str(file_name)).name

    try:
        target_dir.mkdir(parents=True, exist_ok=True)

        with save_path.open("wb") as output_file:
            if hasattr(uploaded_file, "getbuffer"):
                output_file.write(uploaded_file.getbuffer())
            elif hasattr(uploaded_file, "read"):
                _write_readable_file(uploaded_file, output_file)
            else:
                raise TypeError("上传文件对象必须支持 getbuffer() 或 read()。")

        return save_path
    except OSError as exc:
        raise OSError(f"保存上传文件失败：{exc}") from exc


def _write_readable_file(uploaded_file: Any, output_file: BinaryIO) -> None:
    """Write a generic file-like object while preserving its current interface."""
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    content = uploaded_file.read()
    if isinstance(content, str):
        content = content.encode("utf-8")
    if not isinstance(content, bytes):
        raise TypeError("上传文件 read() 返回值必须是 bytes 或 str。")

    output_file.write(content)


def match_file_by_prefix(upload_dir: str | Path, prefix: str) -> Path | None:
    """Find the first uploaded file whose name starts with the expected prefix."""
    directory = Path(upload_dir)

    try:
        if not directory.exists() or not directory.is_dir():
            return None

        matched_files = sorted(
            file_path
            for file_path in directory.iterdir()
            if file_path.is_file() and file_path.name.startswith(prefix)
        )
        return matched_files[0] if matched_files else None
    except OSError as exc:
        raise OSError(f"按前缀匹配上传文件失败：{exc}") from exc


def check_required_files(
    config: FileConfig, upload_dir: str | Path
) -> list[RequiredFileStatus]:
    """Check whether every required file in the config exists in upload_dir."""
    required_statuses: list[RequiredFileStatus] = []

    try:
        for file_config in _iter_file_configs(config):
            if not file_config.get("required"):
                continue

            file_key = str(file_config.get("file_key", ""))
            display_name = str(file_config.get("display_name", ""))
            expected_prefix = str(file_config.get("prefix", ""))

            if not file_key or not display_name or not expected_prefix:
                required_statuses.append(
                    {
                        "file_key": file_key,
                        "display_name": display_name,
                        "expected_prefix": expected_prefix,
                        "uploaded": False,
                        "actual_file_path": None,
                        "message": "配置缺少 file_key、display_name 或 prefix。",
                    }
                )
                continue

            actual_file_path = match_file_by_prefix(upload_dir, expected_prefix)
            uploaded = actual_file_path is not None

            required_statuses.append(
                {
                    "file_key": file_key,
                    "display_name": display_name,
                    "expected_prefix": expected_prefix,
                    "uploaded": uploaded,
                    "actual_file_path": str(actual_file_path) if uploaded else None,
                    "message": "已上传。" if uploaded else "未找到匹配前缀的上传文件。",
                }
            )

        return required_statuses
    except OSError:
        raise
    except Exception as exc:
        raise ValueError(f"检查必传文件失败：{exc}") from exc


def _iter_file_configs(config: FileConfig) -> list[FileConfig]:
    """Flatten all configured upload file groups into a single list."""
    upload_files = config.get("upload_files", {})
    if not isinstance(upload_files, dict):
        raise ValueError("配置文件缺少 upload_files 节点，或格式不正确。")

    file_configs: list[FileConfig] = []
    for group_name, group_files in upload_files.items():
        if group_files is None:
            continue
        if not isinstance(group_files, list):
            raise ValueError(f"上传配置分组 {group_name} 必须是列表。")
        for file_config in group_files:
            if not isinstance(file_config, dict):
                raise ValueError(f"上传配置分组 {group_name} 中存在非字典配置项。")
            file_configs.append(file_config)

    return file_configs
