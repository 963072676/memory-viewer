# Memory Viewer v2 — P2 测试计划

> **版本**: 1.0
> **日期**: 2026-05-29
> **基于**: P2_ITERATION_PLAN.md
> **现有测试**: 41 个用例（P0+P1），全部通过

---

## 目录

1. [F-12 版本更新说明](#f-12-版本更新说明)
2. [F-13 暗色模式](#f-13-暗色模式)
3. [F-14 时间线视图](#f-14-时间线视图)
4. [F-15 记忆归档](#f-15-记忆归档)
5. [F-16 虚拟列表](#f-16-虚拟列表)
6. [F-17 记忆变更通知](#f-17-记忆变更通知)
7. [测试汇总](#测试汇总)

---

## F-12 版本更新说明

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_changelog.py`

```python
# === GET /api/changelog ===

def test_changelog_returns_200(client):
    """GET /api/changelog 返回 200"""
    ...

def test_changelog_returns_list(client):
    """响应为列表，每项包含 version, date, changes 字段"""
    ...

def test_changelog_ordered_by_version_desc(client):
    """版本列表按版本号降序排列"""
    ...

def test_changelog_changes_have_required_fields(client):
    """每个 change 包含 title, description, type 字段"""
    ...

def test_changelog_change_type_is_valid(client):
    """type 字段为 feature/fix/improvement 之一"""
    ...

def test_changelog_date_format(client):
    """date 字段为合法日期格式（YYYY-MM-DD）"""
    ...

def test_changelog_appears_in_swagger(client):
    """/api/docs 中包含 /api/changelog 端点"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-12-1 | **首次访问自动弹窗** | **P0** | 清除 localStorage，首次访问页面 | What's New Modal 自动弹出 |
| FE-12-2 | 关闭后不再弹出 | P0 | 关闭 Modal → 刷新页面 | Modal 不再自动弹出 |
| FE-12-3 | 版本更新后重新弹出 | P0 | 模拟版本号变更 → 访问页面 | Modal 重新自动弹出 |
| FE-12-4 | Markdown 渲染 | P1 | 查看包含标题、列表、粗体的变更内容 | 正确渲染 markdown 格式 |
| FE-12-5 | 侧边栏手动查看 | P1 | 点击侧边栏"更新日志" | 显示历史版本列表 |
| FE-12-6 | Modal 关闭方式 | P1 | 点击关闭按钮 / 点击遮罩 / 按 Esc | Modal 正常关闭 |

### 边界条件

- localStorage 被禁用 → 使用内存状态，不崩溃
- CHANGELOG.json 为空数组 → 显示"暂无更新记录"
- CHANGELOG.json 格式错误 → API 返回 500，前端显示错误提示
- 超长变更内容（>5000 字符）→ Modal 可滚动

### 验收检查清单（AC）

- [ ] **AC-F12-1**：首次访问 Modal 自动弹出 ⭐ P0
- [ ] **AC-F12-2**：关闭后刷新不再弹出
- [ ] **AC-F12-3**：版本更新后重新弹出 ⭐ P0
- [ ] **AC-F12-4**：Markdown 格式正确渲染
- [ ] **AC-F12-5**：侧边栏可查看历史版本
- [ ] **AC-F12-6**：API 返回降序版本列表

---

## F-13 暗色模式

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-13-1 | **Light/Dark 切换** | **P0** | 点击主题切换按钮 | 页面在亮色/暗色间切换，过渡动画流畅 |
| FE-13-2 | **跟随系统模式** | **P0** | 选择"系统"模式 → 操作系统切换暗色 | 页面自动跟随系统主题 |
| FE-13-3 | **主题持久化** | **P0** | 设置 Dark → 刷新页面 | 仍为 Dark 模式 |
| FE-13-4 | 无 FOUC 闪烁 | P1 | 快速刷新页面 | 无白色背景闪现 |
| FE-13-5 | 暗色模式文字可读 | P1 | 切换暗色模式 → 检查所有页面文字 | 对比度 ≥ 4.5:1 |
| FE-13-6 | 暗色模式适配 Dashboard | P1 | 暗色模式下访问 /dashboard | 图表颜色适配暗色背景 |
| FE-13-7 | 暗色模式适配 Modal | P1 | 暗色模式下打开创建/编辑 Modal | Modal 样式正确 |
| FE-13-8 | 暗色模式搜索高亮 | P2 | 暗色模式下搜索 | 高亮标记可见且不刺眼 |
| FE-13-9 | 三态循环切换 | P2 | 连续点击主题按钮 | Light → Dark → System → Light 循环 |

### 后端测试

F-13 为纯前端功能，无后端 API 测试。

### 边界条件

- localStorage 中无 theme 值 → 默认"系统"模式
- 系统不支持 `prefers-color-scheme` → 降级为 Light 模式
- CSS 变量未定义的组件 → 使用浏览器默认样式，不崩溃
- 切换主题时有动画进行中 → 不产生冲突

### 验收检查清单（AC）

- [ ] **AC-F13-1**：Light/Dark 切换正常 ⭐ P0
- [ ] **AC-F13-2**：跟随系统模式正常 ⭐ P0
- [ ] **AC-F13-3**：主题偏好持久化 ⭐ P0
- [ ] **AC-F13-4**：无 FOUC 闪烁
- [ ] **AC-F13-5**：暗色模式下所有页面视觉正确

---

## F-14 时间线视图

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-14-1 | **时间线页面渲染** | **P0** | 访问 /timeline | 记忆按日期分组显示，有时间轴线条 |
| FE-14-2 | **日期分组正确性** | **P0** | 检查分组逻辑 | 今天/昨天/本周/本月/更早 分组正确 |
| FE-14-3 | **时间轴视觉元素** | P1 | 查看时间线 | 竖线 + 节点圆点 + 日期标签渲染正确 |
| FE-14-4 | 卡片内容完整 | P1 | 查看任意记忆卡片 | 显示 title、type tag、strength、时间 |
| FE-14-5 | 卡片点击交互 | P1 | 点击记忆卡片 | 打开详情或展开内容 |
| FE-14-6 | 空数据状态 | P1 | 无记忆数据时访问 | 显示"暂无记忆记录" |
| FE-14-7 | 导航入口 | P1 | 从导航栏进入 | /timeline 路由可访问 |
| FE-14-8 | 大数据量渲染 | P2 | 200+ 条记忆 | 时间线流畅渲染（配合虚拟列表） |

### 后端测试

F-14 为纯前端功能，无后端 API 测试。

### 边界条件

- 所有记忆同一天 → 只有一个分组
- 记忆跨年（2025 + 2026）→ 年份分组正确
- createdAt 为空 → 归入"未知日期"分组或使用 updatedAt
- 仅 1 条记忆 → 时间线正常渲染

### 验收检查清单（AC）

- [ ] **AC-F14-1**：记忆按日期分组显示 ⭐ P0
- [ ] **AC-F14-2**：时间轴线条+节点渲染正确
- [ ] **AC-F14-3**：今天/昨天/本周/本月/更早 分组逻辑正确
- [ ] **AC-F14-4**：卡片显示完整信息
- [ ] **AC-F14-5**：空数据友好提示

---

## F-15 记忆归档

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_agentmemory_archive.py`

```python
# === PATCH /api/agentmemory/{memory_id}/archive ===

def test_archive_memory(client, sample_memory_id):
    """归档记忆，返回 archived=true"""
    ...

def test_unarchive_memory(client, archived_memory_id):
    """取消归档，返回 archived=false"""
    ...

def test_archive_nonexistent_id(client):
    """归档不存在的 ID，返回 404"""
    ...

def test_archive_toggle_idempotent(client, sample_memory_id):
    """对已归档记忆再次归档，archived 仍为 true"""
    ...

# === GET /api/agentmemory/paginated 过滤 ===

def test_paginated_excludes_archived_by_default(client):
    """默认分页不返回已归档记忆"""
    ...

def test_paginated_includes_archived_when_flag_true(client):
    """include_archived=true 返回全部记忆（含已归档）"""
    ...

def test_archived_memory_still_searchable(client, archived_memory_id):
    """已归档记忆可通过搜索 API 找到"""
    ...

def test_archive_preserves_other_fields(client, sample_memory_id):
    """归档后其他字段（content, strength 等）不变"""
    ...

def test_archive_field_in_response(client, sample_memory_id):
    """GET 单条记忆响应包含 archived 字段"""
    ...

def test_archive_default_false(client, sample_memory_id):
    """新建记忆 archived 默认为 false"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-15-1 | **归档操作** | **P0** | 点击"归档"按钮 | 记忆从默认列表消失 |
| FE-15-2 | **取消归档** | **P0** | 开启"显示已归档" → 点击"取消归档" | 记忆恢复到默认列表 |
| FE-15-3 | **默认过滤已归档** | **P0** | 正常浏览列表 | 不显示已归档记忆 |
| FE-15-4 | 显示已归档开关 | P1 | 开启"显示已归档"开关 | 已归档记忆以半透明显示 |
| FE-15-5 | 已归档视觉标记 | P1 | 查看已归档卡片 | 半透明/灰色边框/角标 |
| FE-15-6 | 归档不影响搜索 | P1 | 搜索已归档记忆的关键词 | 搜索结果中包含已归档记忆 |
| FE-15-7 | 批量归档 | P2 | 选择多条 → 批量归档 | 全部归档成功 |

### 边界条件

- 归档所有记忆 → 列表显示空状态
- 归档后编辑该记忆 → 编辑正常，archived 状态不变
- 归档后删除该记忆 → 删除正常
- 分页场景下归档 → 当前页刷新，总数更新

### 验收检查清单（AC）

- [ ] **AC-F15-1**：归档后记忆从默认列表消失 ⭐ P0
- [ ] **AC-F15-2**：开启"显示已归档"可查看已归档记忆
- [ ] **AC-F15-3**：取消归档后恢复到默认列表 ⭐ P0
- [ ] **AC-F15-4**：默认分页不返回已归档记忆 ⭐ P0
- [ ] **AC-F15-5**：include_archived=true 返回全部
- [ ] **AC-F15-6**：归档不影响其他字段
- [ ] **AC-F15-7**：搜索可找到已归档记忆

---

## F-16 虚拟列表

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-16-1 | **≤200 条使用普通滚动** | **P0** | 50 条记忆浏览列表 | 使用普通 DOM 渲染 |
| FE-16-2 | **>200 条自动切换虚拟滚动** | **P0** | 300 条记忆浏览列表 | 自动启用虚拟滚动 |
| FE-16-3 | **虚拟滚动流畅性** | **P0** | 快速上下滚动 | 60fps，无白屏闪烁 |
| FE-16-4 | 虚拟滚动下点击 | P1 | 点击可视区域卡片 | 正常响应（展开/详情） |
| FE-16-5 | 虚拟滚动+过滤 | P1 | 过滤后条数 ≤200 | 自动切回普通滚动 |
| FE-16-6 | 虚拟滚动+搜索 | P1 | 搜索后结果 >200 | 保持虚拟滚动 |
| FE-16-7 | 初始加载性能 | P1 | 加载 500 条记忆 | 首屏渲染 < 2s |

### 后端测试

F-16 为纯前端功能，无后端 API 测试。

### 边界条件

- 恰好 200 条 → 使用普通滚动（阈值为 >200）
- 201 条 → 启用虚拟滚动
- 虚拟滚动下删除记忆至 200 条 → 切回普通滚动
- 虚拟滚动下创建记忆 → 列表更新，保持虚拟滚动模式

### 验收检查清单（AC）

- [ ] **AC-F16-1**：≤200 条使用普通滚动 ⭐ P0
- [ ] **AC-F16-2**：>200 条自动启用虚拟滚动 ⭐ P0
- [ ] **AC-F16-3**：快速滚动无卡顿 ⭐ P0
- [ ] **AC-F16-4**：虚拟滚动下功能正常
- [ ] **AC-F16-5**：过滤/搜索联动正常

---

## F-17 记忆变更通知

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_webhook.py`

```python
# === 通知触发 ===

def test_create_memory_triggers_notification(client, mock_webhook):
    """创建记忆后触发飞书通知"""
    ...

def test_update_memory_triggers_notification(client, mock_webhook, sample_memory_id):
    """编辑记忆后触发飞书通知"""
    ...

def test_delete_memory_triggers_notification(client, mock_webhook, sample_memory_id):
    """删除记忆后触发飞书通知"""
    ...

# === 通知内容 ===

def test_notification_contains_event_type(mock_webhook):
    """通知包含事件类型（created/updated/deleted）"""
    ...

def test_notification_contains_memory_title(mock_webhook):
    """通知包含记忆标题"""
    ...

def test_notification_contains_timestamp(mock_webhook):
    """通知包含操作时间戳"""
    ...

# === Webhook 配置 API ===

def test_get_webhook_config(client):
    """GET /api/webhook/config 返回当前配置"""
    ...

def test_update_webhook_config(client):
    """PUT /api/webhook/config 更新配置"""
    ...

def test_update_webhook_url(client):
    """更新 webhook URL"""
    ...

def test_disable_webhook(client):
    """禁用 webhook 后不发送通知"""
    ...

def test_disable_webhook_no_notification(client, mock_webhook):
    """禁用状态下 CRUD 操作不触发通知"""
    ...

# === 异常处理 ===

def test_webhook_failure_does_not_block_request(client, failing_webhook):
    """webhook 发送失败不阻塞主请求"""
    ...

def test_webhook_failure_logs_error(client, failing_webhook):
    """webhook 失败记录错误日志"""
    ...

def test_webhook_invalid_url(client):
    """webhook URL 无效时返回配置错误"""
    ...
```

### 前端测试

F-17 为纯后端功能，无独立前端页面。可通过以下方式验证：
- 查看飞书群消息卡片是否正确接收
- 通过 Swagger UI 测试 webhook 配置 API

### 边界条件

- webhook URL 超时（>5s）→ 不阻塞，记录超时错误
- 连续快速 CRUD → 每次操作都触发通知（不合并）
- webhook_config.json 不存在 → 使用默认配置（禁用）
- 飞书 webhook 签名密钥错误 → 发送失败，记录 403 错误

### 验收检查清单（AC）

- [ ] **AC-F17-1**：创建记忆触发飞书通知 ⭐ P0
- [ ] **AC-F17-2**：编辑记忆触发通知
- [ ] **AC-F17-3**：删除记忆触发通知
- [ ] **AC-F17-4**：webhook 配置 API 可用
- [ ] **AC-F17-5**：禁用后不发送通知
- [ ] **AC-F17-6**：发送失败不阻塞主请求
- [ ] **AC-F17-7**：消息卡片格式正确

---

## 测试汇总

| 功能 | 后端用例数 | 前端用例数 | 边界条件数 | AC 数 |
|------|-----------|-----------|-----------|-------|
| F-12 版本更新说明 | 7 | 6 | 4 | 6 |
| F-13 暗色模式 | 0 | 9 | 4 | 5 |
| F-14 时间线视图 | 0 | 8 | 4 | 5 |
| F-15 记忆归档 | 10 | 7 | 4 | 7 |
| F-16 虚拟列表 | 0 | 7 | 4 | 5 |
| F-17 记忆变更通知 | 14 | 0 | 4 | 7 |
| **合计** | **31** | **37** | **24** | **35** |

### 新增测试文件清单

| 文件 | 用例数 | 功能 |
|------|--------|------|
| `backend/tests/test_changelog.py` | 7 | F-12 changelog API |
| `backend/tests/test_agentmemory_archive.py` | 10 | F-15 归档 API |
| `backend/tests/test_webhook.py` | 14 | F-17 通知 + webhook API |

### 执行优先级

#### ⭐ P0 — 必须通过（上线阻塞）

| 用例 | 功能 | 说明 |
|------|------|------|
| FE-12-1 | 首次访问自动弹窗 | 核心交互，首次体验 |
| FE-12-3 | 版本更新后重新弹出 | 版本比对逻辑正确性 |
| FE-13-1 | Light/Dark 切换 | 核心功能 |
| FE-13-2 | 跟随系统模式 | 三种模式之一 |
| FE-13-3 | 主题持久化 | 用户体验基本要求 |
| FE-14-1 | 时间线页面渲染 | 核心功能 |
| FE-14-2 | 日期分组正确性 | 核心逻辑 |
| FE-15-1 | 归档操作 | 核心功能 |
| FE-15-3 | 默认过滤已归档 | 数据隔离正确性 |
| FE-15-4 | 取消归档 | 可逆操作 |
| FE-16-1 | ≤200 条普通滚动 | 不影响现有行为 |
| FE-16-2 | >200 条虚拟滚动 | 核心功能 |
| FE-16-3 | 虚拟滚动流畅性 | 性能指标 |
| FE-17-1 | 创建触发通知 | 核心功能 |
| test_paginated_excludes_archived_by_default | 归档过滤 | 数据正确性 |
| test_archive_memory | 归档 API | 核心 API |
| test_create_memory_triggers_notification | 通知触发 | 核心 API |

#### 🟡 P1 — 应该通过（影响用户体验）

| 用例 | 功能 | 说明 |
|------|------|------|
| FE-12-4 | Markdown 渲染 | 内容展示质量 |
| FE-12-5 | 侧边栏手动查看 | 入口可用性 |
| FE-13-4 | 无 FOUC 闪烁 | 视觉体验 |
| FE-13-5 | 暗色模式文字可读 | 可访问性 |
| FE-13-6 | Dashboard 暗色适配 | 子页面一致性 |
| FE-14-3 | 时间轴视觉元素 | 视觉完整性 |
| FE-14-4 | 卡片内容完整 | 信息展示 |
| FE-15-5 | 显示已归档开关 | 高级功能 |
| FE-15-6 | 归档不影响搜索 | 搜索完整性 |
| FE-16-4 | 虚拟滚动下点击 | 交互可用性 |
| FE-16-5 | 虚拟滚动+过滤联动 | 功能集成 |
| FE-17-2 | 编辑触发通知 | 通知完整性 |
| FE-17-3 | 删除触发通知 | 通知完整性 |
| test_changelog_ordered_by_version_desc | API 数据正确性 | 排序逻辑 |
| test_unarchive_memory | 取消归档 API | 可逆操作 |
| test_notification_contains_event_type | 通知内容 | 消息质量 |

#### 🟢 P2 — 最好通过（边界和优化）

| 用例 | 功能 | 说明 |
|------|------|------|
| FE-12-6 | Modal 关闭方式 | 交互细节 |
| FE-13-8 | 暗色搜索高亮 | 视觉细节 |
| FE-13-9 | 三态循环切换 | 交互细节 |
| FE-14-8 | 大数据量渲染 | 性能边界 |
| FE-15-7 | 批量归档 | 高级功能 |
| FE-16-6 | 虚拟滚动+搜索 | 集成边界 |
| FE-16-7 | 初始加载性能 | 性能指标 |
| test_webhook_failure_does_not_block_request | 异常处理 | 健壮性 |
| test_archive_toggle_idempotent | 幂等性 | 边界逻辑 |
| 所有边界条件用例 | 各功能 | 边界覆盖 |

### 已有测试影响

现有 41 个测试用例（P0+P1）**不修改**，P2 新增 31 个后端用例，预计总计 **72 个**后端测试。

> 注：F-15 归档功能修改了分页 API 的默认行为（默认排除已归档），需确认现有分页测试是否受影响。如有冲突，需同步更新现有测试的 fixture 数据。

---

## 评审附录（qa-worker）

> **评审日期**: 2026-05-29
> **评审结论**: ⚠️ **需补充** — 现有 68 个用例覆盖了主要功能路径，但存在 **15 个遗漏场景**，建议补充后通过。

---

### 一、逐功能评审

#### F-12 版本更新说明 — ⚠️ 需补充 3 条

| # | 遗漏场景 | 严重程度 | 说明 |
|---|---------|---------|------|
| 1 | **版本降级场景** | 🟡 中 | 用户从 v2.1 降级到 v2.0，localStorage 中 `lastReadVersion` 高于当前版本。应不弹窗还是重置？测试计划未覆盖此路径。 |
| 2 | **localStorage `lastReadVersion` 被手动篡改/损坏** | 🟢 低 | 值为非法字符串（如 `"abc"`）时，版本比对逻辑是否能兜底？ |
| 3 | **changelog 数据为空数组 `[]`** | — | 已列为边界条件但**未纳入测试用例编号**，建议增加 FE-12-7。 |

#### F-13 暗色模式 — ⚠️ 需补充 3 条

| # | 遗漏场景 | 严重程度 | 说明 |
|---|---------|---------|------|
| 4 | **系统偏好实时变化监听** | 🟡 中 | FE-13-2 测了"选择系统模式→OS切换"，但未明确验证 `matchMedia('prefers-color-scheme').addEventListener('change', ...)` 的实时回调。应补充：在页面运行中改变系统暗色模式，页面是否**无需刷新**自动切换。 |
| 5 | **第三方组件库主题冲突** | 🟡 中 | 迭代计划提到使用 CSS 变量方案，但未测试 Element Plus / Ant Design Vue 等组件库的内置主题是否与自定义 `data-theme` 冲突。如有组件库依赖，需验证。 |
| 6 | **SSR 预渲染场景** | 🟢 低 | 虽项目为 SPA 不需要 SSR，但若未来部署到 Nuxt 等环境，`localStorage` 在服务端不可用。建议在边界条件中明确标注"SPA only，不考虑 SSR"即可。 |

#### F-14 时间线视图 — ⚠️ 需补充 3 条

| # | 遗漏场景 | 严重程度 | 说明 |
|---|---------|---------|------|
| 7 | **>1000 条记忆的时间线性能** | 🟡 中 | FE-14-8 只测了 200+ 条，但迭代计划中虚拟列表阈值为 200，时间线视图作为独立页面也需要验证 1000+ 条场景（含虚拟列表集成）。 |
| 8 | **时区处理** | 🟡 中 | 迭代计划提到按 `createdAt` 分组，但未明确时区。若服务器 UTC、客户端 UTC+8，"今天"的分组可能不一致。需要测试用例验证。 |
| 9 | **跨年日期分组** | — | 已列为边界条件但**未纳入测试用例编号**，建议增加 FE-14-9。 |

#### F-15 记忆归档 — ⚠️ 需补充 3 条

| # | 遗漏场景 | 严重程度 | 说明 |
|---|---------|---------|------|
| 10 | **归档后统计数据交互** | 🟡 中 | Dashboard 统计面板（P1 已完成）是否包含已归档记忆？归档后统计数字是否变化？测试计划未覆盖归档与统计的联动。 |
| 11 | **批量归档部分失败** | 🟡 中 | FE-15-7 只测了"全部归档成功"，未测批量操作中某条 ID 不存在（404）时的处理：是全部回滚还是部分成功？ |
| 12 | **归档操作是否触发 F-17 通知** | 🟡 中 | 归档是 PATCH 操作，但 F-17 通知只测了 CRUD（create/update/delete）。归档/取消归档是否应触发通知？迭代计划未明确，需确认设计意图。 |

#### F-16 虚拟列表 — ⚠️ 需补充 2 条

| # | 遗漏场景 | 严重程度 | 说明 |
|---|---------|---------|------|
| 13 | **动态切换时滚动位置保持** | 🟡 中 | 用户在列表中间位置时，过滤/搜索导致数量从 >200 变为 ≤200（或反向），切换模式后滚动位置是否跳到顶部？需验证。 |
| 14 | **虚拟滚动下键盘导航** | 🟢 低 | 迭代计划提到 P0+P1 有快捷键功能，虚拟滚动下 Tab/方向键导航是否正常？ |

#### F-17 记忆变更通知 — ⚠️ 需补充 2 条

| # | 遗漏场景 | 严重程度 | 说明 |
|---|---------|---------|------|
| 15 | **webhook 失败重试机制** | 🟡 中 | 测试计划有"失败不阻塞"和"记录错误日志"，但未验证是否**重试**。迭代计划提到 `asyncio` 异步化，是否包含重试策略（如 exponential backoff）？需明确并测试。 |
| 16 | **webhook URL 无效时配置 API 的行为** | — | `test_webhook_invalid_url` 存在但描述模糊。应明确：是在 PUT 配置时校验 URL 格式（即时报错），还是发送时才发现？ |

---

### 二、跨功能集成遗漏

| # | 场景 | 说明 |
|---|------|------|
| 17 | **F-13 × F-12**：暗色模式下 What's New Modal 样式 | 迭代计划明确提到"F-13 需覆盖 F-12 Modal 样式"，但测试计划中 FE-13-7 只写了"打开创建/编辑 Modal"，未包含 What's New Modal。 |
| 18 | **F-13 × F-14**：暗色模式下时间线视图 | 迭代计划提到需覆盖，但测试计划未明确测试时间线在暗色模式下的渲染。 |
| 19 | **F-15 × F-16**：归档后虚拟列表模式切换 | 归档大量记忆使总数从 >200 降至 ≤200，是否正确切回普通滚动？ |
| 20 | **F-15 × F-14**：已归档记忆在时间线视图中是否显示 | 时间线视图是否默认过滤已归档记忆？迭代计划未明确。 |

---

### 三、建议补充的测试用例

```python
# === F-12 补充 ===

def test_changelog_empty_array(client):
    """CHANGELOG.json 为空数组 → 返回空列表，前端显示'暂无更新记录'"""

# 前端补充
# FE-12-7: localStorage lastReadVersion 值损坏 → 不崩溃，默认弹窗
# FE-12-8: 版本降级场景（当前版本 < lastReadVersion）→ 不弹窗或重置

# === F-13 补充 ===

# FE-13-10: 系统偏好实时变化（matchMedia change 事件）→ 页面自动切换，无需刷新
# FE-13-11: 暗色模式下 What's New Modal 样式正确
# FE-13-12: 暗色模式下 TimelineView 样式正确

# === F-14 补充 ===

# FE-14-9: 跨年日期（2025-12-31 + 2026-01-01）→ 分组正确显示年份
# FE-14-10: 1000+ 条记忆时间线性能 → 配合虚拟列表流畅渲染
# FE-14-11: 时区一致性 → 服务器 UTC、客户端 UTC+8 下"今天"分组正确

# === F-15 补充 ===

# FE-15-8: 归档后 Dashboard 统计数字更新
# FE-15-9: 批量归档部分失败 → 返回错误详情，成功的仍生效（或全部回滚，需明确）
# BE-F15-10: 归档操作是否触发 webhook 通知（需确认设计意图）

# === F-16 补充 ===

# FE-16-8: 动态切换模式时滚动位置保持（不跳到顶部）
# FE-16-9: 虚拟滚动下 Tab/方向键键盘导航正常

# === F-17 补充 ===

# test_webhook_retry_on_failure: webhook 失败后是否重试（如有重试机制）
# test_webhook_config_invalid_url_format: PUT 配置时 URL 格式校验
```

---

### 四、评审总结

| 维度 | 评价 |
|------|------|
| 功能路径覆盖 | ✅ 良好，主要 happy path 和主要异常路径均已覆盖 |
| 边界条件覆盖 | ⚠️ 部分边界条件仅列在文字描述中，未纳入正式用例编号（如 F-12 空数组、F-14 跨年） |
| 跨功能集成 | ❌ 缺失，F-13 暗色模式与其他功能的集成测试不足 |
| 并发/重试 | ❌ F-17 重试策略未明确，缺少相关用例 |
| 数据交互 | ⚠️ F-15 归档与统计/时间线/通知的交互未覆盖 |

**结论**：现有 68 用例 + 41 回归用例 = 109 用例基础扎实，建议补充 **20 条**遗漏用例（12 条前端 + 2 条后端 + 6 条跨功能），补充后预计总计 **129 条**，可满足 P2 上线质量要求。
