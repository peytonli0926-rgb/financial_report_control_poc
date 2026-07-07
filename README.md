# IFRS 18 报表列报规则切换平台

IFRS 18 报表列报规则切换平台是一个本地离线运行的银行财报处理工具。当前版本聚焦 IFRS 18 列报规则切换、加工规则解析、核心报表生成、PDF 年报披露金额提取和一致性校验。

完整产品说明见 [PRD](docs/PRD.md)。

## 核心特点

- 本地离线运行，不联网
- 不调用外部 API
- 不接入大语言模型
- 输入文件、输出报告和中间结果全部保存在本地
- 使用规则解析和 PDF 文本解析完成资产负债表校验闭环
- 报表类型由 `config/report_types.yaml` 配置驱动，新增报表时优先扩展配置

## 四步流程

1. 上传基础文件
2. 上传加工规则并解析指定报表规则
3. 选择资产负债表、利润表或合并股东权益变动表并生成报表；合并股东权益变动表需要在第 3 步上传 Excel 报表表样，并会复用资产负债表、利润表已加工指标
4. 上传 PDF 年报并执行披露金额校验

## 支持文件

基础文件：

- `1-1-20251231科目余额表.xlsx`
- `1-2-20251231审计调整_底稿_母行.xlsx`
- `1-3-20251231审计调整_底稿_子公司.xlsx`
- `1-4-20251231审计调整_合并抵消底稿.xlsx`

规则文件：

- `2-1-报表指标-加工规则.xlsx`

PDF 文件：

- `4-1-重庆农村商业银行股份有限公司2025年年度报告.pdf`

报表表样文件：

- 第 3 步选择“合并股东权益变动表”后上传 `.xlsx` 或 `.xlsm` 表样，系统会解析表样并按指标名称写入生成金额

## 运行方式

安装依赖：

```bash
pip install -r requirements.txt
```

启动本地页面：

```bash
streamlit run app.py --server.port 8502
```

如果使用项目内虚拟环境：

```bash
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
```

浏览器访问：

```text
http://localhost:8502
```

## Windows 本地安装包

生成便携安装包目录：

```powershell
.\packaging\build_windows_package.bat
```

生成 zip 压缩包：

```powershell
.\packaging\build_windows_package.bat -Zip
```

如需把当前 `data/upload` 和 `data/output` 中的运行数据也打进去：

```powershell
.\packaging\build_windows_package.bat -IncludeRuntimeData -Zip
```

安装包生成后位于：

```text
dist/ifrs18_report_presentation_rule_switch_platform/
```

使用方式：

1. 将 `dist/ifrs18_report_presentation_rule_switch_platform` 复制到目标机器。
2. 双击 `start_ifrs18_platform.bat`。
3. 首次运行会创建 `.venv` 并安装依赖。
4. 浏览器访问 `http://127.0.0.1:8502`。

说明：当前是本地便携包，不是 MSI 安装向导。若目标环境要求“下一步/完成”式安装，可在该目录外层使用 Inno Setup 或 NSIS 制作安装器。

## 输出结果

系统会将中间结果和最终报告写入：

```text
data/output/
```

主要输出包括：

- `资产负债表规则解析结果.xlsx`
- `资产负债表生成结果_中间表.xlsx`
- `资产负债表生成版.xlsx`
- `PDF披露金额解析结果.xlsx`
- `PDF校验结果.xlsx`
- `利润表规则解析结果.xlsx`
- `利润表生成结果_中间表.xlsx`
- `利润表生成版.xlsx`
- `利润表_PDF披露金额解析结果.xlsx`
- `利润表_PDF校验版.xlsx`
- `合并股东权益变动表规则解析结果.xlsx`
- `合并股东权益变动表生成结果_中间表.xlsx`
- `合并股东权益变动表生成版.xlsx`

## 项目结构

```text
ifrs18_report_presentation_rule_switch_platform/
├── app.py
├── requirements.txt
├── config/
│   └── file_templates.yaml
│   └── report_types.yaml
├── data/
│   ├── upload/
│   └── output/
├── docs/
│   └── PRD.md
├── engine/
│   ├── file_manager.py
│   ├── rule_parser.py
│   ├── balance_sheet.py
│   ├── pdf_extractor.py
│   ├── validator.py
│   ├── report_template.py
│   └── report_writer.py
└── README.md
```

## 核心模块

- `engine/file_manager.py`：文件配置、上传和完整性检查
- `engine/report_config.py`：报表类型配置读取
- `engine/rule_parser.py`：加工规则解析
- `engine/report_generator.py`：通用报表生成引擎
- `engine/report_template.py`：上传表样解析和按表样写入生成报表
- `engine/balance_sheet.py`：资产负债表平衡检查和兼容入口
- `engine/income_statement.py`：利润表兼容入口
- `engine/pdf_extractor.py`：PDF 文本和披露金额提取
- `engine/validator.py`：生成金额与 PDF 披露金额校验
- `engine/report_writer.py`：Excel 报告输出

## 当前限制

- 当前 POC 主要面向重庆农商行 2025 年资产负债表、利润表和合并股东权益变动表场景
- 暂未从科目余额表重新计算全部指标
- 暂不支持图片扫描型 PDF OCR
- 暂不包含用户权限、任务调度和系统集成能力

## 云端审计 Agent 财政部映射

数据映射中心的“科目映射上传”支持使用云端大模型作为审计 Agent，自动把上传文件中的 `FSLine`、`NoteLine` 映射为：

- `Grouping_Consolidated`：合并口径财政部报表项目，即列4。
- `Grouping_Standalone`：单体口径财政部报表项目，即列5。
- `Confidence`：模型判断置信度。
- `MappingBasis`：审计 Agent 给出的映射依据。
- `ReviewFlag`：是否需要人工复核。

### 配置云端模型

系统使用 OpenAI-compatible `/chat/completions` 接口。可接入 OpenAI、Azure OpenAI 或其他兼容服务。

Windows PowerShell 示例：

```powershell
$env:FRC_AUDIT_AGENT_API_KEY="你的API Key"
$env:FRC_AUDIT_AGENT_BASE_URL="https://api.openai.com/v1"
$env:FRC_AUDIT_AGENT_MODEL="你的模型名称"
```

可选超时配置：

```powershell
$env:FRC_AUDIT_AGENT_TIMEOUT_SECONDS="90"
```

如果未配置 `FRC_AUDIT_AGENT_API_KEY`、`FRC_AUDIT_AGENT_BASE_URL`、`FRC_AUDIT_AGENT_MODEL`，页面会提示“云端审计 Agent 尚未配置”，生成映射时只使用本地确认库和本地规则兜底。

### 映射优先级

生成映射时按以下顺序执行：

1. 已确认映射库精确命中：`FSLine + NoteLine + 公司类型`。
2. 已确认映射库按明细命中：`NoteLine + 公司类型`。
3. 云端审计 Agent：根据公司属性、合并/单体口径、金融行业审计经验生成列4和列5。
4. 本地规则兜底：云端不可用或返回失败时使用本地规则，并对低置信度项目标记复核。

### 使用流程

1. 进入 `数据映射` -> `科目映射上传`。
2. 点击对应机构类型的 `上传`，上传仅包含 `序号`、`FSLine`、`NoteLine` 的 Excel。
3. 点击 `查看结果`，此时显示上传原始内容。
4. 点击 `生成映射`，系统调用云端审计 Agent 生成列4、列5。
5. 再点击 `查看结果`，此时显示映射后的内容。
6. 点击 `下载映射`，本地修改复核结果。
7. 将修改后的映射结果再次上传，系统会把它作为最终结果保存，并沉淀到：

```text
data/output/data_mapping/fiscal_mapping_agent/已确认映射库.xlsx
```

后续同类 `FSLine`、`NoteLine` 会优先复用该确认库，减少重复调用云端模型。
