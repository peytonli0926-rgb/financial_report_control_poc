# CR: 移除 app_recovered_full.cpython-314.pyc 运行时依赖

## 背景

当前项目入口 `app.py` 通过 `marshal.loads(data[16:])` 加载并执行 `app_recovered_full.cpython-314.pyc`。这会导致项目强依赖 CPython 3.14 字节码文件，跨 Python 版本、跨平台运行存在较高风险。

目标是将 `.pyc` 中的应用逻辑恢复为 `.py` 源码，让项目运行只依赖源码文件。

## 范围

本次整改范围：

- 新增源码承载文件，逐步恢复 `.pyc` 中的基础应用逻辑。
- 保留现有 `app.py` 包装层和近期业务补丁。
- 在验证通过后，将 `app.py` 的加载来源从 `.pyc` 切换到源码模块。
- 最终移除运行时 `.pyc` 依赖。

本次整改不包含：

- 业务规则重构。
- 页面视觉大改。
- 报表指标口径调整。
- 删除备份文件或历史恢复资产。

## 回退方案

用户已将以下文件备份到 `D:\peyton`：

- `app.py`
- `app_recovered_full.cpython-314.pyc`
- `recovered_app.py`

若整改过程中出现不可恢复问题，可将备份文件复制回项目根目录，恢复当前运行链路：

```text
app.py -> app_recovered_full.cpython-314.pyc
```

同时，`app_recovered_full.cpython-314.pyc` 和 `recovered_app.py` 已提交到 GitHub，可作为第二层回退资产。

## 阶段 1: 固化现状

状态：已完成。

内容：

- 确认当前 `app.py` 依赖 `.pyc` 运行。
- 确认 `.pyc` 已提交并推送到 GitHub。
- 确认用户已做本地文件备份。

验收标准：

- 当前程序仍可按原方式运行。
- 关键恢复资产不丢失。

## 阶段 2: 新增源码承载文件

状态：进行中。

内容：

- 新增 `app_recovered_source.py`。
- 建立源码恢复的结构、说明、导出对象清单。
- 先保证文件可被 Python 编译。
- 不修改 `app.py` 的运行入口。
- 不切换 `.pyc` 加载链路。

验收标准：

- `python -m py_compile app_recovered_source.py` 通过。
- 当前系统仍然继续使用 `.pyc` 运行。

## 阶段 3: 恢复基础应用逻辑

状态：进行中。

优先恢复 `app.py` 当前直接依赖的 `_app[...]` 对象：

- `st`
- `pd`
- `re`
- `ACCESS_CONTROL_PATH`
- `UPLOAD_DIR`
- `OUTPUT_DIR`
- `app_href`
- `is_authenticated`
- `render_login_page`
- `render_unified_navigation`
- `render_top_user_bar`
- `render_workflow_home`
- `authenticate_user`
- `user_auth_token`
- `user_role_keys`
- `load_access_control`
- `current_user`
- `find_uploaded_file`
- `save_access_control`
- `_worksheet_to_html`
- `_format_excel_cell_value`
- `render_published_workbook_view`
- `render_permission_assignment_page`
- `main`
- `apply_global_styles`
- `build_report_dataset`
- `build_pdf_metric_values_df`
- `_pdf_metric_period_pair`

验收标准：

- `app_recovered_source.py` 可 import。
- 关键函数签名和当前 `app.py` 期望一致。
- 不依赖 `app_recovered_full.cpython-314.pyc`。

当前进展：

- 已恢复路径常量、`st`、`pd`、`re`。
- 已恢复权限基础函数、认证函数、用户 token 函数。
- 已恢复上传文件查找函数。
- 已恢复导航、首页、登录页、权限页的基础实现。
- 已恢复 Excel 单元格格式化和 worksheet HTML 展示基础实现。
- 已恢复 `build_report_dataset` 和 `build_pdf_metric_values_df` 的基础接口。
- 已恢复生成报表主流程函数 `render_report_generation_action`。
- 已恢复 PDF 校验主流程函数 `render_pdf_validation_action`。
- 已恢复生成结果读取函数 `load_generated_report_for_view`。
- 已恢复 PDF 校验数据加载和标准化函数。
- 已恢复发布报表索引函数 `load_published_reports`、`published_entries_for_report`、`find_published_entry`。
- 已恢复发布报表写入函数 `publish_report`。
- 已恢复查看报表页面和生成报表页面的可执行基础流程。
- 已恢复 `central_bank_cash`、`interbank_deposits`、`derivative_financial_instruments` 三类明细生成器分派。
- 已恢复 `B0258`、`B0259` 存款缴存比率 PDF 百分数映射逻辑。
- 已恢复发布模板查找函数 `find_publish_template_file`。
- 已将 `publish_report` 扩展为双模式兼容：
  - DataFrame + 发布模板：按模板生成发布版。
  - 生成版文件路径 + 机构：复制生成版生成发布版并登记索引。
- 已修复阶段 3 第二批页面基础流程中的中文文案占位问题。
- 已通过 `python -m py_compile app_recovered_source.py`。
- 已确认 `RECOVERY_REQUIRED_EXPORTS` 清单没有缺失对象。

当前限制：

- 尚未切换 `app.py` 运行入口。
- 页面主流程仍是基础实现，不等价于 `.pyc` 中完整 Streamlit 页面。
- 复杂模板发布、完整导航视觉、历史页面细节仍需在后续批次恢复完整行为。
- PDF 校验已恢复基础流程；`B0258`、`B0259` 比例映射已补齐，但其他特殊 PDF 指标列映射仍需继续对照 `.pyc` 和现有 `app.py` 验证。
- `derivative_financial_instruments` 暂未发现发布模板；若要按模板发布五、4，需要补充对应模板文件。

阶段 3 收尾检查：

- `app.py` 对 `_app[...]` 的读取项共 28 个。
- `app_recovered_source.py` 已覆盖全部 28 个读取项。
- `app.py` 对 `_app[...]` 的写入项共 17 个，其中 `handle_login_submit`、`sync_remembered_login_token`、`render_base_file_uploaders`、`render_product_header` 属于覆盖写入项，不是阶段 4 加载时的读取阻断。
- `render_base_file_uploaders` 已补基础实现，避免后续流程需要该对象时缺失。
- 关键函数签名已对齐：
  - `render_unified_navigation`
  - `render_published_workbook_view`
  - `build_report_dataset`
  - `build_pdf_metric_values_df`
  - `_pdf_metric_period_pair`
  - `_worksheet_to_html`
  - `_format_excel_cell_value`
- `app_recovered_source.py` 已通过编译。
- 源码模块 import 通过。
- B0258/B0259 PDF 百分数映射单元测试通过。

阶段 4 最小切换判断：

- 技术上已具备最小切换条件：`app.py` 可从源码模块字典取得当前所需读取对象。
- 业务上仍需谨慎：源码模块主流程为基础恢复版，尚不能承诺与 `.pyc` 中完整 UI 和所有历史页面细节完全等价。
- 建议阶段 4 使用极小补丁，只替换 `_load_recovered_app()` 来源，不删除 `.pyc`，并保留一键回退路径。

## 阶段 4: 最小切换入口

状态：已完成。

内容：

- 小幅修改 `app.py`。
- 将 `_load_recovered_app()` 的来源从 `.pyc` 切换为 `app_recovered_source.__dict__`。
- 保留当前 `app.py` 后续覆盖逻辑。

验收标准：

- `app.py` 不再 import `marshal`。
- `app.py` 不再读取 `app_recovered_full.cpython-314.pyc`。
- 页面可启动。

当前进展：

- `app.py` 已改为 `import app_recovered_source as recovered_source`。
- `_load_recovered_app()` 已改为返回 `recovered_source.__dict__`。
- `marshal` import 已移除。
- `RECOVERED_PYC_PATH` 运行时常量已移除。
- `app_recovered_full.cpython-314.pyc` 未删除，继续作为回退资产保留。
- `python -m py_compile app.py app_recovered_source.py` 已通过。
- `import app` 已通过。

## 阶段 5: 回归验证

状态：进行中。

重点验证：

- 登录页面。
- 上传文件。
- 生成报表。
- 发布报表。
- 查看报表。
- PDF 校验。
- 权限管理。
- 五、4 衍生金融工具。
- B0270-B0293。
- B0258/B0259 比例展示。

验收标准：

- 核心流程可运行。
- 近期修复不回退。
- Mac 环境不再因 CPython 3.14 `.pyc` 无法运行。

当前验证结果：

- `python -m py_compile app.py app_recovered_source.py` 通过。
- `import app` 通过。
- `app.py` 已确认不包含 `marshal`、`RECOVERED_PYC_PATH` 和 `.pyc` 加载字符串。
- Streamlit 启动级 smoke test 通过，服务启动后 10 秒仍存活。
- 权限配置读取通过。
- `admin/admin123` 认证通过，错误密码认证失败。
- 规则文件定位通过：`data/upload/2-1-报表指标-加工规则.xlsx`。
- 年报 PDF 定位通过：`data/upload/4-1-重庆农村商业银行股份有限公司2025年年度报告.pdf`。
- 发布索引读取通过，当前发布记录 9 条。
- `balance_sheet` 发布模板可定位。
- `derivative_financial_instruments` 发布模板暂未找到。
- 五、1、五、2、五、4 明细生成器均可返回数据。
- 五、4 生成结果包含 `B0270` 到 `B0293` 共 24 个指标。
- 五、4 关键指标验证：
  - `B0272 = 8,803,789`
  - `B0275 = 5,949,387`
  - `B0277 = 125,000`
  - `B0276 = 14,878,176`
- PDF 解析验证通过：
  - 五、1 可解析 7 行。
  - 五、4 可解析 24 行。
- 受控发布 smoke test 通过，临时发布文件和发布索引变更已清理。
- PDF 校验合成用例通过。
- 五、4 实际生成数据 + 年报 PDF 解析 + 校验链路通过。
- 五、7-1 金融投资 PDF 2024 年集团/本行金额已写入 `金融投资_PDF指标值.xlsx` 的对应期间列，并生成 `金融投资_PDF机构时间指标值.xlsx`。
- 五、7-1 金融投资 PDF 机构时间指标值包含集团/本行、20251231/20241231 两个时间维度，共 20 行；2024 年集团金额已按年报截图识别为 84,554,813、297,248,006、244,824,694、1,375,617、628,003,130。
- 修复五、7-1 金融投资发布版 2024 年列取数错误：模板填充现在优先按明确期间列读取 `PDF机构时间指标值.xlsx`，并支持将 `A0007集团上期` 这类占位符规范为 `A0007集团 + 20241231` 后取值；发布版 A0007 2024 年列已更正为 84,554,813。
- 复核五、7-2 金融投资-交易性金融资产 B0413/B0415/B0416：当前生成中间表分别为 6,976.94、-68,934.57、-139,562.60 千元，PDF 披露集团本期正确值分别为 973,092、458,214、297,865 千元。
- 五、7-2 规则问题初判：`11020103+11020203科目余额借方轧差值`、`11010104+11010204+11020104+11020204科目余额借方轧差值`、`11020106+11020206科目余额借方轧差值` 这类写法只给最后一个科目附加取数口径，当前解析器会漏掉前置裸科目号；即使将全部科目逐项展开，按现有科目余额+审计/抵销口径计算也不能还原 PDF 披露正确值，说明还存在科目范围或合并调整口径问题。
- 已生成五、7-2 PDF 识别辅助文件：`金融投资-交易性金融资产_PDF披露金额解析结果.xlsx`、`金融投资-交易性金融资产_PDF指标值.xlsx`、`金融投资-交易性金融资产_PDF机构时间指标值.xlsx`。

阶段 5 发现并修复的问题：

- 问题：五、4 PDF 解析中，`B0270`、`B0278`、`B0286` 对应父级行被子项金额污染。
- 修复：在 `app_recovered_source.py` 增加五、4 PDF 解析后处理，将以下三项 PDF 披露金额按用户确认的位置识别为 0：
  - `货币衍生工具名义金额`
  - `货币衍生工具公允价值资产`
  - `货币衍生工具公允价值负债`
- 修复后验证：
  - `B0270` PDF 集团/本行 = 0，校验一致。
  - `B0278` PDF 集团/本行 = 0，校验一致。
  - `B0286` PDF 集团/本行 = 0，校验一致。
  - `B0272` PDF 集团/本行仍为 8,803,789，校验一致。

## 阶段 6: 清理与提交

状态：未开始。

内容：

- 移除运行时 `.pyc` 依赖。
- 保留 `.pyc` 作为历史恢复资产，或在确认稳定后另行决定是否移除。
- 提交整改代码。

验收标准：

- 项目运行只依赖 `.py` 源码。
- Git 状态清晰。
- 回退路径明确。
