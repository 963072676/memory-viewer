# P32 迭代计划

> **日期**: 2026-05-31  
> **阶段**: P32  
> **目标**: 实现 F-24 记忆版本历史

---

## 状态

P31 (F-23 多Agent记忆对比) 已完成。
backlog 剩余: **F-24 记忆版本历史**, F-27 MCP Server模式。
选择 **F-24 记忆版本历史** 作为 P32 目标。

---

## F-24 记忆版本历史 功能描述

**问题**: 用户编辑记忆后无法追溯变更历史，错误修改无法回滚。

**解决方案**:
- 后端：每次编辑记忆前自动保存快照（版本），支持查询历史和回滚
- 前端：新增 VersionHistoryView 版本历史视图，支持查看历史版本列表、diff 展示、一键回滚

### 现状分析

| 组件 | 状态 | 说明 |
|------|------|------|
| `backend/app/services/versioning.py` | ✅ 存在 | save_snapshot, get_versions, rollback_to_version |
| `backend/app/routers/versioning.py` | ✅ 存在 | GET /{id}/versions, POST /{id}/versions/{version}/rollback |
| `backend/app/main.py` 路由注册 | ✅ 已注册 | prefix=/api/agentmemory |
| 前端 VersionHistoryView.vue | ❌ 缺失 | 需新建 |
| 编辑时自动保存版本 | ❌ 缺失 | update_memory 需集成 save_snapshot |
| 前端 API 客户端 | ❌ 缺失 | 需新增 versioning API 调用 |

---

## 任务拆分

### P32-T1: 后端编辑时自动保存版本快照

**问题**: 当前 `update_memory` 函数编辑记忆时不会自动保存版本快照。

**实现**:
1. 修改 `backend/app/services/agentmemory.py` 中 `update_memory` 函数
2. 在更新前调用 `versioning.save_snapshot(memory)` 保存当前状态
3. 确保回滚后新版本也被正确记录

**验收标准**:
- AC-F24-T1-1: 调用 update_memory 后，版本文件中有新的快照记录
- AC-F24-T1-2: 版本号连续递增（v1, v2, v3...）
- AC-F24-T1-3: 快照包含 title, content, concepts, strength, type

### P32-T2: 后端版本历史 API 完善

**实现**:
- `GET /api/agentmemory/{id}/versions` — 已存在
- `POST /api/agentmemory/{id}/versions/{version}/rollback` — 已存在
- 新增 `GET /api/agentmemory/{id}/versions/{version}` — 获取单个版本详情
- 新增 `GET /api/agentmemory/{id}/versions/{v1}/diff/{v2}` — 对比两个版本的差异

**验收标准**:
- AC-F24-T2-1: GET versions 返回按时间倒序排列的版本列表
- AC-F24-T2-2: rollback 后返回更新后的 memory 对象
- AC-F24-T2-3: diff 端点返回两个版本之间的内容差异（新增/删除/修改的行）

### P32-T3: 前端版本历史 API 客户端

**实现**:
1. 新增 `frontend/src/api/versioning.ts`
2. 端点: `getVersions(memoryId)`, `rollbackVersion(memoryId, version)`, `getVersionDiff(memoryId, v1, v2)`

**验收标准**:
- AC-F24-T3-1: API 客户端方法签名与后端端点一一对应
- AC-F24-T3-2: TypeScript 类型完整（MemoryVersion, VersionDiff）

### P32-T4: 前端 VersionHistoryView.vue

**实现**:
1. 新增 `frontend/src/views/VersionHistoryView.vue`
2. 从 MemoryCard 或详情页入口进入
3. 版本列表：展示 version 号、时间戳、主要变更字段
4. diff 展示：使用 diff 算法高亮显示 content 变更
5. 回滚按钮：确认对话框 + API 调用 + 成功后跳转回详情页

**验收标准**:
- AC-F24-T4-1: 从记忆详情页可进入版本历史页
- AC-F24-T4-2: 版本列表按时间倒序
- AC-F24-T4-3: 可查看两个版本的 diff
- AC-F24-T4-4: 回滚操作有确认提示

### P32-T5: 前端版本历史入口集成

**实现**:
1. 修改 `frontend/src/components/MemoryCard.vue` 或详情页，添加"历史"按钮
2. 修改 `frontend/src/router/index.ts` 添加路由 `/memory/:id/history`
3. 版本历史入口仅在有编辑权限时显示

**验收标准**:
- AC-F24-T5-1: 每条记忆卡片或详情页有"历史"入口
- AC-F24-T5-2: 路由 `/memory/:id/history` 正常访问

### P32-T6: 验证

**实现**:
1. pytest 测试版本 API
2. vue-tsc 类型检查
3. 手动测试编辑后版本是否自动保存

**验收标准**:
- AC-F24-T6-1: pytest 无新增失败
- AC-F24-T6-2: vue-tsc 无错误
- AC-F24-T6-3: 编辑记忆后版本号 +1

---

## 验收标准（汇总）

| ID | 描述 | 优先级 |
|----|------|--------|
| AC-F24-1 | 编辑记忆后自动保存版本快照 | P0 |
| AC-F24-2 | GET /api/agentmemory/{id}/versions 返回版本列表 | P0 |
| AC-F24-3 | POST rollback 恢复到指定版本，内容与目标版本一致 | P0 |
| AC-F24-4 | 前端版本历史页面正常渲染 | P0 |
| AC-F24-5 | 可查看两个版本之间的 diff | P1 |
| AC-F24-6 | 无编辑历史时返回空列表 | P1 |
| AC-F24-7 | pytest 无新增失败 | P0 |
| AC-F24-8 | vue-tsc 无错误 | P0 |

---

## 技术细节

### 版本数据模型

```json
// versions/{memory_id}.json
{
  "versions": [
    {
      "version": 1,
      "snapshot": {
        "title": "...",
        "content": "...",
        "concepts": [...],
        "strength": 7,
        "type": "pattern"
      },
      "timestamp": "2026-05-31T10:00:00Z"
    }
  ]
}
```

### Diff 展示

- 使用 `diff` 库（`npm install diff`）进行文本对比
- 变更类型：新增（绿色）、删除（红色）、修改（黄色）
- 前后版本对比，展示变化内容

### 路由设计

```
/memory/:id          → 记忆详情页（有"历史"按钮）
/memory/:id/history  → 版本历史页（VersionHistoryView）
```

---

## 文件清单

| 操作 | 文件路径 |
|------|---------|
| 修改 | `backend/app/services/agentmemory.py` |
| 新增 | `backend/app/routers/versioning.py` (已存在，需确认) |
| 修改 | `backend/app/main.py` (已确认路由注册) |
| 新增 | `frontend/src/api/versioning.ts` |
| 新增 | `frontend/src/views/VersionHistoryView.vue` |
| 修改 | `frontend/src/components/MemoryCard.vue` |
| 修改 | `frontend/src/router/index.ts` |
| 新增 | `frontend/tests/api/versioning.test.ts` |