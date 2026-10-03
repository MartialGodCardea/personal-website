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
   * 5. Water band — 常驻水面 + 跟随光标的涟漪
   *
   * 高度场（两张 Float32 缓冲交替推进的波动方程）+ 逐像素位移着色。
   * 模拟网格远小于 CSS 像素（约 1/4），再由浏览器放大，既轻又柔。
   * 页面不在视口内时停机；prefers-reduced-motion 时只画一帧静水。
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
    waterBand();
    startRotators();
    observePlates();

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
