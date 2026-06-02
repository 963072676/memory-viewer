# Memory Viewer — P15 记忆源适配器系统

> **日期**: 2026-05-29
> **目标**: 建立 MemorySource 抽象层，支持 Hermes/agentmemory/mem0 三个适配器

---

## 架构设计

```
MemorySource (抽象基类 - backend/app/adapters/base.py)
├── HermesAdapter      — 读 ~/.hermes/memories/*.md
├── AgentMemoryAdapter — 读 agentmemory JSON 缓存 / MCP
├── Mem0Adapter        — 对接 mem0 REST API
├── JsonFileAdapter    — 读任意 JSON 文件
└── CustomHTTPAdapter  — 对接任意 HTTP API
```

## 任务清单

### T1: 适配器基类（P0）
创建 backend/app/adapters/base.py：
```python
from abc import ABC, abstractmethod
from typing import Optional

class MemoryItem:
    id: str
    title: str
    content: str
    type: str
    concepts: list[str]
    strength: float
    created_at: str
    updated_at: str
    source: str  # 来源适配器名称
    metadata: dict

class MemorySource(ABC):
    name: str
    source_type: str  # hermes, agentmemory, mem0, json_file, custom_http
    
    @abstractmethod
    async def list(self, limit=50, offset=0) -> list[MemoryItem]: ...
    
    @abstractmethod
    async def get(self, id: str) -> Optional[MemoryItem]: ...
    
    @abstractmethod
    async def search(self, query: str, limit=20) -> list[MemoryItem]: ...
    
    @abstractmethod
    async def health(self) -> bool: ...
    
    # 可选实现
    async def create(self, data) -> MemoryItem: raise NotImplementedError
    async def update(self, id, data) -> MemoryItem: raise NotImplementedError
    async def delete(self, id) -> bool: raise NotImplementedError
```

### T2: Hermes 适配器（P0）
创建 backend/app/adapters/hermes.py：
- 读取 memories_dir 下的 *.md 文件
- 解析 frontmatter（YAML header）获取 metadata
- content = markdown body
- 支持 profiles_dir 下的多 profile

### T3: AgentMemory 适配器（P0）
创建 backend/app/adapters/agentmemory.py：
- 复用现有 agentmemory.py 的读取逻辑
- 包装为 MemorySource 接口

### T4: Mem0 适配器（P1）
创建 backend/app/adapters/mem0.py：
- 对接 mem0 REST API（https://api.mem0.ai）
- 需要 MEM0_API_KEY 环境变量
- list/get/search/create/update/delete

### T5: 适配器注册中心（P0）
创建 backend/app/adapters/registry.py：
- 从 memory-viewer.yaml 的 sources 配置加载适配器
- 统一查询接口：list_all(), search_all(), get_by_id()
- 自动检测 enabled=auto 的适配器是否可用

### T6: 统一 API 端点（P0）
修改 routers/：
- GET /api/sources — 列出所有已注册的记忆源
- GET /api/sources/{name}/memories — 查询指定源
- GET /api/memories/unified — 聚合所有源的记忆
- GET /api/memories/unified/search — 跨源搜索

### T7: 前端适配（P1）
- 侧边栏增加"记忆源"页面
- 显示各源状态（在线/离线/错误）
- 统一列表中显示来源标签

## 验收标准
- [ ] memory-viewer.yaml 配置 3 个源，启动后 /api/sources 返回 3 个
- [ ] /api/memories/unified 聚合所有源的记忆
- [ ] 跨源搜索返回合并结果
- [ ] 189 条回归测试通过
- [ ] 前端构建通过
