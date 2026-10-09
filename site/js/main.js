/* ==========================================================================
   WANG SONGLIN — site behaviour
   Adapted from the oniguili.jp front-end: opening flicker, staggered reveal,
   live date, active navigation, scroll-activated plates, image rotators.
   ========================================================================== */
(function () {
  "use strict";

  var root = document.documentElement;
  var sleep = function (ms) {
    return new Promise(function (r) {
      setTimeout(r, ms);
    });
  };
  var $ = function (sel, ctx) {
    return (ctx || document).querySelector(sel);
  };
  var $$ = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  };

  /* ------------------------------------------------------------------ *
   * 1. Today's date, written vertically in the top-right corner
   * ------------------------------------------------------------------ */
  function renderDate() {
    var el = $(".todays_date");
    if (!el) return;
    var now = new Date();
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var d = now.getDate();
    var suffix = ["th", "st", "nd", "rd"];
    var v = d % 100;
    var ord = suffix[(v - 20) % 10] || suffix[v] || suffix[0];
    el.textContent =
      "( " + months[now.getMonth()] + ". " + d + ord + ", " + now.getFullYear() + " )";
  }

  /* ------------------------------------------------------------------ *
   * 2. Active navigation state
   * ------------------------------------------------------------------ */
  function markNavigation() {
    var nav = $("#globalnav");
    if (!nav) return;
    var page = document.body.getAttribute("data-page") || "home";
    var link = nav.querySelector('a[data-nav="' + page + '"]');
    if (!link) return;                       /* home = nothing highlighted */
    link.classList.add("active");
    nav.classList.add("has-active");
  }

  /* ------------------------------------------------------------------ *
   * 3. Plates light up when they reach the lower third of the viewport
   * ------------------------------------------------------------------ */
  function observePlates() {
    var plates = $$("#main_contents .img");
    if (!plates.length) return;
    if (!("IntersectionObserver" in window)) {
      plates.forEach(function (p) { p.classList.add("is-active"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        entry.target.classList.toggle("is-active", entry.isIntersecting);
      });
    }, { rootMargin: "0px 0px -70% 0px" });
    plates.forEach(function (p) { io.observe(p); });
  }

  /* ------------------------------------------------------------------ *
   * 4. Rotating plates  (data-images="[..]")
   * ------------------------------------------------------------------ */
  function startRotators() {
    $$("[data-images]").forEach(function (host) {
      var img = host.querySelector("img");
      if (!img) return;
      var list;
      try {
        list = JSON.parse(host.getAttribute("data-images"));
      } catch (e) {
        return;
      }
      if (!Array.isArray(list) || list.length < 2) return;
      var i = 0;
      var interval = parseInt(host.getAttribute("data-interval"), 10) || 4200;
      setInterval(function () {
        i = (i + 1) % list.length;
        img.style.transition = "opacity .45s ease";
        img.style.opacity = "0";
        setTimeout(function () {
          img.src = list[i];
          img.style.opacity = "1";
        }, 450);
      }, interval);
    });
  }

  /* ------------------------------------------------------------------ *
   * 5. Water band — 常驻水面 + 跟随光标的涟漪 【当前状态：已下线】
   *
   * 高度场（两张 Float32 缓冲交替推进的波动方程）+ 逐像素位移着色。
   * 模拟网格远小于 CSS 像素（约 1/4），再由浏览器放大，既轻又柔。
   * 页面不在视口内时停机；prefers-reduced-motion 时只画一帧静水。
   *
   * 2026-10-03 起暂时下线：程序生成的水面叠在实拍照片上观感不佳。
   * 恢复步骤（缺一不可）：
   *   1) 把 <canvas class="water"> 与 <div class="water-glow"> 加回 .trip；
   *   2) 打开 boot() 里被注释掉的 waterBand() 调用；
   *   3) 把 "#water-band canvas.water" 加回 initLightbox() 的 bindImages() 选择器。
   * 对应的 CSS（.trip .water / .trip .water-glow）已保留，无需改动。
   * ------------------------------------------------------------------ */
  function waterBand() {
    var host = $("#water-band");
    var canvas = host && $("canvas.water", host);
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext("2d", { alpha: false });
    var calm = !!(window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches);

    var DAMP = 0.990;   /* 每帧衰减，越小越"黏" */
    var SLOPE = 7.5;    /* 波面梯度 → 位移强度 */
    var SPEC = 62;      /* 波峰高光 */

    var W = 0, H = 0;
    var cur, prev, tex, frame;
    var raf = 0, visible = false, nextDrop = 0;
    var lastX = 0, lastY = 0, lastT = 0;

    /* 水体底纹：上浅下深的深度渐变 + 焦散细纹，一次性烘到 tex */
    function paintTexture() {
      for (var y = 0; y < H; y++) {
        var v = y / (H - 1);
        var base = 124 - 104 * Math.pow(v, 0.9);
        for (var x = 0; x < W; x++) {
          var u = x / (W - 1);
          /* 垂直方向频率高于水平方向 = 被压缩的水面透视，形成横向细纹 */
          var c =
            Math.sin((u * 3.0 + v * 9.0) * Math.PI) * 0.5 +
            Math.sin((u * -2.2 + v * 14.0) * Math.PI + 1.7) * 0.34 +
            Math.sin((u * 7.5 + v * 23.0) * Math.PI + 0.6) * 0.2;
          if (c < 0) c = 0;
          c = Math.pow(c, 2.4) * 56 * (1.08 - v * 0.62);
          var n = (Math.random() - 0.5) * 4;
          var i = (y * W + x) * 3;
          tex[i] = base + c + n;
          tex[i + 1] = base + c * 1.02 + n;
          tex[i + 2] = base + c * 1.08 + n * 1.1;   /* 一丝冷调 */
        }
      }
    }

    /* 一滴扰动：以中心为谷的余弦衰减 */
    function drop(cx, cy, radius, power) {
      var x0 = Math.max(0, Math.round(cx - radius));
      var x1 = Math.min(W - 1, Math.round(cx + radius));
      var y0 = Math.max(0, Math.round(cy - radius));
      var y1 = Math.min(H - 1, Math.round(cy + radius));
      for (var y = y0; y <= y1; y++) {
        for (var x = x0; x <= x1; x++) {
          var d = Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy));
          if (d > radius) continue;
          cur[y * W + x] -= power * Math.cos((d / radius) * Math.PI * 0.5);
        }
      }
    }

    function seed() {
      drop(W * 0.30, H * 0.62, W * 0.045, 0.30);
      drop(W * 0.72, H * 0.40, W * 0.038, 0.22);
    }

    function resize() {
      var rect = host.getBoundingClientRect();
      var w = Math.round(Math.min(480, Math.max(240, rect.width / 3)));
      var h = Math.round(Math.min(560,
        Math.max(170, w * rect.height / Math.max(1, rect.width))));
      if (w * h > 120000) {                    /* 上限，保证低端设备也跑得动 */
        var k = Math.sqrt(120000 / (w * h));
        w = Math.max(200, Math.round(w * k));
        h = Math.max(150, Math.round(h * k));
      }
      if (w === W && h === H) return;
      W = w; H = h;
      canvas.width = W;
      canvas.height = H;
      cur = new Float32Array(W * H);
      prev = new Float32Array(W * H);
      tex = new Uint8ClampedArray(W * H * 3);
      frame = ctx.createImageData(W, H);
      for (var a = 3; a < frame.data.length; a += 4) frame.data[a] = 255;
      paintTexture();
      seed();
    }

    function advance() {
      for (var y = 1; y < H - 1; y++) {
        var row = y * W;
        for (var x = 1; x < W - 1; x++) {
          var i = row + x;
          prev[i] = ((cur[i - 1] + cur[i + 1] + cur[i - W] + cur[i + W]) * 0.5
            - prev[i]) * DAMP;
        }
      }
      var swap = cur; cur = prev; prev = swap;
    }

    function draw() {
      var d = frame.data, k = 0;
      for (var y = 0; y < H; y++) {
        var row = y * W;
        var rowUp = y > 0 ? row - W : row;
        var rowDn = y < H - 1 ? row + W : row;
        for (var x = 0; x < W; x++) {
          var i = row + x;
          var iL = x > 0 ? i - 1 : i;
          var iR = x < W - 1 ? i + 1 : i;
          var dx = (cur[iL] - cur[iR]) * SLOPE;
          var dy = (cur[rowUp + x] - cur[rowDn + x]) * SLOPE;
          if (dx > 8) dx = 8; else if (dx < -8) dx = -8;
          if (dy > 8) dy = 8; else if (dy < -8) dy = -8;
          var sx = x + dx;
          var sy = y + dy;
          if (sx < 0) sx = 0; else if (sx > W - 1) sx = W - 1;
          if (sy < 0) sy = 0; else if (sy > H - 1) sy = H - 1;
          var ti = ((sy | 0) * W + (sx | 0)) * 3;
          var hi = cur[i] > 0 ? cur[i] * SPEC : cur[i] * (SPEC * 0.28);
          d[k] = tex[ti] + hi;
          d[k + 1] = tex[ti + 1] + hi;
          d[k + 2] = tex[ti + 2] + hi * 1.05;
          k += 4;
        }
      }
      ctx.putImageData(frame, 0, 0);
    }

    function frameLoop(now) {
      raf = 0;
      if (!visible) return;
      if (now > nextDrop) {
        drop(1 + Math.random() * (W - 2), 1 + Math.random() * (H - 2),
          W * (0.02 + Math.random() * 0.04), 0.16 + Math.random() * 0.26);
        nextDrop = now + 1200 + Math.random() * 1700;
      }
      advance();
      draw();
      raf = window.requestAnimationFrame(frameLoop);
    }

    function start() {
      if (calm || raf) return;
      raf = window.requestAnimationFrame(frameLoop);
    }

    function stop() {
      if (raf) window.cancelAnimationFrame(raf);
      raf = 0;
    }

    function pointerMove(e) {
      if (calm) return;
      var rect = canvas.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      var x = (e.clientX - rect.left) / rect.width * W;
      var y = (e.clientY - rect.top) / rect.height * H;
      var now = e.timeStamp || Date.now();
      if (now - lastT < 45) return;                 /* 限流，免得刷成噪点 */
      var speed = Math.sqrt((x - lastX) * (x - lastX) + (y - lastY) * (y - lastY));
      lastX = x; lastY = y; lastT = now;
      drop(x, y, Math.max(2.2, W * 0.026), Math.min(0.26, 0.08 + speed * 0.03));
    }

    resize();
    if (calm) {                                    /* 静水一帧，不再动 */
      advance();
      advance();
      draw();
      return;
    }

    host.addEventListener("pointermove", pointerMove);
    host.addEventListener("pointerdown", function (e) {
      var rect = canvas.getBoundingClientRect();
      drop((e.clientX - rect.left) / rect.width * W,
        (e.clientY - rect.top) / rect.height * H, W * 0.045, 0.4);
    });
    window.addEventListener("resize", function () {
      resize();
      start();
    });
    window.addEventListener("orientationchange", function () {
      resize();
      start();
    });
    if ("ResizeObserver" in window) {
      new ResizeObserver(function () { resize(); }).observe(host);
    }

    if (!("IntersectionObserver" in window)) {
      visible = true;
      start();
      return;
    }
    new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { visible = entry.isIntersecting; });
      visible ? start() : stop();
    }, { rootMargin: "160px 0px" }).observe(host);
  }

  /* ------------------------------------------------------------------ *
   * 7. Image lightbox — 全屏预览 + 滚轮缩放 + 拖拽平移 + 边界限制
   * ------------------------------------------------------------------ */
  function initLightbox() {
    if ($("#lightbox")) return;

    var overlay = document.createElement("div");
    overlay.id = "lightbox";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "图片预览");
    overlay.innerHTML =
      '<div id="lightbox-close" aria-label="关闭预览">' +
        '<svg viewBox="0 0 24 24"><line x1="6" y1="6" x2="18" y2="18"/>' +
        '<line x1="18" y1="6" x2="6" y2="18"/></svg></div>' +
      '<div id="lightbox-stage"><img id="lightbox-img" alt="预览"></div>';
    document.body.appendChild(overlay);

    var stage = $("#lightbox-stage", overlay);
    var img = $("#lightbox-img", overlay);
    var closeBtn = $("#lightbox-close", overlay);

    var MIN = 0.5, MAX = 3;
    var scale = 1, tx = 0, ty = 0;
    var dragging = false, sx = 0, sy = 0, sTx = 0, sTy = 0;
    var baseW = 0, baseH = 0, opened = false;

    function apply() {
      img.style.transform = "translate(" + tx + "px," + ty + "px) scale(" + scale + ")";
    }
    function reset() {
      scale = 1; tx = 0; ty = 0;
      apply();
    }
    function clampPan() {
      if (scale <= 1) { tx = 0; ty = 0; return; }
      var extraX = (baseW * (scale - 1)) / 2;
      var extraY = (baseH * (scale - 1)) / 2;
      if (Math.abs(tx) > extraX) tx = tx > 0 ? extraX : -extraX;
      if (Math.abs(ty) > extraY) ty = ty > 0 ? extraY : -extraY;
    }

    function open(src) {
      reset();
      img.src = src;
      opened = false;
      overlay.classList.add("is-animating");
      requestAnimationFrame(function () {
        overlay.classList.add("is-open");
        overlay.classList.remove("is-animating");
      });
      document.body.style.overflow = "hidden";
      opened = true;
    }

    function close() {
      if (!opened) return;
      opened = false;
      overlay.classList.remove("is-open");
      overlay.classList.add("is-animating");
      setTimeout(function () {
        overlay.classList.remove("is-animating");
        img.removeAttribute("src");
        document.body.style.overflow = "";
      }, 300);
    }

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay || e.target === stage) close();
    });
    closeBtn.addEventListener("click", function (e) { e.stopPropagation(); close(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay.classList.contains("is-open")) close();
    });

    img.addEventListener("load", function () {
      baseW = img.clientWidth;
      baseH = img.clientHeight;
    });

    overlay.addEventListener("wheel", function (e) {
      if (!overlay.classList.contains("is-open")) return;
      e.preventDefault();
      var delta = e.deltaY < 0 ? 1.12 : 1 / 1.12;
      var next = Math.min(MAX, Math.max(MIN, scale * delta));
      if (Math.abs(next - 1) < 0.02) next = 1;
      scale = next;
      clampPan();
      apply();
    }, { passive: false });

    function pointerDown(e) {
      if (!overlay.classList.contains("is-open")) return;
      if (scale <= 1) return;
      dragging = true;
      stage.classList.add("is-dragging");
      sx = e.clientX; sy = e.clientY;
      sTx = tx; sTy = ty;
      try { stage.setPointerCapture(e.pointerId); } catch (_) {}
    }
    function pointerMove(e) {
      if (!dragging) return;
      tx = sTx + (e.clientX - sx);
      ty = sTy + (e.clientY - sy);
      clampPan();
      apply();
    }
    function pointerUp(e) {
      dragging = false;
      stage.classList.remove("is-dragging");
      try { stage.releasePointerCapture(e.pointerId); } catch (_) {}
    }
    stage.addEventListener("pointerdown", pointerDown);
    stage.addEventListener("pointermove", pointerMove);
    stage.addEventListener("pointerup", pointerUp);
    stage.addEventListener("pointercancel", pointerUp);

    function bindImages() {
      var selector = [
        "#main_contents .img img",
        "#main_contents figure img"
      ].join(",");
      $$(selector).forEach(function (el) {
        if (el.__lbound) return;
        el.__lbound = true;
        el.style.cursor = "zoom-in";
        el.addEventListener("click", function (e) {
          var src;
          if (el.tagName && el.tagName === "CANVAS") {
            try { src = el.toDataURL("image/png"); } catch (_) { return; }
          } else {
            src = el.currentSrc || el.src;
          }
          if (!src) return;
          e.preventDefault();
          e.stopPropagation();
          open(src);
        });
      });
    }

    bindImages();
    window.__rebindLightbox = bindImages;
  }

  /* ------------------------------------------------------------------ *
   * 8. Ripple text — 水面区域文字逐字涟漪，与水面动画帧同步
   *    幅度 ≤ 字体自身高度 5%，GPU 加速，低性能设备降级静态
   * ------------------------------------------------------------------ */
  function initRippleText() {
    var sig = $(".trip .signature");
    if (!sig) return;

    var calm = !!(window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    var poorPerf = !("requestAnimationFrame" in window);
    if (calm || poorPerf) return;

    var text = sig.textContent || "";
    sig.textContent = "";
    var chars = [];
    for (var i = 0; i < text.length; i++) {
      var s = document.createElement("span");
      s.className = "ripple-char";
      s.textContent = text.charAt(i) === " " ? "\u00A0" : text.charAt(i);
      sig.appendChild(s);
      chars.push(s);
    }
    if (!chars.length) return;

    function sampleFontHeight() {
      var t = chars[0];
      var h = t.offsetHeight || 24;
      return Math.max(4, h);
    }

    var fontH = sampleFontHeight();
    var AMP = fontH * 0.05;     /* 严格控制在字高 5% 以内 */
    var WAVE_PERIOD = 2.4;      /* 秒，与水面随机滴落平均周期一致 */

    var rafId = 0, visible = true, start = performance.now();

    function frame(now) {
      rafId = 0;
      if (!visible) return;
      var t = (now - start) / 1000;
      for (var i = 0; i < chars.length; i++) {
        var phase = i * 0.55;
        var dy = Math.sin((t / WAVE_PERIOD) * Math.PI * 2 + phase) * AMP;
        var dx = Math.sin((t / (WAVE_PERIOD * 0.72)) * Math.PI * 2 + phase * 1.3) * AMP * 0.35;
        chars[i].style.transform = "translate3d(" +
          dx.toFixed(3) + "px," + dy.toFixed(3) + "px,0)";
      }
      rafId = requestAnimationFrame(frame);
    }

    function start() { if (rafId) return; rafId = requestAnimationFrame(frame); }
    function stop() { if (rafId) cancelAnimationFrame(rafId); rafId = 0; }

    window.addEventListener("resize", function () {
      fontH = sampleFontHeight();
      AMP = fontH * 0.05;
    });

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { visible = en.isIntersecting; });
        visible ? start() : stop();
      }, { rootMargin: "120px 0px" }).observe(sig);
    } else {
      start();
    }
  }

  /* ------------------------------------------------------------------ *
   * 9. Contact modal — 联系方式遮罩弹窗（微信 / 电话 / 邮箱）
   *    拦截 SNS 导航里的 a[data-contact]，改为在当前页弹出遮罩层，
   *    背景用 backdrop-filter 做轻微高斯模糊。两种形态由 data-contact 决定：
   *      data-contact="qr"   → 展示 href 指向的图片（微信二维码）
   *      data-contact="text" → 展示 data-value（电话 / 邮箱）+ 复制按钮
   *    href 保留 tel: / mailto: / 图片地址，因此无 JS 时会退回原生行为。
   * ------------------------------------------------------------------ */
  function initContactModal() {
    var triggers = $$("a[data-contact]");
    if (!triggers.length) return;
    if ($("#contact-modal")) return;

    var overlay = document.createElement("div");
    overlay.id = "contact-modal";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-labelledby", "contact-label");
    overlay.innerHTML =
      '<div id="contact-card">' +
        '<button id="contact-close" type="button" aria-label="关闭">' +
          '<svg viewBox="0 0 24 24"><line x1="6" y1="6" x2="18" y2="18"/>' +
          '<line x1="18" y1="6" x2="6" y2="18"/></svg>' +
        '</button>' +
        '<img id="contact-img" alt="" hidden>' +
        '<p id="contact-label"></p>' +
        '<p id="contact-value" hidden></p>' +
        '<button id="contact-copy" type="button" hidden>复制</button>' +
      '</div>';
    document.body.appendChild(overlay);

    var img = $("#contact-img", overlay);
    var label = $("#contact-label", overlay);
    var value = $("#contact-value", overlay);
    var copyBtn = $("#contact-copy", overlay);
    var closeBtn = $("#contact-close", overlay);
    var lastFocus = null;
    var opened = false;
    var copyTimer = 0;

    /* 复制：优先异步剪贴板 API（需要 https / localhost），
       失败或不可用时退回临时 textarea + execCommand，
       这样在本机 http:// 预览时也能正常复制。 */
    function copied() {
      copyBtn.textContent = "已复制";
      copyBtn.classList.add("is-done");
      if (copyTimer) window.clearTimeout(copyTimer);
      copyTimer = window.setTimeout(resetCopy, 1600);
    }
    function resetCopy() {
      copyTimer = 0;
      copyBtn.textContent = "复制";
      copyBtn.classList.remove("is-done");
    }
    function legacyCopy(text) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.top = "-1000px";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (_) { ok = false; }
      document.body.removeChild(ta);
      if (ok) copied();
    }
    function copy(text) {
      if (!text) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(copied, function () {
          legacyCopy(text);
        });
      } else {
        legacyCopy(text);
      }
    }

    function open(trigger) {
      if (opened) return;
      opened = true;
      lastFocus = document.activeElement;

      var href = trigger.getAttribute("href") || "";
      var text = trigger.getAttribute("data-value") || "";
      var isQr = trigger.getAttribute("data-contact") === "qr" &&
        href && href.charAt(0) !== "#";

      label.textContent = trigger.getAttribute("data-label") || "";

      if (isQr) {
        img.src = href;
        img.alt = label.textContent || "二维码";
        img.hidden = false;
        value.hidden = true;
        value.textContent = "";
        copyBtn.hidden = true;
      } else {
        /* 文本模式：清掉图片地址，避免残留请求 */
        img.hidden = true;
        img.removeAttribute("src");
        img.alt = "";
        value.textContent = text;
        value.hidden = !text;
        copyBtn.hidden = !text;
        resetCopy();
      }

      overlay.classList.add("is-open");
      root.classList.add("has-modal");
      closeBtn.focus();
    }

    function close() {
      if (!opened) return;
      opened = false;
      overlay.classList.remove("is-open");
      root.classList.remove("has-modal");
      if (copyTimer) { window.clearTimeout(copyTimer); copyTimer = 0; }
      resetCopy();
      /* 焦点还给触发按钮，键盘用户不会丢失位置 */
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    triggers.forEach(function (trigger) {
      trigger.addEventListener("click", function (e) {
        /* 只要标了 data-contact 就接管点击；href 仅作无 JS 兜底 */
        e.preventDefault();
        open(trigger);
      });
    });

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) close();       /* 点遮罩空白处关闭 */
    });
    closeBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      close();
    });
    copyBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      copy(value.textContent || "");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && opened) close();
    });
  }

  /* ------------------------------------------------------------------ *
   * 6. Opening sequence — letters flicker, nav staggers, page settles
   * ------------------------------------------------------------------ */
  function opening() {
    var nameEnSpans = $$(".name_en span");
    var navItems = $$("#globalnav > ul > li");

    if (!nameEnSpans.length) {
      root.classList.remove("is-loading");
      try { sessionStorage.setItem("hasVisited", "true"); } catch (e) {}
      return;
    }

    var tick = 100;
    var flickerDuration = nameEnSpans.length * tick + 300;

    /* shuffle every letter except the first, so the opening letter holds */
    var order = nameEnSpans.map(function (_, i) { return i; });
    for (var i = order.length - 1; i > 1; i--) {
      var j = Math.floor(Math.random() * i) + 1;
      var tmp = order[i];
      order[i] = order[j];
      order[j] = tmp;
    }

    var count = 0;
    var flicker = setInterval(function () {
      var idx = count < order.length
        ? order[count]
        : Math.floor(Math.random() * nameEnSpans.length);
      var span = nameEnSpans[idx];
      span.style.transition = "opacity .5s ease";
      span.classList.add("is-visible");
      setTimeout(function () {
        span.style.transition = "opacity .8s ease";
        span.classList.remove("is-visible");
      }, 300);
      count++;
    }, tick);

    var navDone = (async function () {
      await sleep(flickerDuration - 500);
      for (var n = 0; n < navItems.length; n++) {
        navItems[n].classList.add("is-visible");
        await sleep(100);
      }
    })();

    var restDone = (async function () {
      await sleep(flickerDuration - 500 + navItems.length * 100 - 100);
      ["h1.id", ".todays_date", ".name_ja", "footer", "#main_contents"].forEach(function (sel) {
        var el = $(sel);
        if (el) el.classList.add("is-visible");
      });
    })();

    Promise.all([navDone, restDone]).then(function () {
      return sleep(500);
    }).then(function () {
      clearInterval(flicker);
      nameEnSpans.forEach(function (s) {
        s.style.transition = "opacity .8s ease";
        s.classList.remove("is-visible");
      });
      root.classList.remove("is-loading");
      try { sessionStorage.setItem("hasVisited", "true"); } catch (e) {}
    });
  }

  /* ------------------------------------------------------------------ *
   * boot
   * ------------------------------------------------------------------ */
  function boot() {
    renderDate();
    markNavigation();
    /* 水面涟漪特效已下线（2026-10-03）。恢复步骤见上方 waterBand() 的注释。 */
    // waterBand();
    startRotators();
    observePlates();
    initLightbox();
    initRippleText();
    initContactModal();

    if (root.classList.contains("is-loading")) {
      opening();
    } else {
      root.classList.remove("is-loading");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
