# Memory Viewer v2 Bug Fix Report

## 问题1：侧边栏无法收回

### 根本原因
`sidebarCollapsed` 状态在 `stores/ui.ts` 中初始值为硬编码 `false`，且没有持久化到 localStorage。
刷新页面后状态丢失。

### 修复方法
**文件：** `frontend/src/stores/ui.ts`

**修改内容：**
1. 初始化时从 localStorage 读取状态：`localStorage.getItem('sidebarCollapsed') === 'true'`
2. 添加 `watch` 监听变化并保存到 localStorage

```typescript
// 修改前
const sidebarCollapsed = ref(false)

// 修改后
const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')

// Persist sidebar collapsed state to localStorage
watch(sidebarCollapsed, (val) => {
  localStorage.setItem('sidebarCollapsed', String(val))
})
```

---

## 问题2：刷新页面报错 "Memory not found: collectio"

### 根本原因
当用户访问包含 `collection` 查询参数的页面并刷新时：
1. 路由 `/memory/:id` 将 "collection" 作为 memory ID 解析
2. `MemoryDetailView.vue` 调用 `fetchAgentMemoryById("collection")`
3. 后端 `/api/agentmemory/collection` 返回 404

错误消息 "Memory not found: collectio" 是因为后端错误消息长度为 28 字符，"collection" 被截断为 "collectio"。

### 修复方法
**文件：** `frontend/src/views/MemoryDetailView.vue`

**修改内容：**
在 `loadMemory()` 函数中添加 ID 有效性检查，当 ID 为 "collection" 或其他无效值时，显示错误并跳转到 `/agentmemory`。

```typescript
// 修改前
async function loadMemory() {
  const id = route.params.id as string
  if (!id) {
    error.value = 'Missing memory ID'
    return
  }

// 修改后
async function loadMemory() {
  const id = route.params.id as string
  if (!id || id === 'collection') {
    error.value = 'Invalid memory ID'
    router.push('/agentmemory')
    return
  }
```

---

## 文件修改清单

| 文件 | 修改内容 | 状态 |
|------|----------|------|
| `frontend/src/stores/ui.ts` | 添加 `sidebarCollapsed` 的 localStorage 持久化 | ✅ 已修复 |
| `frontend/src/views/MemoryDetailView.vue` | 添加 ID 有效性检查，防止无效 ID 触发 API 调用 | ✅ 已修复 |

---

## 测试建议

1. **侧边栏测试：**
   - 点击收起按钮 → 侧边栏应收缩到 60px
   - 刷新页面 → 收起状态应保持
   - 重新打开浏览器 → 收起状态应保持

2. **Memory not found 测试：**
   - 直接访问 `/memory/collection` → 应显示 "Invalid memory ID" 并跳转到 `/agentmemory`
   - 正常访问 `/memory/<valid-uuid>` → 应正常加载记忆详情