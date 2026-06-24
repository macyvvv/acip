# 076 Review Gate Policy

## Conclusion

Review Gates convert execution output into decision-ready summaries for ChatGPT and Human.

## Review Gate Checks

- scope preserved
- current objective preserved
- validation executed
- runtime boundary preserved
- secret boundary preserved
- external action boundary preserved
- rollback available
- Human decision required or not required

## Rules

- Human receives only decision-ready summaries.
- Review preparation is not Human work.
- Repository overrides conversation.
