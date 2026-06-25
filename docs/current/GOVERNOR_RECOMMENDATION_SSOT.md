# GOVERNOR_RECOMMENDATION_SSOT

Governor recommendations are persisted in `runtime/governor/governor_recommendations.json` as the repository recommendation source of truth.

## Rules

- recommendation version must be explicit
- runtime artifact is read before regenerating when present
- the repository governor may regenerate deterministically when the runtime artifact is missing or stale
