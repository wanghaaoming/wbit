# 更新日志 / Changelog

本项目的所有显著变更记录在此文件中。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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
