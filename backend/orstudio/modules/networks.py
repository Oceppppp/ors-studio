from __future__ import annotations

import heapq
import math
from collections import deque

from .common import require


def _nodes_and_edges(nodes, edges):
    names = [str(node) for node in nodes]
    require(names and len(set(names)) == len(names), "nodes must be non-empty and unique")
    normalized = []
    known = set(names)
    for index, edge in enumerate(edges):
        u, v = str(edge["from"]), str(edge["to"])
        require(u in known and v in known, f"edge {index + 1} references an unknown node")
        normalized.append((u, v, edge))
    return names, normalized


def shortest_path(nodes, edges, source, target):
    names, normalized = _nodes_and_edges(nodes, edges)
    source, target = str(source), str(target)
    node_set = set(names)
    require(source in node_set and target in node_set, "source and target must exist in nodes")
    adj = {node: [] for node in names}
    for u, v, edge in normalized:
        weight = float(edge.get("cost", edge.get("weight", 1)))
        require(math.isfinite(weight), "edge costs must be finite")
        require(weight >= 0, "Dijkstra requires non-negative edge costs")
        adj[u].append((v, weight))
    dist = {node: float("inf") for node in names}
    prev = {}
    dist[source] = 0
    queue = [(0, source)]
    while queue:
        distance, node = heapq.heappop(queue)
        if distance != dist[node]:
            continue
        if node == target:
            break
        for neighbor, weight in adj[node]:
            candidate = distance + weight
            if candidate < dist[neighbor]:
                dist[neighbor] = candidate
                prev[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))
    if dist[target] == float("inf"):
        return {"path": [], "cost": None, "reachable": False}
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    path.reverse()
    return {"path": path, "cost": dist[target], "reachable": True, "assumptions": ["Directed edges; Dijkstra requires non-negative finite weights."]}


def minimum_spanning_tree(nodes, edges):
    names, normalized = _nodes_and_edges(nodes, edges)
    weighted = []
    for u, v, edge in normalized:
        weight = float(edge.get("cost", edge.get("weight", 1)))
        require(math.isfinite(weight), "edge costs must be finite")
        weighted.append((weight, u, v))
    parent = {node: node for node in names}

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    chosen = []
    for weight, u, v in sorted(weighted):
        if find(u) != find(v):
            parent[find(u)] = find(v)
            chosen.append({"from": u, "to": v, "cost": weight})
    require(len(chosen) == len(names) - 1, "network is disconnected; no spanning tree exists")
    return {"edges": chosen, "total_cost": sum(edge["cost"] for edge in chosen), "assumptions": ["Undirected network; Kruskal minimum spanning tree. Edge costs must be finite; negative costs are permitted."]}


def maximum_flow(nodes, edges, source, sink):
    names, normalized = _nodes_and_edges(nodes, edges)
    source, sink = str(source), str(sink)
    node_set = set(names)
    require(source in node_set and sink in node_set and source != sink, "source/sink must be distinct known nodes")
    capacity = {node: {neighbor: 0.0 for neighbor in names} for node in names}
    for u, v, edge in normalized:
        amount = float(edge["capacity"])
        require(math.isfinite(amount), "edge capacities must be finite")
        require(amount >= 0, "edge capacities must be non-negative")
        capacity[u][v] += amount
    residual = {node: dict(row) for node, row in capacity.items()}
    total = 0.0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            node = queue.popleft()
            for neighbor, remaining in residual[node].items():
                if remaining > 1e-12 and neighbor not in parent:
                    parent[neighbor] = node
                    queue.append(neighbor)
        if sink not in parent:
            break
        bottleneck = float("inf")
        node = sink
        while parent[node] is not None:
            predecessor = parent[node]
            bottleneck = min(bottleneck, residual[predecessor][node])
            node = predecessor
        node = sink
        while parent[node] is not None:
            predecessor = parent[node]
            residual[predecessor][node] -= bottleneck
            residual[node][predecessor] += bottleneck
            node = predecessor
        total += bottleneck
    return {"max_flow": total, "assumptions": ["Directed capacitated network; Edmonds-Karp augmenting-path algorithm. Capacities must be finite and non-negative."]}
