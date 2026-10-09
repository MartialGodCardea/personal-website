# -*- coding: utf-8 -*-
"""Screenshot a page at a realistic viewport and scroll offset.

Desktop: python _shot.py <page> <scrollY> <out> [w] [h]
Mobile:  python _shot.py <page> <scrollY> <out> <w> <h> frame
         (Chrome on Windows clamps the headless window to ~500px wide, so small
          viewports are emulated with an iframe of the requested size.)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = r"C:\Users\Antho\AppData\Local\Temp\wbprofile"
PORT = 8899

SCROLL = """
<script>
(function () {
  function go() {
    document.documentElement.style.scrollBehavior = 'auto';
    window.scrollTo(0, %d);
  }
  if (document.readyState === 'complete') go();
  else window.addEventListener('load', go);
  window.addEventListener('load', function () { setTimeout(go, 300); });
})();
</script>
"""

# Review helper: collapse the viewport-height rhythm so a whole page fits in one
# tall capture. Never used for the delivered site.
COMPACT = """
<style id="__review">
  /* 首页有「开屏动画」：<html> 初始带 .is-loading，脚本跑完后才移除。
     headless 的 virtual-time 不会推进这段动画，首屏会整块 opacity:0 拍成空白。
     这里是评审辅助样式（不进交付包），把 loading 态直接还原成「动画已结束」的
     稳定终态，让每次截图都落在同一个状态。
     注意 .name_en span 的终态是 opacity: var(--latin-ghost)（0.05 的背景水印），
     不是 1 —— 写成 1 会把水印拍成全黑的假象。 */
  html.is-loading .name_en span { opacity: var(--latin-ghost) !important; }
  html.is-loading h1.id,
  html.is-loading .todays_date,
  html.is-loading .name_ja,
  html.is-loading footer,
  html.is-loading #globalnav > ul > li,
  html.is-loading #main_contents { opacity: 1 !important; transform: none !important; }
  #main_contents { margin-top: 40px !important; margin-bottom: 40px !important; }
  #main_contents .inner { margin-top: 80px !important; }
  #main_contents .index_outer .page_intro { margin-bottom: 60px !important; }
  #main_contents .index_outer .list .item { margin-bottom: 60px !important; }
  #main_contents .index_outer.design_index .list .item { margin-bottom: 80px !important; }
  #main_contents .index_outer .history,
  #main_contents .index_outer .skills { margin-top: 60px !important; }
  .trip { height: 620px !important; }
</style>
"""

FRAME = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:#ffffff;overflow:hidden}}
iframe{{display:block;width:{w}px;height:{h}px;border:0}}
</style></head><body><iframe src="{src}"></iframe></body></html>
"""


def shot(rel, offset, out, w=1440, h=900, framed=False, compact=False):
    src = os.path.join(SITE, rel.replace("/", os.sep))
    d = os.path.dirname(src)
    tmp = os.path.join(d, "_shot.html")
    html = open(src, encoding="utf-8").read()
    extra = (COMPACT if compact else "") + (SCROLL % offset)
    open(tmp, "w", encoding="utf-8").write(
        html.replace("</body>", extra + "</body>"))
    url_dir = os.path.dirname(rel).strip("/")
    url = "http://127.0.0.1:%d/%s_shot.html" % (PORT, (url_dir + "/") if url_dir else "")

    win = "%d,%d" % (w, h)
    target = url
    if framed:
        frame_path = os.path.join(SITE, "_frame.html")
        open(frame_path, "w", encoding="utf-8").write(
            FRAME.format(w=w, h=h, src=url))
        target = "http://127.0.0.1:%d/_frame.html" % PORT
        win = "%d,%d" % (max(w + 40, 560), h + 40)

    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--user-data-dir=" + PROFILE, "--virtual-time-budget=12000",
                    "--window-size=" + win, "--screenshot=" + out, target],
                   capture_output=True)
    os.remove(tmp)
    print("  shot %-24s y=%-5d %sx%s%s%s" % (rel, offset, w, h,
                                             " framed" if framed else "",
                                             " compact" if compact else ""))


if __name__ == "__main__":
    rel, off, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    w = int(sys.argv[4]) if len(sys.argv) > 4 else 1440
    h = int(sys.argv[5]) if len(sys.argv) > 5 else 900
    framed = "frame" in sys.argv[6:]
    compact = "compact" in sys.argv[6:]
    shot(rel, off, out, w, h, framed, compact)
