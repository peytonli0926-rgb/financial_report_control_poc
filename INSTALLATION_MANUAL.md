# 财报智控平台安装手册

## 1. 安装包文件

交付安装包为：

```text
financial_report_control_platform.zip
```

解压后得到目录：

```text
financial_report_control_platform/
```

主要入口文件：

```text
start_platform.bat
```

## 2. 安装环境要求

### 操作系统

- Windows 10 或 Windows 11
- 建议使用 64 位系统

### Python 环境

- 需要安装 Python 3.14.x
- Python 需要加入系统 PATH
- 可在命令行执行以下命令确认：

```powershell
python --version
```

或：

```powershell
py --version
```

注意：当前包包含 `app_recovered_full.cpython-314.pyc`，要求 Python 3.14.x 环境。低版本 Python 可能无法运行该缓存文件。

### 网络要求

- 首次运行会创建本地 `.venv` 虚拟环境并安装 Python 依赖。
- 首次安装依赖时需要能访问 Python 包索引源，例如 PyPI 或企业内网镜像。
- 依赖安装完成后，系统本身为本地离线运行，不调用外部 API。

### 浏览器

- Chrome、Edge 或其他现代浏览器均可。
- 默认访问地址：

```text
http://127.0.0.1:8501
```

### 端口

- 默认使用本机 `8501` 端口。
- 如果端口被占用，可使用 PowerShell 指定其他端口启动：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\packaging\windows\start_app.ps1 -Port 8502
```

## 3. 安装和启动步骤

1. 将 `financial_report_control_platform.zip` 复制到目标 Windows 机器。
2. 解压 ZIP 文件。
3. 进入解压后的 `financial_report_control_platform` 目录。
4. 双击 `start_platform.bat`。
5. 首次运行时，程序会自动创建 `.venv` 虚拟环境并安装依赖。
6. 启动完成后，浏览器会自动打开：

```text
http://127.0.0.1:8501
```

如果浏览器没有自动打开，请手动复制上述地址到浏览器访问。

## 4. 仅安装依赖

如需先安装依赖但不启动系统，可双击：

```text
packaging/windows/安装依赖.bat
```

或执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\packaging\windows\start_app.ps1 -NoBrowser -InstallOnly
```

## 5. 依赖清单

安装包中的 `requirements.txt` 当前包含：

```text
streamlit
pandas
openpyxl
pymupdf
pyyaml
numpy
```

## 6. 数据目录说明

运行数据位于安装目录下的 `data` 目录：

```text
data/upload   上传文件目录
data/output   报表生成结果目录
```

安装包默认包含 `data/upload` 下的 `1-1` 至 `1-5` AI 输入文件，以及 `data/output` 下的三份 AI 输出文件。具体清单见：

```text
DELIVERY_FILE_LIST.md
```

配置文件位于：

```text
config/
```

如需配置访问控制，可参考：

```text
config/access_control.example.json
```

并按实际需要创建：

```text
config/access_control.json
```

## 7. 停止系统

在启动窗口中按：

```text
Ctrl+C
```

或直接关闭启动窗口。

## 8. 常见问题

### 提示找不到 Python

请安装 Python 3.14.x，并确认 `python` 或 `py` 命令可在命令行中执行。

### 依赖安装失败

请确认目标机器可以访问 Python 包索引源。企业网络环境下，可先配置 pip 镜像源后再执行安装。

### 8501 端口被占用

可改用其他端口，例如：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\packaging\windows\start_app.ps1 -Port 8502
```

然后访问：

```text
http://127.0.0.1:8502
```

### 浏览器无法访问

请确认启动窗口没有报错，并确认访问地址为本机地址：

```text
http://127.0.0.1:8501
```
