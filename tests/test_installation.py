#!/usr/bin/env python3
"""
VRPTW Installation Verification Test.

Tests that all core modules can be imported and basic functionality works.

Usage:
    python -m pytest tests/test_installation.py -v
    or
    python tests/test_installation.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest


class TestInstallation(unittest.TestCase):
    """Test that all modules can be imported."""

    def test_import_models(self):
        """Test models module import."""
        from models import Location, Client, Depot, Route, Solution, TimeWindow
        self.assertIsNotNone(Location)
        self.assertIsNotNone(Client)
        self.assertIsNotNone(Depot)
        self.assertIsNotNone(Route)
        self.assertIsNotNone(Solution)
        self.assertIsNotNone(TimeWindow)

    def test_import_distance_utils(self):
        """Test distance_utils module import."""
        from distance_utils import DistanceCalculator, SolutionEvaluator
        self.assertIsNotNone(DistanceCalculator)
        self.assertIsNotNone(SolutionEvaluator)

    def test_import_solution_generator(self):
        """Test solution_generator module import."""
        from solution_generator import SolutionGenerator
        self.assertIsNotNone(SolutionGenerator)

    def test_import_neighborhood(self):
        """Test neighborhood module import."""
        from neighborhood import (
            TwoOptOperator,
            OrOptOperator,
            RelocateOperator,
            CrossExchangeOperator,
        )
        self.assertIsNotNone(TwoOptOperator)
        self.assertIsNotNone(OrOptOperator)
        self.assertIsNotNone(RelocateOperator)
        self.assertIsNotNone(CrossExchangeOperator)

    def test_import_genetic_algorithm(self):
        """Test genetic_algorithm module import."""
        from genetic_algorithm import GeneticAlgorithm
        self.assertIsNotNone(GeneticAlgorithm)

    def test_import_tabu_search(self):
        """Test tabu_search module import."""
        from tabu_search import TabuSearch
        self.assertIsNotNone(TabuSearch)

    def test_import_initialization_strategy(self):
        """Test initialization_strategy module import."""
        from initialization_strategy import InitializationStrategy
        self.assertIsNotNone(InitializationStrategy)

    def test_basic_model_creation(self):
        """Test basic model creation."""
        from models import Location, TimeWindow, Client, Depot, Route, Solution

        loc = Location(0, 0)
        depot = Depot(0, loc, 100)
        client = Client(1, Location(10, 10), 10, TimeWindow(0, 100))

        route = Route(depot, 100)
        route.add_client(client)

        self.assertEqual(len(route.clients), 1)
        self.assertEqual(route.current_load, 10)

    def test_solution_creation(self):
        """Test solution creation."""
        from models import Location, TimeWindow, Client, Depot, Solution

        loc = Location(0, 0)
        depot = Depot(0, loc, 100)
        clients = [Client(i, Location(10 + i, 10 + i), 10, TimeWindow(0, 100)) for i in range(1, 6)]

        solution = Solution(depot, clients, num_vehicles=3)

        self.assertEqual(len(solution.routes), 3)
        self.assertEqual(len(solution.clients), 5)


def main():
    """Run tests."""
    print("\n" + "=" * 80)
    print("VRPTW INSTALLATION TEST")
    print("=" * 80 + "\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestInstallation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("✓ All tests passed! Installation OK.")
    else:
        print("✗ Some tests failed. Check the output above.")
    print("=" * 80 + "\n")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
