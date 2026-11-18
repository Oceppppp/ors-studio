from __future__ import annotations

import math
from collections import defaultdict, deque

from .common import require


def solve_cpm(activities):
    items = {str(activity["id"]): activity for activity in activities}
    require(len(items) == len(activities) and items, "activity IDs must be unique and non-empty")
    predecessors = {}
    indegree = {key: 0 for key in items}
    successors = defaultdict(list)
    for key, activity in items.items():
        duration = float(activity["duration"])
        require(math.isfinite(duration) and duration >= 0, f"duration for {key} must be finite and >= 0")
        pred_list = [str(value) for value in activity.get("predecessors", [])]
        require(len(set(pred_list)) == len(pred_list), f"predecessors for {key} must not contain duplicates")
        predecessors[key] = pred_list
        for predecessor in pred_list:
            require(predecessor in items and predecessor != key, f"unknown/self predecessor {predecessor} in {key}")
            successors[predecessor].append(key)
            indegree[key] += 1

    queue = deque(key for key, degree in indegree.items() if degree == 0)
    order = []
    while queue:
        key = queue.popleft()
        order.append(key)
        for next_key in successors[key]:
            indegree[next_key] -= 1
            if indegree[next_key] == 0:
                queue.append(next_key)
    require(len(order) == len(items), "precedence graph contains a cycle")

    earliest_start, earliest_finish = {}, {}
    for key in order:
        earliest_start[key] = max((earliest_finish[pred] for pred in predecessors[key]), default=0)
        earliest_finish[key] = earliest_start[key] + float(items[key]["duration"])
    project_duration = max(earliest_finish.values())

    latest_start, latest_finish = {}, {}
    for key in reversed(order):
        latest_finish[key] = min((latest_start[successor] for successor in successors[key]), default=project_duration)
        latest_start[key] = latest_finish[key] - float(items[key]["duration"])

    table = []
    for key in order:
        slack = latest_start[key] - earliest_start[key]
        table.append({
            "id": key,
            "duration": float(items[key]["duration"]),
            "predecessors": predecessors[key],
            "ES": earliest_start[key],
            "EF": earliest_finish[key],
            "LS": latest_start[key],
            "LF": latest_finish[key],
            "slack": slack,
            "critical": abs(slack) < 1e-8,
        })
    critical = [activity["id"] for activity in table if activity["critical"]]
    return {
        "project_duration": project_duration,
        "activities": table,
        "critical_activities": critical,
        "critical_path": critical,
        "assumptions": [
            "Deterministic activity durations; activity-on-node network; critical activities are listed in topological order.",
            "If multiple critical paths exist, critical_activities/critical_path lists all critical activities, not every complete path sequence.",
        ],
    }


def _representative_critical_path(activity_rows, project_duration):
    """Return one complete critical path, choosing the first predecessor on ties."""
    by_id = {row["id"]: row for row in activity_rows}
    terminal_candidates = [
        row for row in activity_rows
        if row["critical"] and abs(row["EF"] - project_duration) < 1e-8
    ]
    if not terminal_candidates:
        return []
    current = terminal_candidates[-1]["id"]
    path = [current]
    while True:
        row = by_id[current]
        candidates = [
            predecessor for predecessor in row["predecessors"]
            if predecessor in by_id
            and by_id[predecessor]["critical"]
            and abs(by_id[predecessor]["EF"] - row["ES"]) < 1e-8
        ]
        if not candidates:
            break
        current = candidates[0]
        path.append(current)
    path.reverse()
    return path


def solve_pert(activities):
    converted = []
    variance_by_id = {}
    for activity in activities:
        optimistic, most_likely, pessimistic = map(
            float, (activity["optimistic"], activity["most_likely"], activity["pessimistic"])
        )
        require(
            all(math.isfinite(value) for value in (optimistic, most_likely, pessimistic))
            and optimistic <= most_likely <= pessimistic,
            f"PERT estimates for {activity['id']} must be finite and satisfy optimistic <= most_likely <= pessimistic",
        )
        variance = ((pessimistic - optimistic) / 6) ** 2
        variance_by_id[str(activity["id"])] = variance
        converted.append({
            "id": activity["id"],
            "duration": (optimistic + 4 * most_likely + pessimistic) / 6,
            "predecessors": activity.get("predecessors", []),
        })

    result = solve_cpm(converted)
    result["activities"] = [
        {**row, "variance": variance_by_id[row["id"]]}
        for row in result["activities"]
    ]
    representative_path = _representative_critical_path(result["activities"], result["project_duration"])
    result["representative_critical_path"] = representative_path
    result["critical_path_variance"] = sum(variance_by_id[key] for key in representative_path)
    result["project_standard_deviation"] = math.sqrt(result["critical_path_variance"])
    result["method"] = "PERT expected time (a+4m+b)/6"
    result["assumptions"].append(
        "When several complete critical paths exist, variance and standard deviation refer to one representative critical path; the first eligible predecessor is selected deterministically."
    )
    return result
