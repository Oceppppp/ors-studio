from __future__ import annotations

from .modules import assignment, decision_analysis, finance, forecasting, game_theory, inventory, markov, mrp, networks, operations, optimization, project_management, quality, simulation, statistics, transportation, waiting_lines

MODULES = [
    {"key":"aggregate_planning","name":"Aggregate Planning","category":"Production Management","description":"Plan regular/overtime production, inventory, and backlog across periods using a linear cost model.","model":"aggregate_lp","readiness":"Implemented — scoped model","default_params":{"demand":[100,120,110],"regular_capacity":110,"overtime_capacity":20,"regular_unit_cost":10,"overtime_unit_cost":15,"holding_cost":1,"backlog_cost":20}},
    {"key":"assembly_line_balancing","name":"Assembly Line Balancing","category":"Production Management","description":"Assign precedence-constrained tasks to stations using the Largest Candidate Rule.","model":"largest_candidate","readiness":"Implemented — heuristic","default_params":{"cycle_time":10,"tasks":[{"id":"A","time":4,"predecessors":[]},{"id":"B","time":3,"predecessors":["A"]},{"id":"C","time":2,"predecessors":["A"]},{"id":"D","time":4,"predecessors":["B","C"]}]}},
    {"key":"assignment","name":"Assignment","category":"Optimization","description":"Minimize cost or maximize profit with one-to-one Hungarian assignment.","model":"hungarian","readiness":"Implemented","default_params":{"sense":"min","cost_matrix":[[9,2,7],[6,4,3],[5,8,1]]}},
    {"key":"breakeven","name":"Breakeven / Cost-Volume Analysis","category":"Financial & Decision","description":"Calculate contribution margin, break-even quantity/revenue, and target-profit volume.","model":"single_product_cv","readiness":"Implemented — single product","default_params":{"fixed_cost":50000,"variable_cost_per_unit":25,"selling_price_per_unit":50,"target_profit":20000}},
    {"key":"capital_investment","name":"Capital Investment","category":"Financial & Decision","description":"Calculate NPV, detected IRR roots, and simple/discounted payback.","model":"npv_irr_payback","readiness":"Implemented — standard cash flows","default_params":{"initial_investment":100000,"cash_flows":[30000,35000,40000,45000],"discount_rate":0.1}},
    {"key":"decision_analysis","name":"Decision Analysis","category":"Financial & Decision","description":"Evaluate payoff tables using maximax, maximin, minimax regret, EMV, EOL, and EVPI.","model":"payoff_criteria","readiness":"Implemented","default_params":{"payoffs":[[80,30,-20],[50,40,10],[20,50,40]],"probabilities":[0.3,0.5,0.2]}},
    {"key":"forecasting","name":"Forecasting","category":"Forecasting & Statistics","description":"Naive, moving average, weighted moving average, simple exponential smoothing, and linear trend forecasting.","model":"time_series","readiness":"Implemented — selected methods","default_params":{"method":"moving_average","values":[120,132,128,145,150,160,158,170],"window":3,"horizon":3}},
    {"key":"game_theory","name":"Game Theory","category":"Optimization","description":"Solve two-player zero-sum payoff matrices and find pure/mixed strategies.","model":"zero_sum_mixed_strategy","readiness":"Implemented — two-player zero-sum","default_params":{"payoff_matrix":[[3,1],[0,2]]}},
    {"key":"goal_programming","name":"Goal Programming","category":"Optimization","description":"Weighted goal programming with under- and over-achievement deviation variables.","model":"weighted_goals","readiness":"Implemented — weighted priorities","default_params":{"objective":[0,0],"goals":[{"coefficients":[1,1],"target":10},{"coefficients":[2,1],"target":14}],"weights":[1,2],"constraints":[{"coefficients":[1,0],"sense":"<=","rhs":8},{"coefficients":[0,1],"sense":"<=","rhs":8}]}},
    {"key":"integer_programming","name":"Integer & Mixed Integer Programming","category":"Optimization","description":"Solve integer, binary, and mixed-integer linear models with HiGHS.","model":"milp","readiness":"Implemented","default_params":{"sense":"max","objective":[3,5],"integrality":[1,1],"constraints":[{"coefficients":[1,0],"sense":"<=","rhs":4},{"coefficients":[0,2],"sense":"<=","rhs":12},{"coefficients":[3,2],"sense":"<=","rhs":18}]}},
    {"key":"inventory","name":"Inventory","category":"Production Management","description":"EOQ, EPQ, and reorder-point/safety-stock models.","model":"eoq_epq_rop","readiness":"Implemented — selected deterministic models","default_params":{"model":"eoq","annual_demand":12000,"ordering_cost":150,"holding_cost":4,"unit_cost":10}},
    {"key":"job_shop_scheduling","name":"Job Shop Scheduling","category":"Production Management","description":"Create a feasible greedy job/machine schedule and calculate makespan.","model":"greedy_job_shop","readiness":"Implemented — heuristic","default_params":{"jobs":[{"id":"J1","operations":[{"machine":"M1","duration":3},{"machine":"M2","duration":2}]},{"id":"J2","operations":[{"machine":"M2","duration":2},{"machine":"M1","duration":4}]}]}},
    {"key":"layout","name":"Layout / Operations Layout","category":"Production Management","description":"Evaluate facility flow-distance using Manhattan or Euclidean department-center distances.","model":"load_distance","readiness":"Implemented — evaluation model","default_params":{"distance":"manhattan","departments":[{"id":"A","x":0,"y":0},{"id":"B","x":10,"y":0},{"id":"C","x":10,"y":5}],"flows":[{"from":"A","to":"B","flow":100},{"from":"B","to":"C","flow":60}]}},
    {"key":"learning_curves","name":"Learning Curves","category":"Production Management","description":"Estimate unit-time or cumulative-average learning curves.","model":"wright_learning","readiness":"Implemented — Wright models","default_params":{"first_unit_time":10,"learning_rate":0.8,"units":10,"basis":"unit"}},
    {"key":"linear_programming","name":"Linear Programming","category":"Optimization","description":"Solve continuous LP models with min/max objectives, variable bounds, slacks, and solver marginals.","model":"continuous_lp","readiness":"Implemented","default_params":{"sense":"max","objective":[3,5],"constraints":[{"coefficients":[1,0],"sense":"<=","rhs":4},{"coefficients":[0,2],"sense":"<=","rhs":12},{"coefficients":[3,2],"sense":"<=","rhs":18}],"bounds":[[0,None],[0,None]]}},
    {"key":"location","name":"Location","category":"Production Management","description":"Calculate a weighted center-of-gravity candidate location.","model":"center_of_gravity","readiness":"Implemented — center of gravity","default_params":{"points":[{"name":"A","x":10,"y":20,"weight":100},{"name":"B","x":40,"y":10,"weight":200},{"name":"C","x":25,"y":50,"weight":150}]}},
    {"key":"lot_sizing","name":"Lot Sizing","category":"Production Management","description":"Solve deterministic uncapacitated dynamic lot sizing with Wagner–Whitin dynamic programming.","model":"wagner_whitin","readiness":"Implemented — dynamic lot sizing","default_params":{"demand":[50,40,60,30],"setup_cost":100,"holding_cost":2}},
    {"key":"markov_analysis","name":"Markov Analysis","category":"Forecasting & Statistics","description":"Calculate finite-step state distributions and a stationary-distribution estimate.","model":"transition_matrix","readiness":"Implemented — finite-state chain","default_params":{"transition_matrix":[[0.8,0.2],[0.3,0.7]],"initial_state":[1,0],"periods":5}},
    {"key":"mrp","name":"Material Requirements Planning","category":"Production Management","description":"Perform time-phased BOM explosion, inventory netting, and LFL/FOQ lot sizing.","model":"bom_explosion","readiness":"Implemented — LFL/FOQ","default_params":{"mps":{"PARENT":[0,50,40,30]},"bom":{"PARENT":[{"item":"COMP-A","quantity":2},{"item":"COMP-B","quantity":1}]} ,"inventory":{"COMP-A":20,"COMP-B":0},"lead_times":{"PARENT":1,"COMP-A":1,"COMP-B":2}}},
    {"key":"networks","name":"Networks","category":"Optimization","description":"Shortest path (Dijkstra), minimum spanning tree (Kruskal), or maximum flow (Edmonds–Karp).","model":"graph_algorithms","readiness":"Implemented — three core algorithms","default_params":{"model":"shortest_path","nodes":["A","B","C","D"],"edges":[{"from":"A","to":"B","cost":2,"capacity":5},{"from":"A","to":"C","cost":5,"capacity":4},{"from":"B","to":"C","cost":1,"capacity":3},{"from":"B","to":"D","cost":4,"capacity":3},{"from":"C","to":"D","cost":2,"capacity":6}],"source":"A","target":"D","sink":"D"}},
    {"key":"productivity","name":"Productivity","category":"Production Management","description":"Calculate partial and multifactor productivity ratios.","model":"productivity_ratios","readiness":"Implemented","default_params":{"output":1000,"inputs":{"labor_hours":200,"material_kg":500,"machine_hours":50}}},
    {"key":"project_management","name":"Project Management (PERT/CPM)","category":"Project Management","description":"Calculate critical path, early/late dates, slack, and PERT expected durations/variance.","model":"cpm_pert","readiness":"Implemented — CPM and PERT","default_params":{"method":"cpm","activities":[{"id":"A","duration":3,"predecessors":[]},{"id":"B","duration":2,"predecessors":["A"]},{"id":"C","duration":4,"predecessors":["A"]},{"id":"D","duration":2,"predecessors":["B","C"]}]}},
    {"key":"quality_control","name":"Quality Control","category":"Forecasting & Statistics","description":"X-bar/R charts for constant subgroup size and p charts for varying sample size.","model":"control_charts","readiness":"Implemented — selected control charts","default_params":{"model":"xbar_r","subgroups":[[10,11,9,10,12],[11,10,12,10,11],[9,10,10,11,10],[12,13,11,12,10]]}},
    {"key":"reliability","name":"Reliability","category":"Production Management","description":"Calculate independent component series or parallel system reliability.","model":"series_parallel","readiness":"Implemented — independent components","default_params":{"configuration":"series","components":[0.95,0.98,0.99]}},
    {"key":"simulation","name":"Simulation","category":"Forecasting & Statistics","description":"Reproducible Monte Carlo simulation for normal, uniform, triangular, and Poisson distributions.","model":"monte_carlo","readiness":"Implemented — Monte Carlo distributions","default_params":{"distribution":"normal","runs":10000,"seed":42,"mean":100,"sd":15}},
    {"key":"statistics","name":"Statistics","category":"Forecasting & Statistics","description":"Descriptive statistics including dispersion, quartiles, skewness, and excess kurtosis.","model":"descriptive_statistics","readiness":"Implemented — descriptive statistics","default_params":{"values":[12,15,14,10,18,20,17,16,13,15]}},
    {"key":"transportation","name":"Transportation","category":"Optimization","description":"Initial solutions by Northwest Corner, Least Cost, VAM, or LP-optimal transportation allocation.","model":"transportation_lp","readiness":"Implemented — initial and optimal","default_params":{"method":"optimal","costs":[[8,6,10],[9,12,13],[14,9,16]],"supply":[20,30,25],"demand":[10,35,30]}},
    {"key":"waiting_lines","name":"Waiting Lines","category":"Production Management","description":"M/M/1 and M/M/c steady-state queueing performance measures.","model":"mm1_mmc","readiness":"Implemented — M/M/1 and M/M/c","default_params":{"model":"mm1","arrival_rate":2,"service_rate":3}},
    {"key":"work_measurement","name":"Work Measurement","category":"Production Management","description":"Calculate normal/standard time and estimated sample size from time-study observations.","model":"time_study","readiness":"Implemented — time study","default_params":{"observed_times":[1.2,1.1,1.25,1.18,1.22,1.16,1.19,1.21],"performance_rating":1.05,"allowance":0.12,"relative_accuracy":0.05}}
]

MODULE_MAP={m["key"]:m for m in MODULES}


def run_module(module_key: str, params: dict) -> dict:
    if module_key not in MODULE_MAP:
        raise ValueError(f"Unknown module: {module_key}")
    if not isinstance(params, dict):
        raise ValueError("parameters must be a JSON object")
    if module_key=="aggregate_planning": return operations.aggregate_planning(params)
    if module_key=="assembly_line_balancing": return operations.assembly_line_balance(params["tasks"],params["cycle_time"],params.get("rule","largest_candidate"))
    if module_key=="assignment": return assignment.solve_assignment(params["cost_matrix"],params.get("sense","min"))
    if module_key=="breakeven": return finance.solve_breakeven(params["fixed_cost"],params["variable_cost_per_unit"],params["selling_price_per_unit"],params.get("target_profit",0))
    if module_key=="capital_investment": return finance.solve_capital_investment(params["initial_investment"],params["cash_flows"],params["discount_rate"])
    if module_key=="decision_analysis": return decision_analysis.solve_decision_analysis(params["payoffs"],params.get("probabilities"))
    if module_key=="forecasting": return forecasting.run(params)
    if module_key=="game_theory": return game_theory.solve_zero_sum(params["payoff_matrix"])
    if module_key=="goal_programming": return optimization.solve_goal_programming(params["objective"],params["goals"],params.get("constraints"),params.get("weights"))
    if module_key=="integer_programming": return optimization.solve_integer_program(params["objective"],params["constraints"],params.get("integrality"),params.get("sense","min"),params.get("bounds"))
    if module_key=="inventory": return inventory.solve_inventory(params)
    if module_key=="job_shop_scheduling": return operations.schedule_job_shop(params["jobs"])
    if module_key=="layout": return operations.evaluate_layout(params["departments"],params["flows"],params.get("distance","manhattan"))
    if module_key=="learning_curves": return operations.learning_curve(params["first_unit_time"],params["learning_rate"],params["units"],params.get("basis","unit"))
    if module_key=="linear_programming": return optimization.solve_linear_program(params["objective"],params["constraints"],params.get("sense","min"),params.get("bounds"))
    if module_key=="location": return operations.center_of_gravity(params["points"])
    if module_key=="lot_sizing": return operations.solve_lot_sizing(params["demand"],params["setup_cost"],params["holding_cost"])
    if module_key=="markov_analysis": return markov.solve_markov(params["transition_matrix"],params["initial_state"],params.get("periods",1))
    if module_key=="mrp": return mrp.solve_mrp(params["mps"],params.get("bom",{}),params.get("inventory"),params.get("scheduled_receipts"),params.get("lead_times"),params.get("lot_sizes"))
    if module_key=="networks":
        model=params.get("model","shortest_path")
        if model=="shortest_path":return networks.shortest_path(params["nodes"],params["edges"],params["source"],params["target"])
        if model=="minimum_spanning_tree":return networks.minimum_spanning_tree(params["nodes"],params["edges"])
        if model=="maximum_flow":return networks.maximum_flow(params["nodes"],params["edges"],params["source"],params["sink"])
        raise ValueError("networks model must be shortest_path, minimum_spanning_tree, or maximum_flow")
    if module_key=="productivity": return operations.productivity(params["output"],params["inputs"])
    if module_key=="project_management":
        if params.get("method","cpm")=="pert":return project_management.solve_pert(params["activities"])
        return project_management.solve_cpm(params["activities"])
    if module_key=="quality_control":
        if params.get("model","xbar_r")=="p_chart":return quality.p_chart(params["defectives"],params["sample_sizes"],params.get("sigma",3))
        return quality.xbar_r_chart(params["subgroups"],params.get("A2"),params.get("D3"),params.get("D4"))
    if module_key=="reliability": return operations.reliability(params)
    if module_key=="simulation": return simulation.monte_carlo(params)
    if module_key=="statistics": return statistics.describe(params["values"])
    if module_key=="transportation": return transportation.solve_transportation(params["costs"],params["supply"],params["demand"],params.get("method","vogel"))
    if module_key=="waiting_lines":
        if params.get("model","mm1")=="mmc":return waiting_lines.solve_mmc(params["arrival_rate"],params["service_rate"],params["servers"])
        return waiting_lines.solve_mm1(params["arrival_rate"],params["service_rate"])
    if module_key=="work_measurement": return operations.work_measurement(params["observed_times"],params.get("performance_rating",1),params.get("allowance",0),params.get("confidence_z",1.96),params.get("relative_accuracy",.05))
    raise ValueError(f"No solver registered for module: {module_key}")
