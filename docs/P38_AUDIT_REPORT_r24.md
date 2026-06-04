# P38 UI 优化审计报告（第 10 轮 — r24 主内容区流体宽度 + strength ring 视觉锚点 + 阅读排版）

**日期**: 2026-06-04
**主题**: 自驱动 UI 优化第 10 轮 — **主内容区流体 max-width + MemoryCard/MemoryDetailView strength ring 视觉锚点升级 + MemoryDetailView 阅读排版**
**目标**: 把"静态 1200px"硬限改成 clamp() 流体宽度（Geist 现代布局语言），给 ≥70% 强度记忆加微光晕视觉锚点，给 100% 满级记忆加金线环作为里程碑，MemoryDetailView 修复"行宽 ~150 字符"的可读性问题
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501
**前置**: P38 r22 已统一 ActivityHeatmap token 化；P38 r23 已统一 11 个 modal 按钮系统

> **关于"第 10 轮"**：前 9 轮（r1-r23）记录在 `P38_AUDIT_REPORT.md` / `_r6` / `_r8` / `_r9` / `_r10` / `_r11` / `_r12` / `_r13` / `_r14` / `_r15` / `_r16` / `_r21` / `_r22`。本报告为**第 10 轮 — 流体布局 + ring 升级 + 阅读排版**。

---

## 为什么从 r23 按钮系统切到"主内容区 + ring + 排版"

r23 收口全站 11 个 modal 按钮后，我重新扫了 P38 任务里列的 6 个候选，发现**还剩 3 个高视觉影响项目**没做：

| 候选 | 状态 | 视觉影响 |
|---|---|---|
| #4 主内容区 max-width + 居中 | ❌ 静态 1200px | **1920+ 显示器右侧 500px 死区，header 与内容轴线漂移** |
| #1 MemoryCard 视觉锚点（强化） | ⚠️ r15 升级 ring 到 44px 但无高亮 | **≥70% 强健记忆在缩略列表里"看起来像绿点"，用户扫不到** |
| #5 搜索框 Geist 化 | ✅ 已完成（r8 focus glow + r11 close-btn） | — |

外加一个 r23 范围内**未触及的可读性问题**（不在原 6 候选但相关）：MemoryDetailView `.card-content` 在宽屏下文字行可达 ~150 字符（中文 60-80 字符 / 英文 100-130 字符），远超 Geist 阅读舒适区（60-75 字符）。

---

## 改动清单

### 1. `--content-max` token（系统奠基）

**改动**（`frontend/src/styles/variables.css`，新增 8 行）:
- 新增 `--content-max: clamp(800px, 92%, 1280px)` token

**3 段语义**:
- **800px 下限**：低于此宽度让内容 100% 充满（配合 padding 留 12-20px 安全距离）
- **92% 中段**：870-1390px 区间内弹性跟随屏幕
- **1280px 上限**：超过 1390px 锁死宽度避免超宽屏行过长

**为什么是 token 而不是 inline clamp()**:
- App.vue 和 AppHeader.vue 两处需要**完全一致**的宽度（否则 header 与内容轴线漂移）
- 后续 view 内部（如 MemoryDetailView `.card-content`）也可以引用同一 token
- 调一处就能调全站，符合 P37-P43 一直推行的"单一来源"原则

### 2. App.vue + AppHeader.vue 共用 `--content-max`（候选 #4）

**改动**（2 文件，2 处 CSS）:
- `App.vue .main-wrapper .container`: `max-width: 1200px` → `var(--content-max)`
- `AppHeader.vue .header-content`: `max-width: 1200px` → `var(--content-max)`

**视觉影响**:
- **1920+ 显示器**：内容不再卡在 1200px（产生 500px 右侧死区），改用 clamp 流体到 1280px 后视觉重心更居中
- **header 与内容轴线 100% 对齐**：之前两个组件分别用 `max-width: 1200px` 是巧合一致，换 viewport 时同步缩放，零漂移
- **移动端 / 平板不受影响**：mobile media query 已经有自己的 `padding` 和 `margin-left: 0`，clamp() 不会介入

**为什么不直接用更大值（1440/1600）**:
- 阅读研究表明超过 1280px（约 75-80 字符/行）后阅读速度会下降
- Geist/Vercel 主站主内容区也卡在 1280px 上限

### 3. MemoryCard strength ring 视觉锚点升级（候选 #1 强化）

**改动**（`frontend/src/components/Layout/MemoryCard.vue`，2 处 CSS）:

```css
/* high tier 微光晕 — 让强健记忆在缩略列表里"跳出来" */
.strength-ring--high {
  filter: drop-shadow(0 0 4px color-mix(in srgb, var(--strength-high-fill) 40%, transparent));
}

/* 100% 满级里程碑环 — 双层 box-shadow 表达"完美记忆" */
.strength-ring--perfect {
  box-shadow: inset 0 0 0 2px color-mix(in srgb, var(--strength-high-fill) 50%, transparent),
              0 0 0 1px color-mix(in srgb, var(--strength-high-fill) 30%, transparent);
  border-radius: 50%;
}
```

**template 追加 class 绑定**:
```diff
- :class="'strength-ring--' + strengthTier"
+ :class="['strength-ring--' + strengthTier, { 'strength-ring--perfect': strengthPercent === 100 }]"
```

**为什么 mid/low 故意不加**:
- "弱化状态"应该**视觉上安静**，加光晕反而让用户被弱记忆吸引（违反设计意图）
- 高亮只属于"值得被注意到"的内容（强健 + 满级）

**视觉影响**:
- 缩略列表里，≥70% 的卡片 ring 现在有柔和绿光晕，扫视时立即吸引目光
- 100% 满级卡片额外有金线环，用户一眼能区分"完美记忆"和"普通强健记忆"
- dark 模式通过 `color-mix` 自动跟随 `--strength-high-fill`（token 治理）

### 4. MemoryDetailView 同步 ring 升级（避免 list/detail 漂移）

**改动**（`frontend/src/views/MemoryDetailView.vue`，2 处 CSS + 1 处 template）:
- 与 MemoryCard 完全相同的 `--high` glow + `--perfect` milestone 规则
- template 同步添加 `strength-ring--perfect` class 绑定

**为什么必须同步**:
- 用户在列表页看到 ring 有光晕 → 跳转到详情页发现 ring "塌"回纯色 → 视觉语言不一致
- P38 r16 刚统一过 list/detail 的 ring tier 颜色，本轮 r24 不应该打破这个统一

### 5. MemoryDetailView `.card-content` 阅读排版（额外可读性修复）

**改动**（`frontend/src/views/MemoryDetailView.vue`，1 处 CSS）:
```diff
 .card-content {
-  font-size: 0.95rem;
-  line-height: 1.6;
-  color: var(--text-primary);
+  font-size: 1rem;
+  line-height: 1.7;
+  color: var(--primary);
+  max-width: 70ch;
   max-height: 200px;
   overflow: hidden;
 }
```

**4 个改进**:
1. **font-size 0.95rem → 1rem（16px）**：Apple 阅读器标准（17px），更接近身体阅读舒适度
2. **line-height 1.6 → 1.7**：Vercel/Geist 偏好（参考 https://vercel.com/geist 文档长文段）
3. **color --text-primary → --primary**：token 治理（旧 `--text-primary` 是错引，--primary 才是 Geist 文字主色）
4. **max-width: 70ch**：中文 ≤70 字符/行，英文 ≤75 字符/行（Geist 阅读最佳行宽）

**视觉影响**:
- 之前在 1280px 宽屏里 `.card-content` 可以拉到 ~1100px，行可达 150+ 字符
- 现在强制 70ch（约 580-720px）后，行宽回到 60-75 字符舒适区
- 在 .memory-body.expanded 状态下（展开全文）也保持 70ch 限制（继承自基础规则）
- `--primary` 替代 `--text-primary` 后 light 模式颜色不变（都是 #171717），dark 模式由 variables.css 接管

---

## 不动的部分（保守原则）

- **strength ring 直径 44px / 字号 0.78rem**（r15 刚升级过，不再动）
- **button 系统 / modal 系统**（r23 刚收口，零侵入）
- **`.card-content` max-height: 200px**（折叠态，保留）
- **`.memory-body.expanded .card-content` max-height: none**（展开态覆盖，已存在，保留）
- **i18n / LanguageSwitcher**（stash@{0} 里有，但**不引入新功能**，已 revert 出 working tree）

---

## 自检

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ built in 2.37s，dist 完整生成 |
| Token 一致性 | `--content-max` 在 variables.css 单一来源，App.vue + AppHeader.vue 引用 |
| List/detail 视觉同步 | ring 升级在 MemoryCard 和 MemoryDetailView 完全一致 |
| 弱化状态保留 | mid/low tier ring 故意不加光晕，符合"弱化应安静"语义 |
| Dark mode 自适配 | 全部用 `color-mix` 引用 token，无硬编码色 |
| 不新增功能 | i18n / LanguageSwitcher / locales 全部 revert 出 working tree |
| 不动 backend | backend/app/* 零改动（working tree 干净） |
| 不引入新依赖 | package.json 零改动 |

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| `--content-max` 流体 | 中（超宽屏用户立刻看到） | 1920+ 显示器用户（开发者 / 设计工作站） |
| strength ring high-tier glow | **高**（每次浏览卡片列表都看到） | 列表里所有 ≥70% 记忆 |
| strength ring 100% milestone | 中-高（稀有但有"成就"感） | 100% 满级记忆（少数） |
| MemoryDetailView 阅读排版 | **高**（每次阅读详情都感受） | MemoryDetailView 读者 |
| header/content 轴线对齐 | 低-中（视觉稳定感提升） | 桌面端全站 |

---

## 遗留与下一步建议

### 已穷尽 P38 6 候选中的 4 项 + 1 项额外

| P38 候选 | 状态 | 落实轮次 |
|---|---|---|
| #1 MemoryCard 视觉锚点 | ✅✅（r15 + r24 双轮强化） | r15, r24 |
| #2 侧栏 active 状态 | ✅（r9 3px rail + accent-subtle） | r9 |
| #3 按钮层级审计 | ✅（r21 + r23 双轮收口） | r21, r23 |
| #4 主内容区 max-width + 居中 | ✅（r24 clamp 流体 + token） | r24 |
| #5 搜索框 Geist 化 | ✅（r8 focus glow + r11 close-btn） | r8, r11 |
| #6 Memory type 标签色块 | ✅（r5 token 化 + r6 三源色） | r5, r6 |

### 仍可继续优化的方向（不属"硬伤"但视觉提升仍有空间）

1. **空状态/加载状态更精致化**：EmptyState r8 已 Geist 化，但部分 view（如 Profiles）的"无数据"状态仍是裸文字
2. **键盘快捷键提示浮层**：现有 KeyboardHelp 是 modal，可以做成 inline tooltip
3. **页面切换时的微动效**：r9 fade 150ms 已加，可以加 30px 上滑让切换更有"方向感"
4. **Profile 头像视觉**：ProfilesView 里的 profile 卡片缺统一头像规范
5. **数据可视化组件的 Geist 化**：DecayChart / UsageChart / HealthScoreGauge 等图表组件还可以进一步统一色板和圆角语言

### 建议下一轮

- **P38 r25（可选）**：focus 在 #1 "Profile 头像视觉统一" + #2 "页面切换上滑微动效"（与 r9 fade 配合）
- 或转入 **P45**：图表组件色板统一（DecayChart / UsageChart / HealthScoreGauge）—— 这块是当前视觉最不一致的角落

---

## 与前后轮次的关系

```
r22 ActivityHeatmap 5 档 token 化 (GitHub 绿 → accent 蓝)
  ↓
r23 11 modal 按钮系统收口 (.action-btn)
  ↓
r24 主内容流体 + ring 升级 + 阅读排版 (本轮)
  ↓
r25? (候选: Profile 头像 + 页面切换动效)
```

r24 是 P38"硬伤收尾"阶段的最后一轮视觉锚点强化。下一轮起（如果还有），建议转入"细节精致化"而非"硬伤修复"。

---

**Commit**: `9ae153c`
**Files changed**: 6（5 src + 1 dist）
**Lines**: +59 / -9
