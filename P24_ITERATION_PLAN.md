# P24 迭代计划

> **日期**: 2026-05-31  
> **阶段**: P24  
> **目标**: 记忆分享集成 (F-42 收尾) + 健康扫描器 (F-68)

---

## 任务清单

| ID | 功能 | 类型 | 优先级 | 依赖 | 预估工时 |
|----|------|------|--------|------|----------|
| P24-T1 | F-42 记忆分享集成 | frontend | P0 | backend已就绪 | 1.5h |
| P24-T2 | F-68 健康扫描器 | frontend+backend | P1 | 无 | 2h |

---

## 详细设计

### P24-T1: F-42 记忆分享集成

**后端改动**: 无（已就绪）

**前端改动**:
- `MemoryDetailView.vue` 增加"分享"按钮
- 导入并使用 `ShareModal.vue`
- API: `POST /api/sharing/memories/{id}/share`

**验收标准**:
- AC-F42-1: MemoryDetailView 有分享按钮
- AC-F42-2: 点击分享打开 ShareModal
- AC-F42-3: 生成分享链接

---

### P24-T2: F-68 健康扫描器

**后端改动**: `health_scanner_service.py`

**前端改动**:
- `HealthScanView.vue`
- `HealthScoreGauge.vue`
- 7 项健康检查可视化

**验收标准**:
- AC-F68-1: 扫描视图显示健康分数
- AC-F68-2: 各检查项状态可视化
- AC-F68-3: 扫描历史

---

## 验证要求

每完成一个任务后必须运行：
```bash
cd /opt/data/memory-viewer/v2
python3 -m pytest backend/tests/ -q --tb=short 2>&1 | tail -3
cd frontend && npx vue-tsc --noEmit 2>&1 | grep "error TS" | wc -l
```

---

## 预期成果

- 完成 F-42 集成 + F-68 基础框架
- pytest 无错误，vue-tsc 无错误