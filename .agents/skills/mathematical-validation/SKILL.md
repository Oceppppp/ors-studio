---
name: mathematical-validation
description: Design independent numerical tests and validation invariants for ORS optimization, forecasting, inventory, statistics, network, queueing, and simulation models.
---
# Mathematical Validation

## Procedure
1. Write the mathematical model in notation and plain language.
2. Define assumptions, units, variable domains, objective sense, tolerances, and rounding policy.
3. Construct a small hand-solvable benchmark with expected intermediate and final results.
4. Construct edge cases: zero values, negative values where permitted, infeasible, unbounded, degenerate, missing inputs, and limits.
5. Add invariant/property tests such as flow conservation, supply-demand balance, assignment uniqueness, probability normalization, inventory balance, precedence, and feasibility.
6. Compare a sample against a second independent method or external benchmark.
7. Test reproducibility for stochastic algorithms using fixed seeds.
8. Record solver/library/version and numerical tolerance in test metadata.
9. Separate solver status from business interpretation.
10. Document any heuristic or approximation and its limitations.

## Output
A validation note with equations, expected values, test IDs, tolerances, independent check, and known limitations.
