# ROOT_MIGRATION_SPLIT_PLAN

## Goal

運営基盤（repository operating system / governance / runtime）と事業プロジェクトを
物理レイアウト上で分離し、保守性と責務境界を明確化する。

## Source of Truth

- Business list: `platform/system/runtime/business/business_registry.md`
- Existing migration risk plan: `platform/system/runtime/root_hygiene/root_migration_split_plan.json`

## Current Business Scope (Registry Driven)

- Active
	- `kabukicho_survival_map`
	- `somia`
- Greenfield
	- `music_platform`
	- `text_syndicate`
	- `dreamcore_video`
	- `physics_math_visualization`

## Target Top-Level Separation

- `platform/`: 運営基盤・ガバナンス・共通ツール
- `businesses/`: 事業単位の実装・コンテンツ・事業固有運用

## Ideal Root Shape (Policy)

ルート直下は原則として次の3種類だけを許可する。

1. `platform/`
2. `businesses/`
3. 最小限の設定・メタファイル

### Keep At Root (Minimal Config/Meta)

- `.git/`
- `.github/`
- `.gitignore`
- `.env` / `.env.example`
- `README.md`
- `CLAUDE.md`
- `AGENTS.md` (historical)
- `VERSION`
- `requirements-dev.txt`
- `netlify.toml`
- `selftest.yml`

Temporary during migration:

- compatibility symlinks may remain at legacy root paths until all references are migrated.

上記以外の業務コード・運用コード・事業コンテンツは、最終的に `platform/` または `businesses/` 配下へ集約する。

### Root Cleanup Targets

- Platform sideへ集約: `platform/adr/`, `platform/baseline/`, `platform/basis/`, `platform/context/`, `platform/contracts/`, `platform/docs/`, `platform/specs/`, `platform/system/`, `platform/scripts/`, `platform/archive/`, `platform/knowledge/`, `platform/packs/`, `platform/wbs/`, `platform/app/`, `platform/inbox/`, `platform/releases/`, `platform/web/`, `platform/.platform/system/`, `platform/scratch/`
- Business side canonical targets: `businesses/dreamcore_video/content`, `businesses/physics_math_visualization/content`, `businesses/platform/somia/content`, `businesses/kabukicho_survival_map/app`

### Platform Target Contents

- `platform/system/`
- `platform/basis/`
- `platform/adr/`
- `platform/contracts/`
- `platform/specs/`
- `platform/docs/` (governance/runtime docs)
- `platform/scripts/`

### Businesses Target Contents

- `businesses/kabukicho_survival_map/`
- `businesses/platform/somia/`
- `businesses/music_platform/` (greenfield placeholder)
- `businesses/text_syndicate/` (greenfield placeholder)
- `businesses/dreamcore_video/`
- `businesses/physics_math_visualization/`

## Migration Policy

- First pass is non-breaking and additive (no destructive moves).
- Use a compatibility bridge (temporary symlink or redirect docs) during transition.
- Keep `business_registry.md` paths synchronized at each migration step.
- Apply approval gate for high-reference and runtime-coupled paths.

## Phased Execution

### Phase 1: Structural Bootstrap (Low Risk)

- Create `platform/` and `businesses/` as canonical containers.
- Add per-business placeholder README and ownership metadata.
- Add migration map document (`from -> to`) for each existing top-level path.

### Phase 2: Business Content Consolidation (Medium Risk)

- Move standalone business roots under `businesses/`.
	- `dreamcore_video -> businesses/dreamcore_video`
	- `physics_math_visualization -> businesses/physics_math_visualization`
	- `somia -> businesses/somia` (content root)
- Kabukicho product root moved to `businesses/kabukicho_survival_map/app` (temporary compatibility symlink retired 2026-07-16).
- Update references, WBS links, and runtime materialized docs.

Status note (2026-07-16):

- `dreamcore_video` moved to `businesses/dreamcore_video/content`
- `physics_math_visualization` moved to `businesses/physics_math_visualization/content`
- `somia` moved to `businesses/platform/somia/content`
- Kabukicho product root moved to `businesses/kabukicho_survival_map/app`
- compatibility symlink retired at legacy roots: `dreamcore_video`, `physics_math_visualization` (2026-07-16)
- compatibility symlink retired at legacy product path: `platform/app/products/kabukicho_survival_map` (2026-07-16)
- compatibility symlink retired at legacy root: `somia` (2026-07-16)

Compatibility note:

- legacy root symlink retired (2026-07-16): `somia` legacy root path removed
- legacy kabukicho product symlink retired (2026-07-16): legacy product location now removed
- platform first batch moved with compatibility symlinks:
	- `adr -> platform/adr`
	- `basis -> platform/basis`
	- `contracts -> platform/contracts`
	- `specs -> platform/specs`
- platform second batch moved with compatibility symlinks:
	- `baseline -> platform/baseline`
	- `context -> platform/context`
	- `docs -> platform/docs`
	- `scripts -> platform/scripts`
	- `archive -> platform/archive`
	- `knowledge -> platform/knowledge`
	- `packs -> platform/packs`
	- `wbs -> platform/wbs`
	- `system -> platform/system`
- additional platform moves with compatibility symlinks:
	- `app -> platform/app`
	- `inbox -> platform/inbox`
	- `releases -> platform/releases`
	- `web -> platform/web`
	- `.system -> platform/.system`
	- `scratch -> platform/scratch`

### Phase 3: Product Code Unification (Medium/High Risk)

- Unify business runtime/app code under `businesses/<slug>/` with clear sublayout.
- Introduce compatibility layer for legacy imports and scripts.
- Rewire CI and validation scripts to new roots.

### Phase 4: Platform Extraction (High Risk)

- Migrate operating-platform/system/governance assets to `platform/`.
- Retire legacy top-level paths after validation and rollback checkpoints.
- Enforce root whitelist (only `platform/`, `businesses/`, and minimal config/meta files).

## Success Criteria

- A new contributor can distinguish platform vs business at first glance.
- Every business has one canonical root under `businesses/`.
- `business_registry.md` points only to canonical roots.
- Selftest/validation scripts pass before and after each phase.
