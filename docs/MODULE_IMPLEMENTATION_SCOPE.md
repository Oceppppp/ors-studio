# ORS Module Implementation Scope — v0.4.0

This register describes the actual solver variants exposed by the current build. A module appearing in the navigation means that the stated variant is callable; it does **not** imply exact parity with every model, report, or option in every POM-QM release.

| Module | Working implementation in the current build | Important scope boundary |
|---|---|---|
| Aggregate Planning | Linear cost model with regular/overtime production, inventory and backlog | No hiring/layoff, subcontracting, or nonlinear workforce costs |
| Assembly Line Balancing | Largest Candidate Rule, precedence validation, station utilization | Heuristic; not a global optimum proof |
| Assignment | Hungarian algorithm, min/max, rectangular matrices | No explicit user-supplied forbidden-assignment mask or custom dummy penalty yet |
| Breakeven | Single-product contribution margin, BEP, target profit | No multi-product sales mix |
| Capital Investment | NPV, IRR root detection, simple and discounted payback | Period-end cash-flow convention; IRR sign-changing roots are searched numerically from −90% to 1,000%, so roots outside the range or without a sign change may be missed |
| Decision Analysis | Maximax, maximin, minimax regret, EMV, EOL, EVPI | Payoff table model; decision tree UI is not implemented |
| Forecasting | Naive, MA, WMA, simple exponential smoothing, linear trend | No seasonality decomposition/Holt-Winters in this release |
| Game Theory | Two-player zero-sum mixed strategy LP and saddle point | General-sum games and extensive-form games excluded |
| Goal Programming | Weighted deviation LP | Lexicographic/preemptive priority levels excluded |
| Integer Programming | SciPy/HiGHS MILP; integer/binary/semi-continuous variable domains | Solver-specific bounds/gap and advanced cuts are not exposed |
| Inventory | EOQ, EPQ, reorder point and normal-approximation safety stock | EOQ/EPQ require positive ordering/setup cost; quantity discounts and single-period newsvendor are not included |
| Job Shop Scheduling | Feasible greedy input-order operation schedule and makespan | Heuristic; not an optimal job-shop solver or full sequence optimizer |
| Layout | Load-distance evaluation with Manhattan or Euclidean distance | Layout generation/space constraints are not optimized |
| Learning Curves | Wright unit-time and cumulative-average models | Other learning-curve formulations excluded |
| Linear Programming | Continuous LP via SciPy HiGHS, min/max, bounds, slacks, marginals | Graphical corner visualization and full sensitivity ranges not included |
| Location | Weighted center of gravity | No discrete facility-location optimizer or road-network distance |
| Lot Sizing | Wagner–Whitin dynamic lot-size DP | No capacity constraint, quantity discounts, or stochastic demand |
| Markov Analysis | Finite-step transition and stationary-distribution estimate | Advanced absorbing/first-passage analysis not exposed |
| MRP | BOM explosion, netting, lead-time offset, LFL/FOQ | No capacity-constrained MRP or full ERP calendar integration |
| Networks | Dijkstra shortest path, Kruskal MST, Edmonds–Karp maximum flow | Min-cost flow and CPM network diagrams are separate modules |
| Productivity | Partial and multifactor productivity ratios | Index/price-adjusted productivity requires user-prepared comparable units |
| Project Management | Deterministic CPM and three-time-estimate PERT | Resource leveling and probabilistic completion-date simulation excluded; PERT variance is reported for one representative complete critical path if multiple paths tie |
| Quality Control | X-bar/R and p charts | Other chart families, capability indices and run-rule suites not included |
| Reliability | Independent component series and parallel systems | Standby, repairable systems, and lifetime distributions excluded |
| Simulation | Seeded Monte Carlo: normal, uniform, triangular, Poisson | No general discrete-event simulator in this release |
| Statistics | Descriptive statistics, quantiles, skewness, kurtosis | Inferential tests/regression diagnostics are not included in this module |
| Transportation | Northwest Corner, Least Cost, VAM initial solutions and LP-optimal transport | MODI/stepping-stone iteration trace not shown |
| Waiting Lines | M/M/1 and M/M/c steady-state measures | Finite capacity, finite population, priority, and non-exponential models excluded |
| Work Measurement | Time study normal/standard time and approximate sample size | Work-sampling proportion estimate is not included |

## Completion rule

A submodel is marked complete only after its documented variant has a solver, validation, test evidence, API exposure, UI example parameters, and displayed assumptions. This build passes the smoke test for the default example of each of the 29 module keys. It has not been certified against the full feature set of a particular installed POM-QM version because that version and its submodel screenshots/sample outputs have not been provided.
