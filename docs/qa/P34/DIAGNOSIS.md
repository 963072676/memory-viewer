# P34 现状诊断报告

> 诊断时间: 2026-06-02
> 诊断范围: AppSidebar.vue + MemoryCard.vue
> 目的: 给 dev-worker 一稿过的修复指令

---

## 0. 关键发现

1. **mobile-first 原生模式（Header + Tab Bar + Bottom Sheet）代码已存在**于 `AppSidebar.vue`，断点 `767px`，**这部分不用改**。
2. **`App.vue` 的 `.main-wrapper` 用 `margin-left: 220px` 给 desktop sidebar 让位**——硬编码值，与 sidebar 实际宽度解耦。
3. **MemoryCard 的 select-checkbox 始终 absolute 定位**，**没根据多选模式切换**——这是 BUG #2 直接根因。
4. **截图中"极窄容器"很可能是某个父级被压缩**，但更直接的证据是 **select-checkbox 的 absolute 定位 + 无 v-if 控制 + card-header 无 padding-left = 必然遮挡**。

---

## 1. BUG #1 根因分析

### 1.1 AppSidebar.vue 状态
- `.sidebar` width: 220px / collapsed 64px ✅
- mobile 模式独立（mobile-header, mobile-tab-bar, bottom-sheet）✅
- 断点 `@media (max-width: 767px)` ✅

### 1.2 截图证据
- **img_0b65b6d1b788.jpg**: 极窄画布（80-100px 宽）内看到 "灰色 `>` 按钮 + 粉色气泡 + 蓝色 Home 卡片"
- 该图实际是 **mobile-tab-bar 的某个 tab 在错误宽度下的视觉**——`width: 100vw` 但父容器被压缩

### 1.3 根因
- **App.vue `.main-wrapper` 的 `margin-left: 220px` 是硬编码**
- 当 viewport 实际 < 220px 时（不应该发生但发生了，比如浏览器 DevTools 模拟极窄屏 + sidebar collapsed 到 64px）：
  - `.main-wrapper.sidebar-collapsed { margin-left: 60px; max-width: calc(100vw - 60px); }`
  - 但 `100vw - 60px` 在 sidebar 实际 64px 时仍有 4px 误差，**最大宽度算错**
  - **更糟**：当 viewport 被错误地缩到 100px（用户截图状态），`100vw - 60px = 40px` 不足以放下 mobile-tab-bar 的 5 个 tab-item
  - mobile-tab-bar 自身 `position: fixed; left: 0; right: 0;` **强制全宽**，但视口实际只有 100px，**它会把内容压扁**

### 1.4 修复方案
- **App.vue `.main-wrapper` 不用 `margin-left: 220px` 硬编码**，改用 CSS Grid 或 Flex 布局让 sidebar 自然占位
- 或：**保持 hardcode 但加 `min-width: 0` 防溢出 + 测试 viewport < 220px 时正确切换为 mobile 模式**
- **`@media (max-width: 767px)` 时** sidebar 整体不占位（已用 `display: none` 处理），main-wrapper `margin-left: 0` ✅ 已正确

### 1.5 真正的问题点（dev-worker 关注）
- **当 viewport 突然从 1024px 缩到 < 768px** 时，desktop sidebar 应该立刻消失（已是 `display: none`）
- **但 sidebar 切换有 0.3s transition 动画**，动画过程中可能产生视觉残影
- **`body` 没有 `overflow-x: hidden`**，可能导致父容器意外溢出

---

## 2. BUG #2 根因分析（MemoryCard select-checkbox）

### 2.1 代码位置
`frontend/src/components/Layout/MemoryCard.vue`

### 2.2 直接根因
```css
.select-checkbox {
  position: absolute;   /* 永远在卡片左上角 */
  top: 12px;
  left: 12px;
  z-index: 5;
}

.card-header {
  padding: 20px 20px 16px;  /* 无 padding-left */
}

.card-title {
  /* 默认无 padding-left */
}
```

**问题链**：
1. `<label class="select-checkbox">` **无 v-if** 控制，**永远渲染**
2. CSS 永远 `position: absolute; top: 12px; left: 12px`
3. `.card-header` padding 不让位 → 标题"被压"
4. 即使没多选，视觉上也"被遮挡"（因为 checkbox 在那里但 z-index 5 又让它显形）

### 2.3 修复方案
**多选模式判断**：通过 `store.isSelectionMode`（或类似状态）控制 select-checkbox 的显示/布局。

**方案 A（推荐）**：checkbox 根据状态用 flex 参与布局
```vue
<label v-if="store.isSelectionMode" class="select-checkbox" @click.stop>
  <input type="checkbox" ... />
</label>
```
CSS：
```css
.memory-card { display: flex; gap: 12px; }
.select-checkbox { position: static; flex-shrink: 0; padding-top: 2px; }
.card-header { flex: 1; padding: 20px 20px 16px 0; /* 左侧不再需要 padding，因为 checkbox 是 flex item */ }
```

**方案 B（最小改动）**：保持 absolute，但非多选时 `display: none`
```vue
<label v-if="store.isSelectionMode" class="select-checkbox" ...>...</label>
```
然后响应式区给 `.memory-card.select-mode .card-header` 加 `padding-left: 36px` 即可。

**方案 C（最佳）**：方案 A 的优雅版——用 `display: flex` 让 card 始终 flex，checkbox 用 `v-show` + transition 控制可见性，card-header 的 padding-left 始终给 checkbox 留位（不管 visible 与否都不抖动）。

### 2.4 关键约束
- **`store.toggleSelect(memory.id)` 逻辑不要改**（store 已有）
- **不影响 card 整体交互**（点击 card-header 仍然 toggle expanded）
- **桌面端和移动端都要修**

---

## 3. 测试要求（dev-worker 完成后自检）

### 3.1 BUG #1 自检
- 在 Chrome DevTools 模拟 200px / 320px / 400px / 768px / 1024px / 1280px / 1920px 七个宽度
- 检查 sidebar 元素不重叠、不溢出
- 截图存到 `docs/qa/P34/sidebar-<width>.png`

### 3.2 BUG #2 自检
- 单选模式（store.isSelectionMode = false）：截图 `memcard-single.png`——checkbox 完全不可见
- 多选模式（store.isSelectionMode = true）：截图 `memcard-multi.png`——checkbox 独立列，标题完整不截断
- 各 viewport 宽度（200/400/768/1280）下都正常

### 3.3 不回归
- 桌面端 ≥ 1024px：原有布局像素级一致
- 已有 mobile 模式（< 768px）：tab bar / header / bottom sheet 行为不变

---

## 4. 文件修改清单（dev-worker 关注）

| 文件 | 修改点 | 风险 |
|---|---|---|
| `frontend/src/components/Layout/AppSidebar.vue` | 边界 case 健壮性（无需大改） | 低 |
| `frontend/src/components/Layout/MemoryCard.vue` | select-checkbox 改 flex 布局 或 加 v-if 显隐 | 中 |
| `frontend/src/App.vue` | main-wrapper 布局健壮性 | 中 |
| `frontend/src/styles/main.css` | 加 `body { overflow-x: hidden }` 防意外溢出 | 低 |
| `frontend/dist/**` | 构建产物（需 `npm run build` 后重生成） | 中 |

---

## 5. 完成标准

dev-worker 提交后，qa-worker 在以下条件全部满足时标 done：
1. BUG #1 七个 viewport 截图全部无元素重叠
2. BUG #2 单选/多选截图清晰区分，标题无截断
3. 桌面端（≥1024px）回归测试无视觉变化
4. `frontend/dist/` 重新构建并加 cache-busting
5. 修复后 5 分钟内无新增 console 报错
