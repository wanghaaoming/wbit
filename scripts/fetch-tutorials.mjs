/**
 * WBit · 教程栏目自动采集脚本
 * ------------------------------------------------------------
 * 从 GitHub Search API 按「主题 + 星标门槛」抓取教程类仓库，
 * 去重、剔除已在人工精选清单里的条目，生成：
 *   site/data/tutorials-auto.js   —— 浏览器直接 <script> 加载
 *   site/data/tutorials-auto.json —— 供其他工具消费
 *
 * 与 site/data/tutorials.js 的分工：
 *   tutorials.js       人工精选（官方文档、必读清单），质量优先，稳定不变。
 *   tutorials-auto.js  自动采集（脚本产出），覆盖长尾，随仓库热度滚动更新。
 * 页面把两者合并展示，人工组在前、自动组在后。
 *
 * 用法：
 *   node scripts/fetch-tutorials.mjs                    # 全量采集
 *   node scripts/fetch-tutorials.mjs --limit 3          # 只跑前 N 个查询（调试）
 *   node scripts/fetch-tutorials.mjs --min-stars 200    # 覆盖默认星标门槛
 *   GITHUB_TOKEN=xxx node scripts/fetch-tutorials.mjs   # 提高限流额度（30 次/分钟）
 *
 * 注意：匿名调用 GitHub Search API 只有 10 次/分钟，脚本默认按 6.8s 间隔串行。
 * 在 CI 里请配置 GITHUB_TOKEN（.github/workflows/update-tutorials.yml 已接好）。
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT_DIR = path.join(ROOT, 'site', 'data');
const MANUAL_FILE = path.join(OUT_DIR, 'tutorials.js');
const TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || '';

const argOf = (name, fallback) => {
  const i = process.argv.indexOf(name);
  return i > -1 ? Number(process.argv[i + 1]) || fallback : fallback;
};
const LIMIT = argOf('--limit', Infinity);
const MIN_STARS = argOf('--min-stars', 0);
const PER_QUERY = 20;          // 每个查询取多少条
const PER_GROUP = 12;          // 每组最终最多展示多少条
const INTERVAL = TOKEN ? 2200 : 6800;

/* 采集分组：id/title/desc/icon/color 与 tutorials.js 的组结构一致，
 * queries 里是 GitHub 搜索语句，order 决定组内排序方式。 */
const GROUPS = [
  {
    id: 'agent-docs',
    title: '编程 Agent · 热门项目',
    desc: '按星标自动收录的编程 Agent 与 AI 编辑器，持续更新',
    icon: 'bot',
    color: '#FF7A45',
    order: 'stars',
    queries: [
      'topic:claude-code',
      'topic:coding-agent',
      'topic:ai-coding-assistant',
      'topic:codex',
      'topic:copilot',
      'topic:cursor-ai',
      'topic:ai-programmer',
    ],
  },
  {
    id: 'agent-build',
    title: '自己造 Agent · 框架与范式',
    desc: 'Agent 框架、多智能体编排与工作流引擎',
    icon: 'blocks',
    color: '#0A84FF',
    order: 'stars',
    queries: [
      'topic:agent-framework',
      'topic:llm-agents',
      'topic:multi-agent',
      'topic:autonomous-agents',
      'topic:agentic',
    ],
  },
  {
    id: 'mcp',
    title: 'MCP 与工具生态',
    desc: 'Model Context Protocol 服务端、客户端与目录',
    icon: 'plug',
    color: '#30B0C7',
    order: 'stars',
    queries: ['topic:mcp', 'topic:model-context-protocol', 'mcp server in:name,description'],
  },
  {
    id: 'prompt',
    title: 'Prompt 与上下文工程',
    desc: '提示词模板、系统提示词合集与上下文管理实践',
    icon: 'sparkles',
    color: '#7C5CFF',
    order: 'stars',
    queries: ['topic:prompt-engineering', 'topic:system-prompts', 'topic:prompt-library'],
  },
  {
    id: 'dev',
    title: '通用编程教程',
    desc: '成体系的教程、路线图与实战课程',
    icon: 'code',
    color: '#34C759',
    order: 'stars',
    queries: [
      'topic:tutorial stars:>3000',
      'topic:roadmap stars:>3000',
      'topic:learning stars:>2000',
      'tutorial in:name,description stars:>5000',
    ],
  },
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function search(q, attempt = 0) {
  const query = MIN_STARS > 0 ? `${q} stars:>${MIN_STARS}` : q;
  const url = new URL('https://api.github.com/search/repositories');
  url.searchParams.set('q', query);
  url.searchParams.set('sort', 'stars');
  url.searchParams.set('order', 'desc');
  url.searchParams.set('per_page', String(PER_QUERY));

  const headers = {
    Accept: 'application/vnd.github+json',
    'User-Agent': 'wbit-tutorial-indexer',
    'X-GitHub-Api-Version': '2022-11-28',
  };
  if (TOKEN) headers.Authorization = ['Bearer', TOKEN].join(' ');

  const res = await fetch(url, { headers });
  if (res.status === 403 || res.status === 429) {
    if (attempt >= 3) throw new Error(`限流，放弃查询: ${query}`);
    const retryAfter = Number(res.headers.get('retry-after')) || 0;
    const wait = retryAfter ? retryAfter * 1000 : 60000;
    console.warn(`  ⏳ 触发限流，等待 ${Math.round(wait / 1000)}s 后重试 (${attempt + 1}/3)`);
    await sleep(wait);
    return search(q, attempt + 1);
  }
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${query}: ${(await res.text()).slice(0, 200)}`);
  return res.json();
}

/* 人工精选里已出现的链接，自动采集时跳过，避免同一教程出现两次 */
function readManualUrls() {
  const urls = new Set();
  if (!fs.existsSync(MANUAL_FILE)) return urls;
  const text = fs.readFileSync(MANUAL_FILE, 'utf8');
  for (const m of text.matchAll(/u:\s*'([^']+)'/g)) urls.add(normalizeUrl(m[1]));
  return urls;
}

function normalizeUrl(u) {
  return String(u || '').trim().replace(/\/+$/, '').toLowerCase();
}

const fmtStars = (n) => (n >= 1000 ? `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k` : String(n));

function toItem(repo) {
  return {
    n: repo.name,
    d: (repo.description || '暂无简介').replace(/\s+/g, ' ').slice(0, 120),
    u: repo.html_url,
    t: `★ ${fmtStars(repo.stargazers_count || 0)}`,
  };
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const manual = readManualUrls();
  const seen = new Set();
  const tasks = [];
  for (const g of GROUPS) for (const q of g.queries) tasks.push({ group: g.id, q });

  const picked = new Map(GROUPS.map((g) => [g.id, []]));
  const runTasks = tasks.slice(0, LIMIT);
  let ok = 0;

  console.log(`▶ 教程采集：${runTasks.length} 个查询，间隔 ${INTERVAL}ms，${TOKEN ? '已使用 token' : '匿名模式'}`);
  if (manual.size) console.log(`  人工精选已收录 ${manual.size} 条链接，重复项将跳过`);

  for (let i = 0; i < runTasks.length; i++) {
    const { group, q } = runTasks[i];
    try {
      const data = await search(q);
      let added = 0;
      for (const repo of data.items || []) {
        const key = normalizeUrl(repo.html_url);
        if (!key || seen.has(key) || manual.has(key) || repo.archived) continue;
        seen.add(key);
        picked.get(group).push(repo);
        added++;
      }
      ok++;
      console.log(`  [${String(i + 1).padStart(2, '0')}/${runTasks.length}] ${q} → ${data.items?.length || 0} 条，新增 ${added}`);
    } catch (e) {
      console.warn(`  [${i + 1}/${runTasks.length}] ✗ ${q}: ${e.message}`);
    }
    if (i < runTasks.length - 1) await sleep(INTERVAL);
  }

  const groups = GROUPS.map((g) => ({
    id: g.id,
    title: g.title,
    desc: g.desc,
    icon: g.icon,
    color: g.color,
    items: (picked.get(g.id) || [])
      .sort((a, b) => (b.stargazers_count || 0) - (a.stargazers_count || 0))
      .slice(0, PER_GROUP)
      .map(toItem),
  })).filter((g) => g.items.length);

  const payload = {
    updatedAt: new Date().toISOString().slice(0, 10),
    source: 'GitHub Search API',
    queryCount: ok,
    groups,
  };

  const jsBody = `/* 自动生成，请勿手工编辑。由 scripts/fetch-tutorials.mjs 产出 */
/* 与 site/data/tutorials.js 的人工精选合并展示 */
window.__GH_NAV_TUTORIALS_AUTO__ = ${JSON.stringify(payload)};
`;
  fs.writeFileSync(path.join(OUT_DIR, 'tutorials-auto.js'), jsBody, 'utf8');
  fs.writeFileSync(path.join(OUT_DIR, 'tutorials-auto.json'), JSON.stringify(payload, null, 2), 'utf8');

  const total = groups.reduce((a, g) => a + g.items.length, 0);
  console.log(`\n✅ 完成：${total} 条教程，成功 ${ok}/${runTasks.length} 个查询`);
  console.log(`   → ${path.join(OUT_DIR, 'tutorials-auto.js')} (${(fs.statSync(path.join(OUT_DIR, 'tutorials-auto.js')).size / 1024).toFixed(0)} KB)`);
  if (!total) console.log('   ⚠ 没有抓到任何条目：检查网络是否可达 api.github.com，或降低 --min-stars');
}

main().catch((e) => {
  console.error('采集失败：', e);
  process.exit(1);
});
