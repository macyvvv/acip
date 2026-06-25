# EP-0104 Implementation Spec

## Conclusion

Implement Executable Specification Foundation so EPs can be represented as machine-readable contracts.

## Objective

Create a lightweight YAML-based EP contract format and validation scripts that allow workers to consume structured EP instructions from the repository.

## Scope

Codex must add:

- EP contract JSON schema
- EP contract YAML template
- EP-0104 sample contract
- EP contract validator script
- active contract loader script
- EP-0104 validation script
- GitHub Actions workflow
- README

## Constraints

- Repository remains the SSOT.
- Markdown remains useful documentation but YAML is the executable contract.
- Do not remove existing Markdown specs.
- Do not introduce new runtime execution.
- Do not introduce new external service mutation.
- Do not require secrets.
- Keep implementation dependency-light.

## Validation

Primary:

```bash
python scripts/validate_ep_0104.py
```

Regression:

```bash
python scripts/validate_ep_0103.py
python scripts/validate_ep_0102.py
python scripts/validate_ep_0101.py
python scripts/validate_ep_0100.py
```
