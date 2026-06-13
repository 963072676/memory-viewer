# Vendor EOL Tracking

> 跟踪项目关键依赖的 EOL (End-of-Life) 状态。dev-worker 在执行依赖升级前必须先看本文件。
> 创建于 2026-06-13 PM-20260612-002 F3。

---

## vue-i18n v9 → v11

### 当前状态
- **当前版本**:`vue-i18n@^9.13.0`(见 `frontend/package.json` L16)
- **EOL 日期**:vue-i18n v9 维护期已结束 — 2025-12 起仅安全补丁, 无新功能
- **迁移目标**:`vue-i18n@^11.0.0`(Vue 3.5+ 兼容)

### 影响范围
- `frontend/src/main.ts` — i18n 初始化(createI18n 配置)
- `frontend/src/locales/{zh-CN,en-US}.json` — locale 消息(异步按需加载)
- `frontend/src/components/LanguageSwitcher.vue` — 切语言入口
- 所有 `frontend/src/**/*.vue` 用 `$t()` / `t()` 的文件 — 翻译调用

### 主要 Breaking Changes (v9 → v11)
1. **`globalInjection: true` 默认行为变更** — v11 默认全局注入 `$t`, 但 composition API 推荐用 `useI18n()` 显式拿
2. **类型签名升级** — `I18nLocale` 类型结构变化, 我们的 `createI18n()` 返回类型需更新
3. **fallback 策略** — `fallbackLocale: 'zh-CN'` 仍支持, 但默认 warn 行为更严格
4. **异步加载** — `dynamic import` 模式保持兼容, 不需要改 `loadMessages`

### 跟踪状态
- **当前阶段**:跟踪中, **本工单不执行迁移**(只跟踪)
- **下次评估**:2026 Q4 前完成(用户拍板)
- **Owner**:dev-worker(等 chief 派单)

### 验证
迁移完成后必须验证:
- `npm run type-check` 0 errors
- `npm run build` 成功
- 切语言(中文 → 英文 → 中文)无 fallback warn 刷屏
- zh-CN 首屏 < 20K(继承 PM-20260612-001 AC-11)

### 参考链接
- vue-i18n 官方迁移指南:https://vue-i18n.intlify.dev/guide/migration/breaking10.html
- v10 → v11 迁移:https://vue-i18n.intlify.dev/guide/migration/breaking11.html

---

## 其他跟踪项 (占位, 待补)

| 依赖 | 当前版本 | EOL | 状态 |
|---|---|---|---|
| `pinia` | `^2.1.0` | 健康 | OK |
| `vue` | `^3.4.0` | 健康 | OK |
| `vue-router` | `^4.3.0` | 健康 | OK |
| `vue-virtual-scroller` | `^2.0.0-beta.8` | beta 状态, 关注 | 评估中 |
| `force-graph` | `^1.51.4` | 关注中 | 评估中 |
