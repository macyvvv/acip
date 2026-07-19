from pathlib import Path
import json
import shutil

def export_run(run_dir: Path) -> Path:
    generation = run_dir / "generation.jsonl"
    if not generation.exists():
        raise FileNotFoundError("generation.jsonl not found")
    out = run_dir / "export"
    images = out / "images"
    captions = out / "captions"
    images.mkdir(parents=True, exist_ok=True)
    captions.mkdir(parents=True, exist_ok=True)
    manifest = []
    for line in generation.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("status") != "generated":
            continue
        src = run_dir / row["image"]
        dst = images / src.name
        shutil.copy2(src, dst)
        caption = row["character_id"] + ", " + ", ".join(row["dimensions"].values())
        (captions / f"{src.stem}.txt").write_text(caption, encoding="utf-8")
        manifest.append({**row, "export_image": str(dst.relative_to(out))})
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
