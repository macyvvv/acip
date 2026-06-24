# Relationship Model

## Conclusion

Asset relationships must be explicit to support reuse, revision, and drift control.

## Relationship Types

- parent_of
- derived_from
- supersedes
- superseded_by
- related_to
- depends_on
- blocks
- duplicates
- replaces
- deprecated_by
- supports
- contradicts

## Required Relationship Fields

- source_id
- relationship_type
- target_id
- reason
- created_at
- reviewer
- status

## Rules

- Derived outputs must reference source asset id.
- Supersession must preserve prior reasoning.
- Contradictions should escalate to review or ADR.
- Repository overrides conversation.
