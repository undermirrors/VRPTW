#!/usr/bin/env python3
"""
VRPTW Initialization Strategy Tests.

Tests basic model functionality and solution generation.

Usage:
    python -m pytest tests/test_vrptw_init.py -v
    or
    python tests/test_vrptw_init.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest


class TestVRPTWInitialization(unittest.TestCase):
    """Test VRPTW initialization strategies."""

    def setUp(self):
        """Set up test fixtures."""
        from models import Location, TimeWindow, Client, Depot

        self.depot = Depot(0, Location(0, 0), 100)
        self.clients = [
            Client(i, Location(10 + i, 10 + i), 10, TimeWindow(0, 100))
            for i in range(1, 6)
        ]

    def test_initial_solution_feasible(self):
        """Test that initial solutions are capacity feasible."""
        from solution_generator import SolutionGenerator

        solution = SolutionGenerator.generate_random_solution(
            self.depot, self.clients, self.depot.capacity
        )

        # Check capacity feasibility
        for route in solution.routes:
            self.assertLessEqual(route.current_load, route.capacity)

    def test_nearest_neighbor_generation(self):
        """Test nearest neighbor solution generation."""
        from solution_generator import SolutionGenerator

        solution = SolutionGenerator.nearest_neighbor(
            self.depot, self.clients, self.depot.capacity
        )

        # All clients should be assigned
        assigned = set()
        for route in solution.routes:
            assigned.update(route.clients)

        self.assertEqual(len(assigned), len(self.clients))

    def test_greedy_insertion_generation(self):
        """Test greedy insertion solution generation."""
        from solution_generator import SolutionGenerator

        solution = SolutionGenerator.greedy_insertion(
            self.depot, self.clients, self.depot.capacity
        )

        # All clients should be assigned
        assigned = set()
        for route in solution.routes:
            assigned.update(route.clients)

        self.assertEqual(len(assigned), len(self.clients))

    def test_solution_feasibility_check(self):
        """Test solution feasibility checking."""
        from solution_generator import SolutionGenerator

        solution = SolutionGenerator.nearest_neighbor(
            self.depot, self.clients, self.depot.capacity
        )

        # Solution should be feasible
        self.assertTrue(solution.is_feasible())

    def test_route_operations(self):
        """Test route operations maintain feasibility."""
        from models import Route, Location, TimeWindow, Client

        route = Route(self.depot, 100)

        # Add clients one by one
        for i in range(3):
            client = Client(i, Location(10 + i, 10 + i), 20, TimeWindow(0, 100))
            route.add_client(client)

        # Route should have 3 clients
        self.assertEqual(len(route.clients), 3)
        self.assertEqual(route.current_load, 60)

        # Route should still be feasible
        self.assertLessEqual(route.current_load, route.capacity)

    def test_distance_calculation(self):
        """Test distance calculations."""
        from distance_utils import DistanceCalculator
        from models import Location

        loc1 = Location(0, 0)
        loc2 = Location(3, 4)

        distance = DistanceCalculator.get_distance(loc1, loc2)

        # Should be 5 (3-4-5 triangle)
        self.assertAlmostEqual(distance, 5.0, places=5)

    def test_solution_distance_calculation(self):
        """Test solution total distance calculation."""
        from solution_generator import SolutionGenerator
        from distance_utils import DistanceCalculator

        solution = SolutionGenerator.nearest_neighbor(
            self.depot, self.clients, self.depot.capacity
        )

        distance = DistanceCalculator.solution_distance(solution)

        # Distance should be positive
        self.assertGreater(distance, 0)


def main():
    """Run tests."""
    print("\n" + "=" * 80)
    print("VRPTW INITIALIZATION & CORE FUNCTIONALITY TESTS")
    print("=" * 80 + "\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestVRPTWInitialization)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Check the output above.")
    print("=" * 80 + "\n")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
