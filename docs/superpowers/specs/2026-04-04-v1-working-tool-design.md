# V1 Working Tool Design

## 1. Goal

把现有的面试 Demo 和方法论资产，升级成一套 `可工作的本地轻量工具`。

V1 的目标不是做成完整桌面软件，也不是继续停留在展示原型，而是先完成一个最小但真实可用的工作闭环：

`进入工作台 -> 录入一个新场景 -> 实时得到结论 -> 生成摘要 -> 保存为记录 -> 后续回看`

这套工具需要同时支持两个独立工作台：

- `WaterBase Mount Workspace`
- `Overseas PV Structural Technical Framework Workspace`

二者共享同一套底层方法论资产，但面向不同使用者和不同工作任务。

## 2. Users And Job Context

### WaterBase Mount

真实使用者：

- 光伏支架产品经理
- 售前产品经理
- 方案经理

典型任务：

- 识别场景
- 快速预判推荐路径
- 判断标准化 / 参数化 / 非标边界
- 输出客户可读摘要
- 把项目经验沉淀成产品化资产

### Overseas PV Structural Technical Framework

真实使用者：

- 海外光伏结构设计管理者
- 技术评审负责人
- 设计院管理者

典型任务：

- 前期技术评审
- 荷载与基础关注点识别
- 设计院审核要点输出
- 风险闭环
- 多区域标准与合规适配

## 3. Product Form

V1 采用：

`模块化本地 Web App + 极轻本地后端`

不采用继续堆静态网页的方式，也不在第一版就上 Electron / Tauri 这类桌面壳。

原因：

- 当前重点是先把核心能力做成可工作的工具
- 现有 Demo、规则和模板可以最大程度复用
- 后续增加更多工作台时，Web App + 轻后端更容易扩展
- 未来如果需要桌面化，可以在核心层稳定后再加壳

同时，V1 不再允许把“静态 Demo 思维”带进底层工程实现。  
这意味着：

- 业务层不能直接读写本地文件
- 实时推演必须有明确状态机
- 保存记录必须具备最低限度的安全写盘保障
- 规则未命中时必须进入人工介入的兜底流

## 4. V1 Scope

### In Scope

- 一个统一入口页
- 两个独立工作台
- 一个通用记录详情页
- 本地记录保存与回看
- 实时结果判断
- 摘要导出
- 规则、案例、模板的基础关联
- 记录层的 `DAL / Repository` 抽象
- `pending / ready / error / manual_override` 状态机
- 保存前的状态校验与按钮锁定
- 本地超时提示与错误恢复
- 输入净化与输出转义的最低安全层

### Out Of Scope

- 登录
- 权限
- 多用户协作
- 远程同步
- 完整记录列表页
- 云端数据库
- 复杂审批流
- 真正的结构计算引擎
- 全量国际规范数值化引擎

## 5. Core Experience

### 统一入口页

入口页不是简单模式选择器，而是一个应用首页。

应包含：

1. 应用标题和说明
2. 两个工作台入口
3. `Recent Records` 区块
4. 快速动作：
   - 新建 WaterBase 记录
   - 新建 Technical Review 记录

`Recent Records` 第一版默认显示 6 条。

### 两个工作台

两个工作台使用统一的页面框架，但保留各自的领域字段与输出逻辑。

页面结构：

1. Header
2. 分段表单区
3. 粘性结果卡
4. 保存 / 导出动作区

工作台页面在宽屏下采用：

- 左侧分段表单
- 右侧粘性结果卡

在窄屏下退化为：

- 顶部结论卡
- 下方单栏表单

工作台页面必须显式体现状态机：

- `idle`
  初始状态，尚未形成有效结论
- `pending`
  正在推演，禁止保存和导出
- `ready`
  已形成可用结论，可保存和导出
- `error`
  本地后端失败、超时或解析异常
- `manual_override`
  规则未命中或超出自动评审边界，必须人工介入

在 `pending` 和 `error` 状态下：

- 保存按钮必须禁用
- 导出按钮必须禁用
- 页面必须给出明确提示，而不是静默失败

### 记录详情页

V1 采用一个通用详情页，而不是为两个工作台各做一个详情页。

详情页结构：

1. 顶部结论卡
2. 输入快照
3. 输出详情
4. 导出内容
5. 关联资产

不同工作台通过记录类型切换细节内容展示。

## 6. Data Model

### 统一记录中心索引字段

所有记录都至少包含以下索引字段：

- `id`
- `workspace`
- `title_zh`
- `title_en`
- `status`
- `tags`
- `created_at`
- `updated_at`
- `summary`

说明：

- `title_zh` / `title_en` 默认由系统自动生成，但允许用户修改
- 索引字段的作用是统一管理、检索、回看，而不是承载所有业务细节

### WaterBase Mount 专属 schema

#### 场景输入

- `structure_type`
- `is_retrofit`
- `span_level`
- `wind_level`
- `corrosion_level`
- `interference_level`
- `om_requirement`
- `support_condition`
- `target_market`

#### 判断输出

- `recommended_path`
- `standardization_level`
- `material_direction`
- `region_note`

#### 风险与摘要

- `primary_risks`
- `summary`

#### 可选工程扩展字段

V1 不强制所有记录都填写数值型工程参数，但需要为后续升级预留扩展位：

- `engineering_inputs`
- `constraint_notes`

#### 资产关联

- `linked_rule_ids`
- `linked_case_ids`
- `export_history`

### Overseas Technical Review 专属 schema

#### 项目输入

- `project_type`
- `structure_scenario`
- `load_environment`
- `foundation_condition`
- `site_constraint`
- `target_market`

#### 评审输出

- `review_conclusion`
- `review_signal`

#### 评审内容

- `technical_focus`
- `load_foundation_focus`
- `design_institute_focus`
- `risk_alerts`
- `summary`

#### 可选工程扩展字段

V1 需要预留数值化字段的扩展位，但不要求第一版全部规则都依赖它们：

- `engineering_inputs`
  例如：
  - `design_wind_speed`
  - `ground_snow_load`
  - `seismic_category`
- `compliance_notes`

#### 资产关联

- `linked_rule_ids`
- `linked_case_ids`
- `linked_gate_ids`
- `linked_checklist_ids`
- `export_history`

## 7. Storage Strategy

V1 采用分层存储，而不是“所有内容都写进 JSON 文件”：

- 规则库与静态资产：`JSON / Markdown`
- 场景记录与索引：`SQLite`
- 导出内容：`Markdown / TXT`

理由：

- 规则、案例、模板这类静态资产适合保留文件形态，方便人工维护
- 记录层存在并发写入、多标签页、异常中断等现实问题，不适合继续用 `records.json` 直写
- SQLite 仍然是本地单文件形态，但具备基本事务、锁和查询能力，更适合 V1 的真实工作闭环
- 后续如果迁移到远端数据库，SQLite 也更接近正式数据层

### 写盘约束

无论是 SQLite 还是导出文件，都必须遵守：

- 业务层不直接操作文件系统
- 导出写盘采用 `临时文件 -> 完整性校验 -> 原子替换` 的策略
- 当写盘失败时，必须保留当前界面中的摘要文本，允许用户手动复制，不能让结果直接丢失

## 8. Shared Core

虽然是两个独立工作台，但底层需要共享一套核心模块：

1. `Rule Engine`
   根据输入匹配规则并生成初步结论

2. `Record Service`
   负责新建、保存、读取和更新记录

3. `Export Service`
   负责生成 `.md / .txt` 摘要

4. `Asset Linking`
   把记录与规则、案例、控制门、审核清单关联起来

5. `Title Generator`
   自动生成中英文标题

6. `State Guard`
   管理 `idle / pending / ready / error / manual_override` 的流转

7. `Sanitizer`
   对用户输入、模板输出和详情渲染做基础净化与转义

### Data Access Layer

必须引入 `Repository / DAL` 抽象，禁止在业务逻辑中直接使用底层文件或数据库 API。

至少包含：

- `RecordRepository`
- `RuleRepository`
- `AssetRepository`
- `ExportRepository`

V1 阶段：

- `RecordRepository` 使用 SQLite 实现
- 规则、案例和模板可继续由文件仓储实现

这样做的目的，是把存储替换成本控制在基础设施层，而不是蔓延到工作台逻辑中。

## 9. Record Creation Flow

### WaterBase Mount

1. 进入工作台
2. 输入场景参数
3. 进入 `pending` 状态并实时显示推荐路径与标准化等级
4. 生成产品摘要
5. 保存为记录
6. 后续进入详情页回看

如果规则未命中：

- 自动切换到 `manual_override`
- 显示“需人工介入 / 专项评审”的结论
- 仍允许生成带免责说明的摘要

### Overseas Technical Review

1. 进入工作台
2. 输入项目边界
3. 进入 `pending` 状态并实时显示技术评审结论
4. 生成技术评审摘要
5. 保存为记录
6. 后续进入详情页回看

如果规则未命中：

- 自动切换到 `manual_override`
- 输出“超出自动评审边界”的提示
- 生成要求人工复核的技术评审摘要

## 10. Output Layer

V1 的输出不是附属功能，而是核心资产层的一部分。

每个工作台都应支持：

- 复制摘要
- 导出 `.md`
- 导出 `.txt`

并且记录详情页应能回看历史导出结果。

导出层必须满足两个最低要求：

- 导出失败时，不能影响当前记录内容
- 导出文本必须经过基础转义和净化，防止输入内容污染渲染或破坏文件结构

## 11. Why This Is Software Instead Of A Demo

之前的产物更接近：

- 原型
- 静态规则演示器
- 面试展示资产

V1 之所以升级为软件，是因为它开始具备：

- 状态持久化
- 记录管理
- 统一应用入口
- 工作台与详情页结构
- 资产关联
- 可持续扩展的 shared core
- 明确状态机
- Repository / DAL
- 最低限度的错误恢复与手动兜底

## 12. Future Compatibility

虽然 V1 暂不做多用户和同步，但架构需要明确为未来预留空间：

- 用户体系
- 权限
- 协作
- 远程同步
- 更多工作台
- 数据库存储

当前设计刻意把“统一记录索引层”和“工作台专属 schema”分开，就是为了避免后续扩展时推翻整体结构。

### V1 与 V1.1 的边界

为了避免把完整工程平台的要求全部压进第一版，当前阶段做如下划分：

#### V1 必做

- SQLite 记录层
- DAL 抽象
- 状态机
- 手动兜底
- 基础输入净化
- 本地超时与错误提示

#### V1.1 再做

- 更细的数值型工程字段全面落地
- 更强的规范控制门与合规矩阵
- 更复杂的规则树优化
- 更完整的列表页与筛选系统
- 用户、权限、同步预埋接口的正式实现

## 13. Implementation Order

建议按以下顺序实现：

1. 搭应用壳和统一首页
2. 先搭 `Repository / DAL` 和 SQLite 记录层
3. 搭 shared core 的最小骨架
4. 先实现 `WaterBase Mount Workspace`
5. 再实现 `Overseas Technical Review Workspace`
6. 实现通用记录详情页
7. 最后统一 Recent Records、导出历史和错误恢复提示

原因：

- WaterBase 当前资产更成熟
- 先打通一条完整闭环，再复制到第二条线最稳
- 先打好存储层和状态机，能避免后面返工业务层

## 14. Verification Criteria

V1 最低验证标准：

1. 能从首页进入任一工作台
2. 能录入一个新场景
3. 在推演期间进入 `pending`，且禁止保存
4. 能实时得到结论或进入 `manual_override`
5. 能保存为本地记录
6. 本地保存失败时不会破坏已有记录，且界面仍可复制当前摘要
7. 能从 Recent Records 打开详情页
8. 能导出 `.md / .txt`
9. 能在详情页看到关联的规则 / 案例 / 控制门 / 审核清单信息
10. 多标签页同时操作时，记录层不会因为直接文件覆盖而损坏

## 15. Final Positioning

V1 的正确定位不是：

“面试时更炫的网页”

而是：

`一套面向真实工作使用的本地轻量工具`

它要同时承担两层价值：

1. 当前可用于面试展示
2. 长期可沉淀为个人知识资产和工作方法论工具
