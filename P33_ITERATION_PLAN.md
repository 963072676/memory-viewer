# P33 迭代计划

> **日期**: 2026-05-31
> **阶段**: P33
> **目标**: 实现 F-27 MCP Server 模式

---

## 状态

P32 (F-24 记忆版本历史) 已完成。
backlog 剩余: **F-27 MCP Server 模式** (最后一个未完成项)。
选择 **F-27 MCP Server 模式** 作为 P33 目标。

---

## F-27 MCP Server 模式 功能描述

**问题**: 其他 Agent 无法直接查询 Memory Viewer 的记忆数据，需要通过 HTTP API 手动调用。

**解决方案**:
- 将 Memory Viewer 暴露为标准 MCP Server，支持 stdio 传输协议
- 其他 Agent 可通过 MCP 协议直接查询、搜索、创建记忆
- 基于现有 `app/routers/mcp.py` 的 JSON-RPC 实现进行扩展

### 现状分析

| 组件 | 状态 | 说明 |
|------|------|------|
| `backend/app/routers/mcp.py` | ✅ 存在 | JSON-RPC 2.0 over HTTP，`/mcp/jsonrpc` 端点已注册 |
| Methods: `memory.list`, `memory.get`, `memory.search`, `memory.create` | ✅ 存在 | 基础 CRUD 操作 |
| MCP stdio transport | ❌ 缺失 | 当前使用 HTTP transport，需新增 stdio 支持 |
| MCP tool schema / manifest | ❌ 缺失 | 需定义标准 MCP tool definitions |
| MCP `memory.update` method | ❌ 缺失 | 需补充 update/delete 方法 |
| MCP `memory.delete` method | ❌ 缺失 | 需补充 update/delete 方法 |
| MCP auth (API Key via env) | ✅ 存在 | `_MCP_API_KEY` 环境变量认证 |

---

## 技术方案

### MCP 协议实现

MCP (Model Context Protocol) 标准使用 **stdio 传输**（stdin/stdout），与现有 HTTP/JSON-RPC 并行运行。

**架构**:
```
Other Agent (MCP Client)
        ↓ stdio
mcp_server.py (stdio transport) → Memory Viewer backend services
        ↓
Hermes Agent
```

**启动方式**:
```bash
python -m app.mcp_server
# 或
uvicorn app.main:app --host 0.0.0.0 --port 8501  # HTTP 模式继续可用
```

### 方法设计 (JSON-RPC 2.0)

| Method | Parameters | Description |
|--------|------------|-------------|
| `memory.list` | `limit`, `offset`, `type` | 列出记忆，支持分页和类型过滤 |
| `memory.get` | `id` | 获取单条记忆详情 |
| `memory.search` | `query`, `limit` | 搜索记忆 |
| `memory.create` | `title`, `content`, `type`, `concepts`, `strength` | 创建新记忆 |
| `memory.update` | `id`, `title`, `content`, `type`, `concepts`, `strength` | 更新记忆 |
| `memory.delete` | `id` | 删除记忆 |
| `health.check` | — | 健康检查 |

### MCP Tool Manifest

标准 MCP `initialize` 响应需包含 tools manifest：
```json
{
  "protocolVersion": "2024-11-05",
  "capabilities": {"tools": {}},
  "tools": [
    {"name": "memory_list", "description": "...", "inputSchema": {...}},
    {"name": "memory_get", "description": "...", "inputSchema": {...}},
    {"name": "memory_search", "description": "...", "inputSchema": {...}},
    {"name": "memory_create", "description": "...", "inputSchema": {...}},
    {"name": "memory_update", "description": "...", "inputSchema": {...}},
    {"name": "memory_delete", "description": "...", "inputSchema": {...}}
  ]
}
```

---

## 任务拆分

### P33-T1: MCP stdio transport 实现

**实现**:
1. 新建 `backend/app/mcp_server.py`
2. 使用 `sys.stdin/stdout` 实现 stdio 传输
3. 解析 MCP JSON-RPC 消息
4. 调用现有 services 中的 MCP 方法

**验收标准**:
- AC-F27-T1-1: `python -m app.mcp_server` 启动后不阻塞
- AC-F27-T1-2: 从 stdin 读取 JSON-RPC 请求，返回 stdout JSON-RPC 响应

### P33-T2: MCP `initialize` 协议握手

**实现**:
1. 处理 `initialize` 请求，返回 protocolVersion + capabilities
2. 处理 `tools/list` 请求，返回 tool manifest
3. 处理 `tools/call` 请求，分发到对应方法

**验收标准**:
- AC-F27-T2-1: `initialize` 返回正确的 protocol version
- AC-F27-T2-2: `tools/list` 返回完整 tool definitions

### P33-T3: 补充 `memory.update` 和 `memory.delete` 方法

**实现**:
1. 在 `mcp.py` router 中补充 `memory.update` 和 `memory.delete`
2. 复用 `agentmemory` service 中的 `update_memory` 和 `delete_memory`

**验收标准**:
- AC-F27-T3-1: `memory.update` 可更新记忆字段
- AC-F27-T3-2: `memory.delete` 可删除记忆

### P33-T4: MCP Server 入口脚本

**实现**:
1. 新建 `backend/mcp_server.py` 作为独立入口
2. 支持 `--port` 参数指定 HTTP 模式端口
3. 支持 `--api-key` 参数指定认证密钥

**验收标准**:
- AC-F27-T4-1: `python backend/mcp_server.py` 启动 stdio MCP Server
- AC-F27-T4-2: `python backend/mcp_server.py --port 8501` 启动 HTTP MCP Server

### P33-T5: MCP 认证机制完善

**实现**:
1. 环境变量 `MCP_API_KEY` 控制是否需要认证
2. stdio 模式下通过 header 传递 API Key（伪装 MCP 协议头）

**验收标准**:
- AC-F27-T5-1: 无 `MCP_API_KEY` 时，不进行认证
- AC-F27-T5-2: 有 `MCP_API_KEY` 时，请求必须携带正确密钥

### P33-T6: 集成测试

**实现**:
1. MCP Client 模拟脚本测试 stdio 交互
2. 验证所有方法正确响应

**验收标准**:
- AC-F27-T6-1: 使用 mcp 官方测试客户端验证
- AC-F27-T6-2: pytest 无新增失败

---

## 验收标准（汇总）

| ID | 描述 | 优先级 |
|----|------|--------|
| AC-F27-1 | MCP Server 支持 stdio 传输启动 | P0 |
| AC-F27-2 | MCP Server 支持 HTTP/JSON-RPC 启动 | P0 |
| AC-F27-3 | `memory.list` 返回记忆列表（分页） | P0 |
| AC-F27-4 | `memory.get` 返回单条记忆详情 | P0 |
| AC-F27-5 | `memory.search` 返回搜索结果 | P0 |
| AC-F27-6 | `memory.create` 创建新记忆 | P0 |
| AC-F27-7 | `memory.update` 更新记忆 | P0 |
| AC-F27-8 | `memory.delete` 删除记忆 | P0 |
| AC-F27-9 | `initialize` 协议握手正常 | P0 |
| AC-F27-10 | `tools/list` 返回完整工具定义 | P0 |
| AC-F27-11 | API Key 认证机制正常工作 | P0 |
| AC-F27-12 | pytest 无新增失败 | P0 |

---

## 文件清单

| 操作 | 文件路径 |
|------|---------|
| 新增 | `backend/app/mcp_server.py` (stdio transport 实现) |
| 修改 | `backend/app/routers/mcp.py` (补充 update/delete) |
| 新增 | `backend/mcp_server.py` (独立入口脚本) |
| 新增 | `backend/tests/test_mcp_server.py` |
| 修改 | `backend/requirements.txt` (如需新依赖) |
| 修改 | `README.md` (MCP Server 使用说明) |

---

## 依赖关系

```
P33-T1 (stdio transport)
    ↓
P33-T2 (initialize + tools/list)
    ↓
P33-T3 (update/delete methods) ← 可并行
    ↓
P33-T4 (entry script)
    ↓
P33-T5 (auth)
    ↓
P33-T6 (integration test)
```

---

## 技术说明

### stdio vs HTTP

MCP 协议标准使用 stdio，但 Memory Viewer 同时提供 HTTP API。
两种模式共用同一套 business logic (services)，仅传输层不同。

### MCP Protocol Version

当前 MCP 草案版本: `2024-11-05` (根据 Anthropic MCP 规范)

### JSON-RPC 2.0 错误码

| code | meaning |
|------|---------|
| -32600 | Invalid Request |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32000 | Internal error |
| -32001 | Authentication failed |