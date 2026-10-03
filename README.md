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
| `site/css/style.css` | 全部样式（1015 行，13 个分节） |
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
- **换照片** → 覆盖 `site/img/` 下的同名文件，**当前 13 张是占位图**

## 交接给 AI agent

请让它先读 **[AGENTS.md](./AGENTS.md)** —— 里面有完整的设计约束、文件地图、
常见改动做法、构建命令和已知坑。不要只丢代码给它。
