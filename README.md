# financial_report_control_poc

财报智控平台 Local POC 是一个本地离线运行的银行财报处理工具。当前版本聚焦“重庆农商行 2025 年财报校验”，支持基础文件上传、加工规则解析、资产负债表、利润表和合并股东权益变动表生成、PDF 年报披露金额提取和一致性校验。

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
streamlit run app.py
```

如果使用项目内虚拟环境：

```bash
./.venv/bin/streamlit run app.py
```

浏览器访问：

```text
http://localhost:8501
```

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
financial_report_control_poc/
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
