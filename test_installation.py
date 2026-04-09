#!/usr/bin/env python3
"""
Installation Test Script for VRPTW

This script verifies that all components are correctly installed and working.
Run it after installing dependencies to ensure the project is ready to use.

Usage:
    python test_installation.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_imports():
    """Test that all modules can be imported."""
    print("\n" + "="*70)
    print("TEST 1: Module Imports")
    print("="*70)

    modules = [
        ("models", "from models import Location, Client, Route, Solution"),
        ("data_loader", "from data_loader import DataLoader, VRPTProblem"),
        ("distance_utils", "from distance_utils import DistanceCalculator, SolutionEvaluator"),
        ("solution_generator", "from solution_generator import SolutionGenerator"),
        ("neighborhood", "from neighborhood import NeighborhoodManager"),
        ("genetic_algorithm", "from genetic_algorithm import GeneticAlgorithm"),
        ("tabu_search", "from tabu_search import TabuSearch"),
    ]

    all_passed = True
    for module_name, import_stmt in modules:
        try:
            exec(import_stmt)
            print(f"  ✓ {module_name}")
        except Exception as e:
            print(f"  ✗ {module_name}: {e}")
            all_passed = False

    return all_passed


def test_data_loading():
    """Test that problem files can be loaded."""
    print("\n" + "="*70)
    print("TEST 2: Data Loading")
    print("="*70)

    try:
        from data_loader import DataLoader

        # Check if data directory exists
        if not os.path.isdir("data"):
            print("  ✗ data/ directory not found")
            return False

        # Try to load one problem
        vrp_files = [f for f in os.listdir("data") if f.endswith('.vrp')]

        if not vrp_files:
            print("  ✗ No .vrp files found in data/")
            return False

        # Load first problem
        test_file = os.path.join("data", vrp_files[0])
        problem = DataLoader.load_problem(test_file)

        print(f"  ✓ Loaded problem: {problem.name}")
        print(f"    - Clients: {problem.num_clients}")
        print(f"    - Capacity: {problem.capacity}")
        print(f"    - Depot: {problem.depot.id}")

        return True
    except Exception as e:
        print(f"  ✗ Data loading failed: {e}")
        return False


def test_solution_generation():
    """Test that initial solutions can be generated."""
    print("\n" + "="*70)
    print("TEST 3: Solution Generation")
    print("="*70)

    try:
        from data_loader import DataLoader
        from solution_generator import SolutionGenerator
        from distance_utils import DistanceCalculator

        # Load a small problem
        vrp_files = [f for f in os.listdir("data") if f.endswith('.vrp')]
        test_file = os.path.join("data", vrp_files[0])
        problem = DataLoader.load_problem(test_file)

        # Test different generation methods
        methods = [
            ("Random", SolutionGenerator.generate_random_solution),
            ("Nearest Neighbor", SolutionGenerator.nearest_neighbor),
            ("Greedy Insertion", SolutionGenerator.greedy_insertion),
            ("Clarke-Wright", SolutionGenerator.savings_algorithm),
        ]

        all_generated = True
        for name, method in methods:
            try:
                solution = method(problem.depot, problem.clients, problem.capacity)
                distance = DistanceCalculator.solution_distance(solution)
                vehicles = solution.get_num_vehicles()
                print(f"  ✓ {name}: distance={distance:.2f}, vehicles={vehicles}")
            except Exception as e:
                print(f"  ✗ {name}: {e}")
                all_generated = False

        return all_generated
    except Exception as e:
        print(f"  ✗ Solution generation failed: {e}")
        return False


def test_genetic_algorithm():
    """Test that Genetic Algorithm can run."""
    print("\n" + "="*70)
    print("TEST 4: Genetic Algorithm")
    print("="*70)

    try:
        from data_loader import DataLoader
        from genetic_algorithm import GeneticAlgorithm
        from distance_utils import DistanceCalculator

        # Load a small problem
        vrp_files = [f for f in os.listdir("data") if f.endswith('.vrp')]
        test_file = os.path.join("data", vrp_files[0])
        problem = DataLoader.load_problem(test_file)

        # Run GA with minimal settings
        ga = GeneticAlgorithm(
            depot=problem.depot,
            clients=problem.clients,
            capacity=problem.capacity,
            population_size=10,
            generations=5
        )

        print("  Running GA with 10 population, 5 generations...")
        solution = ga.evolve(verbose=False)
        distance = DistanceCalculator.solution_distance(solution)
        vehicles = solution.get_num_vehicles()

        print(f"  ✓ GA completed successfully")
        print(f"    - Final distance: {distance:.2f}")
        print(f"    - Vehicles: {vehicles}")

        return True
    except Exception as e:
        print(f"  ✗ Genetic Algorithm failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tabu_search():
    """Test that Tabu Search can run."""
    print("\n" + "="*70)
    print("TEST 5: Tabu Search")
    print("="*70)

    try:
        from data_loader import DataLoader
        from tabu_search import TabuSearch
        from distance_utils import DistanceCalculator

        # Load a small problem
        vrp_files = [f for f in os.listdir("data") if f.endswith('.vrp')]
        test_file = os.path.join("data", vrp_files[0])
        problem = DataLoader.load_problem(test_file)

        # Run TS with minimal settings
        ts = TabuSearch(
            depot=problem.depot,
            clients=problem.clients,
            capacity=problem.capacity,
            max_iterations=50
        )

        print("  Running TS with 50 iterations...")
        solution = ts.search(verbose=False)
        distance = DistanceCalculator.solution_distance(solution)
        vehicles = solution.get_num_vehicles()

        print(f"  ✓ TS completed successfully")
        print(f"    - Final distance: {distance:.2f}")
        print(f"    - Vehicles: {vehicles}")

        return True
    except Exception as e:
        print(f"  ✗ Tabu Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """Test that visualization module works."""
    print("\n" + "="*70)
    print("TEST 6: Visualization")
    print("="*70)

    try:
        from visualization.plotter import RouteVisualizer

        viz = RouteVisualizer(figsize=(10, 8))
        print(f"  ✓ RouteVisualizer imported successfully")
        print(f"    - Available methods:")
        print(f"      - plot_solution()")
        print(f"      - plot_comparison()")
        print(f"      - plot_convergence()")
        print(f"      - plot_distance_comparison()")

        return True
    except Exception as e:
        print(f"  ✗ Visualization module failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("VRPTW Installation Test")
    print("="*70)

    results = []

    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Data Loading", test_data_loading()))
    results.append(("Solution Generation", test_solution_generation()))
    results.append(("Genetic Algorithm", test_genetic_algorithm()))
    results.append(("Tabu Search", test_tabu_search()))
    results.append(("Visualization", test_visualization()))

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {test_name:<30} {status}")

    print(f"\n  Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n" + "="*70)
        print("✓ All tests passed! Installation is correct.")
        print("="*70)
        print("\nYou can now run:")
        print("  - python src/main.py          (Full experiments)")
        print("  - python example_usage.py     (8 examples)")
        print("  - See README.md for more info")
        print("="*70 + "\n")
        return 0
    else:
        print("\n" + "="*70)
        print("✗ Some tests failed. Please check the output above.")
        print("="*70)
        print("\nTroubleshooting:")
        print("  1. Ensure you're in the VRPTW directory")
        print("  2. Activate the virtual environment: source .venv/bin/activate")
        print("  3. Install requirements: pip install -r requirements.txt")
        print("  4. Check that data/*.vrp files exist")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
