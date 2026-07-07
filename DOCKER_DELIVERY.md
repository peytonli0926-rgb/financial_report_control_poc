# IFRS 18 Docker 交付包制作说明

目标：将 IFRS 18 报表列报规则切换平台打包为 Docker 离线安装包，客户无需安装 Python 或适配依赖环境，只需安装 Docker Desktop / Docker Engine。

## 1. 构建镜像

在工程根目录执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\packaging\docker\build_image.ps1
```

默认镜像名：

```text
ifrs18-report-platform:latest
```

## 2. 导出客户交付包

构建完成后执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\packaging\docker\export_package.ps1
```

输出位置：

```text
dist\ifrs18-report-platform-docker\
dist\ifrs18-report-platform-docker.zip
```

交付给客户 `ifrs18-report-platform-docker.zip` 即可。

## 3. 客户启动方式

客户解压 zip 后双击：

```text
启动_IFRS18_Docker.bat
```

访问：

```text
http://127.0.0.1:8502
```

## 4. 包内容说明

Docker 镜像内置：

- IFRS 18 应用程序：`app.py`
- 独立配置文件：`config/`
- 计算引擎：`engine/`
- 已上传演示数据：`data/upload`
- AI 输入输出文件：`data/ai_input`、`data/ai_output`
- 当前输出和发布数据：`data/output`

镜像排除：

- `.venv`
- `.git`
- `dist`
- 日志文件
- 历史恢复源码文本

## 5. 注意事项

- 镜像基于 `python:3.14-slim`，因为当前应用会加载 `app_recovered_full.cpython-314.pyc`。
- 容器内部端口为 `8502`，客户宿主机默认映射为 `8502`。
- Docker 环境中不能直接调用宿主机 Excel；追溯文件链接会提供下载。
