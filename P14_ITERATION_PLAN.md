# Memory Viewer — P14 开源化基础改造

> **日期**: 2026-05-29
> **目标**: 消除硬编码，建立配置系统，让任何人 clone 后能一键运行

---

## 任务清单

### T1: 消除硬编码路径（P0）
- config.py 中所有默认路径改为相对于项目目录（./data/...）
- backup.py, versioning.py 的 BACKUP_DIR/VERSIONS_DIR 从 config 读取
- 支持 memory-viewer.yaml 配置文件（优先级：环境变量 > yaml > 默认值）

### T2: 配置文件系统（P0）
- 创建 config/defaults.yaml（默认配置模板）
- 创建 backend/app/config_loader.py（读取 yaml + 环境变量合并）
- config.py 改为从 config_loader 读取

### T3: Docker 通用化（P0）
- docker-compose.yml 改为通用配置（不绑定 /opt/data）
- Dockerfile 添加配置文件挂载说明
- 创建 docker-compose.example.yml（带注释的示例）

### T4: README.md（P0）
- 项目简介（一句话）
- 功能列表（精选 10 个核心功能）
- 快速开始（clone → 配置 → docker compose up）
- 截图（可用现有 /tmp/memory-viewer-v2.png）
- 架构图（文字版）
- 配置说明
- API 文档链接（/api/docs）
- 开发指南
- License: MIT

### T5: 环境变量清理（P1）
- 所有配置项统一前缀 MV_（Memory Viewer）
- 创建 .env.example 文件
- 文档中列出所有支持的环境变量

### T6: 项目结构整理（P1）
- 创建 data/ 目录（默认数据目录）
- 创建 docs/ 目录
- 移动迭代计划文件到 docs/iterations/
- 创建 CONTRIBUTING.md

## 验收标准
- [ ] clone 后不修改任何代码即可 docker compose up
- [ ] README 包含完整的快速开始指南
- [ ] 所有路径通过环境变量或配置文件可覆盖
- [ ] .env.example 包含所有配置项及说明
