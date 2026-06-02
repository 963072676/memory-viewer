"""Graph service (F-18): build concept co-occurrence graph from memories.

Nodes = memory entries
Edges = shared concepts (weight = number of shared concepts)
Only edges with weight >= 1 are included.
"""

from app.services.agentmemory import get_all_memories


def build_graph() -> dict:
    """Build a graph of memory relationships based on shared concepts.

    Returns {nodes, edges, meta}.
    """
    memories = get_all_memories()

    # Filter: only non-archived with concepts
    active = [m for m in memories if not m.get("archived", False)]

    # Build concept -> memory index for efficient lookup
    concept_index: dict[str, list[int]] = {}
    for idx, m in enumerate(active):
        for c in m.get("concepts", []):
            concept_index.setdefault(c, []).append(idx)

    # Nodes
    nodes = []
    for idx, m in enumerate(active):
        nodes.append({
            "id": m.get("id", f"node_{idx}"),
            "label": m.get("title", "Untitled"),
            "type": m.get("type", "unknown"),
            "strength": m.get("strength", 5),
            "size": max(5, m.get("strength", 5) * 3),
        })

    # Edges: compute pairwise shared concepts using concept index
    # Use a set to track processed pairs
    edge_map: dict[tuple[int, int], list[str]] = {}

    for concept, indices in concept_index.items():
        # For each pair of memories sharing this concept
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                a, b = indices[i], indices[j]
                key = (min(a, b), max(a, b))
                edge_map.setdefault(key, []).append(concept)

    edges = []
    max_weight = 0
    for (a, b), shared in edge_map.items():
        weight = len(shared)
        max_weight = max(max_weight, weight)
        edges.append({
            "source": active[a].get("id", f"node_{a}"),
            "target": active[b].get("id", f"node_{b}"),
            "weight": weight,
            "shared_concepts": sorted(shared),
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "meta": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "max_weight": max_weight,
        },
    }
