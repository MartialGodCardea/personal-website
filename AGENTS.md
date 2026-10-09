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

> ⚠️ **踩过的坑（2026-10-03）**：`@media (min-width: 835px)` 里曾用 `display: flex`
> 覆盖 `.journal-home-wrap` / `.prof-home-wrap`。`subgrid` **只在父级是 grid 时生效**，
> 父级一变 flex 就静默失效，子列塌陷到十几像素——首页正文退化成「一行一个字」，
> 整页被拉长到一万多像素。
> 结论：**桌面端也不要拿 flex 去覆盖这两处的 grid**，那里只需要定位微调。

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
├── 技术架构.md               # 技术选型与整体结构说明（偏科普，改动前可先扫一遍）
├── 字体规范.md               # 字体清单与选型记录（复刻版 vs 原站真实字体）
├── 美术体检报告.md           # 美术问题清单：本轮已修 / 建议后续修（含验收命令）
├── site/                     # ★ 交付物：整个网站，可直接部署
│   ├── index.html            # 首页（四段式：design / journal / notes / prof）
│   ├── css/style.css         # ★ 全部样式，1286 行，15 个分节
│   ├── js/main.js            # 全部交互，9 个职责 + boot（见 §4.4）
│   ├── fonts/                # 2 个自托管 woff2：中文子集 + 西文子集（见 §6.5）
│   ├── img/                  # 12 张 JPG（10 张占位图 + water-bg.jpg + wechat-qr.jpg）+ 3 个 SVG
│   ├── profile/index.html    # 关于我
│   ├── projects/index.html   # 做过的事（4 个案例）
│   ├── notes/                # 写下的字：index.html + 8 篇
│   └── journal/              # 日常与照片：index.html + 6 篇
└── tools/                    # 构建与校验脚本，★ 不参与部署
    ├── build_pages.py        # 生成 notes/ 与 journal/ 全部页面
    ├── build_font_subset.py  # 生成中文 + 西文两套字体子集（含 cmap 覆盖自校验）
    ├── make_placeholders.py  # 用 Pillow 生成占位图
    ├── screenshot.py         # Chrome headless 截图（含移动端 iframe 模拟）
    ├── pack_handoff.py       # 打包 website-handoff.zip（排除 .git / .workbuddy-ai）
    ├── pngtool.py            # 纯标准库 PNG 像素探针（QA 用）
    └── font-src/             # 西文源字体（Newsreader 可变字体，OFL），供离线重建子集
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
| 10 | Water band（实拍水面照片 + 署名；**涟漪特效已下线**，见 §4.6） |
| 11 | Opening animation |
| 12 | Responsive |
| 13 | Image Lightbox（图片预览浮层） |
| 14 | Contact modal（联系方式弹窗：微信 / 电话 / 邮箱） |

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

只改 `css/style.css` 的 `/* 1. Tokens */` 一节。颜色、间距、缓动、圆角、阴影、
字体栈**全部**收敛在这一个 `:root` 里，改这一节即可全局生效：

```css
:root {
  /* —— 基础色 —— */
  --paper: #ffffff;        /* 底色 */
  --ink: #000000;          /* 正文色 */
  --ghost: #fafafa;        /* ★ 浮层专用：配合 difference 混合，别乱改 */
  --latin-ghost: 0.05;     /* 巨型背景字透明度 */
  --sel: #333333;          /* 选中文字背景 */
  --hairline: rgba(0, 0, 0, 0.14);
  --ink-soft: #111;        /* 次级深色（水面暗底等） */
  --muted: #6b6b6b;        /* 弱化文字（版权、脚注） */
  --water: #12161a;        /* 水面横幅底色 */

  /* —— 布局 —— */
  --gap: 24px;             /* 列间距 */
  --pad-x: 40px;           /* 左右页边距 */
  --nav-top: 40svh;        /* 导航起始高度 */

  /* —— 缓动 —— */
  --ease:        cubic-bezier(0.25, 0.1, 0.25, 1);   /* 通用 */
  --ease-in-out: cubic-bezier(0.42, 0, 0.58, 1);     /* 对称进出 */
  --ease-out:    cubic-bezier(0.22, 1, 0.36, 1);     /* 只减速（入场） */

  /* —— 形状 —— */
  --radius: 4px;
  --radius-sm: 2px;
  --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.2);
  --shadow-lg: 0 18px 60px rgba(0, 0, 0, 0.3);
  --overlay-blur: 7px;     /* 两个浮层的背景高斯模糊半径 */

  /* —— 字体 —— */
  --font-display: "Newsreader", "Noto Serif SC", …;  /* 西文衬线（首选自托管） */
  --font-cjk:     "Noto Serif SC", …;                /* 中文衬线 */
  --font-body:    "PingFang SC", …;                  /* 正文无衬线 */
}
```

字体栈是 `--font-display` / `--font-cjk` / `--font-body` 三个变量，改这里全站生效。
**`--font-display` 的首选西文现在是自托管的 `Newsreader`**（不再是 Bodoni Moda），
中文由 `--font-cjk` 的 `Noto Serif SC` 全站子集兜底——两套字体都是自托管、零外部请求，
字体文件与子集重建方法见 §6.5。

> 缓动原先在各处散写成裸 `ease` / `ease-in-out` / `cubic-bezier(...)`，现已全部收敛
> 到上面三个 token。加新过渡时请复用 token，不要再写裸值。

### 4.4 改交互行为

`js/main.js` 是一个 IIFE。下表按 `boot()` 里的**实际执行顺序**排列
（文件内的注释编号有历史漂移，以本表为准）：

| 函数 | 作用 |
|---|---|
| `renderDate()` | 右上角竖排日期，实时生成 |
| `markNavigation()` | 读 `body[data-page]`，给对应导航项加 `.active`（首页不高亮） |
| ~~`waterBand()`~~ | 动态水面涟漪。**已下线**（`boot()` 里被注释掉），见 §4.6 |
| `startRotators()` | 读 `[data-images]` JSON，定时交叉淡入换图 |
| `observePlates()` | `IntersectionObserver` 给 `#main_contents .img` 加 `.is-active`（触发显色） |
| `initLightbox()` | 图片灯箱：0.5–3x 缩放 / 拖拽 / 滚轮 / ESC（见 §4.7） |
| `initRippleText()` | 水面署名文字逐字随动画帧起伏（幅度 ≤ 字高 5%，几乎不可见） |
| `initContactModal()` | 联系方式遮罩弹窗：微信二维码 / 电话 / 邮箱，背景高斯模糊（见 §4.7） |
| `opening()` | 首屏字母闪烁 + 导航逐项入场，`sessionStorage.hasVisited` 保证只播一次 |

> **新增页面时必须设置 `<body data-page="...">`**，取值与 `NAV` 里的 key 一致
> （`home` / `profile` / `projects` / `notes` / `journal`），否则导航高亮会错。
> 新页面请复用 `tools/build_pages.py` 里的 `header()` 生成器，别手抄头部。

### 4.5 换真实照片

把照片放进 `site/img/`，**保持原有文件名**即可，布局不用动：

`design-01..04.jpg`（首页大图轮播）、`profile.jpg`、`journal-01..03.jpg`、
`note-01..02.jpg`。

**这 10 张目前是抽象占位图**，见 §7。（`trip-01..03.jpg` 三张已随照片横幅改版停用并删除，
见 §4.6。）

另有 `water-bg.jpg`（水面横幅底图）与 `wechat-qr.jpg`（微信二维码）是**真实素材**，
不是占位图，分别见 §4.6 与 §4.7。换图时同名替换即可。

### 4.6 水面横幅（原「旅行带」）

页面底部那条 100vh 的横幅（`#water-band`）＝ **实拍水面照片 ＋ 署名题款**。

**底层是实拍照片**，由 CSS 分节 10 的 `.trip::before` 承载（`site/img/water-bg.jpg`），
并以 `filter: grayscale(100%)` 现算灰调。用伪元素承载而非直接给 `.trip` 设
`background`，是为了让灰调**只作用于照片本身**，不波及署名文字；想恢复彩色只需删掉
那一行 `filter`。

> 素材来源：Wikimedia Commons 的 *Ripples on a mountain lake (Unsplash).jpg*，
> **CC0 1.0 公有领域奉献**（作者 Braxton Stuntz），可自由商用、无需署名。
> 处理：裁取涟漪区域 → 缩至 2400×1388 → JPEG q78（约 438 KB）。
> 原图 12.2 MB / 5769×3836，如需重新裁切请从 Commons 重新下载。
>
> ⚠️ 这张照片**自带明显的同心涟漪**（雨点打在水面上）。如果哪天觉得"底部水圈太抢眼"，
> 那是照片内容，不是特效——换一张平静水面的照片（同名替换 `water-bg.jpg`）即可。

**上层原本的程序波纹：2026-10-03 起已下线。**

用户反馈程序生成的水面叠在实拍照片上观感不佳，故暂时撤下，等找到参考实例复刻后再补。
代码与样式都**保留但断开**，恢复只需三步（缺一不可）：

1. 把 `<canvas class="water" aria-hidden="true"></canvas>` 与
   `<div class="water-glow" aria-hidden="true"></div>` 加回 `.trip` 内。
   ——共 19 个 HTML。其中 `notes/` 与 `journal/` 的 16 页由 `tools/build_pages.py`
   的 `TRIP` 常量生成，**改完必须重跑脚本**，否则会被覆盖（见 §4.1）；
2. 打开 `js/main.js` 里 `boot()` 中被注释掉的 `waterBand();`；
3. 把 `"#water-band canvas.water"` 加回 `initLightbox()` 的 `bindImages()` 选择器
   （点水面 canvas 会导出 PNG 快照放大）。

原理备查：两张 `Float32Array` 高度场交替推进波动方程，逐像素做位移采样 + 波峰高光；
模拟网格约为 CSS 像素的 1/3 且像素数封顶 12 万，再由浏览器放大，既轻又柔；鼠标划过
注入涟漪（按速度决定强度）、按下是一记更大的落水，另有约 1.2–2.9 秒一次的随机环境
滴落；离屏时 `IntersectionObserver` 停机，`prefers-reduced-motion: reduce` 时只画一帧
静水。调参集中在 `waterBand()` 顶部：`DAMP`（衰减）、`SLOPE`（位移强度）、`SPEC`（高光）。

> `trip-01..03.jpg` 与 `data-trips` / 随机换图逻辑已随本次改版**退出使用**，
> 三张图已于 2026-10-03 随死资产清理**删除**（`pickTrip()` 亦一并移除）。
> 要恢复照片横幅，需从 git 历史取回 `TRIP` 模板与 `pickTrip()`，并把图片文件补回 `site/img/`。

### 4.7 两个浮层：图片灯箱与联系方式弹窗

两者都是 `position: fixed` 遮罩 + `backdrop-filter` 模糊，但**刻意分开实现**，
因为语义不同、交互诉求也不同。

**图片灯箱**（`initLightbox()` / CSS 分节 13）——用于内容图片，需要放大细看：

- JS 自建 DOM（所以在 HTML 里搜不到 `#lightbox`，这是正常的）。
  支持 0.5–3x 缩放、拖拽平移、滚轮缩放、ESC / 点遮罩 / 关闭按钮退出。
- 绑定选择器写死在 `bindImages()` 里：
  `#main_contents .img img`、`#main_contents figure img`。
  **新增图片容器时要把选择器补进去，否则新图点了没反应。**
  （原第 3 条 `.plate img` 与第 4 条 `#water-band canvas.water` 已分别随死代码清理、
  涟漪特效下线移除，见 §4.6。）
- 动态插入的图片需要重绑，调用 `window.__rebindLightbox()`。

**联系方式弹窗**（`initContactModal()` / CSS 分节 14）——工具型弹层，三种联系方式共用：

- 触发：SNS 导航里带 `data-contact` 的 `<a>`。JS 拦截点击、弹出遮罩层，**不跳转**。
  两种形态由属性值决定：

  | 形态 | 触发写法 | 弹窗内容 |
  |---|---|---|
  | `qr` | `<a href="img/wechat-qr.jpg" data-contact="qr" data-label="微信 · 扫码添加">` | `href` 指向的图片 |
  | `text` | `<a href="tel:+8613768692678" data-contact="text" data-label="电话 Phone" data-value="+86 137 6869 2678">` | `data-value` 文本 + 复制按钮 |

  图片取自 `href`、文本取自 `data-value`，所以根目录（`img/`）与子目录（`../img/`）
  都无需额外配置。
- **无 JS 时 `href` 仍然有效**（`tel:` / `mailto:` / 图片地址），会退回原生行为——
  这是有意的降级路径。改这些链接时**不要**把 `href` 删成 `#`。
- 复制按钮优先用 `navigator.clipboard`，失败退回 `textarea + execCommand`，
  因此本机 `http://` 预览也能复制；成功后按钮显示「已复制」1.6 秒。
- 背景模糊 `backdrop-filter: blur(7px)`；打开时给 `<html>` 加 `.has-modal` 锁住滚动；
  关闭后焦点归还触发按钮（键盘用户不丢位置）。
- 卡片宽度 `min(90vw, 400px)`、文本字号上限 18px，是为了让 28 字符的邮箱
  `anthonywang171003@gmail.com` 在桌面端**正好单行放下**（换行会断在 `gmail.`
  后面，观感很差）。**改字号或内边距前先量一下邮箱宽度。**
- 二维码形态刻意**不做缩放**、也**不套灰调**：必须保持彩色与锐利，灰阶或插值都会
  影响扫码识别率。这与 `.img` 的 grayscale 规范是有意区分的，**不要"统一"掉**。

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
- **`.gitignore`** — 排除 `__pycache__/`、编辑器目录、`site/_*.html`（截图与字体自查
  用的临时评审页）、`*.png`（截图产物；**项目内没有任何 png 资源**，12 张图均为 JPG）、
  `_font-compare/`（字体对比样张，临时产物）、以及 `website-handoff.zip`
  （可由仓库内容随时重新打包，无需入库）。

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
- **fonttools[woff]** 仅 `build_font_subset.py` 需要（`--flavor=woff2` 依赖 brotli）。
  同样装在隔离 venv，重新安装：`<venv>/Scripts/pip install "fonttools[woff]"`
- **Chrome** 仅 `screenshot.py` 需要。本机：`C:\Program Files\Google\Chrome\Application\chrome.exe`

### 5.2 常用命令

```bash
# 重新生成 notes/ 与 journal/ 全部页面
python tools/build_pages.py

# 重新生成 10 张占位图（需要 Pillow）
python tools/make_placeholders.py

# 重建两套字体子集（需要 fonttools[woff]，含 cmap 覆盖自校验）
python tools/build_font_subset.py

# 截图（本地需先起静态服务器在 8899 端口）
cd site && python -m http.server 8899 --bind 127.0.0.1 &
python tools/screenshot.py index.html 0 out.png 1440 900            # 桌面
python tools/screenshot.py index.html 0 out.png 390 1900 frame compact  # 移动端整页

# 重新打包交付压缩包 website-handoff.zip
python tools/pack_handoff.py
```

`pack_handoff.py` 会自动排除 `.git/`、`.workbuddy-ai/`、`__pycache__/`、`*.zip`
以及 `_*` 开头的临时评审页（`site/_shot.html` 等），
所以可以放心反复执行。**改完内容记得重打一次**，否则交付包是旧的。

`screenshot.py` 参数：`<页面(相对 site/)> <scrollY> <输出绝对路径> [宽] [高] [frame] [compact]`
- `frame` — 用定宽 iframe 模拟移动端（**必须**，见 §6.1）
- `compact` — 注入评审用压缩 CSS，让整页塞进一张长截图。**仅用于截图，绝不进交付代码。**

### 5.3 改完自查清单

1. `python tools/build_pages.py` 无报错，且**重跑一次不产生任何差异**（幂等）
2. 全站链接无断链（19 个 HTML、252 条站内引用）
3. 桌面 1440px + 移动 390px 双端目视确认
4. 未引入任何外部依赖（不要加 CDN、不要加 npm 包）
5. **若新增了中文内容**：跑一次 `python tools/build_font_subset.py`，
   确认末尾打印的 cmap 覆盖自校验通过（无 `missing` 字符），否则新字会掉字。
6. 改了交付内容就重跑 `python tools/pack_handoff.py`

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

### 6.2b 截图不要依赖滚动：`scroll-behavior: smooth` + virtual-time 不推进

`html { scroll-behavior: smooth }`（§2 base）会让 `window.scrollTo()` / `scrollIntoView()`
变成**动画**，而这个动画在 Chrome `--virtual-time-budget` 下不推进，结果是截图永远停在
第 0 屏——若此刻内容还在开场淡入（`html.is-loading` 把 `#main_contents` 设为
`opacity: 0`），拍出来就是一张纯白图。

要截某个滚动位置，注入脚本里必须先关掉平滑滚动、并强制结束开场隐藏态：

```js
document.documentElement.style.scrollBehavior = 'auto';
document.documentElement.classList.remove('is-loading');
['h1.id', '.todays_date', '.name_ja', 'footer', '#main_contents']
  .forEach(function (s) { var e = document.querySelector(s); if (e) e.classList.add('is-visible'); });
window.scrollTo(0, y);
```

但**滚动后再截图在本机仍不可靠**（合成帧不跟随滚动）。最稳的办法是干脆不滚动：
用 `compact` + 超高视口（如 `1440x3900`）一次拍下整页，再按坐标裁切。

`scrollIntoView()` 尤其别用：`#wrapper` 带 `overflow: hidden`，会被它当成祖先滚动容器
从内部滚走，结果同样是白屏。

### 6.3 目录式链接在 `file://` 下失效

全站已统一为显式 `index.html`（例如 `profile/index.html` 而非 `profile/`）。
新增链接请沿用这个写法，否则本地双击打开会 404。

### 6.4 `tools/` 里的脚本用 `__file__` 定位项目根

```python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
```

所以**不要**把脚本挪出 `tools/`，否则路径会错。移动后请同步改这段。

### 6.5 两套自托管字体子集：全站中文 + 西文

`site/fonts/` 下只有两个文件，都是**从站点实际用到的字符**裁出来的子集，全站零外部请求：

| 文件 | 字体 | 大小 | 保留的可变轴 | 覆盖 |
|---|---|---|---|---|
| `noto-serif-sc-subset.woff2` | Noto Serif SC | **≈ 355 KB** | `wght` 200–900 | 全站中文 + 全角标点 + 拉丁数字（**964 个码位**） |
| `newsreader-latin.woff2` | Newsreader | **≈ 83 KB** | `wght` 200–800 **+** `opsz` 6–72 | 仅西文（104 个码位） |

两套都由 `tools/build_font_subset.py` **一次生成**（脚本支持中西双目标）：

```bash
pip install "fonttools[woff]"          # woff2 输出需要 brotli，走 woff extra
python tools/build_font_subset.py
```

脚本做的事，按顺序：

1. 扫描 `site/**/*.html`、`site/css/*.css`、`site/js/*.js`，收集所有会**渲染出来**的字符；
2. **先剥掉注释**——CSS/JS 的 `/* … */` 与 HTML 的 `<!-- … -->` 永远不会显示。
   不剥的话中文子集会从 389 KB 涨到 395 KB（注释里的中文被误算进去了）。
   JS 的 `//` 行注释**刻意不剥**（会把 `https://` 截断）；
3. 用 `pyftsubset` 按字符集裁剪，`layout_features=["*"]` 保留全部 OpenType 特性，
   `--flavor=woff2` 输出压缩；
4. **自校验**：把产物 woff2 读回来取 `getBestCmap()`，断言「收集到的字符集 ⊆ 产物 cmap」，
   少一个就报错退出（附 `U+XXXX` 与 Unicode 名称）。
   控制字符（`Cc` 类，如换行 `U+000A`）没有字形，收集阶段就排除。

> **为什么保留可变轴而不锁死一个字重**：中文子集保留 `wght 200–900`，一份文件同时服务
> 名牌的 900 与正文的 400，浏览器取真字重而不是**伪粗体**机械加粗——这正是本轮修掉的
> 「中文拼接感」根因（旧子集只含「王松林」3 字，其余中文掉到 SimSun 再被伪加粗）。
> 西文额外保留 `opsz`，让 340px 的巨型字标自动取显示档、10px 的版权行自动取文本档。

**新增中文内容后要重跑**：任何新写的汉字若不在现有子集里，会 fallback 到系统衬线，
字形对不上。所以改完内容 → 跑一次 `build_font_subset.py` → 覆盖字体文件。
（西文同理，但 Newsreader 只覆盖基础拉丁，正常写作够用。）

> ⚠️ 旧文件 `noto-serif-sc-name.woff2`（2.3 KB / 仅 3 字）已删除，别再引用。

### 6.6 大视口截图时固定元素会被"拉长"

固定定位的浮层（logo、名牌、巨型字）在超高视口下会铺满整个视口高度，看起来散开。
这是截图方式的必然结果，**不是布局 bug**，正常浏览器窗口下是正常的。

---

## 7. 待办 / 已知局限

- [ ] **`site/img/` 下 10 张 JPG 是占位图**——抽象灰阶合成图，仅为让版式读得出来、
      让"悬停显色"有效果可看。`water-bg.jpg` 与 `wechat-qr.jpg` 是真实素材，
      `trip-01..03.jpg` 已停用并删除（见 §4.5 / §4.6）。换成真实照片时保持文件名不变。
- [x] **右上角 SNS 导航 3 项均已接通**（在各页 `<ul class="snsnav">` 内，共 19 个 HTML
      文件；`notes/` 与 `journal/` 的 16 页改 `tools/build_pages.py` 的 `header()`
      后重新生成）：
      `wechat` → `img/wechat-qr.jpg`、`phone` → `tel:+8613768692678`、
      `email` → `mailto:anthonywang171003@gmail.com`。
      三项都走同一个遮罩弹窗，点击**不跳转**（见 §4.7）。
- [ ] **水面涟漪特效处于下线状态**，等用户找到参考实例后照着复刻（见 §4.6）。
      代码与样式都还在，恢复是三步操作。
- [ ] `initRippleText()`（署名逐字浮动）仍启用，但幅度上限只有字高的 5%（约 1px），
      肉眼几乎不可见。若认为它是"死代码"可一并移除，或调大 `AMP` 让它真正起作用。
- [ ] `NOTES` 数据里的 `img` 字段未被使用，可清理（见 §4.1）。
- [x] ~~`tools/make_water_bg.py`~~ **已删除**（2026-10-03，随死资产清理）。
      它生成的是旧的程序化水底图；`water-bg.jpg` 已换成实拍照片，该脚本不再是素材来源。
- [ ] `js/main.js` 内部的分节注释编号有历史漂移（涟漪字编 8、开场编 6），
      功能无影响，整理时对齐即可。
- [ ] 站内搜索、RSS、站点地图（sitemap.xml）均未实现。
- [ ] 无分析统计、无评论系统（纯静态，如需请接第三方）。

---

## 8. 设计参考

- 参考站：<https://www.oniguili.jp/>（西村祥子 / Sayoko Nishimura）
- 已复刻的核心特征：5 列网格 + `subgrid`、`mix-blend-mode: difference` 浮层、
  竖排文字、340px/`opacity:.05` 巨型背景字、72px 错落 CJK 名牌、`svh` 视口节奏、
  灰阶→彩色揭示、首屏字母闪烁入场。
- 配色数值已与参考站逐像素比对一致（logo 最暗像素 `0`、巨型字区 `242`、名牌区 `5`）。
