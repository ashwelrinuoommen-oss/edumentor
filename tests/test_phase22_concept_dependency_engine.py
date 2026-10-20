"""
Tests for Phase 22 — Concept Dependency Engine (NetworkX)

Verifies:
1. Internal generation of dependency graph: Concept A -> Concept B -> Concept C using NetworkX.
2. Topological sorting to guarantee prerequisite ordering.
3. Invariant: If Process -> Thread -> Concurrency, EduMentor must NOT teach Concurrency first.
4. Cycle detection and automatic cycle breaking.
5. Integration with ConceptGraph and Orchestrator.
"""

import unittest
import networkx as nx
from edumentor.dependency_engine import ConceptDependencyEngine, DependencyCycleError
from edumentor.graph import ConceptGraph
from edumentor.orchestrator import EduMentorOrchestrator


class TestPhase22ConceptDependencyEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ConceptDependencyEngine()

    def test_internal_chain_generation_a_b_c(self):
        """
        Verify:
        Internally generate:
        Concept A
           ↓
        Concept B
           ↓
        Concept C
        """
        chain = ["Concept A", "Concept B", "Concept C"]
        graph = self.engine.generate_chain_graph(chain)

        self.assertIsInstance(graph, nx.DiGraph)
        self.assertEqual(graph.number_of_nodes(), 3)
        self.assertEqual(graph.number_of_edges(), 2)

        # Verify edges: A -> B and B -> C
        self.assertTrue(graph.has_edge("Concept A", "Concept B"))
        self.assertTrue(graph.has_edge("Concept B", "Concept C"))
        self.assertFalse(graph.has_edge("Concept C", "Concept A"))

        # Topological sort verification
        order = self.engine.get_topological_order(graph)
        self.assertEqual(order, ["Concept A", "Concept B", "Concept C"])

    def test_process_thread_concurrency_ordering(self):
        """
        User Specification:
        If:
        Process
         ↓
        Thread
         ↓
        Concurrency

        EduMentor should not teach Concurrency first.
        """
        concepts = ["Process", "Thread", "Concurrency"]
        dependencies = [("Process", "Thread"), ("Thread", "Concurrency")]

        graph = self.engine.build_dependency_graph(concepts=concepts, dependencies=dependencies)
        order = self.engine.get_topological_order(graph)

        # 1. EduMentor should not teach Concurrency first
        self.assertNotEqual(order[0], "Concurrency", "Violation: Concurrency was taught first!")

        # 2. Correct ordering must be Process -> Thread -> Concurrency
        self.assertEqual(order[0], "Process")
        self.assertEqual(order[1], "Thread")
        self.assertEqual(order[2], "Concurrency")

        # 3. Learning order validation passes on correct order
        is_valid, msg = self.engine.validate_learning_order(order, graph)
        self.assertTrue(is_valid)
        self.assertIsNone(msg)

        # 4. Learning order validation strictly rejects teaching Concurrency first
        invalid_order_1 = ["Concurrency", "Process", "Thread"]
        is_valid_inv1, err1 = self.engine.validate_learning_order(invalid_order_1, graph)
        self.assertFalse(is_valid_inv1)
        self.assertIn("Concurrency", err1)

        invalid_order_2 = ["Concurrency", "Thread", "Process"]
        is_valid_inv2, err2 = self.engine.validate_learning_order(invalid_order_2, graph)
        self.assertFalse(is_valid_inv2)

        invalid_order_3 = ["Thread", "Concurrency", "Process"]
        is_valid_inv3, err3 = self.engine.validate_learning_order(invalid_order_3, graph)
        self.assertFalse(is_valid_inv3)

    def test_cycle_detection_and_resolution(self):
        """
        Verify that circular dependencies (e.g. A -> B -> C -> A) are automatically
        resolved by removing feedback edges, ensuring a valid DAG for topological sort.
        """
        concepts = ["A", "B", "C"]
        cyclic_deps = [("A", "B"), ("B", "C"), ("C", "A")]

        graph = self.engine.build_dependency_graph(concepts=concepts, dependencies=cyclic_deps)
        self.assertTrue(nx.is_directed_acyclic_graph(graph))
        self.assertGreater(len(self.engine.removed_cycle_edges), 0)

        # Topological sort works without hanging or error
        order = self.engine.get_topological_order(graph)
        self.assertEqual(len(order), 3)

    def test_foundational_and_terminal_concepts(self):
        """Verify root foundational concepts (in-degree 0) vs terminal concepts."""
        concepts = ["Process", "Thread", "Concurrency"]
        dependencies = [("Process", "Thread"), ("Thread", "Concurrency")]
        graph = self.engine.build_dependency_graph(concepts, dependencies)

        foundational = self.engine.get_foundational_concepts(graph)
        self.assertEqual(foundational, ["Process"])

        prereqs_concurrency = self.engine.get_prerequisites("Concurrency", graph)
        self.assertEqual(prereqs_concurrency, ["Thread"])

        ancestors_concurrency = self.engine.get_all_ancestors("Concurrency", graph)
        self.assertEqual(ancestors_concurrency, {"Process", "Thread"})

    def test_graph_metadata_serialization(self):
        """Verify graph metadata serialization for front-end API consumption."""
        concepts = ["Process", "Thread", "Concurrency"]
        dependencies = [("Process", "Thread"), ("Thread", "Concurrency")]
        graph = self.engine.build_dependency_graph(concepts, dependencies)

        metadata = self.engine.get_graph_metadata(graph)
        self.assertEqual(metadata["node_count"], 3)
        self.assertEqual(metadata["edge_count"], 2)
        self.assertTrue(metadata["is_valid_order"])
        self.assertEqual(metadata["topological_sequence"], ["Process", "Thread", "Concurrency"])

    def test_orchestrator_integration_never_teaches_concurrency_first(self):
        """
        Verify that EduMentorOrchestrator initializes curriculum and starts with
        Process, never Concurrency.
        """
        orch = EduMentorOrchestrator(student_name="Ashwel")
        orch.load_sample_module("Operating Systems")

        # In OS curriculum: Process Scheduling must be studied before Concurrency
        topological = orch.topological_order
        self.assertIn("os_process_scheduling", topological)
        self.assertIn("os_threads_concurrency", topological)

        process_idx = topological.index("os_process_scheduling")
        concurrency_idx = topological.index("os_threads_concurrency")

        self.assertLess(process_idx, concurrency_idx, "Foundational Process must precede Threads & Concurrency")
        self.assertEqual(process_idx, 0, "Process Scheduling must be taught first (index 0)")
        self.assertNotEqual(orch.current_concept_id, "os_threads_concurrency", "Concurrency must not be taught first!")
        self.assertEqual(orch.current_concept_id, "os_process_scheduling")


if __name__ == "__main__":
    unittest.main()
