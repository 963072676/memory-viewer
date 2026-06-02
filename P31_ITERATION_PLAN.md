# P31 迭代计划

> **日期**: 2026-05-31  
> **阶段**: P31  
> **目标**: 实现 F-23 多Agent记忆对比

---

## 状态

P30 (F-21 自动去重) 已完成。
backlog 剩余: F-23, F-24, F-27
选择 **F-23 多Agent记忆对比** 作为 P31 目标。

## F-23 多Agent记忆对比 功能描述

**问题**: 用户需要对比不同 Agent profile 之间的记忆差异，发现知识盲区。

**解决方案**:
- 后端：新增 `/api/compare/profiles` 端点，支持对比两个 profile 的记忆差异
- 前端：新增 CompareView 双栏对比视图
- 支持选择两个 profile，展示记忆差异（独有/共有/冲突）

### 实现任务

1. **P31-T1**: 后端对比 API
   - 新增 `backend/app/routers/compare.py`
   - 端点: `GET /api/compare/profiles?left=<profile>&right=<profile>`
   - 返回差异报告（独有记忆、共有记忆、相似度分数）

2. **P31-T2**: 前端对比视图
   - 新增 `frontend/src/views/CompareView.vue`
   - 双栏布局：左侧 Profile A，右侧 Profile B
   - 高亮差异项

3. **P31-T3**: 验证
   - pytest + vue-tsc 无错误

## 验收标准

- AC-F23-1: 可选择两个 profile 进行对比
- AC-F23-2: 差异记忆高亮显示
- AC-F23-3: pytest 无新增失败
- AC-F23-4: vue-tsc 无错误