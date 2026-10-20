import unittest
from edumentor.graph import ConceptGraph


class TestConceptGraph(unittest.TestCase):
    def setUp(self):
        self.sample_concepts = [
            {"id": "c1", "title": "Variables & Types", "summary": "Basic values", "principles": ["types", "memory"]},
            {"id": "c2", "title": "Control Flow", "summary": "Branching & loops", "principles": ["conditions", "loops"]},
            {"id": "c3", "title": "Functions", "summary": "Reusable code", "principles": ["parameters", "returns"]},
            {"id": "c4", "title": "Recursion", "summary": "Self-calling functions", "principles": ["base case", "stack"]}
        ]
        self.sample_deps = [
            ("c1", "c2"),
            ("c2", "c3"),
            ("c3", "c4")
        ]

    def test_topological_order(self):
        cg = ConceptGraph(self.sample_concepts, self.sample_deps)
        order = cg.get_topological_order()
        self.assertEqual(order, ["c1", "c2", "c3", "c4"])

    def test_cycle_resolution(self):
        # Introduce cycle: c4 -> c1
        deps_with_cycle = list(self.sample_deps) + [("c4", "c1")]
        cg = ConceptGraph(self.sample_concepts, deps_with_cycle)
        self.assertTrue(len(cg.removed_cycle_edges) > 0)
        # Should still produce a valid topological order without error
        order = cg.get_topological_order()
        self.assertEqual(len(order), 4)

    def test_concept_tiers(self):
        cg = ConceptGraph(self.sample_concepts, self.sample_deps)
        tiers = cg.get_concept_tiers()
        self.assertEqual(tiers["c1"], 0)
        self.assertEqual(tiers["c2"], 1)
        self.assertEqual(tiers["c3"], 2)
        self.assertEqual(tiers["c4"], 3)

    def test_prerequisites_and_dependents(self):
        cg = ConceptGraph(self.sample_concepts, self.sample_deps)
        self.assertEqual(cg.get_prerequisites("c3"), ["c2"])
        self.assertEqual(cg.get_dependents("c2"), ["c3"])


if __name__ == "__main__":
    unittest.main()
