# 交接说明 · 王松林个人网站

> 给接手本项目的 AI agent / 开发者。**先读完这份文件再动手。**
> 本文档是唯一的权威说明；`README.md` 只是给人看的简短指引。

---

## 1. 这是什么

一个**纯静态**个人博客网站（HTML + CSS + 原生 JS，无框架、无构建步骤、无依赖）。
视觉语言复刻自 <https://www.oniguili.jp/>（西村祥子个人站）的日式编辑网格设计。

- 入口：`site/index.html`
- 内容来源：`../个人介绍.txt`（用户本人资料）
- 部署方式：直接双击 `index.html` 打开，或丢进任意静态托管。**不需要服务器、不需要 npm install。**

---

## 2. 铁律：改之前必须知道的 5 件事

违反这些会让整站视觉崩坏。它们是这个设计语言的骨架。

### 2.1 5 列网格是唯一的布局基准

```css
/* css/style.css · 6. Layout */
#main_contents {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  column-gap: var(--gap);   /* 24px */
}
```

所有内容都通过 `grid-column: N / M` 定位到这 5 列上。**不要引入 flex 或百分比宽度去替代它。**
嵌套元素用 `grid-template-columns: subgrid` 继承列对齐——这是让标题、正文、图片精确对齐的关键。

### 2.2 固定浮层靠 `mix-blend-mode: difference` 反相

logo、日期、导航、巨型名牌、页脚全部是 `position: fixed` + 近白色 `--ghost: #fafafa` +
`mix-blend-mode: difference`。它们在白色背景上不可见，滚动到深色内容上会**自动反相**。

- 改这些元素的颜色时**不要**用 `--ink`（黑），否则反相逻辑会失效、元素消失。
- 想让某个浮层"实心可见"，必须显式去掉 `mix-blend-mode` 并另配颜色。

### 2.3 竖排文字用 `writing-mode: vertical-rl`

logo（`SONGLIN`）、日期（`( Oct. 2nd, 2026 )`）、中文导航都是竖排。改动这些元素的
宽度/高度时注意：竖排下 `width` 控制的是**行数**方向，`height` 控制的是**文字长度**方向。

### 2.4 视口节奏用 `svh`，不是 `px`

```css
#main_contents { margin: 56svh 40px 40svh; }   /* 顶部留出近一屏的空白 */
```

这是参考站"内容从下半屏浮出"的观感来源。改成 `px` 会失去这个特征。

### 2.5 图片是灰阶 → 悬停/滚入变彩色

```css
#main_contents .img img { filter: grayscale(100%); }
.is-active img, .img:hover img { filter: grayscale(0%); }
```

`.is-active` 由 `js/main.js` 的 `IntersectionObserver` 添加（`rootMargin: 0 0 -70% 0`，
即图片进入视口下方 30% 区域时触发）。**换图片时请用彩色原图**，灰阶是 CSS 现算的。

---

## 3. 文件地图

```
个人网站/
├── 个人介绍.txt              # 用户原始资料（内容源头）
├── AGENTS.md                 # 本文件
├── README.md                 # 给人看的简短指引
├── site/                     # ★ 交付物：整个网站，可直接部署
│   ├── index.html            # 首页（四段式：design / journal / notes / prof）
│   ├── css/style.css         # ★ 全部样式，1015 行，13 个分节
│   ├── js/main.js            # 全部交互，6 个职责（见 §4.4）
│   ├── fonts/                # 3 个自托管 woff2
│   ├── img/                  # 14 张 JPG（13 张占位图 + wechat-qr.jpg）+ 4 个 SVG
│   ├── profile/index.html    # 关于我
│   ├── projects/index.html   # 做过的事（4 个案例）
│   ├── notes/                # 写下的字：index.html + 8 篇
│   └── journal/              # 日常与照片：index.html + 6 篇
└── tools/                    # 构建与校验脚本，★ 不参与部署
    ├── build_pages.py        # 生成 notes/ 与 journal/ 全部页面
    ├── make_placeholders.py  # 用 Pillow 生成占位图
    ├── screenshot.py         # Chrome headless 截图（含移动端 iframe 模拟）
    └── pngtool.py            # 纯标准库 PNG 像素探针（QA 用）
```

**`site/css/style.css` 分节索引**（改样式先按这个定位）：

| 节 | 内容 |
|---|---|
| 0 | Fonts（`@font-face`） |
| 1 | Tokens（`:root` 变量，**改配色/间距从这里入手**） |
| 2 | Reset & base |
| 3 | Fixed overlays（logo / 日期 / 导航） |
| 4 | Giant name plate（`王松林` + `SONGLIN`） |
| 5 | Footer |
| 6 | Layout（5 列网格本体） |
| 7 | Home page sections |
| 8 | Inner pages（索引列表） |
| 8b | Article detail（文章详情） |
| 9 | Profile page |
| 10 | Water band（动态水面） |
| 11 | Opening animation |
| 12 | Responsive |

---

## 4. 常见改动怎么做

### 4.1 加一篇「写下的字」笔记

**不要手写 HTML，也不要手改 `notes/index.html`——它会被脚本覆盖。**

编辑 `tools/build_pages.py`，在 `NOTES` 列表里追加一个 dict：

```python
dict(
    slug="my-slug",                 # → 生成 notes/my-slug.html，同时是文件名
    date="2026.10.03",              # 显示用，自由格式
    cat="AI 交付",                   # 分类标签
    img="note-01.jpg",              # ⚠️ 见下方说明
    title="文章标题",
    excerpt="列表页摘要，一到两句。",
    lead="详情页导语，一段话。",
    body="""
<p>正文。可用 <strong>加粗</strong>、<em>斜体</em>。</p>
<h2>小标题</h2>
<ul><li>列表项</li></ul>
<blockquote><p>引用。</p></blockquote>
""",
),
```

然后运行：

```bash
python tools/build_pages.py
```

会重新生成 `notes/my-slug.html` **并重建 `notes/index.html`**（索引是自动从 `NOTES` 派生的）。

> ⚠️ `NOTES` 里的 `img` 字段目前**没有被使用**（只有 `JOURNAL` 的 `img` 会渲染到列表页）。
> 保留无害，也可以删。别指望它显示图片。

### 4.2 加一篇「日常与照片」日记

同上，但改 `JOURNAL` 列表。区别是 `JOURNAL` 的 `img` **会**渲染成列表右侧配图。
需要图片时把图放进 `site/img/`，填文件名即可。

### 4.3 改配色 / 间距 / 字体

只改 `css/style.css` 的 `/* 1. Tokens */` 一节：

```css
:root {
  --paper: #ffffff;        /* 底色 */
  --ink: #000000;          /* 正文色 */
  --ghost: #fafafa;        /* ★ 浮层专用：配合 difference 混合，别乱改 */
  --latin-ghost: 0.05;     /* 巨型背景字透明度 */
  --gap: 24px;             /* 列间距 */
  --pad-x: 40px;           /* 左右页边距 */
  --nav-top: 40svh;        /* 导航起始高度 */
}
```

字体栈是 `--font-display` / `--font-cjk` / `--font-body` 三个变量，改这里全站生效。

### 4.4 改交互行为

`js/main.js` 是一个 IIFE，6 个编号职责，改哪块找对应函数：

| # | 函数 | 作用 |
|---|---|---|
| 1 | `renderDate()` | 右上角竖排日期，实时生成 |
| 2 | `markNavigation()` | 读 `body[data-page]`，给对应导航项加 `.active`（首页不高亮） |
| 3 | `observePlates()` | `IntersectionObserver` 给 `#main_contents .img` 加 `.is-active`（触发显色） |
| 4 | `startRotators()` | 读 `[data-images]` JSON，定时交叉淡入换图 |
| 5 | `waterBand()` | 动态水面：高度场波动 + 跟随光标的涟漪（见 §4.6） |
| 6 | `opening()` | 首屏字母闪烁 + 导航逐项入场，`sessionStorage.hasVisited` 保证只播一次 |

> **新增页面时必须设置 `<body data-page="...">`**，取值与 `NAV` 里的 key 一致
> （`home` / `profile` / `projects` / `notes` / `journal`），否则导航高亮会错。
> 新页面请复用 `tools/build_pages.py` 里的 `header()` 生成器，别手抄头部。

### 4.5 换真实照片

把照片放进 `site/img/`，**保持原有文件名**即可，布局不用动：

`design-01..04.jpg`（首页大图轮播）、`profile.jpg`、`journal-01..03.jpg`、
`note-01..02.jpg`。

**这 13 张目前是抽象占位图**，见 §7。

另有 `wechat-qr.jpg`（微信个人二维码）是**真实素材**，不是占位图，供 `snsnav` 的
`wechat` 链接打开；换码时同名替换即可。

### 4.6 动态水面（原「旅行带」）

页面底部那条 100vh 的横幅已从「随机旅行照片」改成**程序生成的动态水面**
(`#water-band`)，由 `js/main.js` 的 `waterBand()` 驱动：

- 两张 `Float32Array` 高度场交替推进波动方程，逐像素做位移采样 + 波峰高光；
- 模拟网格远小于 CSS 像素（约 1/3，且像素数封顶 12 万），再由浏览器放大，
  既轻又柔；`ResizeObserver` 跟随尺寸变化；
- 鼠标划过注入涟漪（按速度决定强度）、按下是一记更大的落水；另有约 1.2–2.9 秒
  一次的随机环境滴落，避免"死水"；悬停时 `.water-glow` 渐亮，像水面接光；
- 离屏时 `IntersectionObserver` 停机；`prefers-reduced-motion: reduce` 时只画一帧静水。

调参集中在 `waterBand()` 顶部：`DAMP`（衰减）、`SLOPE`（位移强度）、`SPEC`（高光）。
`paintTexture()` 负责水体底纹（深度渐变 + 水平拉伸的焦散细纹）。

> `trip-01..03.jpg` 与 `data-trips` / 随机换图逻辑已随本次改版**退出使用**，
> 图片文件保留备用；要恢复照片横幅就把 `TRIP` 模板换回 `<div class="img">` 并
> 恢复 `pickTrip()`（见 git 历史）。

---

## 5. 构建与校验

### 5.0 版本管理

本项目已初始化为 Git 仓库，主分支 `main`（首次提交 `8fb8d0b`）。**只在本机做版本管理，
尚未配置任何远端**。

> **从压缩包接手的情况**：`website-handoff.zip` **不包含 `.git` 目录**（这是有意为之，
> 见下方说明）。解压后请先执行一次初始化：
>
> ```bash
> cd <解压后的目录>
> git init -b main && git add -A && git commit -m "首次提交：个人网站框架"
> ```
>
> `.gitignore` 与 `.gitattributes` 已在包内，这一步之后仓库配置即正确。

```bash
git status           # 看当前改动
git diff             # 看待提交的具体改动
git log --oneline    # 看历史

git add -A && git commit -m "说明这次改了什么"   # 提交

git checkout .       # 丢弃全部未提交改动（危险，不可逆）
git revert <hash>    # 撤销某次已提交的改动（安全，会留记录）
```

**为什么交付包不带 `.git`**：Git 仓库无法靠文件复制可靠搬运。`.git/index` 记录了文件
的路径、mtime、权限位，换台机器（尤其是跨操作系统）解压后会被判定为"整个工作区被改动"；
若双方各自提交再合并，还会产生对象冲突。它的价值在于**增量历史**，而历史一旦脱离
原本地环境就容易失真。对方自行 `git init` 得到的仓库更干净。

若确实需要连同历史一并交接，用 Git 官方格式而非 zip：

```bash
git bundle create handoff.bundle --all
# 对方：git clone handoff.bundle my-site
```

两个配置文件的用意：

- **`.gitattributes`** — 仓库内统一按 LF 存储换行符。Windows 下编辑器若存成 CRLF，
  Git 会自动转换，避免出现"整个文件都改了"的假 diff。
- **`.gitignore`** — 排除 `__pycache__/`、编辑器目录、截图临时文件（`site/_shot.html`、
  `site/_frame.html`）、`*.png`（截图产物；**项目内没有任何 png 资源**，13 张图均为 JPG）、
  以及 `website-handoff.zip`（可由仓库内容随时重新打包，无需入库）。

**给 AI agent 的提示**：如果要在本仓库上做较大改动，建议先开新分支
（`git switch -c 改动名`），改完确认无误再合回 `main`，这样随时可以放弃。
提交信息请用中文说清"改了什么、为什么"，不要写"update"这类无信息量的词。

> **中文提交信息的编码坑**：Windows Git Bash 下直接 `git commit -m "中文"` 可能因编码
> 报错。加 `-c i18n.logOutputEncoding=UTF-8` 即可：
>
> ```bash
> git -c i18n.logOutputEncoding=UTF-8 commit -q -m "改动说明"
> ```
>
> 另外建议设置 `git config --global core.quotepath false`，否则中文文件名会显示成
> 八进制转义（如 `\344\270\252...`）。

### 5.0b 回档规程（重要）

回档操作的风险**与粒度成正比**。请按下面的分级处理，不要越级。

**先记住三张安全网**——绝大多数"改坏了"都能靠它们救回来：

| 机制 | 作用 | 命令 |
|---|---|---|
| 未提交改动 | 直接丢弃，回到上次提交 | `git checkout .` |
| `reflog` | 记录 HEAD 的每次移动，**被"删除"的提交未必真的没了** | `git reflog` |
| `stash` | 把改动暂时收起来，稍后再取回 | `git stash` / `git stash pop` |

#### 第 1 级：整体退回上一个提交 —— agent 可直接做

丢掉全部**尚未提交**的改动：

```bash
git checkout .          # 丢弃所有未提交改动，不可逆
git status              # 确认干净
```

适用：刚改完发现不对，且还没提交。风险低——上次提交是完好的。

#### 第 2 级：撤销某次已提交的改动 —— agent 可直接做

```bash
git log --oneline               # 找到要撤销的提交哈希
git revert <hash>               # 生成一个"反向提交"来抵消它
```

**这是最安全的回档方式**，因为它保留完整历史、留下操作记录，不删任何东西。
适用：某次提交把东西改坏了。即使撤销错了，也还能再 revert 回来。

#### 第 3 级：回到历史某个时间点看看 —— agent 可做，但要用分支

```bash
git switch -c 试验 <hash>       # 从那个提交开一个新分支去看，不影响 main
git switch main                 # 看完切回来
```

**不要用 `git checkout <hash>` 直接切**——那会进入 detached HEAD 状态，在上面提交
容易丢。始终用「开分支」的方式。

#### 第 4 级：强行让 main 退回历史某点 —— 必须用户在场

```bash
git reset --hard <hash>         # ⚠️ 丢弃该点之后的全部提交
```

这是**破坏性操作**：`<hash>` 之后的提交会从分支上消失（虽然还能靠 `reflog` 找回，
但有时间限制、且容易搞混）。**执行前必须让用户确认，并由用户决策。**

#### 第 5 级：只回退某几行 / 撤销历史中间的某次提交 —— 用户亲自操作

这类需求 Git 没有"一键"方案：

- 只想**部分文件**回到某个状态：
  `git checkout <hash> -- <路径>`（会覆盖当前工作区的那几个文件，先确认）
- 想**保留后面的提交**、只抽掉中间某一次：
  用 `git revert <hash>`（可行，但可能产生冲突需要手工解决），
  或 `git rebase -i`（会重写历史，**高风险，不要在已推送的仓库上用**）

涉及逐行取舍或冲突解决时，**不要交给 agent 独自处理**——它看不到你的真实意图，
容易"解决"成你不想要的样子。此时请用户出面，或让 agent 只做只读分析、
把冲突点列出来后由用户决定。

#### 给 AI agent 的硬性要求

1. **执行任何回档前，先 `git status` 和 `git log --oneline`，把当前状态告诉用户。**
2. **第 1–3 级可以自主执行；第 4 级必须先征得用户同意；第 5 级只做分析，不动手。**
3. **回档前先把当前状态存一份**：`git stash` 或开个备份分支
   （`git branch backup-YYYYMMDD`）。多一步几秒钟，能避免不可逆的损失。
4. **永远不要**在用户未明确要求时执行 `git reset --hard`、`git push --force`、
   `git clean -fd`、`git rebase`。
5. 回档后**必须复验**：跑 `python tools/build_pages.py`、查断链、双端截图（见 §5.3）。

### 5.1 环境

- **Python 3.9+**。本机路径：`C:/Users/Antho/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe`
  （若 `python` 已在 PATH 上，直接用 `python` 即可）
- **Pillow** 仅 `make_placeholders.py` 需要。本机装在隔离 venv：
  `C:/Users/Antho/.workbuddy-ai/binaries/python/envs/default`
  重新安装：`<venv>/Scripts/pip install Pillow`
- **Chrome** 仅 `screenshot.py` 需要。本机：`C:\Program Files\Google\Chrome\Application\chrome.exe`

### 5.2 常用命令

```bash
# 重新生成 notes/ 与 journal/ 全部页面
python tools/build_pages.py

# 重新生成 13 张占位图（需要 Pillow）
python tools/make_placeholders.py

# 截图（本地需先起静态服务器在 8899 端口）
cd site && python -m http.server 8899 --bind 127.0.0.1 &
python tools/screenshot.py index.html 0 out.png 1440 900            # 桌面
python tools/screenshot.py index.html 0 out.png 390 1900 frame compact  # 移动端整页
```

`screenshot.py` 参数：`<页面(相对 site/)> <scrollY> <输出绝对路径> [宽] [高] [frame] [compact]`
- `frame` — 用定宽 iframe 模拟移动端（**必须**，见 §6.1）
- `compact` — 注入评审用压缩 CSS，让整页塞进一张长截图。**仅用于截图，绝不进交付代码。**

### 5.3 改完自查清单

1. `python tools/build_pages.py` 无报错
2. 全站链接无断链（19 个 HTML、约 272 条站内引用）
3. 桌面 1440px + 移动 390px 双端目视确认
4. 未引入任何外部依赖（不要加 CDN、不要加 npm 包）

---

## 6. 已知坑（踩过的，别再踩）

### 6.1 Chrome on Windows 无头模式窗口宽度被钳制在约 500px

`--window-size=390,844` 实际仍按 504px 排版，移动端截图会失真。
**必须**用 `screenshot.py` 的 `frame` 模式（页面套在定宽 iframe 里再截）。

### 6.2 无头截图偶发整片空白 / 黑色块

经 DOM 探针排查（几何、`scrollY`、class 均正确），判定为本机 headless 合成层栅格化缺陷，
**不是 CSS/JS 问题**。绕过方式：`compact` + 超高视口整页截图。
另外 `site/index.html` 里有一段 5 秒兜底 `setTimeout`，防止动效失败时页面永久隐藏——
**不要删掉它。**

### 6.3 目录式链接在 `file://` 下失效

全站已统一为显式 `index.html`（例如 `profile/index.html` 而非 `profile/`）。
新增链接请沿用这个写法，否则本地双击打开会 404。

### 6.4 `tools/` 里的脚本用 `__file__` 定位项目根

```python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
```

所以**不要**把脚本挪出 `tools/`，否则路径会错。移动后请同步改这段。

### 6.5 字体子集：`noto-serif-sc-name.woff2` 只有 2.3 KB

因为它只包含「王松林」三个字（用 Google Fonts 的 `text=` 参数做的子集）。
**如果要让名牌显示别的名字，必须重新生成这个子集**，否则新字会 fallback 到系统衬线字体，
字形和字重都对不上。

### 6.6 大视口截图时固定元素会被"拉长"

固定定位的浮层（logo、名牌、巨型字）在超高视口下会铺满整个视口高度，看起来散开。
这是截图方式的必然结果，**不是布局 bug**，正常浏览器窗口下是正常的。

---

## 7. 待办 / 已知局限

- [ ] **`site/img/` 下 12 张 JPG 是占位图**——抽象灰阶合成图，仅为让版式读得出来、
      让"悬停显色"有效果可看（`wechat-qr.jpg` 是真实素材，`trip-01..03.jpg` 已停用，
      见 §4.5 / §4.6）。换成真实照片时保持文件名不变。
- [ ] **右上角 SNS 导航 3 项，其中 2 项仍是占位**（在各页 `<ul class="snsnav">` 内，
      共 19 个 HTML 文件，改 `tools/build_pages.py` 的 `header()` 后重新生成）：
      `wechat` → `img/wechat-qr.jpg`（已接二维码）、
      `phone` → `href="#"`（待填真实号码）、
      `email` → `mailto:hello@example.com`（示例地址，待换真实邮箱）。
- [ ] `NOTES` 数据里的 `img` 字段未被使用，可清理（见 §4.1）。
- [ ] 站内搜索、RSS、站点地图（sitemap.xml）均未实现。
- [ ] 无分析统计、无评论系统（纯静态，如需请接第三方）。

---

## 8. 设计参考

- 参考站：<https://www.oniguili.jp/>（西村祥子 / Sayoko Nishimura）
- 已复刻的核心特征：5 列网格 + `subgrid`、`mix-blend-mode: difference` 浮层、
  竖排文字、340px/`opacity:.05` 巨型背景字、72px 错落 CJK 名牌、`svh` 视口节奏、
  灰阶→彩色揭示、首屏字母闪烁入场。
- 配色数值已与参考站逐像素比对一致（logo 最暗像素 `0`、巨型字区 `242`、名牌区 `5`）。
