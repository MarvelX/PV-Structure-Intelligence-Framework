# API

FastAPI 本地后端，负责：

- 读取 `data/assets` 中的规则、模板和关联资产
- 提供两个 workspace 的 `evaluate` 接口
- 把记录写入本地 SQLite
- 生成并原子写入导出文件

本地开发：

```bash
uv sync
uv run uvicorn api.main:app --app-dir src --reload --host 127.0.0.1 --port 8000
```
