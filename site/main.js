/* Rea-Cli 落地页交互：菜单 / 复制 / 选项卡 / 工作台聚焦 / 滚动显现 */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Toast（aria-live 复制反馈） ---------- */
  var toast = document.getElementById("toast");
  var toastTimer = null;
  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () {
      toast.classList.remove("is-visible");
    }, 1800);
  }

  /* ---------- 复制（含 file:// 等非安全上下文回退） ---------- */
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(
        function () { return true; },
        function () { return legacyCopy(text); }
      );
    }
    return Promise.resolve(legacyCopy(text));
  }
  function legacyCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "0";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, ta.value.length);
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  Array.prototype.forEach.call(document.querySelectorAll("[data-copy]"), function (btn) {
    btn.addEventListener("click", function () {
      var target = document.querySelector(btn.getAttribute("data-copy"));
      if (!target) return;
      copyText(target.innerText).then(function (ok) {
        btn.classList.add("is-copied");
        showToast(ok ? "已复制到剪贴板" : "复制失败，请手动选择文本");
        window.setTimeout(function () { btn.classList.remove("is-copied"); }, 1600);
      });
    });
  });

  /* ---------- 通用选项卡（含方向键导航） ---------- */
  function setupTabs(tablistSelector) {
    var tablist = document.querySelector(tablistSelector);
    if (!tablist) return;
    var tabs = Array.prototype.slice.call(tablist.querySelectorAll('[role="tab"]'));

    function activate(tab, moveFocus) {
      tabs.forEach(function (t) {
        var selected = t === tab;
        t.setAttribute("aria-selected", selected ? "true" : "false");
        t.classList.toggle("is-active", selected);
        t.tabIndex = selected ? 0 : -1;
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) {
          panel.hidden = !selected;
          panel.classList.toggle("is-active", selected);
        }
      });
      if (moveFocus) tab.focus();
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () { activate(tab, false); });
    });

    tablist.addEventListener("keydown", function (event) {
      var index = tabs.indexOf(document.activeElement);
      if (index < 0) return;
      var next = null;
      if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + 1) % tabs.length;
      else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = tabs.length - 1;
      if (next !== null) {
        event.preventDefault();
        activate(tabs[next], true);
      }
    });
  }
  setupTabs(".flow-tabs");
  setupTabs(".seg");

  /* ---------- 首屏工作台：悬停即切换（点击/焦点仍可用） ---------- */
  var bench = document.querySelector(".bench");
  if (bench) {
    var nodes = Array.prototype.slice.call(bench.querySelectorAll(".bench-node"));
    var panels = Array.prototype.slice.call(bench.querySelectorAll(".bench-panel"));
    var setStage = function (i) {
      if (bench.getAttribute("data-stage") === String(i)) return;
      bench.setAttribute("data-stage", String(i));
      nodes.forEach(function (n, k) {
        n.classList.toggle("is-active", k === i);
        n.setAttribute("aria-pressed", k === i ? "true" : "false");
      });
      panels.forEach(function (p, k) {
        p.classList.toggle("is-focus", k === i);
      });
    };
    nodes.forEach(function (node, i) {
      node.addEventListener("pointerenter", function (event) {
        if (event.pointerType === "mouse" || event.pointerType === "pen") setStage(i);
      });
      node.addEventListener("click", function () { setStage(i); });
      node.addEventListener("focus", function () { setStage(i); });
    });
  }

  /* ---------- 移动端菜单 ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var menu = document.getElementById("mobile-menu");
  if (toggle && menu) {
    var setMenu = function (open) {
      menu.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "关闭菜单" : "打开菜单");
      toggle.classList.toggle("is-open", open);
    };
    toggle.addEventListener("click", function () { setMenu(menu.hidden); });
    menu.addEventListener("click", function (event) {
      if (event.target.closest("a")) setMenu(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !menu.hidden) {
        setMenu(false);
        toggle.focus();
      }
    });
    window.addEventListener("resize", function () {
      if (window.matchMedia("(min-width: 761px)").matches && !menu.hidden) {
        setMenu(false);
      }
    });
  }

  /* ---------- 头部滚动态 ---------- */
  var header = document.getElementById("site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- 实录 GIF 加载失败回退 ---------- */
  var showcaseImg = document.getElementById("showcase-img");
  if (showcaseImg) {
    var markBroken = function () {
      var frame = document.getElementById("showcase-frame");
      if (frame) frame.classList.add("is-broken");
    };
    showcaseImg.addEventListener("error", markBroken);
    if (showcaseImg.complete && showcaseImg.naturalWidth === 0) markBroken();
  }

  /* ---------- 滚动显现 ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(revealEls, function (el) { el.classList.add("in-view"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: "0px 0px -6% 0px" });
    Array.prototype.forEach.call(revealEls, function (el) { io.observe(el); });
  }
})();
