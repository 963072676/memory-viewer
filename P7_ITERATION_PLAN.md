# Memory Viewer v2 — P7 智能交互迭代

> **日期**: 2026-05-29
> **目标**: 增强批量操作效率、引入标签系统、提升搜索体验，完成 P6 延期项
> **特性数量**: 6

---

## 迭代方向

P6 完成了质量打磨（数据修复、暗色模式、响应式、MCP 认证等），P7 转向**用户效率提升**：
- 补完 P6 延期的多实例代理
- 引入标签系统（tags）作为记忆组织的新维度
- 批量操作能力大幅提升管理效率
- 命令面板式快速搜索替代传统搜索栏
- 智能集合自动聚合常用视图
- 记忆模板降低创建门槛

---

## 功能列表

### F44 — 多实例代理（原 F40 延期项）🔴 P0

**描述**: 多实例管理页面切换实例时，通过本地后端代理转发 API 请求到目标实例，实现真正的跨实例记忆浏览。

**复杂度**: 🟡 中

**实现方案**:
- 后端: `POST /api/instances/{instance_id}/proxy` 接收路径和查询参数，转发到目标实例 API
- 后端: `GET /api/instances` 返回已配置的实例列表（从 config 或 .env 读取）
- 前端: InstancesView 实例卡片点击后加载远程数据，带 loading/error 状态
- 前端: 代理请求显示实例来源标签

**验收标准**:
- AC-F44-1: 配置 2+ 实例后，切换实例可看到目标实例的记忆列表
- AC-F44-2: 代理请求超时时显示友好错误提示
- AC-F44-3: 远程实例记忆卡片显示来源实例标识

---

### F45 — 批量操作工具栏 🔴 P0

**描述**: 支持多选记忆条目，批量执行删除、归档、标签添加、导出操作。

**复杂度**: 🟡 中

**实现方案**:
- 前端: MemoryCard 左侧添加复选框，长按或 Shift+点击范围选中
- 前端: 选中 ≥1 条时顶部浮现批量操作工具栏（BatchToolbar 组件）
- 后端: `POST /api/agentmemory/batch` 接收 `{action, ids, params}` 统一处理
- 后端: 支持 actions: `delete`, `archive`, `unarchive`, `add_tags`, `export`

**验收标准**:
- AC-F45-1: 点击卡片复选框可选中/取消选中
- AC-F45-2: 选中后工具栏显示"已选 N 条"+ 操作按钮
- AC-F45-3: 批量删除需二次确认对话框
- AC-F45-4: 批量操作完成后列表自动刷新，工具栏消失

---

### F46 — 记忆标签系统 🟡 P1

**描述**: 为记忆条目添加用户自定义标签（tags），支持按标签筛选和管理。

**复杂度**: 🟡 中

**实现方案**:
- 后端: agentmemory 数据模型扩展 `tags: string[]` 字段
- 后端: `PUT /api/agentmemory/{id}/tags` 设置标签，`GET /api/tags` 返回全部标签及计数
- 后端: `/api/agentmemory/paginated` 增加 `?tag=xxx` 过滤参数
- 前端: MemoryCard 显示标签胶囊，点击标签即筛选
- 前端: TagManager 组件：标签输入（回车添加）+ 自动补全 + 删除
- 前端: Sidebar 或 FilterPanel 增加标签过滤区

**验收标准**:
- AC-F46-1: 编辑记忆时可添加/删除标签
- AC-F46-2: 标签在卡片上以胶囊样式显示
- AC-F46-3: 点击标签自动筛选出同标签记忆
- AC-F46-4: `/api/tags` 返回 `[{tag: "ai", count: 5}, ...]`
- AC-F46-5: 批量操作支持"添加标签"

---

### F47 — 命令面板（Quick Actions） 🟡 P1

**描述**: Ctrl+K / Cmd+K 打开命令面板，支持模糊搜索记忆、快速跳转视图、执行操作。

**复杂度**: 🟡 中

**实现方案**:
- 前端: CommandPalette 组件（全屏 overlay + 搜索框 + 结果列表）
- 前端: 模糊匹配记忆标题/内容，键盘上下选择，Enter 打开
- 前端: 内置命令：`>go dashboard`、`>go graph`、`>create`、`>refresh`、`>export all`
- 后端: `GET /api/search/quick?q=xxx&limit=10` 轻量搜索端点（只返回 id/title/type/snippet）

**验收标准**:
- AC-F47-1: Ctrl+K 打开命令面板，Esc 关闭
- AC-F47-2: 输入关键词实时显示匹配结果（debounce 200ms）
- AC-F47-3: 输入 `>` 前缀切换到命令模式
- AC-F47-4: 键盘 ↑↓ 选择，Enter 执行，结果高亮匹配文字

---

### F48 — 智能集合 🟢 P2

**描述**: 预定义智能集合（Smart Collections），基于规则自动聚合记忆：最近修改、高强度、低健康度、无标签等。

**复杂度**: 🟢 低

**实现方案**:
- 后端: `GET /api/collections` 返回预定义集合及匹配数量
- 后端: 集合规则引擎：`recent_7d`（7天内更新）、`high_strength`（≥8）、`low_health`（<40）、`untagged`（无标签）、`stale`（>30天未更新）
- 前端: Sidebar 新增"智能集合"区域，显示集合名+计数徽章
- 前端: 点击集合跳转到预设过滤视图

**验收标准**:
- AC-F48-1: Sidebar 显示 ≥5 个预定义集合及计数
- AC-F48-2: 点击集合正确过滤显示匹配的记忆
- AC-F48-3: 集合计数实时更新（新建/编辑记忆后刷新）

---

### F49 — 记忆模板 🟢 P2

**描述**: 提供常用记忆创建模板（Bug Report、Code Pattern、Architecture Decision、Meeting Note），一键填充表单。

**复杂度**: 🟢 低

**实现方案**:
- 后端: `GET /api/templates` 返回模板列表（静态数据，无需持久化）
- 后端: 每个模板定义 `{name, type, title_template, content_template, suggested_concepts}`
- 前端: CreateMemoryModal 顶部增加"从模板创建"下拉
- 前端: 选择模板后自动填充 type + content 骨架 + 推荐 concepts

**验收标准**:
- AC-F49-1: 创建对话框可选择 ≥4 个预定义模板
- AC-F49-2: 选择模板后表单自动填充，用户可修改
- AC-F49-3: 不选模板（自定义）行为不变

---

## 开发顺序

```
F44(多实例代理) → F45(批量操作) → F46(标签系统) → F47(命令面板) → F48(智能集合) → F49(模板)
     P0                P0               P1               P1               P2               P2
```

**理由**:
1. F44 先行：补完延期项，后端改动独立
2. F45 紧随：批量操作需要 F46 的标签支持（add_tags action）
3. F46 第三：标签系统是 F48 智能集合的基础（untagged 规则依赖标签）
4. F47 第四：命令面板是纯前端，独立性强
5. F48/F49 最后：低优先级，可选实现

---

## 依赖关系

```
F44 多实例代理 ── 独立（后端 proxy + 前端 InstancesView 增强）
F45 批量操作 ──── 依赖 F46（批量标签操作需要标签系统）
F46 标签系统 ──── 独立（数据模型扩展 + CRUD API + 前端组件）
F47 命令面板 ──── 独立（纯前端 + 轻量搜索 API）
F48 智能集合 ──── 依赖 F46（untagged 规则需要标签数据）
F49 记忆模板 ──── 独立（静态数据 + CreateMemoryModal 扩展）
```

---

## 技术影响

| 功能 | 后端变更 | 前端变更 | 新文件 |
|------|---------|---------|--------|
| F44 | +instances proxy router | InstancesView 增强 | `routers/instance_proxy.py` |
| F45 | +batch endpoint | +BatchToolbar, MemoryCard checkbox | `routers/batch.py`, `BatchToolbar.vue` |
| F46 | +tags CRUD, paginated filter | +TagManager, tag display in cards | `routers/tags.py`, `TagManager.vue` |
| F47 | +quick search endpoint | +CommandPalette | `CommandPalette.vue` |
| F48 | +collections endpoint | +SmartCollections sidebar | `routers/collections.py`, `SmartCollections.vue` |
| F49 | +templates endpoint | CreateMemoryModal 扩展 | `routers/templates.py` |
