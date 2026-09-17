/* Rea-Cli 落地页交互：菜单 / 复制 / 选项卡 / 工作台聚焦 / 滚动显现 */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var I18N = window.SITE_I18N || {};

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
        showToast(ok ? (I18N.copied || "已复制到剪贴板") : (I18N.copyFail || "复制失败，请手动选择文本"));
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
  setupTabs(".seg");

  /* ---------- 平滑波形生成（确定性种子，镜像填充） ---------- */
  function buildWavePath(seed, w, h) {
    var s = (seed >>> 0) || 1;
    function rnd() { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }
    var cx = h / 2, n = Math.floor(w / 3), pts = [], prev = 0.25, i, t, env, target;
    for (i = 0; i <= n; i++) {
      t = i / n;
      env = 0.3 + 0.7 * Math.sin(Math.PI * Math.min(1, Math.max(0.001, t)));
      target = env * (0.3 + 0.7 * rnd());
      prev = prev * 0.52 + target * 0.48;
      pts.push(prev);
    }
    function xAt(k) { return k * w / n; }
    function yTop(k) { return cx - pts[k] * h * 0.42; }
    function yBot(k) { return cx + pts[k] * h * 0.42; }
    var d = "M0," + yTop(0).toFixed(1), k, mx, my;
    for (k = 1; k <= n; k++) {
      mx = ((xAt(k - 1) + xAt(k)) / 2).toFixed(1);
      my = ((yTop(k - 1) + yTop(k)) / 2).toFixed(1);
      d += " Q" + xAt(k - 1).toFixed(1) + "," + yTop(k - 1).toFixed(1) + " " + mx + "," + my;
    }
    d += " L" + w + "," + yTop(n).toFixed(1);
    d += " L" + w + "," + yBot(n).toFixed(1);
    for (k = n - 1; k >= 0; k--) {
      mx = ((xAt(k + 1) + xAt(k)) / 2).toFixed(1);
      my = ((yBot(k + 1) + yBot(k)) / 2).toFixed(1);
      d += " Q" + xAt(k + 1).toFixed(1) + "," + yBot(k + 1).toFixed(1) + " " + mx + "," + my;
    }
    d += " L0," + yBot(0).toFixed(1) + " Z";
    return d;
  }
  function buildSinePath(w, h) {
    var cx = h / 2, amp = h * 0.34, cycles = 7, d = "M0," + cx, x, y;
    for (x = 2; x <= w; x += 2) {
      y = cx - amp * Math.sin((x / w) * Math.PI * 2 * cycles);
      d += " L" + x + "," + y.toFixed(1);
    }
    return d;
  }
  Array.prototype.forEach.call(document.querySelectorAll(".daw-wave"), function (svg) {
    var seed = svg.getAttribute("data-seed");
    var path = svg.querySelector("path");
    if (!path) {
      path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      svg.appendChild(path);
    }
    path.setAttribute("d", seed === "sine" ? buildSinePath(120, 24) : buildWavePath(parseInt(seed, 10), 120, 24));
  });

  /* ---------- 工作流：步骤切换 + 产物飞行衔接 ---------- */
  var flow = document.getElementById("flow");
  if (flow) {
    var flowTabs = Array.prototype.slice.call(flow.querySelectorAll(".flow-tab"));
    var flowTexts = Array.prototype.slice.call(flow.querySelectorAll(".flow-text"));
    var flowCodes = Array.prototype.slice.call(flow.querySelectorAll(".flow-code"));
    var flowLists = Array.prototype.slice.call(flow.querySelectorAll(".verify-list"));
    var flowBody = document.getElementById("flow-body");
    var flowDaw = document.getElementById("flow-daw");
    var flowState = document.getElementById("flow-daw-state");
    var flowLabel2 = document.getElementById("flow-label2");
    var flowVerifyTitle = document.getElementById("flow-verify-title");
    var flowNote = flow.querySelector('[data-vn="1"]');

    var STEP_STATE = I18N.stepState || ["草稿 · 待执行", "隔离实例 · 运行中", "已验证"];
    var STEP_LABEL2 = I18N.stepLabel2 || ["Track 2", "Track 2", "tone 440Hz"];
    var STEP_VERIFY = I18N.stepVerify || ["Rea-Cli 预检查 · 离线", "PROOF.JSON · 执行证明", "工程与音频验证"];

    function swapVisible(els, i) {
      els.forEach(function (el, k) {
        var on = k === i;
        if (on) {
          el.hidden = false;
          el.classList.remove("is-active", "is-on");
          void el.offsetWidth;
          el.classList.add(el.classList.contains("verify-list") ? "is-on" : "is-active");
        } else {
          el.hidden = true;
          el.classList.remove("is-active", "is-on");
        }
      });
    }

    var glowTimer = null;
    function pulseGlow(i) {
      if (reduceMotion) return;
      window.clearTimeout(glowTimer);
      var el = [flowCodes[i], flowDaw, flow.querySelector(".verify")][i];
      if (!el) return;
      el.classList.remove("is-glow");
      void el.offsetWidth;
      el.classList.add("is-glow");
      glowTimer = window.setTimeout(function () { el.classList.remove("is-glow"); }, 560);
    }

    function setStep(i, moveFocus) {
      var prev = parseInt(flow.getAttribute("data-step"), 10) || 0;
      if (prev === i) return;
      flow.setAttribute("data-step", String(i));
      flowTabs.forEach(function (t, k) {
        t.setAttribute("aria-selected", k === i ? "true" : "false");
        t.classList.toggle("is-active", k === i);
        t.tabIndex = k === i ? 0 : -1;
      });
      if (flowBody) flowBody.setAttribute("aria-labelledby", "tab-w" + i);
      swapVisible(flowTexts, i);
      swapVisible(flowCodes, i);
      swapVisible(flowLists, i);
      if (flowState) {
        flowState.textContent = STEP_STATE[i];
        flowState.classList.toggle("daw-state-ok", i === 2);
      }
      if (flowLabel2) {
        flowLabel2.textContent = STEP_LABEL2[i];
        flowLabel2.classList.toggle("daw-label-dim", i < 2);
      }
      if (flowVerifyTitle) flowVerifyTitle.textContent = STEP_VERIFY[i];
      if (flowNote) flowNote.hidden = i !== 1;
      pulseGlow(i);
      if (moveFocus) flowTabs[i].focus();
    }

    flowTabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { setStep(i, false); });
    });
    flow.querySelector(".flow-tabs").addEventListener("keydown", function (event) {
      var index = flowTabs.indexOf(document.activeElement);
      if (index < 0) return;
      var next = null;
      if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + 1) % flowTabs.length;
      else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (index - 1 + flowTabs.length) % flowTabs.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = flowTabs.length - 1;
      if (next !== null) {
        event.preventDefault();
        setStep(next, true);
      }
    });
  }

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
      toggle.setAttribute("aria-label", open ? (I18N.menuClose || "关闭菜单") : (I18N.menuOpen || "打开菜单"));
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
