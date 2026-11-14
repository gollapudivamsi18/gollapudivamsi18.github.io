/* Site behaviour: mobile menu, diagram lightbox, gentle reveal on scroll. No dependencies. */
(function () {
  "use strict";

  // Mobile menu ---------------------------------------------------------------
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("site-nav");
  if (btn && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    };
    btn.addEventListener("click", function () { setOpen(!nav.classList.contains("open")); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) { setOpen(false); btn.focus(); }
    });
  }

  // Diagram lightbox (native <dialog>: focus trap and Esc come for free) ----------
  var dialog = null;
  function openDiagram(src, title, opener) {
    if (!dialog) {
      dialog = document.createElement("dialog");
      dialog.className = "lightbox";
      dialog.setAttribute("aria-labelledby", "lightbox-title");
      dialog.innerHTML =
        '<div class="lightbox-head"><h2 id="lightbox-title"></h2>' +
        '<button type="button" class="icon-btn" aria-label="Close diagram">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>' +
        '<div class="lightbox-body"><img alt=""></div>';
      document.body.appendChild(dialog);
      dialog.querySelector(".icon-btn").addEventListener("click", function () { dialog.close(); });
      dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
      dialog.addEventListener("close", function () { if (dialog._opener) dialog._opener.focus(); });
    }
    dialog.querySelector("#lightbox-title").textContent = title;
    var img = dialog.querySelector("img");
    img.src = src;
    var source = opener.querySelector("img") || document.querySelector('img[src="' + src + '"]');
    img.alt = source ? source.alt : title;
    dialog._opener = opener;
    if (typeof dialog.showModal === "function") dialog.showModal();
    else window.open(src, "_blank", "noopener");
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-diagram]");
    if (!t) return;
    e.preventDefault();
    openDiagram(t.getAttribute("data-diagram"), t.getAttribute("data-title") || "Architecture", t);
  });

  // Reveal on scroll ------------------------------------------------------------
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && items.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -40px 0px", threshold: 0.05 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("in"); });
  }
})();
