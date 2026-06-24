# 021 Asset Risk Policy

## Conclusion

Canonical Assets must expose risks before reuse so ACIP can preserve robustness, brand safety, and operational reliability.

## Risk Categories

- Policy Risk
- Legal / Compliance Risk
- Brand Risk
- Operational Risk
- Strategic Risk
- Maintenance Risk
- Source Drift Risk
- Derivative Drift Risk
- Revenue Misalignment Risk

## Risk Levels

| Level | Meaning |
|---|---|
| low | Safe for normal reuse |
| medium | Reuse requires review |
| high | Human approval required before reuse |

## Risk Rules

- Repository overrides conversation.
- Risk notes must travel with derived outputs.
- High-risk assets require Human approval.
- Approval bypass is prohibited.
- Silent risk downgrades are prohibited.
- Runtime implementation remains out of scope.

## Escalation

Escalate to ADR when risk acceptance affects architecture, operating policy, or long-term governance.
