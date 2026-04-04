# V1 Working Tool Implementation Plan

## Summary

V1 将实现为 `React + TypeScript + FastAPI + SQLite` 的单机本地应用，形态是：

- 一个统一入口页
- 两个独立工作台
- 一个通用记录详情页

目标是把现有静态 Demo 升级为可工作的轻量工具，完成这条真实闭环：

`录入场景 -> 实时推演 -> 生成摘要 -> 手动保存 -> Recent Records 回看`

实施策略采用 `保留并迁移现有 Demo 资产`：尽量复用现有字段、规则 JSON、文案、模板与交互结构，但在新架构里重建前端组件、状态机、Repository / DAL 和 SQLite 记录层。

## Key Changes

### 1. 应用骨架与目录

- 新建双应用结构：
  - `apps/web`
  - `apps/api`
  - `data/assets`
  - `data/runtime`
- 前端使用：
  - `Vite`
  - `React`
  - `TypeScript`
  - `react-router-dom`
  - `@tanstack/react-query`
  - `react-hook-form`
  - `zod`
- 后端使用：
  - `FastAPI`
  - `Pydantic`
  - `SQLAlchemy`
  - `SQLite`
- 环境管理：
  - 前端使用 `npm`
  - 后端使用 `uv`

### 2. Shared Core 与存储层

- 先实现 `Repository / DAL`，业务层禁止直接读写文件或 SQLite
- 最少包含：
  - `RecordRepository`
  - `RuleRepository`
  - `AssetRepository`
  - `ExportRepository`
- 存储策略：
  - 静态资产：`JSON / Markdown`
  - 记录层：`SQLite`
  - 导出：`Markdown / TXT`
- 写盘约束：
  - SQLite 保存通过单后端进程串行提交
  - 导出文件采用 `临时文件 -> 完整性校验 -> 原子替换`
  - 写盘失败时必须保留当前摘要文本并允许手动复制
- `RecordService` 需要处理：
  - `SQLITE_BUSY` 短重试
  - 前端“正在同步记录”提示

### 3. API、状态机与公共接口

- 前端仅通过本地 HTTP JSON API 调用后端
- V1 最小 API：
  - `GET /api/home/recent-records?limit=6`
  - `POST /api/workspaces/waterbase/evaluate`
  - `POST /api/workspaces/overseas/evaluate`
  - `POST /api/records`
  - `GET /api/records/{id}`
- `evaluate` 响应统一返回：
  - `state`
  - `title_zh`
  - `title_en`
  - `summary`
  - `export_markdown`
  - `export_text`
  - `linked_asset_refs`
  - `workspace_specific_result`
- 状态机固定为：
  - `idle`
  - `pending`
  - `ready`
  - `error`
  - `manual_override`
- 行为约束：
  - `pending`：禁止保存、禁止导出
  - `ready`：允许保存和导出
  - `error`：展示错误提示，禁止保存和导出
  - `manual_override`：允许用户补充人工结论后保存

### 4. 两个工作台与页面结构

#### 首页

- 应用标题与说明
- 两个工作台入口
- `Recent Records` 6 条
- 两个快速动作按钮

#### WaterBase Mount Workspace

- 迁移现有 Product Mode 字段、规则和摘要模板
- 保留现有预设场景
- `manual_override` 下允许补充人工结论与备注再保存

#### Overseas Workspace

- 迁移现有 Technical Review 字段、规则和模板
- 保留现有预设场景
- `manual_override` 下允许补充人工评审结论与复核备注再保存

#### 通用页面框架

- Header
- 分段表单区
- 粘性结果卡
- 保存与导出动作区

#### 记录详情页

- 通用详情页，只读回看
- 展示：
  - 顶部结论卡
  - 输入快照
  - 输出详情
  - 导出内容
  - 关联资产
- 不支持在详情页直接编辑主体内容

### 5. 数据模型与资产迁移

#### SQLite 记录表

- `id`
- `workspace`
- `title_zh`
- `title_en`
- `status`
- `tags`
- `summary`
- `manual_override`
- `created_at`
- `updated_at`
- `input_json`
- `output_json`
- `exports_json`
- `links_json`

#### WaterBase Mount

- 迁移现有规则字段命名
- 保留：
  - `linked_rule_ids`
  - `linked_case_ids`
  - `export_history`
  - `engineering_inputs`
  - `constraint_notes`

#### Overseas Technical Review

- 迁移现有规则字段命名
- 保留：
  - `linked_rule_ids`
  - `linked_case_ids`
  - `linked_gate_ids`
  - `linked_checklist_ids`
  - `export_history`
  - `engineering_inputs`
  - `compliance_notes`

#### 资产迁移方式

- 复制两套规则 JSON 到 `data/assets/rules/`
- 复制模板、案例、控制门、审核清单到 `data/assets/`
- 建立稳定 ID 映射，避免前端使用裸文件名
- `title_zh` / `title_en` 由后端自动生成，前端允许保存前修改
- `Sanitizer` 负责：
  - 文本输入净化与转义
  - 数值扩展字段的最小物理常识校验

## Implementation Order

1. 搭应用壳和统一首页
2. 先搭 `Repository / DAL` 和 SQLite 记录层
3. 搭 shared core 的最小骨架
4. 先实现 `WaterBase Mount Workspace`
5. 再实现 `Overseas Technical Review Workspace`
6. 实现通用记录详情页
7. 最后统一 Recent Records、导出历史和错误恢复提示

实现顺序的理由：

- WaterBase 当前资产更成熟
- 先打通一条完整闭环，再复制到第二条线最稳
- 先打好存储层和状态机，能避免后面返工业务层

## Test Plan

### 前端基础

- 首页能进入两个工作台
- `Recent Records` 正确显示最近 6 条
- 宽屏 / 窄屏布局都能正常显示分段表单与结果卡

### 状态机

- 输入变化时进入 `pending`
- `pending` 下保存和导出按钮禁用
- 规则命中后进入 `ready`
- 规则未命中后进入 `manual_override`
- `manual_override` 下必须填写人工结论才能保存

### 后端与存储

- `POST /evaluate` 返回统一结构
- `POST /records` 能写入 SQLite 并在 `GET /recent-records` 中出现
- 多标签页近同时保存时不会损坏记录层
- SQLite busy 时能短重试并给出前端提示

### 导出

- 两个工作台都能导出 `.md` 和 `.txt`
- 导出失败时不会清空界面结果，仍可复制摘要
- 原子写盘策略能保证旧文件不被破坏

### 详情页

- 能按记录类型正确渲染不同 workspace 的输入输出与关联资产
- 能显示规则 / 案例 / 控制门 / 审核清单关联信息

### 迁移与回归

- 现有 Product Mode / Technical Review 的典型场景，在新应用中能得到与当前 Demo 一致或更严格的结果
- 现有模板文案和导出内容在新应用中保持语义一致

## Assumptions

- 前端默认用自定义样式延续现有 Demo 的视觉语言，不引入大型 UI 组件库
- V1 只支持手动保存，不做自动草稿和全自动落盘
- V1 记录详情页只读，不支持编辑已保存记录
- V1 使用单机单用户本地运行，不实现登录、权限、协作和同步，但保留后续扩展空间
- V1 不把所有工程规则数值化；只为 `engineering_inputs` 预留字段与最小校验，深度工程参数化放到 V1.1
