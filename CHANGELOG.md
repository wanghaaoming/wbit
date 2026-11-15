# 更新日志 / Changelog

本项目的所有显著变更记录在此文件中。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.3.0] - 2026-11-15

### 新增
- **收藏导出 Markdown 清单**：收藏页新增按钮，按分类分组、组内按星标排序，含链接、星标、语言、许可证与描述，可直接放进 README 或笔记
- **收藏分享链接**（`#/shared?favs=...`）：把收藏编码进 URL，复制即可分享；新增「分享的收藏」页，支持一键把他人分享的项目加入自己的收藏（自动去重、只提示新增数量），索引外的项目给出 GitHub 直达链接
- **项目对比**（`#/compare`）：详情页新增「加入对比」按钮，最多同时对比 6 个项目；对比页并排展示星标（最高值高亮）、Forks、开放 Issues、语言、许可证、最近提交、创建时间、状态、分类与简介；侧栏「发现」分组提供入口（带 `NEW` 标识与数量徽标）
- **新收录页**（`#/whatsnew`）：`scripts/fetch-repos.mjs` 每次运行产出增量快照 `site/data/whats-new.{js,json}`（与上一版索引对比得出新增 / 移除；首次运行或索引重建标记为基线，不把整库当成新增；保留最近 12 次），页面展示新增项目与更新记录时间线
- **项目详情页 README 自动目录**：从渲染后的 README 提取 `#` / `##` / `###` 标题生成目录（少于 3 个标题时不显示），点击平滑滚动到对应小节

### 变更
- 首页入口由「发现」更名为「**GitHub 精选**」（侧栏、移动端标签栏与页面标题同步）
- 首页主视觉文案由「GitHub 上不缺好项目，缺的是找到它的方式。」改为「给你一份 GitHub 的精选清单。」，强调站点提供的是已筛选的清单，而非又一个搜索入口

### 修复
- 项目导出文件名前缀由 `orbit-favorites-*.json` 更正为 `wbit-favorites-*.json`
- 分享图 `assets/social-preview.svg` 内残留的 `Orbit` 品牌字样与旧仓库地址（`DaiYiqq/orbit-github-nav`）更正为 WBit 与当前仓库；图片中的仓库数量 `3265` 更正为 `3385`，并重新导出 `social-preview.png`

### 合规
- 删除 `COMMERCIAL-LICENSE.md` 与 `docs/` 下的商业许可模板、增长手册：商业许可只能由版权人授予，本衍生项目无权提供或据此收费
- `site/config.js` 的 `developer` 段移除原作者姓名、头像与私人联系方式（Telegram / QQ），联系渠道只保留 GitHub 主页 / 项目仓库 / Issues；`README.md`、`README.en.md`、`CONTRIBUTING.md`、站内文档与 `scripts/push-via-api.mjs` 的提交署名同步清理
- 按 GPL-3.0 要求保留上游署名：README 新增「上游与致谢」章节与版权声明，联系页、站内文档与项目信息栏标注上游项目

### 内部
- `core.js` 的 `mdToHtml` 为每个标题注入稳定 id（`md-sec-N`）；页面使用 hash 路由，目录跳转走 `data-act` 而非 `#id` 锚点
- `store.js` 新增 `compare` 状态与 `addFavs` / `isCompared` / `toggleCompare` / `removeCompare` / `clearCompare`
- Service Worker 预缓存清单加入 `site/data/whats-new.js`
- `scripts/smoke-test.mjs` 的联系页断言同步更新（渠道数 3、去掉「未公开」项）

## [1.2.1] - 2026-11-15

### 修复
- **教程页移动端标签挤压换行**：`#/tutorials` 在 390px 窄屏下，搜索框行内 `max-width:280px;min-width:200px` 的优先级高于媒体查询里的 `min-width:100%`，仍强占 200px，把分组标签条压到 122px；`.chip` 又缺少 `white-space:nowrap`，导致 7 个标签各自换行、行高被撑成两行。现将布局样式移出内联 style（新增 `.tuto-toolbar` 类），`.chip` 加 `white-space:nowrap` + `flex:0 0 auto`，`.chip-scroll` 加 `min-width:0`，窄屏下搜索框独立成行、标签条横向滚动，标签高度稳定在 28px

### 内部
- 自检构建标记 `__ORBIT_BUILD__` 更新为 `wbit-1.2.1`，`config.version` 同步 `1.2.1`
- Service Worker 缓存版本提升为 `wbit-shell-v3`，确保已装 PWA 能拉取到新样式
- 桌面端版本号与站点对齐（`desktop/package.json`、`tauri.conf.json`、`Cargo.toml` 均为 `1.2.1`）
- Rust crate 品牌更名：`orbit-github-nav` → `wbit`，`[lib] name` → `wbit_lib`（`main.rs` 同步）；`description` / `authors` / 注释一并改为 WBit。`identifier` 保留 `cn.orbit.githubnav` 不动，避免已安装用户的应用数据目录变更
- 同步数据 Gist 载荷的 `app` 字段由 `orbit` 改为 `wbit`（旧数据仍可正常读取，`version` 未变）
- 清理仓库：删除 `docs/github-actions/*.yml.txt`（3 份已过期的 workflow 备份，其中 `build-desktop.yml.txt` 仍写着上游 `Orbit-*` 产物名）；`preview/audit.json` 与 `preview/live.png` 是 `perf-audit.mjs` / `check-live.mjs` 的运行副产物，改为不再入库并加入 `.gitignore`
- README 更新：修正「工作流未随仓库提交」的过期说明，目录树补上 `update-tutorials.yml`

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
