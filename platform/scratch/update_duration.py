import os
import glob
import re

def update_duration(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 想定尺の行を8分に置換（12分、15分、18分、20分、22分、25分など→8分）
    new_content = re.sub(
        r'(## 想定尺\s*\n)\d+分',
        r'\g<1>8分',
        content
    )

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    targets = glob.glob(
        "/Users/ariel/Documents/tools/acip/physics_math_visualization/ideas/**/*.md",
        recursive=True
    )
    updated = 0
    for fp in targets:
        if update_duration(fp):
            updated += 1
            print(f"Updated: {os.path.basename(fp)}")
    print(f"\nTotal updated: {updated}")

if __name__ == "__main__":
    main()
