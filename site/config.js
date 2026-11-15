/**
 * WBit · 站点配置
 * ------------------------------------------------------------
 * 网站、PWA、桌面端共用同一份代码与同一份配置。
 * 部署到 GitHub Pages 二级域名时，只需把 githubUser / githubRepo 改成你自己的。
 * 生成的地址： https://<githubUser>.github.io/<githubRepo>/
 * 若使用自定义域名，把 siteUrl 改成你的域名即可。
 *
 * 上游来源与 GPL-3.0 署名见 README「致谢」章节与 CHANGELOG.md。
 */
window.__GH_NAV_CONFIG__ = {
  siteName: 'WBit',
  siteSubtitle: 'GitHub 导航站',
  slogan: '发现值得用的开源项目',

  // ── 许可证与维护方式 ───────────────────────────────────────
  // 站内「维护与联系」页会读取这里显示；改许可证时同步改 LICENSE 文件。
  license: 'GPL-3.0',
  licenseUrl: 'https://github.com/wanghaaoming/wbit/blob/main/LICENSE',
  governance: '社区共同维护',

  // ── GitHub Pages ────────────────────────────────────────────
  githubUser: 'wanghaaoming',            // GitHub 用户名
  githubRepo: 'wbit',   // 仓库名（与 Pages 二级域名一致）
  siteUrl: '',                     // 自定义域名；留空时按当前站点自动推断

  // ── 开发者联系信息 ─────────────────────────────────
  // 只提供公开、可追踪的渠道（GitHub 主页 / 仓库 / Issues）。
  // 不收录任何人的私人联系方式（QQ / Telegram / 电话等）；
  // 站内「维护与联系」页只展示下面这些公开入口。
  developer: {
    name: 'WBit',
    github: 'wanghaaoming',
    githubUrl: 'https://github.com/wanghaaoming',
    avatar: 'https://github.com/wanghaaoming.png',
    repoUrl: 'https://github.com/wanghaaoming/wbit',
    issuesUrl: 'https://github.com/wanghaaoming/wbit/issues',
    note: '欢迎通过 Issues 反馈问题、提出建议或申请收录；本站不提供私人联系方式。',
  },

  // ── 可选登录 / 跨端同步 ─────────────────────────────────────
  // 完全可选：不填也能正常使用（收藏、主题、最近访问保存在本机）。
  // 填写 GitHub OAuth App 的 Client ID 后，可用 Device Flow 登录，
  // 通过私有 Gist 在网站 / 手机 PWA / 桌面端之间同步收藏与设置。
  // 创建方式：GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
  //   Authorization callback URL 可填站点首页，并勾选 "Enable Device Flow"。
  oauthClientId: '',

  // GitHub Search API 实时全站搜索（可选，匿名 10 次/分钟）。
  // 填入只读 token 可提高额度；不填时匿名调用，长尾仓库仍可搜索。
  githubApiToken: '',

  // 数据自动更新周期（由 .github/workflows/update-data.yml 保证）
  refreshDays: 7,
  version: '1.3.0',
};
