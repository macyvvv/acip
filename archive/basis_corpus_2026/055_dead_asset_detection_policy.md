# 055 Dead Asset Detection Policy

## Conclusion

Dead documents reduce maintainability and should be detected mechanically.

## Dead Document Signals

- markdown document has no inbound reference
- document is outside known directories
- document lacks title
- document lacks repository rule or ownership boundary where required
- document belongs to old governance but is not referenced by index, ADR, WBS, README, or validation

## Rule

Dead documents are not automatically deleted. They are surfaced for review.
