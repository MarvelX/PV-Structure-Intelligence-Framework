# V1 Working Tool

本目录是 `V1 Working Tool` 的实现分支工作区，包含：

- `apps/web`: React + TypeScript + Vite 前端
- `apps/api`: FastAPI + SQLite 本地后端
- `data/assets`: 规则、模板、案例、控制门、审核清单
- `data/runtime`: 本地运行时数据与导出目录

## 本地启动

首次进入工作区时：

```bash
cd "/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/.worktrees/codex-v1-working-tool"
npm --prefix apps/web install
uv sync --project apps/api
```

一条命令同时启动前后端：

```bash
npm run dev
```

启动后默认地址：

- Web: `http://127.0.0.1:5173`
- API: `http://127.0.0.1:8000`

## 单独启动

```bash
npm run dev:web
npm run dev:api
```

## 验证

```bash
npm run test:web
npm run build:web
npm run lint:web
npm run test:api
```
