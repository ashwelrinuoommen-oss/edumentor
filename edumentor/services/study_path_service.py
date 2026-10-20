"""
Study path and prerequisite DAG processing service using NetworkX.
"""

from typing import Dict, List, Tuple, Any
from edumentor.graph import ConceptGraph


class StudyPathService:
    def __init__(self, concepts: List[Dict[str, Any]], dependencies: List[Tuple[str, str]]):
        self.graph = ConceptGraph(concepts, dependencies)

    def get_topological_order(self) -> List[str]:
        return self.graph.get_topological_order()

    def get_tiers(self) -> Dict[str, int]:
        return self.graph.get_concept_tiers()

    def get_svg_html(self) -> str:
        return self.graph.generate_html_graph()

    def get_graph_dict(self) -> Dict[str, Any]:
        return self.graph.to_dict()
