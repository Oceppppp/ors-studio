from __future__ import annotations
import math
import numpy as np
from scipy.optimize import linprog
from .common import require, rounded


def aggregate_planning(params):
    demand=np.asarray(params["demand"],float); n=len(demand)
    require(demand.ndim==1 and n>0 and np.isfinite(demand).all() and (demand>=0).all(),"demand must be a non-empty finite non-negative sequence")
    reg_cap=np.broadcast_to(np.asarray(params.get("regular_capacity",float("inf")),float), (n,))
    ot_cap=np.broadcast_to(np.asarray(params.get("overtime_capacity",0),float),(n,))
    cr=float(params.get("regular_unit_cost",1)); co=float(params.get("overtime_unit_cost",cr*1.5)); ch=float(params.get("holding_cost",0)); cb=float(params.get("backlog_cost",100))
    require(not np.isnan(reg_cap).any() and not np.isnan(ot_cap).any() and (reg_cap>=0).all() and (ot_cap>=0).all(),"capacities must be non-negative and cannot be NaN")
    require(all(math.isfinite(v) and v>=0 for v in (cr,co,ch,cb)),"unit costs must be finite and non-negative")
    # Variables [regular production n, overtime production n, ending inventory n, ending backlog n]
    N=4*n;c=np.concatenate([np.full(n,cr),np.full(n,co),np.full(n,ch),np.full(n,cb)])
    Aeq=[];beq=[]
    for t in range(n):
        row=np.zeros(N);row[t]=1;row[n+t]=1;row[2*n+t]=-1;row[3*n+t]=1
        if t>0: row[2*n+t-1]=1;row[3*n+t-1]=-1
        Aeq.append(row);beq.append(demand[t])
    bounds=[(0,reg_cap[t]) for t in range(n)]+[(0,ot_cap[t]) for t in range(n)]+[(0,None)]*(2*n)
    r=linprog(c,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
    require(r.success,f"aggregate plan infeasible: {r.message}")
    x=r.x
    return {"periods":[{"period":t+1,"demand":demand[t],"regular_production":x[t],"overtime_production":x[n+t],"ending_inventory":x[2*n+t],"ending_backlog":x[3*n+t]} for t in range(n)],"total_cost":float(r.fun),"assumptions":["Linear aggregate plan with regular/overtime production, ending inventory and backlog.","No hiring, layoffs, subcontracting, workforce limits, or nonlinear costs are modeled."]}


def assembly_line_balance(tasks, cycle_time, rule="largest_candidate"):
    ct=float(cycle_time);require(math.isfinite(ct) and ct>0,"cycle_time must be finite and > 0")
    items={str(t["id"]):t for t in tasks};require(items and len(items)==len(tasks),"task IDs must be unique")
    times={k:float(v["time"]) for k,v in items.items()};require(all(math.isfinite(v) and v>0 and v<=ct for v in times.values()),"each task time must be finite, > 0, and not exceed cycle time")
    preds={k:set(map(str,v.get("predecessors",[]))) for k,v in items.items()}
    require(all(p in items for ps in preds.values() for p in ps),"unknown task predecessor")
    remaining=set(items);done=set();stations=[]
    while remaining:
        cap=ct;station=[]
        while True:
            eligible=[k for k in remaining if preds[k].issubset(done|set(station)) and times[k]<=cap+1e-9]
            if not eligible:break
            eligible.sort(key=lambda k:(-times[k],k) if rule=="largest_candidate" else (len(preds[k]),-times[k],k))
            chosen=eligible[0];station.append(chosen);cap-=times[chosen]
        require(station,"could not assign any task; check precedence cycle or cycle time")
        stations.append({"station":len(stations)+1,"tasks":station,"work_time":sum(times[k] for k in station),"idle_time":cap})
        done.update(station);remaining.difference_update(station)
    total=sum(times.values());eff=total/(len(stations)*ct)
    return {"stations":stations,"station_count":len(stations),"total_task_time":total,"cycle_time":ct,"line_efficiency":eff,"balance_delay":1-eff,"assumptions":["Largest Candidate Rule heuristic; result is not guaranteed globally optimal.","Precedence is checked before assigning each task; task IDs break ties alphabetically."]}


def schedule_job_shop(jobs):
    require(jobs and len({str(job["id"]) for job in jobs})==len(jobs),"jobs must be non-empty and have unique IDs")
    machine_free={}; job_free={}; schedule=[]
    for job in jobs:
        require(job.get("operations"),f"job {job["id"]} must contain at least one operation")
        jid=str(job["id"]);t=job_free.get(jid,0)
        for ix,op in enumerate(job["operations"]):
            machine=str(op["machine"]);dur=float(op["duration"]);require(math.isfinite(dur) and dur>0,"operation duration must be finite and > 0")
            start=max(t,machine_free.get(machine,0));end=start+dur
            schedule.append({"job":jid,"operation":ix+1,"machine":machine,"start":start,"finish":end,"duration":dur})
            t=end;machine_free[machine]=end
        job_free[jid]=t
    return {"schedule":schedule,"makespan":max(job_free.values(),default=0),"assumptions":["Greedy input-order schedule; each job's operations follow listed order and each machine processes one operation at a time.","This is a feasible dispatch heuristic for the supplied order, not an optimal general job-shop solver."]}


def evaluate_layout(departments, flows, distance="manhattan"):
    require(distance in {"manhattan", "euclidean"}, "distance must be manhattan or euclidean")
    coords={str(d["id"]):(float(d["x"]),float(d["y"])) for d in departments}
    require(all(np.isfinite(point).all() for point in coords.values()), "department coordinates must be finite")
    total=0;details=[]
    for f in flows:
        a,b=str(f["from"]),str(f["to"]);qty=float(f["flow"])
        require(a in coords and b in coords and math.isfinite(qty) and qty>=0,"flow endpoints must exist and flow must be finite and >= 0")
        dx=abs(coords[a][0]-coords[b][0]);dy=abs(coords[a][1]-coords[b][1])
        dist=dx+dy if distance=="manhattan" else math.hypot(dx,dy)
        load=qty*dist;total+=load;details.append({"from":a,"to":b,"flow":qty,"distance":dist,"load_distance":load})
    return {"distance_metric":distance,"pairs":details,"total_load_distance":total,"assumptions":["Departments are represented by their center coordinates; area and aisle constraints are not optimized."]}


def center_of_gravity(points):
    require(points,"points cannot be empty")
    values=[(float(p["x"]),float(p["y"]),float(p["weight"])) for p in points]
    require(all(all(math.isfinite(v) for v in row) for row in values), "coordinates and weights must be finite")
    total=sum(row[2] for row in values);require(total>0 and all(row[2]>=0 for row in values),"weights must be non-negative and sum to > 0")
    x=sum(row[0]*row[2] for row in values)/total;y=sum(row[1]*row[2] for row in values)/total
    return {"x":x,"y":y,"total_weight":total,"assumptions":["Center-of-gravity model uses weighted Euclidean coordinates; it does not account for roads, barriers, or fixed costs."]}


def learning_curve(first_unit_time, learning_rate, units, basis="unit"):
    t1=float(first_unit_time);lr=float(learning_rate);n=int(units)
    require(t1>0 and 0<lr<1 and n>=1,"first_unit_time > 0, learning_rate between 0 and 1, units >= 1 required")
    b=math.log(lr,2)
    if basis=="unit":
        times=[t1*(i**b) for i in range(1,n+1)];return {"basis":"unit-time","exponent":b,"unit_times":times,"total_time":sum(times),"assumptions":["Wright unit-time learning model: T_n=T_1*n^b, where b=log2(learning rate)."]}
    if basis=="cumulative_average":
        avgs=[t1*(i**b) for i in range(1,n+1)];totals=[avgs[i-1]*i for i in range(1,n+1)]
        unit=[totals[0]]+[totals[i]-totals[i-1] for i in range(1,n)]
        return {"basis":"cumulative-average","exponent":b,"cumulative_average_times":avgs,"unit_times":unit,"total_time":totals[-1],"assumptions":["Wright cumulative-average model: average time per unit after n units = T1*n^b."]}
    raise ValueError("basis must be unit or cumulative_average")


def solve_lot_sizing(demand, setup_cost, holding_cost):
    d=np.asarray(demand,dtype=float);n=len(d);K=float(setup_cost);h=float(holding_cost)
    require(d.ndim==1 and n>0 and np.isfinite(d).all() and (d>=0).all() and math.isfinite(K) and math.isfinite(h) and K>=0 and h>=0,"demand must be finite and non-negative; setup/holding costs must be finite and >= 0")
    dp=[0]+[float("inf")]*n;prev=[None]*(n+1)
    for end in range(1,n+1):
        for start in range(end,0,-1):
            # order at start covers demand[start-1:end]
            holding=sum(d[t-1]*(t-start)*h for t in range(start,end+1))
            cost=dp[start-1]+K+holding
            if cost<dp[end]:dp[end]=cost;prev[end]=start
    orders=[];end=n
    while end>0:
        start=prev[end];qty=float(d[start-1:end].sum());orders.append({"period":start,"quantity":qty,"covers_through_period":end});end=start-1
    orders.reverse()
    return {"orders":orders,"minimum_cost":dp[n],"assumptions":["Wagner-Whitin dynamic lot-sizing with zero initial inventory, no capacity constraint, deterministic demand, constant setup and per-unit-period holding cost."]}


def productivity(output, inputs):
    out=float(output);ins={k:float(v) for k,v in inputs.items()};require(math.isfinite(out) and out>=0 and ins and all(math.isfinite(v) and v>0 for v in ins.values()),"output must be finite and >= 0; all input quantities must be finite and > 0")
    partial={k:out/v for k,v in ins.items()};return {"partial_productivity":partial,"multifactor_productivity":out/sum(ins.values()),"total_input":sum(ins.values()),"assumptions":["Output and all input quantities must use economically comparable units/value basis for multifactor productivity to be meaningful."]}


def reliability(params):
    components=[float(x) for x in params["components"]];require(components and all(math.isfinite(x) and 0<=x<=1 for x in components),"component reliabilities must be finite and in [0,1]")
    config=params.get("configuration","series")
    if config=="series":value=math.prod(components)
    elif config=="parallel":value=1-math.prod(1-x for x in components)
    else:raise ValueError("configuration must be series or parallel")
    return {"configuration":config,"system_reliability":value,"component_reliabilities":components,"assumptions":["Components fail independently; all components are required in series; any component can operate in parallel configuration."]}


def work_measurement(observed_times, performance_rating=1.0, allowance=0.0, confidence_z=1.96, relative_accuracy=0.05):
    x=np.asarray(observed_times,dtype=float);require(x.ndim==1 and len(x)>=2 and np.isfinite(x).all() and (x>=0).all(),"observed_times must contain at least two finite non-negative observations")
    rating=float(performance_rating);allow=float(allowance);z=float(confidence_z);acc=float(relative_accuracy)
    require(all(math.isfinite(v) for v in (rating,allow,z,acc)) and rating>0 and 0<=allow<1 and z>0 and acc>0,"rating, allowance, confidence_z and relative_accuracy must be finite and within their valid ranges")
    mean=float(x.mean());sd=float(x.std(ddof=1));normal=mean*rating;standard=normal/(1-allow);required=(z*sd/(acc*mean))**2 if mean else float("inf")
    return {"observations":len(x),"average_observed_time":mean,"sample_standard_deviation":sd,"normal_time":normal,"standard_time":standard,"estimated_required_sample_size":math.ceil(required),"assumptions":["Allowance is defined as a fraction of standard time; performance rating multiplies observed time.","Sample-size formula uses relative precision about the mean and a normal critical value; it is an approximation."]}
