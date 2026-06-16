财报智控平台 Windows 本地运行包

运行方式：
1. 双击“启动财报智控平台.bat”。
2. 首次运行会创建 .venv 并安装 requirements.txt 中的依赖。
3. 浏览器会自动打开 http://127.0.0.1:8501。
4. 如果浏览器未自动打开，请手动访问上述链接。

前置要求：
- Windows 10/11。
- Python 3.11 或以上，并已加入 PATH。
- 首次安装依赖需要能访问 Python 包源；如需完全离线安装，请随包提供 wheelhouse 并调整 start_app.ps1 的 pip 安装参数。

数据目录：
- 上传文件保存在 data/upload。
- 输出文件保存在 data/output。
- 权限配置在 config/access_control.json。

停止服务：
- 关闭启动窗口，或在窗口中按 Ctrl+C。
