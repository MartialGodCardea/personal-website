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
    var plates = $$("#main_contents .img, .trip .img");
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
   * 5. Random trip band  (data-trips="[..]") — 只随机换图，文案固定
   * ------------------------------------------------------------------ */
  function pickTrip() {
    var host = $("#random-trip");
    if (!host) return;
    var trips;
    try {
      trips = JSON.parse(host.getAttribute("data-trips"));
    } catch (e) {
      return;
    }
    if (!Array.isArray(trips) || !trips.length) return;
    var t = trips[Math.floor(Math.random() * trips.length)];
    var img = host.querySelector("img");
    if (img && t.image) img.src = t.image;
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
    pickTrip();
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
