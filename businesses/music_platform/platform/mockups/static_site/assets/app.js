document.querySelectorAll("[data-disabled]").forEach((element) => {
  element.setAttribute("aria-disabled", "true");
  element.addEventListener("click", (event) => {
    event.preventDefault();
    alert("静的モックです。ここでは状態変化の見た目だけを確認します。");
  });
});

document.querySelectorAll(".help").forEach((element) => {
  element.addEventListener("click", (event) => {
    event.stopPropagation();
    const expanded = element.getAttribute("aria-expanded") === "true";
    document.querySelectorAll(".help[aria-expanded='true']").forEach((open) => {
      if (open !== element) open.setAttribute("aria-expanded", "false");
    });
    element.setAttribute("aria-expanded", String(!expanded));
  });
});

document.addEventListener("click", () => {
  document.querySelectorAll(".help[aria-expanded='true']").forEach((element) => {
    element.setAttribute("aria-expanded", "false");
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  document.querySelectorAll(".help[aria-expanded='true']").forEach((element) => {
    element.setAttribute("aria-expanded", "false");
  });
});
