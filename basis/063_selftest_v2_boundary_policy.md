# 063 SelfTest v2 Boundary Policy

## Conclusion

Boundary checks must distinguish prohibited execution from textual discussion of prohibited execution.

## Valid Mentions

Documents may mention prohibited actions to define boundaries, for example:

- auto posting is prohibited
- runtime implementation remains out of scope
- platform API integration requires approval

## Invalid Mentions

Documents may not introduce execution code or approvals that bypass the boundary.

## Rule

SelfTest should fail only when a boundary is operationally violated, not when governance text describes the boundary.
