(function () {
  "use strict";

  // Shared across app/products/* — this repo deliberately has no bundler
  // (see kabukicho_survival_map/architecture.md's "Why no framework/
  // bundler"), so a plain <script src="../shared/dom_escape.js"> tag,
  // loaded before a product's own app.js, is how a second product reuses
  // this instead of re-copying it. Extracted 2026-07-14 after a repo-wide
  // process consultation flagged escapeHtml() as a local, unexported
  // function in kabukicho_survival_map/app.js -- the only product surface
  // that renders untrusted/data-file-sourced content via innerHTML today,
  // and the exact kind of thing CLAUDE.md's duplication concern applies to
  // once a second surface needs the same pattern.
  function escapeHtml(str) {
    return String(str == null ? "" : str).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // Guarded the same way app.js guards its own module.exports, so a plain
  // Node test script can require() this file directly without a browser
  // `window` global.
  if (typeof window !== "undefined") {
    window.AcipDomUtils = { escapeHtml: escapeHtml };
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { escapeHtml: escapeHtml };
  }
})();
