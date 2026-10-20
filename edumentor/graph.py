"""
Knowledge Graph and Dependency DAG Engine using NetworkX.
Provides cycle detection & resolution, topological sorting for study paths,
mastery tier calculation, and graph export for interactive visualization.
"""

from typing import Dict, List, Tuple, Set, Any, Optional
import networkx as nx
from edumentor.dependency_engine import ConceptDependencyEngine


class ConceptGraph:
    """
    Manages concept dependency DAG.
    Edges directed u -> v signify that 'u' is a prerequisite of 'v'.
    """

    def __init__(self, concepts: List[Dict[str, Any]], dependencies: List[Tuple[str, str]]):
        self.raw_concepts = {c["id"]: c for c in concepts}
        self.raw_dependencies = dependencies
        self.dependency_engine = ConceptDependencyEngine()
        self.graph = nx.DiGraph()
        self.removed_cycle_edges: List[Tuple[str, str]] = []
        self._build_graph()

    def _build_graph(self) -> None:
        """Construct graph and break cycles if necessary to guarantee a strict DAG."""
        for cid, cdata in self.raw_concepts.items():
            self.graph.add_node(
                cid,
                title=cdata.get("title", cid),
                summary=cdata.get("summary", ""),
                principles=cdata.get("principles", []),
                status=cdata.get("sm2_status", "new"),
                quality=cdata.get("last_quality_score", 0),
                total_reviews=cdata.get("total_reviews", 0)
            )

        for prereq_id, concept_id in self.raw_dependencies:
            if prereq_id in self.raw_concepts and concept_id in self.raw_concepts:
                if prereq_id != concept_id:
                    self.graph.add_edge(prereq_id, concept_id)

        # Break any cycles to ensure strict DAG for topological sorting
        self._resolve_cycles()

    def _resolve_cycles(self) -> None:
        """Detect and remove feedback edges causing circular dependencies."""
        while not nx.is_directed_acyclic_graph(self.graph):
            try:
                cycle = nx.find_cycle(self.graph, orientation="original")
                # Remove the closing edge of the cycle
                u, v, _ = cycle[-1]
                self.graph.remove_edge(u, v)
                self.removed_cycle_edges.append((u, v))
            except nx.NetworkXNoCycle:
                break

    def get_topological_order(self) -> List[str]:
        """
        Return concepts in topological sort order (prerequisites strictly appear before dependents).
        """
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            return list(self.graph.nodes())

    def validate_learning_order(self, sequence: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """Validate that no concept in sequence is taught before its prerequisites."""
        seq = sequence if sequence is not None else self.get_topological_order()
        return self.dependency_engine.validate_learning_order(seq, self.graph)

    def get_concept_tiers(self) -> Dict[str, int]:
        """
        Compute the topological depth / tier of each concept.
        Root nodes with no prerequisites are tier 0 (Foundational).
        Dependents are 1 + max(tier of prerequisites).
        """
        tiers: Dict[str, int] = {}
        for node in self.get_topological_order():
            prereqs = list(self.graph.predecessors(node))
            if not prereqs:
                tiers[node] = 0
            else:
                tiers[node] = max(tiers.get(p, 0) for p in prereqs) + 1
        return tiers

    def get_prerequisites(self, concept_id: str) -> List[str]:
        """Immediate prerequisites of a concept."""
        if concept_id in self.graph:
            return list(self.graph.predecessors(concept_id))
        return []

    def get_all_ancestors(self, concept_id: str) -> Set[str]:
        """All transitive prerequisites of a concept."""
        if concept_id in self.graph:
            return nx.ancestors(self.graph, concept_id)
        return set()

    def get_dependents(self, concept_id: str) -> List[str]:
        """Concepts that directly require this concept."""
        if concept_id in self.graph:
            return list(self.graph.successors(concept_id))
        return []

    def is_concept_unlocked(self, concept_id: str) -> Tuple[bool, List[str]]:
        """
        Check if all immediate prerequisites have passing understanding (quality >= 3 or reviewed).
        Returns (is_unlocked, missing_prerequisite_titles).
        """
        prereqs = self.get_prerequisites(concept_id)
        missing = []
        for p in prereqs:
            p_data = self.raw_concepts.get(p, {})
            last_q = p_data.get("last_quality_score", 0)
            reviews = p_data.get("total_reviews", 0)
            status = p_data.get("sm2_status", "new")
            if reviews == 0 or last_q < 3 or status == "weak":
                missing.append(p_data.get("title", p))

        return len(missing) == 0, missing

    def get_status_color(self, node_id: str) -> Dict[str, str]:
        """Return dark-theme aesthetic colors based on learning state."""
        cdata = self.raw_concepts.get(node_id, {})
        status = cdata.get("sm2_status", "new")
        last_q = cdata.get("last_quality_score", 0)
        reviews = cdata.get("total_reviews", 0)
        unlocked, _ = self.is_concept_unlocked(node_id)

        if reviews > 0 and (status == "weak" or last_q < 3):
            return {
                "bg": "#2A1215",
                "border": "#EF4444",
                "text": "#FCA5A5",
                "badge": "Needs Revisit",
                "badge_bg": "#450A0A"
            }
        elif status == "mastered" or (reviews >= 3 and last_q >= 4):
            return {
                "bg": "#0D2818",
                "border": "#10B981",
                "text": "#6EE7B7",
                "badge": "Mastered",
                "badge_bg": "#043A1B"
            }
        elif reviews > 0:
            return {
                "bg": "#0C2340",
                "border": "#25D8E8",
                "text": "#A5F3FC",
                "badge": "In Review",
                "badge_bg": "#083344"
            }
        elif unlocked:
            return {
                "bg": "#1E1B4B",
                "border": "#8B5CF6",
                "text": "#C4B5FD",
                "badge": "Ready to Learn",
                "badge_bg": "#2E1065"
            }
        else:
            return {
                "bg": "#161B22",
                "border": "#27303B",
                "text": "#9AA4B2",
                "badge": "Locked",
                "badge_bg": "#0D1117"
            }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize nodes and edges with coordinates and state for front-end rendering."""
        tiers = self.get_concept_tiers()
        topo_order = self.get_topological_order()

        tier_groups: Dict[int, List[str]] = {}
        for node in topo_order:
            t = tiers.get(node, 0)
            tier_groups.setdefault(t, []).append(node)

        nodes = []
        for node in topo_order:
            cdata = self.raw_concepts.get(node, {})
            colors = self.get_status_color(node)
            tier = tiers.get(node, 0)
            unlocked, missing = self.is_concept_unlocked(node)
            nodes.append({
                "id": node,
                "title": cdata.get("title", node),
                "summary": cdata.get("summary", ""),
                "principles": cdata.get("principles", []),
                "tier": tier,
                "tier_name": "Foundational" if tier == 0 else ("Intermediate" if tier == 1 else "Advanced"),
                "status": cdata.get("sm2_status", "new"),
                "quality": cdata.get("last_quality_score", 0),
                "reviews": cdata.get("total_reviews", 0),
                "unlocked": unlocked,
                "missing_prereqs": missing,
                "colors": colors
            })

        edges = []
        for u, v in self.graph.edges():
            edges.append({
                "from": u,
                "to": v,
                "from_title": self.raw_concepts.get(u, {}).get("title", u),
                "to_title": self.raw_concepts.get(v, {}).get("title", v)
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "topo_order": topo_order,
            "tiers": tiers,
            "removed_cycle_edges": self.removed_cycle_edges
        }

    def generate_html_graph(self) -> str:
        """
        Generate a responsive SVG matching the dark SaaS aesthetic (#050608, #0D1117, #25D8E8).
        """
        tiers = self.get_concept_tiers()
        topo_order = self.get_topological_order()

        tier_groups: Dict[int, List[str]] = {}
        for node in topo_order:
            t = tiers.get(node, 0)
            tier_groups.setdefault(t, []).append(node)

        max_tier = max(tier_groups.keys()) if tier_groups else 0
        max_nodes_in_tier = max((len(nodes) for nodes in tier_groups.values()), default=1)

        node_width = 190
        node_height = 62
        horizontal_spacing = 250
        vertical_spacing = 95
        padding = 50

        total_width = max(880, padding * 2 + (max_tier + 1) * horizontal_spacing)
        total_height = max(380, padding * 2 + max_nodes_in_tier * vertical_spacing)

        coords: Dict[str, Tuple[float, float]] = {}
        for t, nodes in tier_groups.items():
            x = padding + t * horizontal_spacing
            tier_height = len(nodes) * vertical_spacing
            start_y = (total_height - tier_height) / 2 + 15
            for i, node in enumerate(nodes):
                y = start_y + i * vertical_spacing
                coords[node] = (x, y)

        svg_edges = []
        for u, v in self.graph.edges():
            if u in coords and v in coords:
                x1, y1 = coords[u]
                x2, y2 = coords[v]
                start_x = x1 + node_width
                start_y = y1 + node_height / 2
                end_x = x2
                end_y = y2 + node_height / 2
                ctrl_x1 = start_x + (end_x - start_x) * 0.5
                ctrl_x2 = start_x + (end_x - start_x) * 0.5
                d = f"M {start_x} {start_y} C {ctrl_x1} {start_y}, {ctrl_x2} {end_y}, {end_x} {end_y}"
                svg_edges.append(f'<path d="{d}" stroke="#27303B" stroke-width="2.5" fill="none" marker-end="url(#arrow)" />')

        svg_nodes = []
        for node in topo_order:
            if node in coords:
                x, y = coords[node]
                cdata = self.raw_concepts.get(node, {})
                title = cdata.get("title", node)
                if len(title) > 23:
                    title = title[:21] + "..."
                
                colors = self.get_status_color(node)
                badge = colors["badge"]

                svg_nodes.append(f"""
                <g class="dag-node" transform="translate({x}, {y})" style="cursor: pointer;">
                    <rect width="{node_width}" height="{node_height}" rx="12" 
                          fill="{colors['bg']}" stroke="{colors['border']}" stroke-width="1.8" />
                    <text x="14" y="26" font-family="'Inter', -apple-system, sans-serif" 
                          font-size="13" font-weight="600" fill="#F5F7FA">{title}</text>
                    <rect x="14" y="36" width="90" height="18" rx="6" fill="{colors['badge_bg']}" stroke="{colors['border']}" stroke-width="0.8" />
                    <text x="20" y="49" font-family="'Inter', -apple-system, sans-serif" 
                          font-size="10" font-weight="700" fill="{colors['text']}">{badge}</text>
                </g>
                """)

        html = f"""
        <div class="dag-container" style="width: 100%; overflow-x: auto; background: #07090E; border: 1px solid #27303B; border-radius: 14px; padding: 14px;">
            <svg width="{total_width}" height="{total_height}" viewBox="0 0 {total_width} {total_height}" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#25D8E8" />
                    </marker>
                </defs>
                <g id="edges">
                    {''.join(svg_edges)}
                </g>
                <g id="nodes">
                    {''.join(svg_nodes)}
                </g>
            </svg>
        </div>
        """
        return html
