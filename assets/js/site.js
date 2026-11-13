/* Small site behaviour: mobile menu toggle. */
(function () {
  "use strict";
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("site-nav");
  if (!btn || !nav) return;
  btn.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    btn.setAttribute("aria-expanded", String(open));
  });
  nav.addEventListener("click", function (e) {
    if (e.target.tagName === "A") {
      nav.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
    }
  });
})();
