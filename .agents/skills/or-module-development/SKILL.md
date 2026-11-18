---
name: or-module-development
description: Implement an Operations Research module in ORS using the common module contract, typed schemas, validated solvers, and isolated tests.
---
# OR Module Development

## Procedure
1. Read the module row and open questions in `docs/MODULE_CATALOG.md` and applicable requirements in `docs/SRS.md`.
2. Confirm model variants, assumptions, units, variable domains, constraints, objective sense, and expected outputs. If parity evidence is missing, mark assumptions explicitly.
3. Define stable `module_key` and `model_key`; add typed input and output schemas.
4. Implement structural validation separately from mathematical solving.
5. Select a solver/algorithm appropriate to the model. Wrap third-party solvers behind an adapter.
6. Normalize solver statuses and preserve raw diagnostics/version metadata.
7. Add golden tests with independent expected results, plus infeasible/boundary cases.
8. Add module registration and API schema exposure.
9. Add UI form metadata, result presentation, and export mapping only after backend contract is stable.
10. Update catalog readiness only when every completion rule passes.

## Guardrails
- Never fake “optimal” when the solver reports feasible/time-limit only.
- Never fabricate iteration logs or sensitivity data.
- Never compare results that do not share comparable units, objective, horizon, and assumptions.
- Avoid importing a different module's private files; use shared contracts or services.
