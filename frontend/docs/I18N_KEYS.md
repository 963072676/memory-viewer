# Memory Viewer i18n Key 总账

> 自动生成自 `scripts/rename_i18n_keys.py`, 2026-06-13 PM-20260612-002
> 起点: ee40f2a; 覆盖: 32 个 hash 后缀 key (25 个被 .vue 引用 + 7 个 orphan in locales)

## 命名空间约定

| Namespace | 用途 | 命名空间 owner |
|---|---|---|
| `i18n.common.*` | 跨视图通用按钮/标签 (back / add / share / edit / text / editable) | 全站 |
| `i18n.onboarding.*` | SetupWizard + TourStep + OnboardingTour (mastered / quick_start / auto_detect / memory_system / visual_anchor / skip_tour / skip_setup) | 引导 |
| `i18n.filter.*` | FilterPanel (type / min_similarity / apply) | 筛选 |
| `i18n.create.*` | CreateMemoryModal + EditMemoryModal + HomeView CTA (title / content / action / creating / tag_hint) | 创建 |
| `i18n.dedup.*` | DedupModal (for_duplicate / of_duplicate) | 去重 |
| `i18n.empty.*` | 空状态 (chart_data / related_memories) | 空态 |
| `i18n.conflict.*` | ConflictCard (keep) | 冲突 |
| `i18n.help.*` | KeyboardHelp (shortcuts) | 帮助 |
| `i18n.search.*` | CommandPalette + TagManager (results / placeholder / searching / by_type) | 搜索 |
| `i18n.source.*` | SourcesView (health / enabled) | 数据源 |

## 重命名总账 (2026-06-13 PM-20260612-002 一次性)

| 旧 key | 新 key | 含义 (zh-CN) | 引用文件数 |
|---|---|---|---|
| `i18n.add_0067ea` | `i18n.common.add` | 添加 | 1 |
| `i18n.apply_b23cab` | `i18n.filter.apply` | 应用筛选 | 1 |
| `i18n.auto_detect_c507cb` | `i18n.onboarding.auto_detect` | 自动检测 | 1 |
| `i18n.back_0cdd24` | `i18n.common.back` | 上一步 | 2 |
| `i18n.content_ca9884` | `i18n.create.content` | 记忆内容 | 2 |
| `i18n.create_0cf084` | `i18n.create.creating` | 创建中 | 0 |
| `i18n.create_memory_ab0956` | `i18n.create.action` | 创建记忆 | 1 |
| `i18n.data_b651d3` | `i18n.empty.chart_data` | 暂无数据 | 2 |
| `i18n.duplicate_memories_ba1fa5` | `i18n.dedup.of_duplicate` | 的重复记忆 | 1 |
| `i18n.duplicate_memories_d9cf3d` | `i18n.dedup.for_duplicate` | 对重复记忆 | 1 |
| `i18n.edit_0cfcaf` | `i18n.common.editable` | 可编辑 | 0 |
| `i18n.enabled_ac8831` | `i18n.source.enabled` | 启用状态 | 1 |
| `i18n.got_a9807e` | `i18n.onboarding.mastered` | 你已掌握 | 1 |
| `i18n.health_aa14d3` | `i18n.source.health` | 健康状态 | 1 |
| `i18n.keep_00642b` | `i18n.conflict.keep` | 保留 | 2 |
| `i18n.keyboard_shortcuts_d65312` | `i18n.help.shortcuts` | 键盘快捷键 | 1 |
| `i18n.memory_system_ca9e41` | `i18n.onboarding.memory_system` | 记忆系统 | 1 |
| `i18n.min_00670d` | `i18n.filter.min_similarity` | 最小 | 1 |
| `i18n.quick_start_b36798` | `i18n.onboarding.quick_start` | 快速开始 | 1 |
| `i18n.related_memories_9b77b2` | `i18n.empty.related_memories` | 暂无相关记忆 | 1 |
| `i18n.results_b5675c` | `i18n.search.results` | 搜索结果 | 1 |
| `i18n.search_memories_b568fd` | `i18n.search.placeholder` | 搜索记忆 | 0 |
| `i18n.searching_0d4da8` | `i18n.search.searching` | 查找中 | 0 |
| `i18n.share_00644b` | `i18n.common.share` | 分享 | 1 |
| `i18n.skip_cca3f7` | `i18n.onboarding.skip_tour` | 跳过引导 | 1 |
| `i18n.skip_cca4b2` | `i18n.onboarding.skip_setup` | 跳过按钮 | 0 |
| `i18n.text_0066dc` | `i18n.common.text` | 文字 | 0 |
| `i18n.title_ca9ba7` | `i18n.create.title` | 记忆标题 | 1 |
| `i18n.type_0d3c5f` | `i18n.search.by_type` | 按类型 | 1 |
| `i18n.type_ca9e09` | `i18n.filter.type` | 记忆类型 | 1 |
| `i18n.type_press_5a1514` | `i18n.create.tag_hint` | 输入标签后回车添加 | 1 |
| `i18n.visual_anchor_797fc3` | `i18n.onboarding.visual_anchor` | 视觉锚点统一 | 0 |

## 已知遗留 (本工单范围外, 留 followup)

- `i18n.core_functionality` 在 `DoneStep.vue` 引用, 但 locales 缺此 key — PM-20260612-001 遗留
- `i18n.intelligent_memory` / `i18n.help_understand` / `i18n.organize_optimize` (DoneStep / WelcomeStep) — PM-20260612-001 遗留
- 7 个 orphan locales key (mapping 已重命名, 但 .vue 没调用): create_0cf084 / edit_0cfcaf / search_memories_b568fd / searching_0d4da8 / skip_cca4b2 / text_0066dc / visual_anchor_797fc3 — 留 followup 接入 UI 或删除

## 重跑

```bash
cd frontend
python3 scripts/rename_i18n_keys.py \
  --mapping scripts/i18n_key_mapping.json \
  --locales src/locales \
  --src src \
  --log rename_i18n_keys.log
```

加 `--dry-run` 只看不动。
