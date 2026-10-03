# 王松林 · 个人网站

纯静态个人博客网站。视觉语言参考 [oniguili.jp](https://www.oniguili.jp/)。

## 快速开始

直接双击 `site/index.html` 用浏览器打开即可，**无需安装任何依赖、无需构建**。

如需本地服务器（推荐，避免个别浏览器的 `file://` 限制）：

```bash
cd site
python -m http.server 8899
# 打开 http://127.0.0.1:8899
```

## 目录

| 路径 | 说明 |
|---|---|
| `site/` | **交付物**。整个网站，可直接部署到任意静态托管 |
| `site/css/style.css` | 全部样式（1006 行，13 个分节） |
| `site/js/main.js` | 全部交互（6 个职责） |
| `tools/` | 构建与校验脚本，不参与部署 |

## 页面

首页 `site/index.html`，其余四个栏目：`profile/`（关于我）、`projects/`（做过的事）、
`notes/`（写下的字，8 篇）、`journal/`（日常与照片，6 篇）。

## 改内容

- **改配色/间距/字体** → `site/css/style.css` 的 `/* 1. Tokens */` 一节
- **加文章** → 编辑 `tools/build_pages.py` 的 `NOTES` / `JOURNAL` 列表，然后
  `python tools/build_pages.py`
  （`notes/index.html` 是自动生成的，手改会被覆盖）
- **换照片** → 覆盖 `site/img/` 下的同名文件，**当前 12 张是占位图**
  （`wechat-qr.jpg` 是真实微信二维码；`trip-01..03.jpg` 已随动态水面改版停用）

## 交接给 AI agent

请让它先读 **[AGENTS.md](./AGENTS.md)** —— 里面有完整的设计约束、文件地图、
常见改动做法、构建命令和已知坑。不要只丢代码给它。

## 版本管理

本项目已是 Git 仓库（主分支 `main`），目前只在本机做版本管理，未配置远端。

**从 `website-handoff.zip` 接手的话**：包里不含 `.git`，先初始化一次：

```bash
git init -b main && git add -A && git commit -m "首次提交：个人网站框架"
```

日常使用：

```bash
git status
git diff
git add -A && git commit -m "改了什么"
git log --oneline
```

### 回档怎么办

| 情况 | 怎么做 | 谁能做 |
|---|---|---|
| 改动还没提交，想全部丢掉 | `git checkout .` | 自己 / agent 都行 |
| 某次已提交的改动想撤销 | `git revert <hash>`（安全，留记录） | 自己 / agent 都行 |
| 想看看历史某个点的样子 | `git switch -c 试验 <hash>`（开分支，别直接切） | 自己 / agent 都行 |
| 想让 main 强行退回某点 | `git reset --hard <hash>` ⚠️ 会丢提交 | **先问清楚再决定** |
| 只回退某几行 | 需要逐行判断，无一键方案 | **建议自己上手** |

**通用原则**：让 agent 回档之前，先让它把 `git status` 和 `git log --oneline` 报给你，
确认要退到哪一步。回档前最好存一份备份分支：`git branch backup-YYYYMMDD`。

详细规程见 [AGENTS.md](./AGENTS.md) §5.0b。

想推到 GitHub / Gitee 时，先在网页端建一个**空仓库**（不要勾选 README），然后：

```bash
git remote add origin <仓库地址>
git push -u origin main
```

推送需要先配好 SSH 密钥或 Personal Access Token，详见 [AGENTS.md](./AGENTS.md) §5.0。
