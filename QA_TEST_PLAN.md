# QA 测试计划 — Memory Viewer v2 前后端分离重构

> 作者: qa-worker | 日期: 2026-05-28 | 版本: 2.0
> 基线: v1 测试报告（65/65 通过，P0×6 + P1×3 全部通过）

---

## 一、重构变更概述

| 维度 | v1 | v2 |
|---|---|---|
| 架构 | 前后端一体（FastAPI 提供 HTML + API） | 前后端分离（独立前端 + 独立 API 服务） |
| 前端 | `index.html` 由 FastAPI `FileResponse` 提供 | 独立静态资源（Nginx / CDN / Vite 构建） |
| API | FastAPI 内嵌，同源 | FastAPI 独立部署，CORS 跨域 |
| 测试 | 混合测试（TestClient 同进程） | 前端独立测试 + API 独立测试 + 集成测试 |

### 核心风险

1. **API 向后兼容性** — 端点路径、请求/响应格式不可变
2. **前端功能退化** — 拆分后前端可能丢失数据加载逻辑
3. **CORS 配置** — 跨域请求是否正确工作
4. **静态资源服务** — 前端部署路径、路由 fallback

---

## 二、回归测试清单（确保 v1 功能不丢失）

### 2.1 API 回归（所有现有 API 测试必须原样通过）

| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| REG-API-01 | `GET /api/agentmemory` 返回 200 | 返回 `{memories: [...]}` 结构 | P0 |
| REG-API-02 | agentmemory 字段完整性 | 每条记录含 id/type/title/content/concepts/files/createdAt/updatedAt/strength/version | P0 |
| REG-API-03 | agentmemory 空缓存 | 缓存文件不存在时返回 `{memories: []}` | P0 |
| REG-API-04 | agentmemory 缓存损坏 | JSON 解析失败时返回 `{memories: []}` | P1 |
| REG-API-05 | `GET /api/hermes-memory` 返回 200 | 返回 `{global: {memory, user}, profiles: {}}` 结构 | P0 |
| REG-API-06 | hermes-memory § 分隔符解析 | 多条记忆正确拆分、trim | P0 |
| REG-API-07 | hermes-memory 空文件 | MEMORY.md 不存在时返回空数组 | P1 |
| REG-API-08 | hermes-memory 单条/多条 | 边界情况解析正确 | P1 |
| REG-API-09 | `GET /api/profiles` 返回列表 | 包含所有有 memories 目录的 profile | P0 |
| REG-API-10 | profiles 排除无 memories 目录 | `no-memories` profile 不出现 | P1 |
| REG-API-11 | 不存在的 API 端点返回 404 | `GET /api/nonexistent` → 404 | P1 |
| REG-API-12 | 特殊字符/emoji 内容保留 | `<script>` 标签、emoji 🧠、换行符原样返回 | P0 |
| REG-API-13 | API 响应时间 < 1s | 三个端点均满足性能基线 | P1 |

### 2.2 前端回归

| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| REG-FE-01 | 页面可访问 | 部署地址返回 200 + HTML | P0 |
| REG-FE-02 | 数据正确加载 | 页面加载后 agentmemory 列表有数据 | P0 |
| REG-FE-03 | 两套系统切换 | AgentMemory 和 Hermes Memory 视图可切换 | P0 |
| REG-FE-04 | 搜索功能 | 输入关键词可过滤记忆条目 | P1 |
| REG-FE-05 | 空状态展示 | 无数据时显示空状态 UI | P1 |
| REG-FE-06 | 错误状态展示 | API 不可达时显示错误状态 UI | P1 |
| REG-FE-07 | 加载骨架屏 | 加载中显示 shimmer 骨架 | P1 |
| REG-FE-08 | XSS 防护 | `escapeHtml` 函数存在且被调用 | P0 |
| REG-FE-09 | 响应式布局 | viewport meta + media query 存在 | P1 |
| REG-FE-10 | Apple 风格 UI | SF Pro 字体、配色、圆角验证 | P2 |

---

## 三、新架构测试

### 3.1 前端独立构建测试

| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| FE-BUILD-01 | 构建成功 | `npm run build` / `vite build` 零错误退出 | P0 |
| FE-BUILD-02 | 产物目录存在 | `dist/` 目录包含 `index.html` | P0 |
| FE-BUILD-03 | 静态资源引用正确 | CSS/JS 资源路径可在浏览器加载 | P0 |
| FE-BUILD-04 | 产物体积合理 | 总产物 < 500KB（gzip 后） | P2 |
| FE-BUILD-05 | 无 TypeScript/ESLint 错误 | lint 检查零 warning | P1 |
| FE-BUILD-06 | 环境变量注入 | API base URL 可通过 env 配置 | P0 |
| FE-BUILD-07 | HTML 模板正确 | `<title>`, `<meta charset>`, `<meta viewport>` 存在 | P1 |

### 3.2 前端独立运行测试

| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| FE-RUN-01 | 开发服务器启动 | `npm run dev` 可启动，端口可访问 | P1 |
| FE-RUN-02 | HMR 热更新 | 修改源码后页面自动刷新 | P2 |
| FE-RUN-03 | API 代理配置 | 开发模式下 `/api/*` 代理到后端 | P0 |
| FE-RUN-04 | 生产模式静态服务 | `npx serve dist` 可正常访问 | P1 |

### 3.3 前端单元/组件测试

| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| FE-UNIT-01 | `escapeHtml` 函数 | `<script>` → `&lt;script&gt;`，emoji 不丢失 | P0 |
| FE-UNIT-02 | API 调用函数 | fetch `/api/agentmemory` 返回正确格式 | P0 |
| FE-UNIT-03 | 空数据渲染 | 空数组时渲染空状态组件 | P1 |
| FE-UNIT-04 | 错误处理逻辑 | fetch 失败时触发 error state | P1 |
| FE-UNIT-05 | 搜索过滤逻辑 | 输入关键词正确过滤列表 | P1 |
| FE-UNIT-06 | 日期格式化 | ISO 日期字符串正确格式化显示 | P2 |
| FE-UNIT-07 | 记忆条目渲染 | 单条记忆正确渲染所有字段 | P1 |

### 3.4 API 独立部署测试

| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| API-DEP-01 | 独立启动 | API 服务不依赖前端文件即可启动 | P0 |
| API-DEP-02 | CORS 头存在 | 响应含 `Access-Control-Allow-Origin` | P0 |
| API-DEP-03 | CORS 预检请求 | `OPTIONS /api/agentmemory` 返回 200 + CORS 头 | P0 |
| API-DEP-04 | 移除 `GET /` 端点 | API 服务不再 serve HTML（或返回 404/提示） | P1 |
| API-DEP-05 | 健康检查端点 | `GET /api/health` 返回 200（新增） | P1 |
| API-DEP-06 | API 文档 | `/docs` 或 `/redoc` 可访问 | P2 |
| API-DEP-07 | 环境变量配置 | `MEMORY_VIEWER_PORT`, `HERMES_HOME` 等生效 | P0 |

### 3.5 跨域集成测试

|| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| CORS-01 | 前端域 → API 域请求成功 | 不同 origin 下 fetch 正常 | P0 |
| CORS-02 | 只允许 GET 方法 | POST/PUT/DELETE 被拒绝 | P1 |
| CORS-03 | 任意 Origin 可访问 | `allow_origins=["*"]` 生效 | P0 |
| CORS-04 | 非 CORS 请求正常 | 同源请求不受影响 | P1 |

### 3.6 配置路径验证测试

|| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| CONFIG-01 | Hermes profiles 目录存在 | `/home/.hermes/profiles` 存在且可读 | P0 |
| CONFIG-02 | Hermes memories 目录存在 | `/opt/data` 存在且可读 | P0 |
| CONFIG-03 | AgentMemory cache 目录存在 | `/opt/data/.agentmemory/` 目录存在 | P0 |
| CONFIG-04 | 路径为绝对路径 | 所有配置路径均为绝对路径 | P1 |
| CONFIG-05 | 无符号链接循环 | 配置路径不包含无效符号链接 | P1 |

> **注意**: 配置路径验证测试使用 session-scope fixture，在所有测试之前运行。若路径不存在，整个测试会话 FAIL（不是 skip）。

### 3.7 文件系统同步测试

|| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| FS-SYNC-01 | API profiles 与文件系统一致 | GET /api/profiles 返回的列表与目录内容一致 | P0 |
| FS-SYNC-02 | Profile memory 条目数量一致 | API 返回的 memory 条目数与 MEMORY.md § 解析结果一致 | P0 |
| FS-SYNC-03 | Memory 内容长度合理 | 每个 memory 内容非空且 < 1MB | P1 |
| FS-SYNC-04 | AgentMemory cache 与 API 一致 | cache 文件条数与 API 返回数一致 | P0 |
| FS-SYNC-05 | 所有 memories 目录可访问 | 每个 profile 的 memories 目录有读权限 | P1 |

### 3.8 CI 自动化验证

|| 测试 ID | 测试项 | 验证内容 | 优先级 |
|---|---|---|---|
| CI-01 | 配置路径检查 | 启动前验证所有配置路径存在 | P0 |
| CI-02 | 后端测试套件 | pytest tests/ 全部通过 | P0 |
| CI-03 | 前端构建 | npm run build 成功且产物完整 | P0 |
| CI-04 | 服务健康检查 | 后端服务启动 + /api/health 返回 200 | P0 |
| CI-05 | API 端点验证 | /api/profiles, /api/agentmemory, /api/hermes-memory 全部可用 | P0 |

> **CI 脚本**: `/opt/data/memory-viewer/v2/ci_validate.sh` — 自动化完整验证流程

---

## 四、验收标准

### P0 — 必须通过（阻塞发布）

| AC 编号 | 验收标准 | 验证方法 |
|---|---|---|
| V2-AC-01 | **API 向后兼容**: 所有 v1 API 端点路径、请求参数、响应格式完全不变 | 回归测试 REG-API-01~13 全部通过 |
| V2-AC-02 | **前端功能完整**: v1 所有前端功能在 v2 中可正常使用 | 回归测试 REG-FE-01~10 全部通过 |
| V2-AC-03 | **独立部署**: API 和前端可独立启动、独立访问 | FE-BUILD-01, FE-BUILD-02, API-DEP-01 通过 |
| V2-AC-04 | **跨域通信**: 前端从不同 origin 调用 API 成功 | CORS-01, CORS-03 通过 |
| V2-AC-05 | **安全基线**: XSS 防护不退化 | REG-FE-08 通过（escapeHtml 存在且被调用） |
| V2-AC-06 | **现有测试全通过**: v1 的 65 条测试全部兼容通过 | `pytest` 全绿（或等价替代） |

### P1 — 应该通过（影响体验）

| AC 编号 | 验收标准 | 验证方法 |
|---|---|---|
| V2-AC-07 | **前端构建产物可部署**: dist/ 目录可直接部署到 Nginx/CDN | FE-BUILD-03, FE-RUN-04 通过 |
| V2-AC-08 | **API 性能不退化**: 响应时间 < 1s 基线保持 | REG-API-13 通过 |
| V2-AC-09 | **开发体验**: 前端开发模式下可代理 API 请求 | FE-RUN-01, FE-RUN-03 通过 |

### P2 — 可选通过（锦上添花）

| AC 编号 | 验收标准 | 验证方法 |
|---|---|---|
| V2-AC-10 | **产物体积合理**: 前端构建产物 gzip < 500KB | FE-BUILD-04 通过 |
| V2-AC-11 | **API 文档可用**: Swagger/Redoc 可访问 | API-DEP-06 通过 |
| V2-AC-12 | **前端单元测试覆盖**: 核心函数有单元测试 | FE-UNIT-01~07 通过 |

---

## 五、自动化测试方案

### 5.1 测试金字塔

```
         ╱ E2E (Playwright) ╲         ← 5~8 条关键路径
        ╱   集成测试 (API+CORS)  ╲      ← 15~20 条
       ╱  前端单元 + API 单元测试  ╲    ← 30~40 条
      ╱─────────────────────────────╲
```

### 5.2 技术栈

| 层级 | 工具 | 说明 |
|---|---|---|
| API 单元测试 | pytest + httpx (AsyncClient) | 现有 test_api.py 迁移，改用 httpx 支持异步 |
| API 集成测试 | pytest + requests | 真实 HTTP 请求测试跨域、部署 |
| 前端单元测试 | Vitest + jsdom | 测试 escapeHtml、API 调用、渲染逻辑 |
| 前端组件测试 | Vitest + @vue/test-utils 或纯 DOM | 测试组件行为 |
| E2E 测试 | Playwright | 关键用户路径端到端验证 |
| 构建测试 | CI 脚本 | npm run build + 断言产物 |

### 5.3 目录结构

```
memory-viewer/
├── v2/
│   ├── backend/
│   │   ├── app.py                    # API 服务
│   │   ├── requirements.txt
│   │   └── tests/
│   │       ├── conftest.py           # 共享 fixtures
│   │       ├── test_api.py           # API 单元测试（迁移自 v1）
│   │       ├── test_api_cors.py      # CORS 专项测试（新增）
│   │       ├── test_api_deploy.py    # 部署集成测试（新增）
│   │       ├── test_config_paths.py # 配置路径验证（新增）
│   │       ├── test_filesystem_sync.py # 文件系统同步测试（新增）
│   │       ├── test_health.py        # 健康检查测试
│   │       └── test_agentmemory.py   # AgentMemory 测试
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── index.html
│   │   │   ├── main.js
│   │   │   └── utils.js             # escapeHtml 等
│   │   ├── tests/
│   │   │   ├── utils.test.js         # 工具函数单元测试
│   │   │   ├── api.test.js           # API 调用逻辑测试
│   │   │   └── render.test.js        # 渲染逻辑测试
│   │   ├── package.json
│   │   └── vite.config.js
│   ├── tests/
│   │   ├── test_e2e.py               # E2E 测试（Playwright）
│   │   ├── test_regression.py        # v1 回归测试套件
│   │   └── test_integration.py       # 跨服务集成测试
│   └── QA_TEST_PLAN.md              # 本文件
```

### 5.4 CI/CD Pipeline

```yaml
# 阶段 1: 后端测试
backend-test:
  steps:
    - pip install -r backend/requirements.txt
    - cd backend && pytest tests/ -v --tb=short
    # 预期: 现有 22 条 + 新增 CORS/部署测试 ≈ 30 条

# 阶段 2: 前端构建 + 测试
frontend-test:
  steps:
    - cd frontend && npm install
    - npm run lint                    # ESLint 零 warning
    - npm run test                    # Vitest 单元测试
    - npm run build                   # 构建验证
    - test -f dist/index.html         # 产物断言
    # 预期: 15~20 条前端测试

# 阶段 3: 集成测试
integration-test:
  steps:
    - 启动 API 服务 (backend/)
    - 启动前端静态服务 (frontend/dist/)
    - pytest tests/test_integration.py -v
    # 预期: 10~15 条集成测试

# 阶段 4: E2E 测试
e2e-test:
  steps:
    - docker-compose up -d
    - pytest tests/test_e2e.py -v     # Playwright
    # 预期: 5~8 条关键路径
```

### 5.5 测试数据策略

| 策略 | 说明 |
|---|---|
| 复用 v1 fixtures | `temp_hermes_home`、`setup_test_data` 等 fixture 直接迁移 |
| Mock API 响应 | 前端测试使用 MSW (Mock Service Worker) 拦截 API |
| 真实数据集成 | CI 最后一阶段使用真实 HERMES_HOME 数据验证 |
| 边界数据 | 空数据、损坏 JSON、超长内容、特殊字符、emoji |

### 5.6 测试数量预估

|| 类别 | v1 | v2 新增 | v2 总计 |
|---|---|---|---|
| API 单元测试 | 16 | +5 (CORS) | 21 |
| Fetch 单元测试 | 6 | 0 | 6 |
| E2E/集成测试 | 43 | +10 (回归) | 53 |
| 前端单元测试 | 0 | +15 | 15 |
| 构建测试 | 0 | +7 | 7 |
| 配置路径测试 | 0 | +5 (CONFIG-01~05) | 5 |
| 文件系统同步测试 | 0 | +5 (FS-SYNC-01~05) | 5 |
| **合计** | **65** | **+47** | **~112** |

> 注：CONFIG 和 FS-SYNC 测试已包含在 pytest 套件中。CI 自动化脚本 `ci_validate.sh` 提供额外的手动/CI 验证。

---

## 六、测试执行计划

### 阶段 1: 重构前基线确认（Day 1）

- [ ] 运行 v1 全部 65 条测试，确认基线 100% 通过
- [ ] 记录 API 响应快照（snapshot），作为 v2 兼容性对照
- [ ] 确认当前 live server 所有端点行为

### 阶段 2: API 独立化测试（Day 2-3）

- [ ] 拆分 API 服务，移除前端 serve 逻辑
- [ ] 运行 API 回归测试 REG-API-01~13
- [ ] 新增 CORS 测试 API-DEP-02, CORS-01~04
- [ ] 新增健康检查端点测试 API-DEP-05

### 阶段 3: 前端独立化测试（Day 3-4）

- [ ] 前端独立构建，运行 FE-BUILD-01~07
- [ ] 前端单元测试 FE-UNIT-01~07
- [ ] 开发模式代理测试 FE-RUN-01~03

### 阶段 4: 集成验证（Day 5）

- [ ] 前后端联调，运行 REG-FE-01~10
- [ ] 跨域集成测试 CORS-01~04
- [ ] E2E 关键路径测试（Playwright）
- [ ] 验收标准 V2-AC-01~12 逐项确认

### 阶段 5: 报告产出（Day 5）

- [ ] 生成 V2 测试报告
- [ ] 标记已知问题和遗留风险
- [ ] 签署验收

---

## 七、风险与缓解

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| v1 测试在 v2 架构下不兼容 | 回归测试失效 | 适配 TestClient → httpx 真实请求 |
| CORS 配置遗漏 | 前端无法调用 API | 专项 CORS 测试 + CI 自动验证 |
| 前端硬编码 API 地址 | 部署环境切换困难 | 环境变量注入 + FE-BUILD-06 测试 |
| 静态资源缓存问题 | 更新后用户看到旧版本 | 构建产物带 hash + 缓存头配置 |
| 前端路由 fallback | 刷新页面 404 | Nginx `try_files` 配置 + 测试 |

---

## 八、产出物清单

|| 文件 | 路径 | 说明 |
|---|---|---|
| 本测试计划 | `v2/QA_TEST_PLAN.md` | 测试策略与用例 |
| 回归测试套件 | `v2/tests/test_regression.py` | v1 功能回归 |
| CORS 测试套件 | `v2/backend/tests/test_api_cors.py` | 跨域专项 |
| 配置路径测试 | `v2/backend/tests/test_config_paths.py` | 配置验证（新增） |
| 文件系统同步测试 | `v2/backend/tests/test_filesystem_sync.py` | 数据一致性（新增） |
| 前端测试套件 | `v2/frontend/tests/*.test.js` | 前端单元测试 |
| 集成测试套件 | `v2/tests/test_integration.py` | 跨服务集成 |
| CI 验证脚本 | `v2/ci_validate.sh` | 自动化 CI 验证（新增） |
| 测试报告 | `v2/QA_TEST_REPORT.md` | 执行结果（执行后产出） |
