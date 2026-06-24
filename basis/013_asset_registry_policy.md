# 013 Asset Registry Policy

## Conclusion

ACIP must maintain an Asset Registry so Canonical Assets can be located, audited, reused, revised, and deprecated without depending on chat memory or ad hoc file discovery.

## Purpose

The Asset Registry is the repository-governed index of Canonical Assets and their relationships.

It exists to provide:

- discoverability
- lifecycle visibility
- source traceability
- reuse control
- revision control
- ROI connection

## Registry Scope

The registry tracks:

- Canonical Assets
- derived Content Objects
- derived Media Objects
- Operational Assets
- deprecated assets

The registry does not track temporary notes, unreviewed drafts, chat transcripts, or external platform posts unless they have been converted into repository-governed assets.

## Required Registry Fields

Each registry entry must include:

- asset_id
- title
- asset_type
- lifecycle_status
- owner
- version
- source_path
- parent_asset_id
- derived_asset_ids
- related_adr
- related_wbs
- quality_gate_status
- reuse_status
- risk_level
- revenue_link
- last_reviewed

## Canonical Rule

Repository overrides conversation.

An asset is not discoverable as canonical unless it has a registry entry and merged source content.

## Done Condition

Asset Registry control is complete when required registry files, registry template, traceability map, validation script, and CI workflow exist and pass.
