# P26 迭代计划

> **日期**: 2026-05-31  
> **阶段**: P26  
> **目标**: Guided Onboarding (F-66)

---

## 任务清单

| ID | 功能 | 类型 | 优先级 | 依赖 | 预估工时 |
|----|------|------|--------|------|----------|
| P26-T1 | F-66 Guided Onboarding | frontend | P0 | 无 | 3h |

---

## 详细设计

### P26-T1: F-66 引导式入职

**后端改动**: 可能需要存储 onboarding 状态

**前端改动**:
- `GuidedOnboardingModal.vue` (新建) - 分步引导弹窗
- 5步流程：欢迎 → 数据源配置 → 首记忆创建 → 快速上手 → 完成
- 进度指示器、可跳过选项、示例数据预填充

**验收标准**:
- AC-F66-1: 新用户首次访问显示引导流程
- AC-F66-2: 用户可跳过不感兴趣的步骤
- AC-F66-3: 完成引导后状态被记住，不再重复显示

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

- 完成 F-66 Guided Onboarding
- pytest 无新错误，vue-tsc 无错误