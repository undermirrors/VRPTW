"""
Example Usage Script for VRPTW Solver

This script demonstrates how to use the VRPTW solver with both Genetic Algorithm
and Tabu Search algorithms. It includes examples of:
1. Loading problem instances
2. Solving with different algorithms
3. Evaluating and comparing solutions
4. Visualizing results
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import DataLoader
from genetic_algorithm import GeneticAlgorithm
from tabu_search import TabuSearch
from distance_utils import DistanceCalculator, SolutionEvaluator
from solution_generator import SolutionGenerator


def example_1_basic_usage():
    """
    Example 1: Basic usage - Load problem and solve with GA
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Usage - Genetic Algorithm")
    print("="*70)

    # Load a problem
    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"\nLoaded problem: {problem.name}")
    print(f"  Clients: {problem.num_clients}")
    print(f"  Vehicle capacity: {problem.capacity}")

    # Create and run GA
    ga = GeneticAlgorithm(
        depot=problem.depot,
        clients=problem.clients,
        capacity=problem.capacity,
        population_size=50,
        generations=50,  # Reduced for quick demo
        crossover_rate=0.8,
        mutation_rate=0.2
    )

    print("\nRunning Genetic Algorithm...")
    solution = ga.evolve(verbose=False)

    # Evaluate solution
    distance = DistanceCalculator.solution_distance(solution)
    vehicles = solution.get_num_vehicles()
    feasible = SolutionEvaluator.is_feasible(solution, problem.clients)

    print(f"\nResults:")
    print(f"  Total distance: {distance:.2f}")
    print(f"  Vehicles used: {vehicles}")
    print(f"  Feasible: {feasible}")


def example_2_tabu_search():
    """
    Example 2: Solve with Tabu Search
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Tabu Search")
    print("="*70)

    # Load problem
    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"\nLoaded problem: {problem.name}")

    # Create and run TS
    ts = TabuSearch(
        depot=problem.depot,
        clients=problem.clients,
        capacity=problem.capacity,
        max_iterations=500,  # Reduced for quick demo
        tabu_tenure=None,  # Auto-calculate
        neighborhood_size=100
    )

    print("\nRunning Tabu Search...")
    solution = ts.search(verbose=False)

    # Evaluate solution
    distance = DistanceCalculator.solution_distance(solution)
    vehicles = solution.get_num_vehicles()
    feasible = SolutionEvaluator.is_feasible(solution, problem.clients)

    print(f"\nResults:")
    print(f"  Total distance: {distance:.2f}")
    print(f"  Vehicles used: {vehicles}")
    print(f"  Feasible: {feasible}")


def example_3_comparison():
    """
    Example 3: Compare GA and TS on the same problem
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Algorithm Comparison")
    print("="*70)

    # Load problem
    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"\nProblem: {problem.name} ({problem.num_clients} clients)")

    # Solve with GA
    print("\n[1/2] Running Genetic Algorithm...")
    ga = GeneticAlgorithm(
        problem.depot, problem.clients, problem.capacity,
        population_size=50, generations=50
    )
    ga_solution = ga.evolve(verbose=False)
    ga_distance = DistanceCalculator.solution_distance(ga_solution)
    ga_vehicles = ga_solution.get_num_vehicles()
    ga_feasible = SolutionEvaluator.is_feasible(ga_solution, problem.clients)

    # Solve with TS
    print("[2/2] Running Tabu Search...")
    ts = TabuSearch(
        problem.depot, problem.clients, problem.capacity,
        max_iterations=500
    )
    ts_solution = ts.search(verbose=False)
    ts_distance = DistanceCalculator.solution_distance(ts_solution)
    ts_vehicles = ts_solution.get_num_vehicles()
    ts_feasible = SolutionEvaluator.is_feasible(ts_solution, problem.clients)

    # Compare
    print("\n" + "-"*70)
    print(f"{'Metric':<25} {'GA':<20} {'TS':<20}")
    print("-"*70)
    print(f"{'Distance':<25} {ga_distance:<20.2f} {ts_distance:<20.2f}")
    print(f"{'Vehicles':<25} {ga_vehicles:<20} {ts_vehicles:<20}")
    print(f"{'Feasible':<25} {str(ga_feasible):<20} {str(ts_feasible):<20}")

    if ga_distance < ts_distance:
        print(f"\n✓ Winner: Genetic Algorithm (by {ts_distance - ga_distance:.2f})")
    else:
        print(f"\n✓ Winner: Tabu Search (by {ga_distance - ts_distance:.2f})")


def example_4_initial_solutions():
    """
    Example 4: Compare different initial solution construction methods
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Initial Solution Construction Methods")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"\nProblem: {problem.name}")

    methods = [
        ("Random", lambda: SolutionGenerator.generate_random_solution(
            problem.depot, problem.clients, problem.capacity)),
        ("Nearest Neighbor", lambda: SolutionGenerator.nearest_neighbor(
            problem.depot, problem.clients, problem.capacity)),
        ("Greedy Insertion", lambda: SolutionGenerator.greedy_insertion(
            problem.depot, problem.clients, problem.capacity)),
        ("Clarke-Wright", lambda: SolutionGenerator.savings_algorithm(
            problem.depot, problem.clients, problem.capacity)),
    ]

    print(f"\n{'Method':<25} {'Distance':<15} {'Vehicles':<12} {'Feasible':<10}")
    print("-"*65)

    for name, method in methods:
        solution = method()
        distance = DistanceCalculator.solution_distance(solution)
        vehicles = solution.get_num_vehicles()
        feasible = SolutionEvaluator.is_feasible(solution, problem.clients)

        print(f"{name:<25} {distance:<15.2f} {vehicles:<12} {str(feasible):<10}")


def example_5_solution_statistics():
    """
    Example 5: Get detailed statistics about a solution
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Solution Statistics")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")

    # Generate a solution
    ga = GeneticAlgorithm(problem.depot, problem.clients, problem.capacity,
                         population_size=30, generations=30)
    solution = ga.evolve(verbose=False)

    # Get detailed statistics
    stats = SolutionEvaluator.get_solution_stats(solution, problem.clients)

    print(f"\nSolution Statistics for {problem.name}:")
    print("-"*50)
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    # Get load distribution
    load_dist = SolutionEvaluator.get_route_load_distribution(solution)
    print(f"\nLoad Distribution by Route:")
    for i, load in enumerate(load_dist):
        percentage = load * 100
        bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
        print(f"  Route {i+1}: {bar} {percentage:.1f}%")


def example_6_multiple_problems():
    """
    Example 6: Run on multiple problems
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Solve Multiple Problems")
    print("="*70)

    # Load first 3 problems
    all_problems = DataLoader.load_all_problems("data")
    problems = all_problems[:3]

    print(f"\nSolving {len(problems)} problems with TS (quick demo)...")
    print(f"{'Problem':<15} {'Clients':<10} {'Distance':<15} {'Vehicles':<10}")
    print("-"*50)

    for problem in problems:
        ts = TabuSearch(
            problem.depot, problem.clients, problem.capacity,
            max_iterations=200  # Quick
        )
        solution = ts.search(verbose=False)
        distance = DistanceCalculator.solution_distance(solution)
        vehicles = solution.get_num_vehicles()

        print(f"{problem.name:<15} {problem.num_clients:<10} {distance:<15.2f} {vehicles:<10}")


def example_7_custom_algorithm_parameters():
    """
    Example 7: Use custom algorithm parameters for different quality/speed tradeoffs
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Quality vs Speed Tradeoffs")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")

    configs = [
        ("Fast (GA)", GeneticAlgorithm(
            problem.depot, problem.clients, problem.capacity,
            population_size=20, generations=500)),
        ("Balanced (GA)", GeneticAlgorithm(
            problem.depot, problem.clients, problem.capacity,
            population_size=50, generations=50)),
        ("High-Quality (GA)", GeneticAlgorithm(
            problem.depot, problem.clients, problem.capacity,
            population_size=100, generations=100)),
    ]

    print(f"\n{'Config':<25} {'Distance':<15} {'Time (s)':<12}")
    print("-"*50)

    import time
    for name, ga in configs:
        start = time.time()
        solution = ga.evolve(verbose=False)
        elapsed = time.time() - start
        distance = DistanceCalculator.solution_distance(solution)

        print(f"{name:<25} {distance:<15.2f} {elapsed:<12.2f}")


def example_8_visualize_solution():
    """
    Example 8: Visualize a solution (requires visualization module)
    """
    print("\n" + "="*70)
    print("EXAMPLE 8: Visualization")
    print("="*70)

    try:
        from visualization.plotter import RouteVisualizer

        problem = DataLoader.load_problem("data/data101.vrp")

        # Solve problem
        ga = GeneticAlgorithm(problem.depot, problem.clients, problem.capacity,
                             population_size=30, generations=30)
        solution = ga.evolve(verbose=False)

        # Create visualizer
        viz = RouteVisualizer(figsize=(14, 10), dpi=100)

        print("\nGenerating visualizations...")

        # Plot solution
        viz.plot_solution(
            solution,
            title=f"VRPTW Solution - {problem.name}",
            show_time_windows=False,
            show_demands=False,
            save_path="results/example_solution.png"
        )

        # Plot convergence
        viz.plot_convergence(
            ga.generation_history,
            algorithm_name="Genetic Algorithm",
            save_path="results/example_convergence.png"
        )

        print("✓ Visualizations saved to results/")

    except ImportError:
        print("Visualization module not available (matplotlib not installed)")


def main():
    """
    Run all examples
    """
    print("\n" + "="*70)
    print("VRPTW SOLVER - EXAMPLE USAGE")
    print("="*70)
    print("\nThis script demonstrates various features of the VRPTW solver")

    try:
        # Run examples
        # example_1_basic_usage()
        # example_2_tabu_search()
        # example_3_comparison()
        # example_4_initial_solutions()
        # example_5_solution_statistics()
        # example_6_multiple_problems()
        # example_7_custom_algorithm_parameters()
        example_8_visualize_solution()

        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Read TECHNICAL_DOCUMENTATION.md for algorithm details")
        print("  2. Check src/main.py for running full experiments")
        print("  3. Modify parameters to find best solutions for your problems")
        print("="*70 + "\n")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Make sure you're in the VRPTW directory and data files are present.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
