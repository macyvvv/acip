import os
import glob
import re

def generate_dc_shorts(filename, content):
    # DreamCore用ショート
    title_match = re.search(r'# (DC-\d+:.+)', content)
    title = title_match.group(1) if title_match else os.path.basename(filename)
    
    # ファイル名やコンテンツから特定のビジュアル要素を推測してカスタマイズ
    concept_match = re.search(r'## コンセプト\s*(.*?)\s*##', content, re.DOTALL)
    concept = concept_match.group(1).strip() if concept_match else ""
    
    shorts_section = f"""
---

## 1分版ショート構成 (Shorts/TikTok)

### タイムライン
- **0:00 - 0:15**: 視覚的フック。映像の冒頭から最も奇妙で美しいリミナルスペースの光景を提示。足音などの環境音のみで静寂を強調し、視聴者を引き込む。
- **0:15 - 0:45**: メカニズムの提示。説明的ナレーションは一切なし。カメラはゆっくりと前進または回転し、空間の歪みや「もう一人の自分」などの異変を客観的に映し出す（標本的扱い）。
- **0:45 - 1:00**: 無限ループ設計。映像のラストシーンが、冒頭の最初のカットと視覚的・音響的に完全に一致し、ループ再生した際に境界がわからないようにシームレスに接続して終了。
"""
    return shorts_section

def generate_pmv_shorts(filename, content):
    # 物理数学用ショート
    title_match = re.search(r'# (PMV-\d+:.+)', content)
    title = title_match.group(1) if title_match else os.path.basename(filename)
    
    concept_match = re.search(r'## 核心概念\s*(.*?)\s*##', content, re.DOTALL)
    concept = concept_match.group(1).strip() if concept_match else "数理概念の可視化"
    
    vis_match = re.search(r'## ビジュアライゼーション手法\s*(.*?)\s*##', content, re.DOTALL)
    vis = vis_match.group(1).strip() if vis_match else "3Dアニメーションによる変形表現"
    
    # 最初のビジュアル手法の1文をフックに使う
    vis_lines = [l.strip() for l in vis.split('\n') if l.strip() and not l.strip().startswith('|')]
    hook_desc = vis_lines[0] if vis_lines else "数理モデルの滑らかな3Dアニメーション"
    hook_desc = re.sub(r'^\d+\.\s*', '', hook_desc)
    
    shorts_section = f"""
---

## 1分版ショート構成 (Shorts/TikTok)

### タイムライン
- **0:00 - 0:15**: ビジュアルフック。数理メカニズムが最も美しく、劇的に動くシーンを冒頭に配置。{hook_desc[:80]}。音楽はアンビエント調のミニマルなテクノ。
- **0:15 - 0:45**: 標本的メカニズム。教育的・数式的な説明は極限まで削り、図形やベクトルがパラメータの変化に応じて有機的に変形し、伸縮し、貼り合わされていく純粋な「動きの標本」として表示。
- **0:45 - 1:00**: シームレスループ。変形が完了した図形が、元のシンプルな初期状態（正方形や初期ベクトルなど）へと逆再生のように滑らかに戻り、最初のフックへと境界線なくループする無限ループ構成。
"""
    return shorts_section

def process_directory(base_dir, is_pmv=True):
    pattern = os.path.join(base_dir, "**/*.md")
    for filepath in glob.glob(pattern, recursive=True):
        if "README" in filepath or "WBS" in filepath or "11_complex_zeta" in filepath:
            # 11_complex_zeta はすでに追記済みなのでスキップ
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # すでに追記されているかチェック
        if "1分版ショート構成" in content:
            continue
            
        if is_pmv:
            shorts = generate_pmv_shorts(filepath, content)
        else:
            shorts = generate_dc_shorts(filepath, content)
            
        new_content = content.rstrip() + "\n" + shorts
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Processed: {os.path.basename(filepath)}")

if __name__ == "__main__":
    # DreamCore
    process_directory("/Users/ariel/Documents/tools/acip/dreamcore_video/ideas", is_pmv=False)
    # PMV (01-10)
    process_directory("/Users/ariel/Documents/tools/acip/physics_math_visualization/ideas", is_pmv=True)
