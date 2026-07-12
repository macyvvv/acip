# 062 Policy Graph Policy

## Conclusion

Repository validation should model relationships between policies, ADRs, WBS, runbooks, contracts, workflows, and validation scripts.

## Graph Nodes

- policy
- ADR
- WBS
- runbook
- contract
- workflow
- validation script
- README
- registry
- catalog

## Graph Edges

- references
- validates
- governs
- implements
- supersedes
- archives
- depends_on

## Rule

Semantic graph warnings are advisory unless they identify broken links, duplicate canonical IDs, boundary violations, or missing required files.
