# P25 迭代计划

> **日期**: 2026-05-31  
> **阶段**: P25  
> **目标**: 健康扫描器 (F-68)

---

## 任务清单

| ID | 功能 | 类型 | 优先级 | 依赖 | 预估工时 |
|----|------|------|--------|------|----------|
| P25-T1 | F-68 健康扫描器 | frontend+backend | P0 | 无 | 2.5h |

---

## 详细设计

### P25-T1: F-68 健康扫描器

**后端改动**: `health_scanner_service.py` + `routers/health_scan.py`

**前端改动**:
- `HealthScanView.vue` (已有6KB)
- `HealthScoreGauge.vue` (已有)
- 7 项健康检查：空元数据、重复项、孤立记忆、低强度、陈旧度、标签缺失、访问频率

**验收标准**:
- AC-F68-1: 显示 0-100 健康分数
- AC-F68-2: 各检查项状态可视化（通过/警告/失败）
- AC-F68-3: 可对警告项进行自动修复

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

- 完成 F-68 健康扫描器
- pytest 无错误，vue-tsc 无错误