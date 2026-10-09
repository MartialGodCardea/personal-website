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
| `site/css/style.css` | 全部样式（1286 行，15 个分节） |
| `site/js/main.js` | 全部交互（9 个职责） |
| `site/fonts/` | 2 个自托管字体子集（中文 + 西文），零外部请求 |
| `tools/` | 构建与校验脚本，不参与部署 |

## 页面

首页 `site/index.html`，其余四个栏目：`profile/`（关于我）、`projects/`（做过的事）、
`notes/`（写下的字，8 篇）、`journal/`（日常与照片，6 篇）。
另有 `site/404.html`（由 `tools/build_pages.py` 生成）与 `site/robots.txt`。

## 改内容

- **改配色/间距/字体** → `site/css/style.css` 的 `/* 1. Tokens */` 一节
  （颜色、间距、缓动、圆角、阴影、字体栈全部收敛在这一个 `:root` 里）
- **加文章** → 编辑 `tools/build_pages.py` 的 `NOTES` / `JOURNAL` 列表，然后
  `python tools/build_pages.py`
  （`notes/index.html` 是自动生成的，手改会被覆盖）
- **换照片** → 覆盖 `site/img/` 下的同名文件，**其中 10 张是占位图**
  （`water-bg.jpg` 水面底图与 `wechat-qr.jpg` 微信二维码是真实素材；
  `trip-01..03.jpg` 已随改版停用并删除）
- **新增了中文内容后** → 跑一次 `python tools/build_font_subset.py` 重建字体子集，
  否则新汉字会 fallback 到系统衬线（详见 `AGENTS.md` §6.5）

## 字体

全站只用两套**自托管**字体子集，零外部请求、不走 Google Fonts：

| 字体 | 用在哪 |
|---|---|
| **Newsreader**（西文衬线） | 巨型字标 `SONGLIN`、日期、版权、导航副标签等西文 |
| **Noto Serif SC**（中文衬线） | 中文名牌「王松林」、署名、弹窗中文标签 |

两套都是从站点实际用到的字符裁出的子集，由 `tools/build_font_subset.py` 一次生成
（需要 `pip install "fonttools[woff]"`）。选型经过与 6 款开源衬线的对比样张，
详见 [字体规范.md](./字体规范.md)。

## 联系方式按钮

右上角 `wechat` / `phone` / `email` 三项点击后都在**当前页弹出遮罩弹窗**，不跳转：
微信显示二维码，电话显示 `+86 137 6869 2678`，邮箱显示 `anthonywang171003@gmail.com`，
后两者带「复制」按钮。弹窗背景有轻微高斯模糊。

> 底部水面的**动态涟漪特效目前已下线**（观感待优化，等找到参考实例再复刻）。
> 现在那里是一张实拍的灰调水面照片 + 题款。恢复方法见 AGENTS.md §4.6。

## 交接给 AI agent

请让它先读 **[AGENTS.md](./AGENTS.md)** —— 里面有完整的设计约束、文件地图、
常见改动做法、构建命令和已知坑。不要只丢代码给它。

想了解这个网站用到了哪些技术、整体怎么组织，看 **[技术架构.md](./技术架构.md)**。

想了解字体是怎么选的、为什么不像 AI 做的，看 **[字体规范.md](./字体规范.md)**；
近期做过哪些美术整改、还剩哪些建议项，看 **[美术体检报告.md](./美术体检报告.md)**。

## 版本管理

本项目是 Git 仓库，主分支 `main`，**已推送到 GitHub**：

| | |
|---|---|
| 仓库 | https://github.com/MartialGodCardea/personal-website |
| 在线站点 | https://martialgodcardea.github.io/personal-website/ |

远端已配置为 `origin`。本机凭据存在 **Windows 凭据管理器**里，
所以 `git push` 直接可用，不需要每次输入 Token
（撤销 Token 后这条凭据会自动失效，重新推送时再认证一次即可）。

**从 `website-handoff.zip` 接手的话**：包里不含 `.git`，先初始化一次：

```bash
git init -b main && git add -A && git commit -m "首次提交：个人网站框架"
git remote add origin https://github.com/MartialGodCardea/personal-website.git
```

日常使用：

```bash
git status
git diff
git add -A && git commit -m "改了什么"
git push
git log --oneline
```

### 部署到线上

站点内容发布在 **`gh-pages` 分支**，那是 GitHub Pages 的发布源。

> **为什么不用「main 分支根目录」发布**：GitHub Pages 只支持从仓库根或 `/docs`
> 发布，而本仓库根目录放的是构建脚本（`tools/`）和文档（`*.md`），成品全在
> `site/` 下。为了不给部署去改仓库结构，改用 `gh-pages` 分支承载站点内容。

**每次改完站点，跑一条命令就上线：**

```bash
python tools/deploy_pages.py
```

它做四件事：检查 `site/` 有无未提交改动 → 取 `main:site` 的 tree 对象 →
在 `gh-pages` 上追加一个提交 → 推送。Pages 构建通常 1~3 分钟，
之后刷新在线地址就能看到更新。

> ⚠️ `gh-pages` 是**生成分支**，别直接在上面改东西 —— 下次发布会被覆盖。
> 所有改动都在 `main` 上做，改完再跑上面的命令。

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

### 线上和本地不一致怎么办

按顺序排查：

1. **改动提交了吗** —— `git status` 看 `site/` 是否干净
2. **推上去了吗** —— `git log --oneline -1 origin/main` 对比本地 `main`
3. **发布了吗** —— 跑一次 `python tools/deploy_pages.py`
4. **Pages 构建成功了吗** —— 仓库 Settings → Pages 看构建状态
5. **浏览器缓存** —— 强制刷新（`Ctrl+Shift+R`）；Pages 的 CDN 也有几分钟缓存

另外注意：全站唯一的绝对路径是 `og:image="/img/og-cover.jpg"`，
在 `/<仓库名>/` 这种子路径下它会指向域名根目录而失效 —— **只影响社交分享缩略图，
不影响站点本身**。等有了正式域名再改成绝对地址即可。
