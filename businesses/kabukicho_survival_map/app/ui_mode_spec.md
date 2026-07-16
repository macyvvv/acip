# UI Mode Specification

## Purpose

This document defines a low-risk UX enhancement for the Kabukicho Survival Map.
The goal is to improve first-action speed and practical usefulness without changing
the app's static-site architecture or narrowing the product into a single use case.

The app remains a broad survival map for Kabukicho. This specification adds a thin
"situation mode" layer on top of the existing category model.

## Problem Statement

The current app is functionally useful, but its first interaction is category-led,
not situation-led.

This causes three UX weaknesses:

1. A first-time visitor does not immediately understand what action is available.
2. The app exposes categories, but not the user's urgent context.
3. High-value scenarios such as staying out until morning are supported by the data,
   but not surfaced as a first-class entry point.

## Product Position

The product should not be repositioned as a "last train missed" app.

Instead:

- The core product remains a general-purpose Kabukicho survival utility.
- "Last train missed" becomes one optional situation mode.
- Other modes may coexist only when they change map search behavior without changing
   the underlying data model.

## Mode Qualification Rule

Not every useful idea should become a mode.

A mode is valid only when it changes all three of the following:

1. which POIs should be emphasized on the map
2. how those POIs should be sorted or grouped
3. what the user is trying to solve spatially right now

This excludes guidance-only ideas from the mode layer.

Examples:

- valid mode: `late_night_mode`
- valid mode: `toilet_now_mode`
- valid mode: `smoking_mode`
- not a mode: "first time in Kabukicho"
- not a mode: weather-only context such as a rain-specific preset

"First time in Kabukicho" may still exist later as onboarding, explanation, or a
guide layer, but not as a primary map mode.

## Design Principle

The app should answer two questions as quickly as possible:

1. What can I solve here right now?
2. Which nearby option best fits my current situation?

This requires a new entry layer above categories.

## Scope

In scope:

- Add situation-mode entry points near the top of the page.
- Keep the existing category navigation.
- Implement the initial high-appeal mode set:
   - `late_night_mode`
   - `toilet_now_mode`
   - `smoking_mode`
- Reorder and prioritize card metadata for decision speed.
- Make the behavior configurable in `app.js`.
- Preserve space for monetization, SEO/AIO, and future GA4 instrumentation.

Out of scope:

- Backend changes
- Data schema rewrite
- UGC features
- Personalized accounts
- AI recommendations
- Replacing categories with modes entirely

## Situation Mode Model

Situation modes are preset views built from existing categories and tags.

They are not new data entities.

Each mode must define:

- `id`
- `label`
- `description`
- `targetCategories`
- `requiredTags`
- `preferredTags`
- `sortStrategy`
- `emptyStateMessage`

## Initial High-Appeal Mode Set

### 1. Default / Explore Normally

- Purpose: preserve the current broad usage pattern.
- Behavior: normal category-based browsing.

### 2. Toilet Now Mode

- Purpose: solve the highest-immediacy utility need.
- Behavior: prioritize nearby toilet POIs and optimize for quickest decision.

### 3. Late Night Mode

- Purpose: help a user who needs to stay functional until morning.
- This is the only special mode explicitly approved at this stage.

### 4. Smoking Mode

- Purpose: quickly find a usable smoking option in Kabukicho.
- Behavior: prioritize smoking POIs and present practical constraints first.

## Deferred / Non-Mode Concepts

The following concepts are useful, but should not be modeled as primary map modes
at this stage:

- first-time visitor guidance
- rain-only context
- editorial neighborhood explanation

These belong to onboarding, help text, or future informational overlays.

## Late Night Mode Definition

### Intent

Late Night Mode is for users who missed the last train or otherwise need to stay in
Kabukicho until morning without breaking down operationally.

### Primary jobs to solve

- Find a place to stay or sit for hours
- Find a shower if available
- Find a toilet
- Find cash access if needed
- Find convenience support nearby
- Find luggage support if carrying bags

### Target categories

- `lodging`
- `toilet`
- `convenience`
- `atm`
- `coin_locker`

### Preferred tags / signals

If present in current data, Late Night Mode should prioritize entries with:

- `24h`
- `overnight_friendly`
- `shower_available`
- `large` or `suitcase_ok`
- higher freshness
- higher reliability

### Sorting behavior

Suggested sort priority for Late Night Mode:

1. distance from current location
2. overnight viability
3. 24h availability
4. freshness
5. reliability

This is not a ranking score exposed to users; it is an internal presentation order.

### Empty state

"朝まで向きの候補が見つかりませんでした。宿泊・ネットかコンビニを個別に確認してください。"

## Toilet Now Mode Definition

### Intent

Toilet Now Mode is for users with the highest immediacy need: finding the fastest
usable restroom near their current position.

### Primary jobs to solve

- Find the nearest usable toilet quickly
- Prefer free and accessible options when available
- Reduce wasted walking and hesitation

### Target categories

- `toilet`

### Preferred tags / signals

If present in current data, Toilet Now Mode should prioritize entries with:

- `24h`
- `free`
- `clean`
- `gender_separated`

### Negative signals

If present in current data, Toilet Now Mode should deprioritize entries with:

- `dirty`
- `long_wait`

### Sorting behavior

Suggested sort priority for Toilet Now Mode:

1. distance from current location
2. 24h availability
3. free usage
4. clean signal
5. freshness

### Empty state

"近くで使いやすいトイレが見つかりませんでした。通常のトイレ一覧に切り替えて探してください。"

## Smoking Mode Definition

### Intent

Smoking Mode is for users who want the quickest realistic path to a usable smoking
spot, not just a list of nominally designated places.

### Primary jobs to solve

- Find a smoking location that is actually usable right now
- Understand whether it is indoor, outdoor, crowded, hidden, or safety-sensitive
- Minimize walking to a place that turns out to be poor in practice

### Target categories

- `smoking`

### Preferred tags / signals

If present in current data, Smoking Mode should prioritize entries with:

- `indoor`
- `24h`
- `rain_ok`

### Negative signals

If present in current data, Smoking Mode should deprioritize entries with:

- `crowded`
- `hidden`
- `unsafe`

### Sorting behavior

Suggested sort priority for Smoking Mode:

1. distance from current location
2. indoor usability
3. 24h availability
4. rain-safe usability
5. freshness
6. reliability

### Empty state

"近くで使いやすい喫煙所が見つかりませんでした。通常の喫煙所一覧で候補を広げてください。"

## Mode-to-Map Relationship

Each approved mode must alter the map, not just the copy around it.

Required map effects:

- change which POIs are plotted or emphasized first
- change the ordering logic used for the associated list
- change what the user perceives as the recommended next place to inspect

Modes must not be treated as decorative landing-page tabs.

## Configuration Guidance

The current data model should be reused as much as possible.

Recommended configuration shape per mode:

- `targetCategories`: categories allowed in the mode
- `preferredTags`: positive ranking hints
- `negativeTags`: ranking penalties
- `sortStrategy`: ordered sort keys
- `headline`: short mode label shown in UI
- `emptyStateMessage`: mode-specific fallback copy

No new source JSON files should be required to launch the initial mode set.

## UX Structure

### Entry layer

Add a compact mode selector above the existing category bar.

Initial labels:

- `近くで探す`
- `今すぐトイレ`
- `終電後モード`
- `喫煙所`

Requirements:

- Must be visually distinct from category chips.
- Must not push the map too far below the fold.
- Must work on mobile without adding a second dense navigation row that feels crowded.

### Category layer

Categories remain visible and usable.

Mode selection changes the filtering/sorting context, but does not remove categories
from the product entirely.

### Card layer

Cards should prioritize decision metadata above descriptive copy.

Recommended top-of-card order:

1. distance
2. freshness
3. mode-relevant badges such as 24h / overnight / smoking availability when relevant
4. warning or gray-zone notice
5. description

### Empty states

Each mode must define a custom empty state and a fallback route back to standard
category browsing.

## Interaction Rules

1. Selecting a mode applies a preset context.
2. Selecting a category inside a mode narrows within that context.
3. Returning to default mode clears mode-specific constraints.
4. Existing manual tag filters remain available, but mode presets are applied first.

## Implementation Shape

No framework changes.

Implementation should remain inside the current static app surface:

- `index.html`: mode selector mount point
- `app.js`: mode configuration + filter/sort logic
- `style.css`: visual differentiation for mode controls and card hierarchy

Additional constraints for future operational work:

- mode and category UI must coexist with sponsored modules without obscuring primary actions
- the most valuable organic content must remain above low-priority informational blocks
- event boundaries should remain clear for later GA4 wiring

## Suggested JS Structure

Add a top-level constant similar to `CATEGORIES`:

- `MODES = [...]`

Add state:

- `activeMode`

Add helpers:

- `getModeDefinition(modeId)`
- `applyModeToPois(modeId, categoryId, pois)`
- `sortPoisForMode(modeId, pois)`
- `renderModeBar()`
- `scorePoiForMode(modeId, poi)` or equivalent ranking helper

The goal is not abstraction for its own sake. The goal is to make future mode tests
safe and local.

## Analytics / Operational Measurement

If analytics is enabled later, the minimum useful events are:

- mode selected
- category selected
- maps link clicked
- location permission granted / denied
- first interaction type

Primary questions:

1. Is Late Night Mode actually used?
2. Is Toilet Now Mode a faster first-action path than default category selection?
3. Does Smoking Mode increase facility-click intent for smoking POIs?
4. Does any mode reduce time-to-first-action?
5. Do users return to standard category browsing after entering a mode, or complete
   their task within the mode?

## Acceptance Criteria

1. The page still works fully as a static site.
2. Existing category browsing still works.
3. A user can enter Late Night Mode in one tap from the main screen.
4. A user can enter Toilet Now Mode and Smoking Mode in one tap from the main screen.
5. Late Night Mode surfaces relevant cross-category facilities without adding a new
   source JSON schema.
6. Card metadata becomes easier to scan for urgent decisions.
7. The feature remains maintainable within the current vanilla JS architecture.

## Rollout Plan

### Phase 1

- Add mode configuration
- Add mode bar UI
- Add Late Night Mode logic
- Add Toilet Now Mode logic
- Add Smoking Mode logic

### Phase 2

- Rework card hierarchy for faster scanning
- Improve visual distinction between mode chips and category chips

### Phase 3

- Add analytics event hooks if GA is configured
- Evaluate which mode deserves strongest default emphasis based on real use

## Non-Goals Clarification

This specification does not propose:

- converting the app into a nightlife editorial product
- focusing the entire product on missed-last-train users
- increasing animation or visual novelty for its own sake

The purpose is operational clarity, not decorative redesign.