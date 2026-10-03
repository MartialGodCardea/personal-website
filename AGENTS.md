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
│   ├── img/                  # 13 张 JPG（★ 占位图）+ 4 个 SVG
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
| 10 | Trip band |
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
| 3 | `observePlates()` | `IntersectionObserver` 给图片加 `.is-active`（触发显色） |
| 4 | `startRotators()` | 读 `[data-images]` JSON，定时交叉淡入换图 |
| 5 | `pickTrip()` | 读 `#random-trip[data-trips]`，随机选一条展示 |
| 6 | `opening()` | 首屏字母闪烁 + 导航逐项入场，`sessionStorage.hasVisited` 保证只播一次 |

> **新增页面时必须设置 `<body data-page="...">`**，取值与 `NAV` 里的 key 一致
> （`home` / `profile` / `projects` / `notes` / `journal`），否则导航高亮会错。
> 新页面请复用 `tools/build_pages.py` 里的 `header()` 生成器，别手抄头部。

### 4.5 换真实照片

把照片放进 `site/img/`，**保持原有文件名**即可，布局不用动：

`design-01..04.jpg`（首页大图轮播）、`profile.jpg`、`journal-01..03.jpg`、
`note-01..02.jpg`、`trip-01..03.jpg`。

**这 13 张目前是抽象占位图**，见 §7。

---

## 5. 构建与校验

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

- [ ] **`site/img/` 下 13 张 JPG 是占位图**——抽象灰阶合成图，仅为让版式读得出来、
      让"悬停显色"有效果可看。换成真实照片时保持文件名不变（见 §4.5）。
- [ ] **右上角 SNS 导航 4 项全是占位**（在各页 `<ul class="snsnav">` 内，需逐页替换，
      共 19 个 HTML 文件）：
      `ML` → `mailto:hello@example.com`、
      `LI` → `https://www.linkedin.com/`（通用首页，非个人主页）、
      `GH` → `https://github.com/`（同上）、
      `WX` → `href="#"`（未填）。
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
