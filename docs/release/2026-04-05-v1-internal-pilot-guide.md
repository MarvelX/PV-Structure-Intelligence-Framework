# PV Structure Intelligence Framework V1 内测试用说明

## 1. 当前版本定位

当前版本是 `V1 可用内测版`，适合小范围真实试用，不是正式发布版。

适用对象：

- 你本人
- 首批 1-5 位内部试用者
- `macOS` 用户

## 2. 启动方式

### 方式 A：直接打开打包产物

应用路径：

`dist/macos/PV Structure Intelligence Framework.app`

双击即可启动。

如果第一次被 macOS 拦截，请先执行：

```bash
xattr -cr "/path/to/PV Structure Intelligence Framework.app"
```

然后重新双击，或执行：

```bash
open "/path/to/PV Structure Intelligence Framework.app"
```

### 方式 B：开发态启动

```bash
cd "/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/.worktrees/codex-v1-working-tool"
npm run setup
npm run dev
```

## 3. 能做什么

当前版本已支持：

- `WaterBase Mount Workspace`
- `Overseas PV Technical Review Workspace`
- 实时评估
- 保存记录
- 回看记录
- 编辑记录
- 删除记录
- 导出摘要

核心流程：

`Evaluate -> Save -> Fetch -> Edit -> Delete -> Export`

## 4. 建议试用流程

建议按下面顺序试用：

1. 进入 `WaterBase` 或 `Technical Review` 工作台
2. 修改字段，确认右侧结果卡会自动刷新
3. 点击 `Save Record`
4. 进入详情页后，确认输入、输出、导出内容都可读
5. 修改摘要或标签后再次保存
6. 返回首页确认 `Recent Records` 已更新
7. 点击 `Export Summary`
8. 测试删除记录，并确认删除前会有二次确认

## 5. 已知限制

- 当前只支持 `macOS`
- 当前打包产物未做正式签名 / notarization
- 多标签页冲突会被安全拦截，但仍需要手动刷新后再保存
- 删除记录后不可恢复
- 当前更适合内部试用，不适合对外正式发布

## 6. 常见说明

### 1. 为什么第一次打不开？

因为当前 `.app` 未签名，macOS 可能触发 Gatekeeper 拦截。  
先执行 `xattr -cr` 即可。

### 2. 为什么删除会弹确认框？

因为删除记录时会同时删除本地导出文件，且当前版本没有回收站，所以必须二次确认。

### 3. “导出内容”里为什么现在不再显示奇怪转义字符？

因为详情页已经改成按原始文本展示，不再把文本内容做 `JSON.stringify` 转义。

## 7. 内测试用清单

发给首批真实试用者时，建议他们逐项勾选：

- 能启动应用
- 能进入首页
- 能打开两个 workspace
- 能触发自动评估
- 能保存一条新记录
- 能在详情页看到输入快照
- 能在详情页看到可读的导出文本
- 能编辑并重新保存
- 能导出摘要文件
- 能删除记录
- 删除前有确认提示
- 删除后首页列表同步消失

## 8. 问题反馈建议

如果试用者反馈问题，优先收集这 4 类信息：

- 使用的是哪个 workspace
- 输入了哪些字段
- 问题发生在 `评估 / 保存 / 回看 / 编辑 / 删除 / 导出` 的哪个步骤
- 是否能稳定复现
