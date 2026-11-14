# 更新日志 / Changelog

本项目的所有显著变更记录在此文件中。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.2.0] - 2026-11-14

### 新增
- **AI 专区 · 教程栏目**（`#/tutorials`）：汇聚 GitHub 优质教程，共 6 组
  - 编程 Agent · 官方文档（Claude Code、OpenAI Codex CLI、Gemini CLI、Cursor、Aider、Cline、Continue、Copilot、Devin、SWE-agent 等）
  - 自己造 Agent · 框架与范式（LangGraph、AutoGen、CrewAI、MetaGPT、smolagents、OpenHands、agent-from-scratch 教程等）
  - Prompt 与上下文工程、MCP 与工具生态、中文资源、通用编程教程
  - 支持分组切换与关键词搜索，复用 AI 导航页的搜索与卡片渲染逻辑
- **教程自动采集脚本** `scripts/fetch-tutorials.mjs`：按 5 组查询调用 GitHub Search API，按星标与更新时间排序，自动剔除已人工收录的链接与归档仓库，输出 `site/data/tutorials-auto.js` / `.json`；支持 `GITHUB_TOKEN` 提速与 403/429 退避重试
- PWA 快捷方式新增「教程」；`manifest` 描述补充教程合集

### 修复
- **左上角品牌图标与 favicon 不一致**：站点内联 SVG 原用 `#5E9BFF → #7C5CFF → #FF6482` 并带中央白点，而 `scripts/gen-icons.py` 生成的 favicon / PNG / ico / icns 用 `#2660EB → #00BEFF → #23E6A0` 加 W 字标。现统一为后者，品牌视觉在网页、PWA、桌面端完全一致
- `.brand-mark` 投影色由紫色 `rgba(124, 92, 255, 0.3)` 改为品牌蓝 `rgba(38, 96, 235, 0.28)`
- 首页与文档中硬编码的仓库数量 `3265` 更正为实际的 `3385`（`app.js`、`site/data/docs.js`、`README.md`、`README.en.md`）

### 内部
- 自检构建标记 `__ORBIT_BUILD__` 更新为 `wbit-1.2.0`，`config.version` 同步 `1.2.0`
- Service Worker 缓存版本 `wbit-shell-v2`，预缓存清单加入两个教程数据文件
- smoke-test 新增「教程栏目」渲染检查与 `/tutorials` 路由检查

## [1.1.0] - 2026-11-14

### 新增
- **Markdown 渲染器升级**（仓库详情页 README 预览）：
  - 支持表格语法（`| 单元格 |`），含 `:-:` 居中 / `--:` 右对齐，无表头分隔行的管道文本按普通段落处理
  - 支持任务列表（`- [x]` / `- [ ]`），渲染为勾选框样式
  - 支持有序列表（`1.` / `2)`）及一层缩进嵌套列表
  - 行内代码（`` `code` ``）受保护，不再被粗体 / 斜体 / 链接规则二次改写

### 修复
- `sitemap.xml` 内全部地址由旧域名 `DaiYiqq.github.io/orbit-github-nav` 更正为 `wanghaaoming.github.io/wbit`
- 旧版浏览器（不支持 ES2022 的 Edge 92 等）访问时优雅跳过云服务 SDK 加载，消除控制台未捕获错误；其余功能不受影响

### 内部
- 自检构建标记 `__ORBIT_BUILD__` 更新为 `wbit-1.1.0`
- smoke-test 联系页断言适配品牌信息

## [1.0.0] - 2026-11-14

### 首发
- 基于 [DaiYiqq/orbit-github-nav](https://github.com/DaiYiqq/orbit-github-nav)（GPL-3.0）的个人化部署与品牌更名：WBit
- GitHub Pages 自动部署（`.github/workflows/deploy-pages.yml`）
- 仓库索引每周自动更新（`.github/workflows/update-data.yml`，当前 3385+ 条）
- 功能完整保留：搜索 / 筛选 / 收藏（本地 + 云同步）/ 源码浏览 / PWA 安装 / PAT 连接 GitHub / 命令面板 / 深浅色主题
- 遵循 GPL-3.0 许可证，保留原作者署名
