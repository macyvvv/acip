#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
PUBLIC_DIR = ROOT / "public"
PRODUCT_DIR = ROOT / "app" / "products"
COMPLETED_DIR = ROOT / "runtime" / "issues" / "completed"


def main() -> int:
    build_public_site(ROOT)
    return 0


def build_public_site(base_path: Path) -> list[Path]:
    public_dir = base_path / "public"
    public_dir.mkdir(parents=True, exist_ok=True)
    generated_paths: list[Path] = []
    for issue in _completed_issues(base_path):
        product_path = _detect_product_directory(base_path, issue)
        if product_path is None:
            continue
        site_path = public_dir / f"product_{issue['issue_number']:04d}"
        if site_path.exists():
            _remove_tree(site_path)
        site_path.mkdir(parents=True, exist_ok=True)
        description = _read_description(product_path)
        title = _site_title(issue, product_path)
        _write_file(site_path / "index.html", _render_html(title, description))
        _write_file(site_path / "style.css", _render_css())
        _write_file(site_path / "script.js", _render_js())
        generated_paths.append(site_path)
    return generated_paths


def _completed_issues(base_path: Path) -> list[dict]:
    completed: list[dict] = []
    completed_dir = base_path / "runtime" / "issues" / "completed"
    if not completed_dir.exists():
        return completed
    for path in sorted(completed_dir.glob("issue_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("issue_number"), int):
            completed.append(data)
    return sorted(completed, key=lambda item: int(item["issue_number"]))


def _detect_product_directory(base_path: Path, issue: dict) -> Path | None:
    deliverables = issue.get("deliverables", [])
    for deliverable in deliverables:
        if not isinstance(deliverable, str):
            continue
        match = re.match(r"(?:app/products|product)/([^/]+)/", deliverable)
        if match:
            candidate_name = match.group(1)
            for candidate in (
                base_path / "app" / "products" / candidate_name,
                base_path / "product" / candidate_name,
            ):
                if candidate.exists():
                    return candidate
    issue_title = str(issue.get("issue_title", "")).lower()
    if "product-0001" in issue_title:
        for candidate in (
            base_path / "app" / "products" / "minimal_launch_brief_generator",
            base_path / "product" / "minimal_launch_brief_generator",
        ):
            if candidate.exists():
                return candidate
    if "product-0002" in issue_title:
        for candidate in (
            base_path / "app" / "products" / "repository_operational_summary",
            base_path / "product" / "repository_operational_summary",
        ):
            if candidate.exists():
                return candidate
    return None


def _site_title(issue: dict, product_path: Path) -> str:
    readme = product_path / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return str(issue.get("issue_title", "Product")).strip()


def _read_description(product_path: Path) -> str:
    readme = product_path / "README.md"
    if not readme.exists():
        return "Static product site."
    lines = readme.read_text(encoding="utf-8").splitlines()
    body_lines = []
    seen_heading = False
    for line in lines:
        if not seen_heading:
            if line.startswith("# "):
                seen_heading = True
            continue
        body_lines.append(line)
    description = "\n".join(line for line in body_lines if line.strip())
    return description.strip() or "Static product site."


def _render_html(title: str, description: str) -> str:
    escaped_title = _escape_html(title)
    escaped_description = _escape_html(description)
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "  <meta charset=\"utf-8\">",
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            f"  <title>{escaped_title}</title>",
            "  <link rel=\"stylesheet\" href=\"style.css\">",
            "  <script defer src=\"script.js\"></script>",
            "  <script async src=\"https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX\"></script>",
            "  <script>",
            "    window.dataLayer = window.dataLayer || [];",
            "    function gtag(){dataLayer.push(arguments);}",
            "    gtag('js', new Date());",
            "    gtag('config', 'G-XXXXXXXXXX');",
            "  </script>",
            "</head>",
            "<body>",
            "  <main class=\"page\">",
            f"    <h1>{escaped_title}</h1>",
            f"    <p class=\"description\">{escaped_description}</p>",
            "    <label for=\"brief-input\">Brief input</label>",
            "    <textarea id=\"brief-input\" rows=\"8\" placeholder=\"Enter launch brief text\"></textarea>",
            "    <div class=\"actions\">",
            "      <button id=\"generate-button\" type=\"button\">Generate</button>",
            "    </div>",
            "    <section>",
            "      <h2>Output</h2>",
            "      <pre id=\"output-area\"></pre>",
            "    </section>",
            "  </main>",
            "</body>",
            "</html>",
        ]
    ) + "\n"


def _render_css() -> str:
    return "\n".join(
        [
            "body {",
            "  font-family: system-ui, sans-serif;",
            "  margin: 0;",
            "  background: #f8fafc;",
            "  color: #0f172a;",
            "}",
            ".page {",
            "  max-width: 960px;",
            "  margin: 0 auto;",
            "  padding: 2rem;",
            "}",
            "textarea {",
            "  width: 100%;",
            "  min-height: 12rem;",
            "  margin: 0.5rem 0 1rem;",
            "}",
            "button {",
            "  padding: 0.75rem 1rem;",
            "}",
            "pre {",
            "  white-space: pre-wrap;",
            "  background: #fff;",
            "  border: 1px solid #cbd5e1;",
            "  padding: 1rem;",
            "}",
        ]
    ) + "\n"


def _render_js() -> str:
    return "\n".join(
        [
            "const input = document.getElementById('brief-input');",
            "const output = document.getElementById('output-area');",
            "const button = document.getElementById('generate-button');",
            "button.addEventListener('click', () => {",
            "  const value = input.value.trim();",
            "  output.textContent = value ? `Generated brief:\\n${value}` : 'No input provided.';",
            "});",
        ]
    ) + "\n"


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _remove_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file() or child.is_symlink():
            child.unlink()
        elif child.is_dir():
            child.rmdir()
    path.rmdir()


if __name__ == "__main__":
    raise SystemExit(main())
