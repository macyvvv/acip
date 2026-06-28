from __future__ import annotations

from pathlib import Path

from scripts.build_public_site import build_public_site


def test_completed_issue_generates_public_site(tmp_path: Path) -> None:
    completed_dir = tmp_path / "runtime" / "issues" / "completed"
    completed_dir.mkdir(parents=True)
    (completed_dir / "issue_0030.json").write_text(
        '{"issue_number": 30, "issue_title": "PRODUCT-0001: Product Launch Checklist", "deliverables": ["product/minimal_launch_brief_generator/README.md"]}',
        encoding="utf-8",
    )
    product_dir = tmp_path / "product" / "minimal_launch_brief_generator"
    product_dir.mkdir(parents=True)
    (product_dir / "README.md").write_text("# Minimal Launch Brief Generator\n\nDesc.", encoding="utf-8")
    (product_dir / "requirements.md").write_text("req", encoding="utf-8")
    (product_dir / "architecture.md").write_text("arch", encoding="utf-8")
    (product_dir / "release_notes.md").write_text("notes", encoding="utf-8")
    (product_dir / "src").mkdir()
    (product_dir / "src" / "__init__.py").write_text("", encoding="utf-8")
    (product_dir / "src" / "minimal_launch_brief_generator.py").write_text("", encoding="utf-8")
    (product_dir / "tests").mkdir()
    (product_dir / "tests" / "test_minimal_launch_brief_generator.py").write_text("", encoding="utf-8")

    generated = build_public_site(tmp_path)

    site = tmp_path / "public" / "product_0030"
    assert site in generated
    assert (site / "index.html").exists()
    assert (site / "style.css").exists()
    assert (site / "script.js").exists()


def test_rebuild_is_idempotent(tmp_path: Path) -> None:
    completed_dir = tmp_path / "runtime" / "issues" / "completed"
    completed_dir.mkdir(parents=True)
    (completed_dir / "issue_0030.json").write_text(
        '{"issue_number": 30, "issue_title": "PRODUCT-0001: Product Launch Checklist", "deliverables": ["product/minimal_launch_brief_generator/README.md"]}',
        encoding="utf-8",
    )
    product_dir = tmp_path / "product" / "minimal_launch_brief_generator"
    product_dir.mkdir(parents=True)
    (product_dir / "README.md").write_text("# Minimal Launch Brief Generator\n\nDesc.", encoding="utf-8")

    build_public_site(tmp_path)
    first = (tmp_path / "public" / "product_0030" / "index.html").read_text(encoding="utf-8")
    build_public_site(tmp_path)
    second = (tmp_path / "public" / "product_0030" / "index.html").read_text(encoding="utf-8")

    assert first == second


def test_required_files_exist(tmp_path: Path) -> None:
    completed_dir = tmp_path / "runtime" / "issues" / "completed"
    completed_dir.mkdir(parents=True)
    (completed_dir / "issue_0030.json").write_text(
        '{"issue_number": 30, "issue_title": "PRODUCT-0001: Product Launch Checklist", "deliverables": ["product/minimal_launch_brief_generator/README.md"]}',
        encoding="utf-8",
    )
    product_dir = tmp_path / "product" / "minimal_launch_brief_generator"
    product_dir.mkdir(parents=True)
    (product_dir / "README.md").write_text("# Minimal Launch Brief Generator\n\nDesc.", encoding="utf-8")

    build_public_site(tmp_path)
    site = tmp_path / "public" / "product_0030"
    assert (site / "index.html").exists()
    assert (site / "style.css").exists()
    assert (site / "script.js").exists()
