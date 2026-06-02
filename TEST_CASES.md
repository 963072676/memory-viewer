# Memory Viewer v2 — 测试用例文档

> 作者: qa-worker | 日期: 2026-05-28 | 版本: 1.0
> 基线: PM_SPEC.md v2.1 (1015行) + QA_TEST_PLAN.md (回归 + 架构)
> 覆盖: 18 个功能 + 6 个 API 端点 + 25 条验收标准

---

## 一、测试范围与策略

### 1.1 覆盖范围

| 类别 | 数量 | 说明 |
|------|------|------|
| P0 功能 (F-01~F-06) | 6 | 暗色模式、排序、展开折叠、Swagger、搜索高亮、快捷键 |
| P1 功能 (F-07~F-12) | 6 | 高级搜索、编辑、删除、统计、自动刷新、导出 |
| P2 功能 (F-13~F-18) | 6 | 创建、时间线、归档、虚拟列表、通知、导入 |
| API 端点 | 6 | 3 个兼容 + 3 个新增 |
| 架构重构 | 5 | 前后端分离、Docker、CORS |
| **合计** | **29** | 功能/架构维度 |

### 1.2 测试分类

| 分类 | 用例数 | 说明 |
|------|--------|------|
| 功能测试 | 97 | 功能行为验证 |
| API 测试 | 48 | 接口契约验证 |
| 前端测试 | 35 | 组件/交互验证 |
| 非功能测试 | 18 | 性能/安全/兼容性 |
| **总计** | **198** | |

### 1.3 优先级分布

| 优先级 | 数量 | 占比 |
|--------|------|------|
| P0 | 52 | 26% |
| P1 | 108 | 55% |
| P2 | 38 | 19% |

---

## 二、P0 功能测试用例

### F-01 暗色模式

#### 功能测试

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F01-01 | 系统暗色自动切换 | 系统偏好设为暗色模式 | 1. 打开页面 | 自动应用暗色主题 | P0 |
| TC-F01-02 | 手动切换暗色 | 默认亮色模式 | 1. 点击 Header 右侧 🌙 按钮 | 切换到暗色模式 | P0 |
| TC-F01-03 | 手动切换亮色 | 暗色模式下 | 1. 点击 ☀️ 按钮 | 切换回亮色模式 | P0 |
| TC-F01-04 | 切换后刷新保持 | 手动切换为暗色 | 1. 刷新页面 | 仍为暗色模式（localStorage 持久化） | P0 |
| TC-F01-05 | 手动覆盖系统偏好 | 系统为亮色 | 1. 手动切换为暗色 2. 刷新页面 | 暗色模式保持，不跟随系统 | P1 |
| TC-F01-06 | 暗色模式对比度 | 暗色模式开启 | 1. 检查所有文本/背景组合 | 对比度 ≥ 4.5:1（WCAG AA） | P0 |
| TC-F01-07 | CSS 变量切换 | 暗色模式开启 | 1. 检查 `--bg`, `--card`, `--text-secondary`, `--accent` 值 | 值符合暗色定义（如 `--bg: #1d1d1f`） | P1 |
| TC-F01-08 | 所有组件暗色兼容 | 暗色模式开启 | 1. 浏览所有页面/组件 | 无白色背景残留、无可读性问题 | P0 |
| TC-F01-09 | 切换动画 | 亮色→暗色 | 1. 点击切换按钮 | 平滑过渡，无闪烁 | P2 |
| TC-F01-10 | `data-theme` 属性 | 暗色模式开启 | 1. 检查 `<html>` 或 `<body>` 的 `data-theme` 属性 | `data-theme="dark"` | P1 |

### F-02 记忆排序

#### 功能测试

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F02-01 | 按时间降序（默认） | 有多条记忆 | 1. 打开页面 | 最新条目在前 | P0 |
| TC-F02-02 | 按时间升序 | 有多条记忆 | 1. 选择排序：时间↑ | 最旧条目在前 | P1 |
| TC-F02-03 | 按强度降序 | 有多条记忆 | 1. 选择排序：强度↓ | strength 高的在前 | P0 |
| TC-F02-04 | 按强度升序 | 有多条记忆 | 1. 选择排序：强度↑ | strength 低的在前 | P1 |
| TC-F02-05 | 按类型排序 | 有多条不同类型记忆 | 1. 选择排序：类型 A-Z | 相同类型聚合在一起 | P0 |
| TC-F02-06 | 排序状态 URL 分享 | 按强度排序 | 1. 复制当前 URL 2. 新标签打开 | URL 含 `?sort=strength&order=desc`，排序状态恢复 | P1 |
| TC-F02-07 | 排序控件位置 | - | 1. 查看页面 | 排序下拉在 SearchBar 或 StatsBar 旁 | P2 |
| TC-F02-08 | 排序后展开/折叠状态 | 部分卡片展开 | 1. 切换排序 | 展开/折叠状态保持 | P1 |
| TC-F02-09 | 排序与搜索联动 | 搜索结果中 | 1. 搜索关键词 2. 切换排序 | 搜索结果按新排序排列 | P1 |
| TC-F02-10 | 排序参数后端验证 | - | 1. `GET /api/agentmemory/paginated?sort=strength&order=desc` | 返回按 strength 降序排列 | P0 |

### F-03 记忆详情展开/折叠

#### 功能测试

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F03-01 | 默认折叠态 | - | 1. 打开页面 | 卡片显示 title + content 前 100 字符 + type tag | P0 |
| TC-F03-02 | 折叠态信息密度 | - | 1. 对比展开/折叠态屏幕可见条目数 | 折叠态条目数 ≥ 2x 展开态 | P0 |
| TC-F03-03 | 点击展开单条 | 折叠态 | 1. 点击某卡片 | 展开显示完整 content + concepts + files + strength + 时间 | P0 |
| TC-F03-04 | 再次点击折叠 | 展开态 | 1. 点击已展开卡片 | 折叠回摘要态 | P0 |
| TC-F03-05 | 展开动画流畅 | - | 1. 展开卡片 | CSS transition 动画 60fps | P1 |
| TC-F03-06 | 全部展开按钮 | - | 1. 点击"全部展开" | 所有卡片展开 | P0 |
| TC-F03-07 | 全部折叠按钮 | 全部展开态 | 1. 点击"全部折叠" | 所有卡片折叠 | P0 |
| TC-F03-08 | 展开态显示 concepts | 展开某卡片 | 1. 查看展开内容 | concepts 标签列表可见 | P1 |
| TC-F03-09 | 展开态显示 files | 展开某含 files 记忆 | 1. 查看展开内容 | files 列表可见 | P1 |
| TC-F03-10 | 长内容截断（折叠态） | content > 100 字符 | 1. 查看折叠态 | 显示前 100 字符 + "..." | P1 |
| TC-F03-11 | 短内容不截断 | content < 100 字符 | 1. 查看折叠态 | 显示完整内容，无 "..." | P2 |

### F-04 Swagger API 文档

#### 功能测试

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F04-01 | Swagger 页面可访问 | 后端运行 | 1. 访问 `/api/docs` | 返回 Swagger UI 页面 | P0 |
| TC-F04-02 | Redoc 页面可访问 | 后端运行 | 1. 访问 `/api/redoc` | 返回 Redoc 页面 | P1 |
| TC-F04-03 | 文档包含所有端点 | - | 1. 查看 Swagger 文档 | 列出所有 `/api/*` 端点 | P1 |
| TC-F04-04 | 文档 title/description | - | 1. 查看 OpenAPI spec | title/description 已配置 | P2 |
| TC-F04-05 | 可在 Swagger 中测试 | - | 1. 在 Swagger UI 中调用 `GET /api/health` | 返回 200 + JSON | P2 |

### F-05 搜索高亮渲染

#### 功能测试

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F05-01 | 搜索关键词高亮 | 搜索"hermes" | 1. 查看搜索结果 | 关键词以黄色高亮显示 | P0 |
| TC-F05-02 | 高亮样式正确 | 搜索结果中 | 1. 检查高亮元素 | `<em>` 标签，`background: #fff3cd`，`padding: 1px 2px`，`border-radius: 2px` | P1 |
| TC-F05-03 | 仅搜索模式高亮 | 正常浏览（无搜索） | 1. 查看记忆列表 | 无高亮标签 | P0 |
| TC-F05-04 | XSS 过滤 | 搜索含 `<script>` | 1. 搜索 `<script>alert(1)</script>` | 不执行脚本，`<script>` 被转义 | P0 |
| TC-F05-05 | 仅允许 `<em>` 标签 | matchSnippet 含 `<b>` | 1. 检查渲染 | `<b>` 被过滤，仅 `<em>` 保留 | P1 |
| TC-F05-06 | 多关键词高亮 | 搜索结果匹配多个位置 | 1. 查看结果 | 每个匹配位置都高亮 | P1 |
| TC-F05-07 | 大小写不敏感高亮 | 搜索"Hermes"（大小写混合数据） | 1. 查看结果 | "hermes"、"HERMES"、"Hermes" 均高亮 | P2 |
| TC-F05-08 | matchSnippet 字段存在 | `GET /api/search?q=hermes` | 1. 检查响应 | 每条结果含 `matchField` + `matchSnippet` | P0 |

### F-06 键盘快捷键

#### 功能测试

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F06-01 | `/` 聚焦搜索 | 无输入框聚焦 | 1. 按 `/` | 搜索输入框获焦 | P0 |
| TC-F06-02 | `Esc` 清除搜索 | 搜索框有内容 | 1. 按 `Esc` | 搜索内容清空 | P0 |
| TC-F06-03 | `R` 刷新数据 | - | 1. 按 `R` | 触发数据刷新 | P0 |
| TC-F06-04 | `1` 切换"全部" Tab | - | 1. 按 `1` | 切换到"全部" Tab | P1 |
| TC-F06-05 | `2` 切换"AgentMemory" Tab | - | 1. 按 `2` | 切换到 AgentMemory Tab | P1 |
| TC-F06-06 | `3` 切换"Hermes Memory" Tab | - | 1. 按 `3` | 切换到 Hermes Memory Tab | P1 |
| TC-F06-07 | 输入框内不触发快捷键 | 搜索框获焦 | 1. 输入 `/` | `/` 字符输入到搜索框，不触发聚焦 | P1 |
| TC-F06-08 | 全局 keydown 监听 | - | 1. 检查代码 | 存在 `document.addEventListener('keydown', ...)` | P2 |

---

## 三、P1 功能测试用例

### F-07 高级搜索面板

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F07-01 | 高级搜索面板打开 | - | 1. 点击高级搜索入口 | FilterPanel 组件展开 | P1 |
| TC-F07-02 | 类型多选过滤 | FilterPanel 打开 | 1. 勾选 "pattern" + "fact" | 仅显示这两类记忆 | P1 |
| TC-F07-03 | 时间范围过滤 | FilterPanel 打开 | 1. 选择时间范围 picker | 仅显示该时间段的记忆 | P1 |
| TC-F07-04 | Strength 滑块过滤 | FilterPanel 打开 | 1. 拖动 strength 滑块到 5-10 | 仅显示 strength 5~10 的记忆 | P1 |
| TC-F07-05 | 数据源切换 | FilterPanel 打开 | 1. 切换到 "hermes" | 仅显示 hermes memory 结果 | P1 |
| TC-F07-06 | 多条件组合过滤 | - | 1. 选择类型=pattern + 时间范围 + source=agentmemory | 结果同时满足所有条件 | P1 |
| TC-F07-07 | 清除所有过滤器 | 已设置多个过滤 | 1. 点击"清除" | 所有过滤器重置，显示全部 | P1 |
| TC-F07-08 | 搜索 API 参数扩展 | - | 1. `GET /api/search?q=test&type=pattern&profile=daily` | 返回同时匹配 type 和 profile 的结果 | P0 |

### F-08 记忆编辑

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F08-01 | 编辑按钮可见 | 展开某 agentmemory 卡片 | 1. 查看展开内容 | 编辑按钮可见 | P1 |
| TC-F08-02 | 编辑弹窗打开 | - | 1. 点击编辑按钮 | EditModal 弹窗打开，显示当前 content/concepts/strength | P1 |
| TC-F08-03 | 修改 content | 编辑弹窗打开 | 1. 修改 content 2. 保存 | content 更新成功 | P1 |
| TC-F08-04 | 修改 concepts | 编辑弹窗打开 | 1. 添加/删除 concept 标签 2. 保存 | concepts 更新成功 | P1 |
| TC-F08-05 | 修改 strength | 编辑弹窗打开 | 1. 调整 strength 滑块 2. 保存 | strength 更新成功 | P1 |
| TC-F08-06 | PUT API 验证 | - | 1. `PUT /api/agentmemory/{id}` with body | 返回 200 + 更新后的记忆对象 | P0 |
| TC-F08-07 | 编辑后列表刷新 | 编辑保存后 | 1. 查看列表 | 列表显示更新后的内容 | P1 |
| TC-F08-08 | 编辑取消 | 编辑弹窗打开 | 1. 点击取消 | 弹窗关闭，数据不变 | P1 |
| TC-F08-09 | 编辑态展开 | 依赖 F-03 | 1. 展开卡片 2. 点击编辑 | 编辑态从展开态进入 | P1 |

### F-09 记忆删除

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F09-01 | 删除按钮可见 | 展开某 agentmemory 卡片 | 1. 查看展开内容 | 删除按钮可见 | P1 |
| TC-F09-02 | 删除确认弹窗 | - | 1. 点击删除按钮 | ConfirmDialog 弹窗出现 | P0 |
| TC-F09-03 | 确认删除 | 确认弹窗打开 | 1. 点击确认 | 记忆被删除，列表刷新 | P1 |
| TC-F09-04 | 取消删除 | 确认弹窗打开 | 1. 点击取消 | 弹窗关闭，记忆仍在 | P1 |
| TC-F09-05 | DELETE API 验证 | - | 1. `DELETE /api/agentmemory/{id}` | 返回 200/204 | P0 |
| TC-F09-06 | 批量删除 | 多条选中 | 1. 选中多条 2. 点击批量删除 3. 确认 | 选中条目全部删除 | P1 |
| TC-F09-07 | 删除审计日志 | 删除操作后 | 1. 检查后端日志 | 记录删除操作（谁、何时、删了什么） | P2 |
| TC-F09-08 | 删除不存在的 ID | - | 1. `DELETE /api/agentmemory/nonexistent` | 返回 404 | P1 |

### F-10 统计仪表盘

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F10-01 | 仪表盘页面可访问 | - | 1. 导航到仪表盘 | DashboardView 加载 | P1 |
| TC-F10-02 | 按类型饼图 | 有不同类型记忆 | 1. 查看饼图 | 正确显示各类型占比 | P1 |
| TC-F10-03 | 按时间折线图 | 有不同时间记忆 | 1. 查看折线图 | 正确显示时间分布 | P1 |
| TC-F10-04 | 按 profile 柱状图 | 有多个 profile | 1. 查看柱状图 | 正确显示各 profile 记忆数 | P1 |
| TC-F10-05 | Strength 分布图 | - | 1. 查看 strength 分布 | 正确显示 strength 分布 | P1 |
| TC-F10-06 | Stats API 验证 | - | 1. `GET /api/stats` | 返回 200 + 统计 JSON | P0 |
| TC-F10-07 | 空数据仪表盘 | 无记忆数据 | 1. 查看仪表盘 | 显示空状态，图表不报错 | P1 |

### F-11 缓存自动刷新

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F11-01 | 定时任务启动 | 后端启动 | 1. 检查日志 | APScheduler 定时任务已注册 | P1 |
| TC-F11-02 | 30 分钟自动刷新 | 后端运行 > 30 分钟 | 1. 检查缓存文件修改时间 | 每 30 分钟自动更新 | P1 |
| TC-F11-03 | 自动刷新 API 数据 | 新增一条记忆 | 1. 等待 30 分钟 2. 调用 API | 新记忆出现在结果中 | P1 |
| TC-F11-04 | 定时任务不阻塞请求 | 自动刷新执行中 | 1. 同时发起 API 请求 | API 请求正常响应 | P1 |

### F-12 记忆导出

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F12-01 | 导出按钮可见 | - | 1. 查看页面 | ExportButton 组件可见 | P1 |
| TC-F12-02 | JSON 格式导出 | - | 1. 选择 JSON 格式 2. 点击导出 | 下载 `.json` 文件，内容为有效 JSON | P1 |
| TC-F12-03 | Markdown 格式导出 | - | 1. 选择 Markdown 格式 2. 点击导出 | 下载 `.md` 文件，内容为有效 Markdown | P1 |
| TC-F12-04 | 单条导出 | 展开某卡片 | 1. 点击该条导出 | 仅导出该条记忆 | P1 |
| TC-F12-05 | 全量导出 | - | 1. 点击"全部导出" | 导出所有记忆 | P1 |
| TC-F12-06 | 导出 API 验证 | - | 1. `GET /api/agentmemory/export` | 返回 200 + JSON/Markdown 内容 | P0 |
| TC-F12-07 | 空数据导出 | 无记忆 | 1. 点击导出 | 导出空文件或提示无数据 | P2 |

---

## 四、P2 功能测试用例

### F-13 记忆创建

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F13-01 | 创建入口 | - | 1. 查看页面 | "新建记忆"按钮可见 | P2 |
| TC-F13-02 | 创建表单 | - | 1. 点击创建入口 | 创建表单弹窗打开 | P2 |
| TC-F13-03 | 填写并提交 | 创建表单打开 | 1. 填写 title/content/type/concepts 2. 提交 | 新记忆创建成功，列表刷新 | P2 |
| TC-F13-04 | POST API 验证 | - | 1. `POST /api/agentmemory` with body | 返回 201 + 新记忆对象 | P1 |
| TC-F13-05 | 概念标签输入 | 创建表单打开 | 1. 输入概念标签 | 标签可添加/删除 | P2 |
| TC-F13-06 | 创建必填校验 | 表单为空 | 1. 直接提交 | 显示必填字段错误提示 | P2 |

### F-14 时间线视图

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F14-01 | 时间线视图入口 | - | 1. 切换到时间线视图 | TimelineView 加载 | P2 |
| TC-F14-02 | 按日期分组 | 有多条不同日期记忆 | 1. 查看时间线 | 记忆按日期分组显示 | P2 |
| TC-F14-03 | 时间线缩放 | - | 1. 缩放时间线 | 可放大/缩小查看 | P2 |
| TC-F14-04 | 空日期不显示 | 某日期无记忆 | 1. 查看时间线 | 该日期不出现在时间线中 | P2 |

### F-15 记忆归档

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F15-01 | 归档按钮 | 展开某卡片 | 1. 点击归档 | 记忆标记为归档 | P2 |
| TC-F15-02 | 归档后默认不显示 | 有归档记忆 | 1. 查看列表 | 归档记忆不显示 | P2 |
| TC-F15-03 | 归档可检索 | 有归档记忆 | 1. 搜索归档记忆内容 | 搜索结果中能找到 | P2 |
| TC-F15-04 | 取消归档 | 归档记忆 | 1. 查看归档列表 2. 取消归档 | 记忆恢复为正常状态 | P2 |

### F-16 虚拟列表

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F16-01 | < 200 条不启用 | 记忆 < 200 条 | 1. 查看列表 | 正常列表渲染，无虚拟滚动 | P2 |
| TC-F16-02 | > 200 条启用 | 记忆 > 200 条 | 1. 查看列表 | 启用虚拟滚动 | P2 |
| TC-F16-03 | 虚拟滚动性能 | 记忆 > 200 条 | 1. 快速滚动 | 无卡顿，DOM 节点数稳定 | P2 |

### F-17 记忆变更通知

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F17-01 | Webhook 配置 | 配置飞书 webhook | 1. 创建/编辑/删除记忆 | 飞书收到通知 | P2 |
| TC-F17-02 | 通知内容格式 | - | 1. 触发通知 | 通知含操作类型、记忆标题、时间 | P2 |
| TC-F17-03 | Webhook 失败处理 | Webhook URL 无效 | 1. 触发通知 | 后端不崩溃，记录错误日志 | P2 |

### F-18 记忆导入

| 用例 ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|----------|--------|
| TC-F18-01 | 导入入口 | - | 1. 查看页面 | 导入按钮可见 | P2 |
| TC-F18-02 | JSON 文件导入 | 准备有效 JSON 文件 | 1. 上传 JSON 文件 | 记忆导入成功 | P2 |
| TC-F18-03 | 导入校验 | 准备格式错误文件 | 1. 上传 | 显示格式错误提示 | P2 |
| TC-F18-04 | 导入去重 | 导入已有记忆 | 1. 上传包含已有 ID 的 JSON | 重复记忆被跳过或合并 | P2 |
| TC-F18-05 | 批量导入 | 准备大量记忆 JSON | 1. 上传 | 全部导入成功，进度提示 | P2 |

---

## 五、API 端点测试用例

### 5.1 向后兼容端点

#### GET /api/agentmemory

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-API-01 | 返回 200 | `GET /api/agentmemory` | 200, `{memories: [...]}` | P0 |
| TC-API-02 | 字段完整性 | 检查每条记录 | 含 id/type/title/content/concepts/files/createdAt/updatedAt/strength/version/isLatest/sessionIds | P0 |
| TC-API-03 | 空缓存 | 缓存文件不存在 | `{memories: []}` | P0 |
| TC-API-04 | 缓存损坏 | JSON 解析失败 | `{memories: []}` | P1 |
| TC-API-05 | 特殊字符保留 | 数据含 `<script>`, emoji 🧠, 换行符 | 原样返回 | P0 |
| TC-API-06 | v1/v2 响应一致 | 对比 v1 和 v2 的 JSON diff | diff 为空 | P0 |

#### GET /api/hermes-memory

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-API-07 | 返回 200 | `GET /api/hermes-memory` | 200, `{global: {memory, user}, profiles: {}}` | P0 |
| TC-API-08 | § 分隔符解析 | 数据含多条 § 分隔 | 正确拆分、trim | P0 |
| TC-API-09 | 空文件 | MEMORY.md 不存在 | 返回空数组 | P1 |
| TC-API-10 | 单条/多条边界 | 单条记忆、多条记忆 | 解析正确 | P1 |
| TC-API-11 | v1/v2 响应一致 | 对比 v1 和 v2 的 JSON diff | diff 为空 | P0 |

#### GET /api/profiles

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-API-12 | 返回列表 | `GET /api/profiles` | 200, 含所有有 memories 目录的 profile | P0 |
| TC-API-13 | 排除无 memories 目录 | 存在 `no-memories` profile | 该 profile 不在结果中 | P1 |
| TC-API-14 | v1/v2 响应一致 | 对比 v1 和 v2 的 JSON diff | diff 为空 | P0 |

### 5.2 新增端点

#### GET /api/health

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-API-15 | 返回 200 | `GET /api/health` | 200, JSON 含 status/version/uptime_seconds/cache_age_seconds/agentmemory_count/hermes_memory_count | P0 |
| TC-API-16 | status 值 | 检查 status 字段 | `"ok"` | P0 |
| TC-API-17 | version 格式 | 检查 version 字段 | `"2.0.0"` 或类似 semver | P1 |
| TC-API-18 | uptime_seconds 合理 | 启动后立即检查 | ≥ 0 | P1 |
| TC-API-19 | count 准确 | 对比实际数据 | agentmemory_count/hermes_memory_count 与实际数据量一致 | P1 |

#### GET /api/search

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-API-20 | 基本搜索 | `GET /api/search?q=hermes` | 200, `{query, total, limit, offset, results}` | P0 |
| TC-API-21 | 跨数据源搜索 | 搜索关键词存在于 agentmemory 和 hermes | results 含两种 source | P0 |
| TC-API-22 | source 过滤 | `?q=test&source=agentmemory` | results 仅含 agentmemory | P0 |
| TC-API-23 | type 过滤 | `?q=test&type=pattern` | results 仅含 type=pattern | P0 |
| TC-API-24 | profile 过滤 | `?q=test&profile=daily` | results 仅含 profile=daily | P0 |
| TC-API-25 | 分页 | `?q=test&limit=2&offset=0` | total 不变, results ≤ 2 条 | P0 |
| TC-API-26 | 分页翻页 | `?q=test&limit=2&offset=2` | offset=2, 返回第 3-4 条 | P1 |
| TC-API-27 | 空结果 | `?q=nonexistent_xyz` | total=0, results=[] | P1 |
| TC-API-28 | 缺少 q 参数 | `GET /api/search` | 400/422 错误 | P0 |
| TC-API-29 | matchField 字段 | 检查每条结果 | matchField 指明匹配字段（title/content/concepts） | P1 |
| TC-API-30 | matchSnippet 字段 | 检查每条结果 | matchSnippet 含 `<em>` 高亮标签 | P0 |
| TC-API-31 | limit 默认值 | 不传 limit | 默认 50 | P1 |
| TC-API-32 | limit 最大值 | `?q=test&limit=300` | 限制为 200 | P1 |

#### GET /api/agentmemory/paginated

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-API-33 | 基本分页 | `GET /api/agentmemory/paginated` | 200, `{total, limit, offset, memories}` | P0 |
| TC-API-34 | 排序 | `?sort=strength&order=desc` | 按 strength 降序 | P0 |
| TC-API-35 | 排序方向 | `?sort=strength&order=asc` | 按 strength 升序 | P1 |
| TC-API-36 | 类型过滤 | `?type=pattern` | 仅返回 pattern 类型 | P1 |
| TC-API-37 | limit/offset | `?limit=5&offset=3` | 返回第 4-8 条 | P1 |
| TC-API-38 | 默认值 | 不传参数 | limit=50, offset=0, sort=updatedAt, order=desc | P1 |

#### PUT /api/agentmemory/{id}

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-API-39 | 正常更新 | `PUT /api/agentmemory/{id}` with body | 200 + 更新后对象 | P0 |
| TC-API-40 | 更新不存在的 ID | `PUT /api/agentmemory/nonexistent` | 404 | P1 |
| TC-API-41 | 部分更新 | 只传 content 字段 | 200, 仅 content 变化 | P1 |
| TC-API-42 | 无效 body | 空 body 或格式错误 | 400/422 | P1 |

#### DELETE /api/agentmemory/{id}

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-API-43 | 正常删除 | `DELETE /api/agentmemory/{id}` | 200/204 | P0 |
| TC-API-44 | 删除不存在的 ID | `DELETE /api/agentmemory/nonexistent` | 404 | P1 |
| TC-API-45 | 删除后不可查 | 删除后 `GET /api/agentmemory` | 该 ID 不在结果中 | P1 |

#### GET /api/stats

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-API-46 | 返回 200 | `GET /api/stats` | 200 + 统计 JSON | P0 |
| TC-API-47 | 按类型统计 | 检查响应 | 含各类型记忆数量 | P1 |
| TC-API-48 | 按时间统计 | 检查响应 | 含时间分布数据 | P1 |

---

## 六、前端组件测试用例

### 6.1 核心组件

| 用例 ID | 组件 | 测试项 | 预期结果 | 优先级 |
|---------|------|--------|----------|--------|
| TC-FE-01 | AppHeader | 标题渲染 | 显示 "Memory Viewer" | P0 |
| TC-FE-02 | AppHeader | 副标题渲染 | 显示 "Hermes Agent 记忆系统全景视图" | P1 |
| TC-FE-03 | AppHeader | 主题切换按钮 | 暗色模式按钮可见 | P0 |
| TC-FE-04 | SearchBar | 输入触发搜索 | 输入后 debounce 触发搜索 | P0 |
| TC-FE-05 | SearchBar | 清空按钮 | 输入内容后清空按钮可见 | P1 |
| TC-FE-06 | StatsBar | 统计数字 | 显示 agentmemory 和 hermes memory 数量 | P1 |
| TC-FE-07 | TabBar | 三个 Tab | "全部"/"AgentMemory"/"Hermes Memory" | P0 |
| TC-FE-08 | TabBar | Tab 切换 | 点击切换视图 | P0 |
| TC-FE-09 | TabBar | 当前 Tab 高亮 | 当前选中 Tab 有高亮样式 | P1 |
| TC-FE-10 | RefreshButton | 点击刷新 | 触发两个 store 的 refresh() | P0 |
| TC-FE-11 | ErrorBanner | 错误显示 | store.error 有值时显示 | P1 |
| TC-FE-12 | ErrorBanner | 关闭 | 点击关闭按钮隐藏 | P2 |

### 6.2 数据卡片

| 用例 ID | 组件 | 测试项 | 预期结果 | 优先级 |
|---------|------|--------|----------|--------|
| TC-FE-13 | MemoryCard | 折叠态渲染 | 显示 title + content 前 100 字符 + type tag | P0 |
| TC-FE-14 | MemoryCard | 展开渲染 | 显示完整 content + concepts + files + strength + 时间 | P0 |
| TC-FE-15 | MemoryCard | 点击展开/折叠 | 切换正常 | P0 |
| TC-FE-16 | MemoryCard | 编辑按钮 | 展开态可见 | P1 |
| TC-FE-17 | MemoryCard | 删除按钮 | 展开态可见 | P1 |
| TC-FE-18 | HermesCard | 条目渲染 | 显示 profile + file + content | P0 |
| TC-FE-19 | HermesCard | 搜索高亮 | matchSnippet 中 `<em>` 正确渲染 | P0 |
| TC-FE-20 | CardGrid | 网格布局 | 卡片按网格排列 | P1 |
| TC-FE-21 | CardGrid | 空状态 | 无数据时显示 EmptyState | P1 |
| TC-FE-22 | ProfileSection | Profile 分组 | 按 profile 名分组显示 | P1 |
| TC-FE-23 | SkeletonLoader | 加载态 | 数据加载中显示骨架屏 | P1 |
| TC-FE-24 | SkeletonLoader | 动画 | shimmer 动画正常 | P2 |
| TC-FE-25 | EmptyState | 空数据 | 显示空状态提示 | P1 |

### 6.3 视图

| 用例 ID | 视图 | 测试项 | 预期结果 | 优先级 |
|---------|------|--------|----------|--------|
| TC-FE-26 | HomeView | 首页加载 | 显示 AgentMemory + Hermes 两个 section | P0 |
| TC-FE-27 | HomeView | 数据加载 | 调用两个 store 的 fetch | P0 |
| TC-FE-28 | AgentMemoryView | 详情页 | 显示所有 agentmemory 卡片 | P1 |
| TC-FE-29 | HermesMemoryView | 详情页 | 按 profile 分组显示 | P1 |
| TC-FE-30 | SearchResultsView | 搜索结果 | 调用 /api/search，统一渲染 | P0 |
| TC-FE-31 | SearchResultsView | 结果统计 | 显示 "找到 N 条结果" | P1 |
| TC-FE-32 | SearchResultsView | 空结果 | 显示空状态 | P1 |

### 6.4 工具函数

| 用例 ID | 函数 | 测试项 | 预期结果 | 优先级 |
|---------|------|--------|----------|--------|
| TC-FE-33 | highlight.ts | 关键词高亮 | 输入文本 + 关键词，返回含 `<em>` 的 HTML | P0 |
| TC-FE-34 | highlight.ts | XSS 过滤 | `<script>` 被过滤，仅 `<em>` 保留 | P0 |
| TC-FE-35 | format.ts | 日期格式化 | ISO 字符串正确格式化 | P1 |

---

## 七、架构与非功能测试用例

### 7.1 前后端分离

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-ARCH-01 | 前端独立构建 | `cd frontend && npm run build` | 零错误，dist/ 生成 | P0 |
| TC-ARCH-02 | 前端产物完整 | 检查 dist/ | 含 index.html + CSS + JS | P0 |
| TC-ARCH-03 | 后端独立启动 | `cd backend && uvicorn app.main:app` | 启动成功，不依赖前端文件 | P0 |
| TC-ARCH-04 | 后端不 serve HTML | `GET /` on backend port | 404 或提示信息 | P1 |
| TC-ARCH-05 | CORS 配置 | 前端 dev (5173) → API (8000) | 跨域请求成功 | P0 |
| TC-ARCH-06 | CORS 预检 | `OPTIONS /api/agentmemory` | 200 + CORS 头 | P0 |
| TC-ARCH-07 | 环境变量配置 | 设置 `VITE_API_BASE` | 前端使用配置的 API 地址 | P0 |
| TC-ARCH-08 | Vite 代理 | `npm run dev` + 请求 `/api/*` | 代理到后端 | P0 |

### 7.2 Docker 部署

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-DP-01 | 一键启动 | `docker compose up -d` | 3 个容器 healthy | P0 |
| TC-DP-02 | 页面可访问 | `http://localhost:8501` | 正常加载 | P0 |
| TC-DP-03 | API 可访问 | `http://localhost:8501/api/health` | 200 + JSON | P0 |
| TC-DP-04 | nginx 路由 | `/ → frontend`, `/api → backend` | 正确路由 | P0 |
| TC-DP-05 | SPA fallback | 直接访问 `/agentmemory` | 返回 index.html（不 404） | P0 |
| TC-DP-06 | 健康检查 | 后端 healthcheck | `curl -f http://localhost:8000/api/health` 成功 | P1 |
| TC-DP-07 | nginx 健康检查 | `GET /nginx-health` | `{"status":"ok"}` | P1 |
| TC-DP-08 | 数据卷挂载 | 检查容器内数据 | `/opt/data` 可读 | P1 |

### 7.3 性能

| 用例 ID | 测试项 | 验收标准 | 优先级 |
|---------|--------|----------|--------|
| TC-NF-01 | 后端启动时间 | < 5 秒（不含 fetch） | P1 |
| TC-NF-02 | API 响应时间 | 所有端点 < 200ms | P0 |
| TC-NF-03 | 前端首屏加载 | < 2 秒 | P1 |
| TC-NF-04 | 前端产物体积 | gzip 后 < 100KB | P2 |
| TC-NF-05 | Docker 镜像大小 | backend < 300MB, frontend < 50MB | P2 |

### 7.4 安全

| 用例 ID | 测试项 | 测试步骤 | 预期结果 | 优先级 |
|---------|--------|----------|----------|--------|
| TC-SEC-01 | XSS 防护 | 搜索 `<script>alert(1)</script>` | 不执行脚本 | P0 |
| TC-SEC-02 | escapeHtml 存在 | 检查代码 | escapeHtml 函数存在且被调用 | P0 |
| TC-SEC-03 | v-html 过滤 | 检查 matchSnippet 渲染 | 仅允许 `<em>` 标签 | P0 |
| TC-SEC-04 | npm audit | `npm audit` | 无 high/critical 漏洞 | P1 |
| TC-SEC-05 | CORS 限制 | 检查 CORS 配置 | 仅允许预期 origin | P1 |

---

## 八、验收标准映射

### 8.1 功能验收 (AC-01 ~ AC-15)

| AC 编号 | 验收标准 | 测试用例覆盖 | 状态 |
|---------|----------|-------------|------|
| AC-01 | v1 API 向后兼容: /api/agentmemory | TC-API-01~06 | 待测 |
| AC-02 | v1 API 向后兼容: /api/hermes-memory | TC-API-07~11 | 待测 |
| AC-03 | v1 API 向后兼容: /api/profiles | TC-API-12~14 | 待测 |
| AC-04 | /api/health 返回服务状态 | TC-API-15~19 | 待测 |
| AC-05 | /api/search 跨数据源搜索 | TC-API-20~21 | 待测 |
| AC-06 | /api/search 过滤支持 | TC-API-22~24 | 待测 |
| AC-07 | /api/search 分页 | TC-API-25~26 | 待测 |
| AC-08 | 前端首页展示全部记忆 | TC-FE-26~27 | 待测 |
| AC-09 | 前端搜索功能 | TC-FE-04, TC-FE-30~32 | 待测 |
| AC-10 | 前端 Tab 切换 | TC-FE-07~09 | 待测 |
| AC-11 | 前端 Profile 切换 | TC-FE-22 | 待测 |
| AC-12 | 前端刷新按钮 | TC-FE-10 | 待测 |
| AC-13 | 前端骨架屏加载态 | TC-FE-23~24 | 待测 |
| AC-14 | 前端错误态展示 | TC-FE-11~12 | 待测 |
| AC-15 | Apple 风格视觉一致性 | 视觉对比测试（人工） | 待测 |

### 8.2 非功能验收 (NF-01 ~ NF-08)

| AC 编号 | 验收标准 | 测试用例覆盖 | 状态 |
|---------|----------|-------------|------|
| NF-01 | 后端启动时间 < 5s | TC-NF-01 | 待测 |
| NF-02 | API 响应时间 < 200ms | TC-NF-02 | 待测 |
| NF-03 | 前端首屏加载 < 2s | TC-NF-03 | 待测 |
| NF-04 | Docker 镜像大小 | TC-NF-05 | 待测 |
| NF-05 | 后端测试覆盖率 > 80% | pytest coverage 报告 | 待测 |
| NF-06 | 前端测试覆盖率 > 70% | vitest coverage 报告 | 待测 |
| NF-07 | CORS 正确配置 | TC-ARCH-05~06 | 待测 |
| NF-08 | 无 npm audit high/critical | TC-SEC-04 | 待测 |

### 8.3 部署验收 (DP-01 ~ DP-05)

| AC 编号 | 验收标准 | 测试用例覆盖 | 状态 |
|---------|----------|-------------|------|
| DP-01 | docker compose up 一键启动 | TC-DP-01 | 待测 |
| DP-02 | localhost:8501 可访问 | TC-DP-02 | 待测 |
| DP-03 | 开发模式后端独立启动 | TC-ARCH-03 | 待测 |
| DP-04 | 开发模式前端独立启动 | TC-ARCH-07~08 | 待测 |
| DP-05 | 前端构建产物可独立部署 | TC-ARCH-01~02 | 待测 |

---

## 九、测试用例统计

| 维度 | P0 | P1 | P2 | 合计 |
|------|----|----|----|----|
| P0 功能 (F-01~F-06) | 24 | 22 | 6 | 52 |
| P1 功能 (F-07~F-12) | 5 | 33 | 4 | 42 |
| P2 功能 (F-13~F-18) | 0 | 2 | 21 | 23 |
| API 端点 | 17 | 26 | 0 | 43 |
| 前端组件 | 9 | 19 | 3 | 31 |
| 架构/非功能 | 12 | 9 | 4 | 25 |
| **合计** | **67** | **111** | **38** | **216** |

---

## 十、测试数据准备

### 10.1 AgentMemory 测试数据

```json
[
  {
    "id": "mem_test_001",
    "type": "pattern",
    "title": "Kanban multi-agent workflow",
    "content": "Hermes built-in Kanban board for multi-agent coordination...",
    "concepts": ["hermes", "kanban", "multi-agent"],
    "files": [],
    "createdAt": "2026-05-25T19:16:57.181Z",
    "updatedAt": "2026-05-25T19:16:57.181Z",
    "strength": 7,
    "version": 1,
    "isLatest": true,
    "sessionIds": []
  },
  {
    "id": "mem_test_002",
    "type": "fact",
    "title": "User prefers concise responses",
    "content": "The user prefers short, direct answers without unnecessary elaboration.",
    "concepts": ["preference", "communication"],
    "files": [],
    "createdAt": "2026-05-26T10:00:00.000Z",
    "updatedAt": "2026-05-26T10:00:00.000Z",
    "strength": 9,
    "version": 1,
    "isLatest": true,
    "sessionIds": []
  },
  {
    "id": "mem_test_003",
    "type": "bug",
    "title": "Memory Viewer XSS vulnerability",
    "content": "<script>alert('xss')</script>Found in search highlight rendering. Fixed by escaping HTML.",
    "concepts": ["security", "xss", "memory-viewer"],
    "files": ["memory-viewer/app.py"],
    "createdAt": "2026-05-27T08:30:00.000Z",
    "updatedAt": "2026-05-27T14:00:00.000Z",
    "strength": 8,
    "version": 2,
    "isLatest": true,
    "sessionIds": ["session_abc"]
  }
]
```

### 10.2 Hermes Memory 测试数据

```
global/MEMORY.md:
§
Hermes is an AI agent platform with multi-agent support.
§
The kanban system allows task decomposition and parallel execution.
§

global/USER.md:
§
User is a developer working on memory-viewer project.
§

profiles/daily/MEMORY.md:
§
Daily agent handles routine tasks and reminders.
§

profiles/dev-worker/MEMORY.md:
§
Dev worker implements code changes based on PM specs.
§
Code review is mandatory before merging.
```

### 10.3 边界测试数据

| 数据类型 | 内容 | 用途 |
|----------|------|------|
| 空字符串 | `""` | content/title 为空 |
| 超长内容 | 10000 字符 | 截断/性能测试 |
| 特殊字符 | `<script>`, `&amp;`, `"` | XSS/转义测试 |
| Emoji | 🧠🤖✨🎯 | 编码测试 |
| Unicode | 中文、日文、阿拉伯文 | 国际化测试 |
| 换行符 | `\n`, `\r\n`, `\r` | 解析测试 |
| 空数组 | `[]` | concepts/files 为空 |
| null 字段 | `null` | 可选字段测试 |
