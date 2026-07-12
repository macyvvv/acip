# 059 Duplicate Detection Policy

## Conclusion

Duplicate governance documents create ambiguity and should be detected before they become operating conflicts.

## Duplicate Signals

- identical H1 titles
- near-identical filename stems
- repeated ADR numbers
- repeated WBS numbers
- repeated workflow names
- repeated issue template names

## Rule

Duplicates fail only when they create canonical ambiguity; otherwise they are warnings.
