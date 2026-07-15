# ISSUE_PORTFOLIO_ROADMAP

## Purpose
Define the canonical portfolio view for tracked repository work so operators can distinguish NOW, NEXT, LATER, and FROZEN instead of treating the queue as an undifferentiated backlog.

## Classification Rules
- `NOW`: one_shot_ready items that are safe, narrow, and currently actionable.
- `NEXT`: ready items that should follow NOW when the current one-shot scope is cleared.
- `LATER`: valid work, but not one_shot_ready under the current baseline.
- `FROZEN`: completed, archived, or historical foundation work excluded from the active approval flow.

## Portfolio Summary
- Issue count: 37
- NOW: 1
- NEXT: 0
- LATER: 5
- FROZEN: 31

## NOW
- Issue #41: PRODUCT-0004 Product Launch Follow-up (`product_incremental`, `one_shot_ready`) — Safe narrow product follow-up is the only current open issue that fits the one-shot baseline cleanly.

## NEXT

## LATER
- Issue #35: Approval Console MVP (`governance/operator`, `not_one_shot_ready`) — Operator tooling improves workflow visibility but is not itself a one-shot execution target.
  - Blocking reason: Approval console is operator-facing control-plane work, not a narrow product/content increment.
- Issue #37: Issue-Centric Operation Validation (`governance/operator`, `not_one_shot_ready`) — Operational validation is important but belongs after the product-facing one-shot workstream.
  - Blocking reason: Validation and operator guidance are control-plane work, not one-shot-ready issue execution.
- Issue #38: Main Protection and Branch/PR Workflow (`governance/operator`, `not_one_shot_ready`) — Main protection is governance work and should not flood the approval console.
  - Blocking reason: Branch protection is a repository governance concern, not a one-shot product increment.
- Issue #39: Main Push Protection Activation and Verification (`governance/operator`, `not_one_shot_ready`) — Hook activation and verification are still operator-process work rather than issue execution candidates.
  - Blocking reason: Local hook activation is a control-plane task and not a one-shot-ready issue candidate.
- Issue #40: Repository Validation Path Repair (`infra_foundation`, `not_one_shot_ready`) — Validation path repair is infrastructure hygiene, useful but not a current one-shot execution target.
  - Blocking reason: This is infrastructure maintenance, not a narrow product/content increment.

## FROZEN
- Issue #3: PACK-0003 Generated Artifact SSOT Pack (`infra_foundation`, `completed`) — Historical foundation pack already completed and recorded in pack execution docs.
- Issue #4: EP-0151 Generated Artifact SSOT Registry (`infra_foundation`, `completed`) — Child of PACK-0003; foundational artifact registry work is already complete.
- Issue #5: EP-0152 Repository Artifact Refresh (`infra_foundation`, `completed`) — Deterministic artifact refresh is historical foundation work.
- Issue #6: EP-0153 Validation Leaves Repository Clean (`governance/operator`, `completed`) — Validation hygiene is already encoded in the repository governance layer.
- Issue #7: EP-0154 Explicit Refresh Workflow (`governance/operator`, `completed`) — Refresh workflow is part of the existing deterministic artifact pipeline.
- Issue #8: EP-0155 Generated Artifact Refresh Validation (`infra_foundation`, `completed`) — Refresh validation is a completed support layer.
- Issue #9: PACK-0004 Agent Handshake Protocol (`governance/operator`, `archived`) — Handshake protocol is a historical governance layer and not active one-shot work.
- Issue #10: EP-0156 Completion Protocol (`governance/operator`, `archived`) — Completion protocol is already embedded in runtime artifacts.
- Issue #11: EP-0157 Repository Completion Marker (`governance/operator`, `archived`) — Completion marker is canonical historical infrastructure.
- Issue #12: EP-0158 ChatGPT Review Intake (`governance/operator`, `archived`) — Review intake already exists as a completed repository-native control plane layer.
- Issue #13: EP-0159 Issue Synchronizer (`infra_foundation`, `archived`) — Issue sync is historical foundation work and no longer active portfolio work.
- Issue #14: EP-0160 Handshake Validation (`governance/operator`, `archived`) — Handshake validation is a sealed governance layer.
- Issue #15: PACK-0005 Event Runtime (`infra_foundation`, `archived`) — Event runtime is historical infrastructure, not active one-shot work.
- Issue #16: EP-0161 Event Contract Validation (`infra_foundation`, `archived`) — Event contract validation is already part of the runtime baseline.
- Issue #17: EP-0162 Issue Event Intake (`infra_foundation`, `archived`) — Issue event intake is completed plumbing.
- Issue #18: EP-0163 Completion Marker Event Intake (`governance/operator`, `archived`) — Completion marker intake is already embedded in the repository workflow.
- Issue #19: EP-0166 Event Runtime Safety Gate (`governance/operator`, `archived`) — Safety gating for the event runtime is historical, not current portfolio work.
- Issue #22: PACK-0010 Planning OS (`governance/operator`, `archived`) — Planning OS is already the repository-native planning baseline.
- Issue #23: PACK-0011 Local Agent Supervisor Bridge (`governance/operator`, `archived`) — Supervisor bridge is an established operator/control-plane capability.
- Issue #24: PACK-0012 Work Planner (`governance/operator`, `archived`) — Work planner is already present and used by current runtime artifacts.
- Issue #25: PACK-0013 Repository OS v2 Release (`broad_architecture`, `archived`) — Release packaging for Repository OS v2 is historical and not active execution work.
- Issue #26: PACK-0014 First Product Launch System (`product_incremental`, `archived`) — First product launch system work is superseded by later product execution artifacts.
- Issue #27: PACK-0015 Local Execution Adapter (`infra_foundation`, `archived`) — Execution adapter work is completed infrastructure, not a current portfolio candidate.
- Issue #28: ACCEPTANCE-0001 Single Product Vertical Slice (`product_incremental`, `completed`) — Acceptance slice is complete and recorded by a standalone product execution record.
- Issue #29: Dynamic Codex Model Resolver (`infra_foundation`, `archived`) — Model resolution work is already present in runtime artifacts and tests.
- Issue #30: PRODUCT-0001 Product Launch Checklist (`product_incremental`, `completed`) — Product launch checklist is completed and has a canonical completion marker.
- Issue #31: CONTENT-0001 Content Draft Review (`content_incremental`, `completed`) — Content draft review already has a completion marker and should stay out of active approval flow.
- Issue #32: PRODUCT-0002 Product Launch Follow-up (`product_incremental`, `completed`) — Product launch follow-up is already completed and frozen.
- Issue #33: PRODUCT-0003 Kabukicho Survival Map MVP (UGC-ready) (`product_incremental`, `completed`) — Kabukicho MVP UGC-ready scope is already completed.
- Issue #34: PRODUCT-0003 Kabukicho Map Data Expansion (`product_incremental`, `completed`) — Kabukicho map data expansion is the current completed product-facing increment.
- Issue #36: PRODUCT-0004 Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities (`research_to_product`, `completed`) — Research-to-product handoff has already been validated end-to-end.

## Roadmap Notes
- Approval candidates are a strict subset of this roadmap, not the roadmap itself.
- Completed and archived issues remain visible for governance but must not re-enter approval candidate flow.
- Broad architecture and operator-control work stays out of the one-shot queue until explicitly promoted.

## Sources
- `system/runtime/github/open_issues.json`
- `system/runtime/issues/completed/`
- `system/runtime/work_planner/latest.json`
- `system/runtime/supervisor/latest.json`
- `system/runtime/repository_state/latest.json`
- `docs/current/AUTONOMOUS_OPERATIONAL_BASELINE.md`
- `docs/current/ISSUE_OPERATOR_QUICKSTART.md`
- `docs/current/ISSUE_CENTRIC_OPERATION.md`
- `docs/current/RESEARCH_TO_ISSUE_OPERATING_PROCEDURE.md`
