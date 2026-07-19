# System Specification — Frozen

## Inputs
- versioned character specification
- versioned sampling policy
- common generation policy
- reference images
- runtime configuration

## Outputs
- raw images
- per-image metadata
- review records
- accepted dataset
- captions
- manifest
- run report

## Completion
要求枚数の採択画像が揃い、必須bucketの最低数を満たし、manifest検証とexport検証が成功すること。

## Failure
API失敗、schema不整合、重複、必須metadata欠落、採択不足は失敗として明示し、resume可能な状態を保持する。
