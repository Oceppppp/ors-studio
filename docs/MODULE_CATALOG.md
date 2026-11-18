# ORS Module Catalog & Parity Register

**Status:** baseline register v0.1.0. This document is intentionally explicit about what is confirmed and what still needs version-specific verification.

## Baseline modules

The 29 modules below follow the chapter/module list in the reference POM-QM for Windows manual. Module labels may vary by textbook edition and software build. `Implemented` must only be used after code, tests, and acceptance criteria pass.

| Key | Display name | Model families to scope | Required validation evidence | Initial readiness |
|---|---|---|---|---|
| `aggregate_planning` | Aggregate Planning | Aggregate production plans; workforce/inventory/shortage cost; supported formulations | Demand/capacity balance; cost reconciliation; feasible/infeasible cases | Planned |
| `assembly_line_balancing` | Assembly Line Balancing | Precedence-constrained station assignment; cycle time; heuristic rules | Precedence respected; every task assigned once; station time <= cycle time | Planned |
| `assignment` | Assignment | Min-cost/max-profit; balanced/unbalanced; forbidden assignments | One-to-one assignment; objective independently recalculated | Planned |
| `breakeven` | Breakeven / Cost-Volume Analysis | Break-even quantity/value; target profit; contribution margin | Algebraic cross-check at BEP and target profit | Planned |
| `capital_investment` | Capital Investment | NPV; IRR; payback variants subject to specification | Cash-flow timeline, discount convention, multiple/no IRR cases | Planned |
| `decision_analysis` | Decision Analysis | Payoff table; decision criteria; EMV/EOL/EVPI; decision tree | Probability sum, payoff arithmetic, criterion direction | Planned |
| `forecasting` | Forecasting | Naive; MA; WMA; exponential smoothing; trend/regression; other methods after parity audit | Chronological split; no leakage; error metric consistency; denominator handling | Planned |
| `game_theory` | Game Theory | Two-player payoff; pure/mixed strategies; dominance where supported | Payoff orientation; equilibrium verification; probability sum | Planned |
| `goal_programming` | Goal Programming | Weighted/preemptive goals; positive/negative deviations | Goal balance equations; priority order; objective reconciliation | Planned |
| `integer_programming` | Integer & Mixed Integer Programming | Integer/binary/mixed linear models | Integrality; feasibility; bounds/gap; optimality status | Planned |
| `inventory` | Inventory | EOQ/EPQ; reorder point; safety stock; quantity discount; single-period variants | Demand/lead-time units, assumptions, inventory cost arithmetic | Planned |
| `job_shop_scheduling` | Job Shop Scheduling | Sequencing/scheduling models and variants verified per reference | Machine/job precedence; no overlap; makespan recomputation | Planned |
| `layout` | Layout / Operations Layout | Process/flexible-flow layout models | Distance/flow calculations; area/constraint validation | Planned |
| `learning_curves` | Learning Curves | Unit-time and cumulative-average model forms | Learning rate domain; unit/cumulative basis; rounding rules | Planned |
| `linear_programming` | Linear Programming | Graphical (2 variables); simplex/HiGHS solve; sensitivity where supported | Feasibility, objective, dual/slack consistency, degeneracy | Planned |
| `location` | Location | Center-of-gravity and location models verified per edition | Coordinate units, weights/demand, distance assumptions | Planned |
| `lot_sizing` | Lot Sizing | Static/dynamic lot-size models verified per edition | Inventory balance, setup/holding cost reconciliation | Planned |
| `markov_analysis` | Markov Analysis | Transition matrix; finite-step; stationary/steady-state distribution | Non-negative probabilities; row/column convention; normalization | Planned |
| `mrp` | Material Requirements Planning | BOM explosion; MPS; netting; lead-time offset; lot rules | BOM acyclic; quantities, lead time, scheduled receipts reconciled | Planned |
| `networks` | Networks | Shortest path; minimum spanning tree; maximum flow | Path validity; tree edge count/connectivity; flow conservation/capacity | Planned |
| `productivity` | Productivity | Partial and multifactor productivity | Unit consistency; ratio/index calculations | Planned |
| `project_management` | Project Management (PERT/CPM) | CPM deterministic; PERT three-time estimates | Precedence DAG; forward/backward pass; critical path recalculation | Planned |
| `quality_control` | Quality Control | Control charts and quality models verified per edition | Correct chart selection; limits; subgroup assumptions; signal rules | Planned |
| `reliability` | Reliability | Series/parallel and supported reliability distributions | Probability bounds; configuration; independence assumptions | Planned |
| `simulation` | Simulation | Monte Carlo and supported discrete-event models | Seed reproducibility; run count; confidence interval; event logic | Planned |
| `statistics` | Statistics | Descriptive statistics; distributions/probability models; supported inferential methods | Sample/population conventions; missing values; numerical checks | Planned |
| `transportation` | Transportation | Northwest Corner; Least Cost; VAM; MODI/stepping-stone as specified | Supply/demand balance; feasibility; optimality check | Planned |
| `waiting_lines` | Waiting Lines | Queueing model families verified per edition | Stability conditions; units; model assumptions and equations | Planned |
| `work_measurement` | Work Measurement | Time study; sample size for time study; work sampling sample size | Rating/allowance conventions; confidence/precision calculations | Planned |

## Version-variant candidates

| Candidate | Reason | Decision needed |
|---|---|---|
| Factor Rating | Appears in some POM-QM module menus/editions but not in the 29-module chapter list used as this baseline. | Confirm whether it is present in the installed version and include as module #30 if required. |
| Alternative names/submodels | POM vs QM labels and textbook-specific naming can differ. | Capture menu screenshots and examples from the exact installed version. |

## Model readiness rules

A model may be marked **Implemented** only when all of these are true:

1. Input and output schema documented.
2. Units, assumptions, limits, and model variants documented.
3. Validator handles invalid and boundary inputs.
4. Solver/algorithm selected and version recorded.
5. Golden tests exist with independently verified expected results.
6. Edge cases are tested.
7. UI form, result view, and export representation exist.
8. At least one end-to-end workflow passes.
9. Known limitations are displayed in UI/help.

## Required parity evidence from the target POM-QM build

For each module/model, collect:

- software version/build information;
- exact menu label and submodel names;
- a representative sample input;
- selected method/options;
- expected output and rounding;
- any trace/iteration report available;
- known limits (maximum rows, variables, tasks, nodes, periods).

Do not use screenshots alone as mathematical validation. Build independent benchmark cases and calculate expected values separately.
