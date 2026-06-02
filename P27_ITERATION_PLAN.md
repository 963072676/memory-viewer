# P27 迭代计划

> **日期**: 2026-05-31  
> **阶段**: P27  
> **目标**: F-67 Advanced Export & Reporting

---

## 任务清单

| ID | 功能 | 类型 | 优先级 | 依赖 | 预估工时 |
|----|------|------|--------|------|----------|
| P27-T1 | F-67 Export & Reporting | backend + frontend | P0 | 无 | 4h |

---

## 详细设计

### P27-T1: 高级导出与报告

**后端改动**:
- `report_service.py` (新建) - 报告生成服务
- Jinja2 模板支持 HTML 报告
- `/api/reports` 端点

**前端改动**:
- `ReportsView.vue` (新建) - 报告查看和下载
- 模板选择器
- 报告历史记录

**验收标准**:
- AC-F67-1: HTML 报告生成
- AC-F67-2: PDF 报告生成（可选）
- AC-F67-3: 图表和统计数据包含在内
- AC-F67-4: 自定义筛选条件应用
- AC-F67-5: 可从历史记录下载
- AC-F67-6: 200条记忆 < 15s

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

- 完成 F-67 Advanced Export & Reporting
- pytest 无新错误，vue-tsc 无错误