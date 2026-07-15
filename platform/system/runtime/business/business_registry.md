# BUSINESS_REGISTRY

## Summary
- Business count: 6
- Active: 2
- Greenfield: 4
- Dormant: 0
- Drifted (active but expected path missing): none

## Businesses
- `kabukicho_survival_map` (active): Kabukicho Survival Map
  - content_root: businesses/kabukicho_survival_map/app (exists=true)
  - product_code_path: businesses/kabukicho_survival_map/app (exists=true)
  - tracking_issue_numbers: [33, 34, 36]
  - notes: Location/survival guide product for Kabukicho. Fixed 2026-07-14: previously pointed at kabukicho_survival_map_mvp (an earlier, much smaller, superseded prototype) -- see CLAUDE.md's explicit warning not to confuse the two. This is the real, from-scratch app.
- `somia` (active): Somia
  - content_root: businesses/somia/content (exists=true)
  - product_code_path: platform/system/platform/scripts/somia (exists=true)
  - tracking_issue_numbers: [45, 46]
  - notes: AI character media / video content business. Image/video generation roles require paid vendor APIs (fal.ai/Kling).
- `music_platform` (greenfield): Music Platform
  - content_root: None (exists=false)
  - product_code_path: None (exists=false)
  - tracking_issue_numbers: []
  - historical_issue_numbers: [32]
  - notes: Was PRODUCT-0002 (issue #32), closed and code deleted. Revived as a greenfield business by explicit operator decision. Likely needs paid audio-generation APIs eventually.
- `text_syndicate` (greenfield): Text Syndicate
  - content_root: None (exists=false)
  - product_code_path: None (exists=false)
  - tracking_issue_numbers: []
  - notes: Provisional slug. Text-only content for Twitter/Threads/note.com, monetized via impressions and affiliate links. No existing code; zero external generation cost, so this is the platform pilot business.
- `dreamcore_video` (greenfield): DreamCore Video
  - content_root: businesses/dreamcore_video/content (exists=true)
  - product_code_path: None (exists=false)
  - tracking_issue_numbers: []
  - notes: DreamCore系（リミナルスペース・超現実的映像）の動画コンテンツ事業。先駆者多数のレッドオーシャンだが、普遍的に需要がある情報であるためレッドオーシャン戦略が有効と判断。品質と世界観で差別化。映像生成にはpaid API（fal.ai/Kling等）が必要になる見込み。
- `physics_math_visualization` (greenfield): Physics & Math Visualization
  - content_root: businesses/physics_math_visualization/content (exists=true)
  - product_code_path: None (exists=false)
  - tracking_issue_numbers: []
  - notes: 物理学・数学の定理のビジュアライゼーション動画事業。レッドオーシャンだが普遍的需要あり。既存の競合コンテンツは原理原則の破綻や納得感の薄さが目立つため、高品質・原理原則に忠実な制作で上位に立てる余地がある。3b1b系の表現力+学術的正確性が差別化軸。
