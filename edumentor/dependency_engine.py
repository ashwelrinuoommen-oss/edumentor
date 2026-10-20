"""
Concept Dependency Engine using NetworkX (Phase 22).

Constructs directed dependency graphs (Concept A -> Concept B -> Concept C),
breaks circular dependencies to guarantee a DAG, performs topological sorting,
and strictly enforces prerequisite curriculum invariants:
e.g., If Process -> Thread -> Concurrency, EduMentor will never teach Concurrency first.
"""

from typing import Dict, List, Tuple, Set, Optional, Any, Union
import networkx as nx


class DependencyCycleError(ValueError):
    """Raised when a dependency cycle cannot be resolved."""
    pass


class ConceptDependencyEngine:
    """
    Dependency engine powered by NetworkX.
    Manages concept prerequisite structures, cycle resolution, and topological curriculum sequencing.
    """

    def __init__(self):
        self.graph: nx.DiGraph = nx.DiGraph()
        self.removed_cycle_edges: List[Tuple[str, str]] = []

    def build_dependency_graph(
        self,
        concepts: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]], List[str]],
        dependencies: Optional[List[Tuple[str, str]]] = None,
        auto_chain_if_empty: bool = False
    ) -> nx.DiGraph:
        """
        Builds a NetworkX DiGraph where edge (u, v) denotes 'u is a prerequisite of v' (u -> v).
        
        Args:
            concepts: List of concept dicts, dict of concept dicts, or list of concept names/IDs.
            dependencies: Optional list of (prerequisite, dependent) tuples.
            auto_chain_if_empty: If True and no dependencies provided, generates Concept 0 -> Concept 1 -> ...
        """
        self.graph = nx.DiGraph()
        self.removed_cycle_edges = []

        # 1. Normalize and register nodes
        node_ids: List[str] = []
        if isinstance(concepts, list):
            for item in concepts:
                if isinstance(item, dict):
                    cid = item.get("id") or item.get("title") or item.get("name")
                    node_ids.append(cid)
                    self.graph.add_node(
                        cid,
                        title=item.get("title", cid),
                        summary=item.get("summary", ""),
                        principles=item.get("principles", []),
                        status=item.get("sm2_status", "new"),
                        quality=item.get("last_quality_score", 0),
                        module_id=item.get("module_id", None)
                    )
                elif isinstance(item, str):
                    node_ids.append(item)
                    self.graph.add_node(item, title=item)
        elif isinstance(concepts, dict):
            for cid, cdata in concepts.items():
                node_ids.append(cid)
                if isinstance(cdata, dict):
                    self.graph.add_node(
                        cid,
                        title=cdata.get("title", cid),
                        summary=cdata.get("summary", ""),
                        principles=cdata.get("principles", []),
                        status=cdata.get("sm2_status", "new"),
                        quality=cdata.get("last_quality_score", 0),
                        module_id=cdata.get("module_id", None)
                    )
                else:
                    self.graph.add_node(cid, title=str(cdata))

        # 2. Add edges from explicit dependencies or concept metadata
        added_edges = 0
        if dependencies:
            for prereq, dependent in dependencies:
                if prereq != dependent:
                    # Auto-add nodes if not present
                    if prereq not in self.graph:
                        self.graph.add_node(prereq, title=prereq)
                    if dependent not in self.graph:
                        self.graph.add_node(dependent, title=dependent)
                    self.graph.add_edge(prereq, dependent)
                    added_edges += 1

        # Check concept metadata for embedded prerequisites (e.g. concept["prerequisites"])
        if isinstance(concepts, list):
            for item in concepts:
                if isinstance(item, dict):
                    cid = item.get("id") or item.get("title") or item.get("name")
                    prereqs = item.get("prerequisites") or item.get("dependencies") or []
                    for p in prereqs:
                        if p != cid:
                            if p not in self.graph:
                                self.graph.add_node(p, title=p)
                            self.graph.add_edge(p, cid)
                            added_edges += 1

        # 3. If auto_chain requested and no edges exist, generate linear chain:
        # Concept A -> Concept B -> Concept C
        if added_edges == 0 and auto_chain_if_empty and len(node_ids) > 1:
            for i in range(len(node_ids) - 1):
                self.graph.add_edge(node_ids[i], node_ids[i + 1])

        # 4. Cycle resolution
        self.resolve_cycles()
        return self.graph

    def generate_chain_graph(self, concept_sequence: List[str]) -> nx.DiGraph:
        """
        Explicitly generates an internal chain:
        Concept A -> Concept B -> Concept C
        """
        dependencies = [(concept_sequence[i], concept_sequence[i + 1]) for i in range(len(concept_sequence) - 1)]
        return self.build_dependency_graph(concepts=concept_sequence, dependencies=dependencies)

    def resolve_cycles(self) -> None:
        """Detect and remove feedback edges causing circular dependencies to guarantee a DAG."""
        while not nx.is_directed_acyclic_graph(self.graph):
            try:
                cycle = nx.find_cycle(self.graph, orientation="original")
                # Break the closing edge of the cycle
                u, v, _ = cycle[-1]
                self.graph.remove_edge(u, v)
                self.removed_cycle_edges.append((u, v))
            except nx.NetworkXNoCycle:
                break

    def get_topological_order(self, graph: Optional[nx.DiGraph] = None) -> List[str]:
        """
        Return concepts in strict topological sort order (prerequisites appear before dependents).
        """
        g = graph if graph is not None else self.graph
        try:
            return list(nx.topological_sort(g))
        except nx.NetworkXUnfeasible:
            # Fallback if unfeasible
            return list(g.nodes())

    def validate_learning_order(
        self,
        sequence: List[str],
        graph: Optional[nx.DiGraph] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifies that in the given learning sequence, no concept is taught before its prerequisites.
        Specifically verifies:
        If Process -> Thread -> Concurrency, Concurrency is NOT taught first.
        """
        g = graph if graph is not None else self.graph
        pos = {node: i for i, node in enumerate(sequence)}

        for u, v in g.edges():
            if u in pos and v in pos:
                if pos[u] > pos[v]:
                    return (
                        False,
                        f"Ordering violation: Prerequisite '{u}' is scheduled at position {pos[u]}, "
                        f"after dependent '{v}' at position {pos[v]}."
                    )

        # Check for foundational invariant: A dependent with prerequisites must not be taught first
        if len(sequence) > 0:
            first_concept = sequence[0]
            if first_concept in g:
                prereqs = list(g.predecessors(first_concept))
                if prereqs:
                    return (
                        False,
                        f"Foundational violation: '{first_concept}' cannot be taught first because "
                        f"it depends on prerequisite(s): {prereqs}."
                    )

        return (True, None)

    def get_prerequisites(self, concept_id: str, graph: Optional[nx.DiGraph] = None) -> List[str]:
        """Immediate prerequisites of a concept."""
        g = graph if graph is not None else self.graph
        if concept_id in g:
            return list(g.predecessors(concept_id))
        return []

    def get_all_ancestors(self, concept_id: str, graph: Optional[nx.DiGraph] = None) -> Set[str]:
        """All transitive prerequisites of a concept."""
        g = graph if graph is not None else self.graph
        if concept_id in g:
            return nx.ancestors(g, concept_id)
        return set()

    def get_dependents(self, concept_id: str, graph: Optional[nx.DiGraph] = None) -> List[str]:
        """Concepts that directly require this concept."""
        g = graph if graph is not None else self.graph
        if concept_id in g:
            return list(g.successors(concept_id))
        return []

    def get_all_descendants(self, concept_id: str, graph: Optional[nx.DiGraph] = None) -> Set[str]:
        """All transitive dependents of a concept."""
        g = graph if graph is not None else self.graph
        if concept_id in g:
            return nx.descendants(g, concept_id)
        return set()

    def get_foundational_concepts(self, graph: Optional[nx.DiGraph] = None) -> List[str]:
        """Concepts with in-degree 0 (no prerequisites)."""
        g = graph if graph is not None else self.graph
        return [node for node in g.nodes() if g.in_degree(node) == 0]

    def get_graph_metadata(self, graph: Optional[nx.DiGraph] = None) -> Dict[str, Any]:
        """Serialize dependency graph for inspection and visualization."""
        g = graph if graph is not None else self.graph
        topological = self.get_topological_order(g)
        is_valid, error = self.validate_learning_order(topological, g)

        nodes = []
        for n in g.nodes():
            data = g.nodes[n]
            nodes.append({
                "id": n,
                "title": data.get("title", n),
                "in_degree": g.in_degree(n),
                "out_degree": g.out_degree(n),
                "is_foundational": g.in_degree(n) == 0
            })

        edges = [{"source": u, "target": v} for u, v in g.edges()]

        return {
            "node_count": g.number_of_nodes(),
            "edge_count": g.number_of_edges(),
            "topological_sequence": topological,
            "is_valid_order": is_valid,
            "order_validation_message": error,
            "removed_cycle_edges": self.removed_cycle_edges,
            "nodes": nodes,
            "edges": edges
        }
