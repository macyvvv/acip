# BUSINESS_REGISTRY

## Summary
- Business count: 5
- Active: 2
- Greenfield: 3
- Dormant: 0
- Drifted (active but expected path missing): none

## Businesses
- `kabukicho_survival_map` (active): Kabukicho Survival Map
  - content_root: businesses/kabukicho_survival_map/app (exists=true)
  - product_code_path: businesses/kabukicho_survival_map/app (exists=true)
  - tracking_issue_numbers: [33, 34, 36]
  - notes: Location/survival guide product for Kabukicho. Fixed 2026-07-14: previously pointed at kabukicho_survival_map_mvp (an earlier, much smaller, superseded prototype) -- see CLAUDE.md's explicit warning not to confuse the two. This is the real, from-scratch app.
- `somia` (active): Somia
  - content_root: businesses/platform/somia/content (exists=true)
  - product_code_path: platform/system/scripts/somia (exists=true)
  - tracking_issue_numbers: [45, 46]
  - notes: AI character media / video content business. Image/video generation roles require paid vendor APIs (fal.ai/Kling).
- `music_platform` (greenfield): Music Platform
  - content_root: None (exists=false)
  - product_code_path: None (exists=false)
  - tracking_issue_numbers: []
  - historical_issue_numbers: [32]
  - notes: Was PRODUCT-0002 (issue #32), closed and code deleted. Revived as a greenfield business by explicit operator decision. Likely needs paid audio-generation APIs eventually.
- `text_syndicate` (greenfield): Text Syndicate
  - content_root: platform/system/runtime/business_agents/text_syndicate (exists=true)
  - product_code_path: None (exists=false)
  - tracking_issue_numbers: []
  - notes: Provisional slug. Text-only content for Twitter/Threads/note.com, monetized via impressions and affiliate links. No existing code; zero external generation cost, so this is the platform pilot business.
- `cf_gb_relative_system` (greenfield): CF/GB Relative System
  - content_root: businesses/cf_gb_relative_system/app (exists=true)
  - product_code_path: businesses/cf_gb_relative_system/app (exists=true)
  - tracking_issue_numbers: []
  - notes: Greenfield business registered for the Phase -1 enabling work. The app path is canonical; executable product code is introduced by the delivery-skeleton work package.
