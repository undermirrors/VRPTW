#!/usr/bin/env python3
"""
Example Script: VRP Mode (without Time Windows) and Vehicle Minimization

This script demonstrates how to use the new parameters:
- ignore_time_windows: True → solves VRP (Vehicle Routing Problem) instead of VRPTW
- minimize_vehicles: True → penalizes the number of vehicles used in the objective

Usage:
    python vrp_example.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import DataLoader
from genetic_algorithm import GeneticAlgorithm
from tabu_search import TabuSearch
from distance_utils import DistanceCalculator, SolutionEvaluator

try:
    from visualization.plotter import RouteVisualizer
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("Warning: Visualization module not available (matplotlib not installed)")


def example_vrptw_mode():
    """
    Example 1: Standard VRPTW mode (with time windows)
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Standard VRPTW Mode (with Time Windows)")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"Problem: {problem.name} ({problem.num_clients} clients)")

    # Solve with GA (VRPTW mode - default)
    ga = GeneticAlgorithm(
        problem.depot,
        problem.clients,
        problem.capacity,
        population_size=30,
        generations=30,
        ignore_time_windows=False,  # Default: respect time windows
        minimize_vehicles=False
    )

    print("\nRunning GA (VRPTW mode)...")
    ga_solution = ga.evolve(verbose=False)
    ga_distance = DistanceCalculator.solution_distance(ga_solution)
    ga_vehicles = ga_solution.get_num_vehicles()
    ga_feasible = SolutionEvaluator.is_feasible(ga_solution, problem.clients)

    print(f"  Distance: {ga_distance:.2f}")
    print(f"  Vehicles: {ga_vehicles}")
    print(f"  Feasible: {ga_feasible}")


def example_vrp_mode():
    """
    Example 2: VRP mode (ignore time windows, only capacity)
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: VRP Mode (Ignore Time Windows)")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"Problem: {problem.name} ({problem.num_clients} clients)")
    print("Note: Time windows are IGNORED in this mode")

    # Solve with GA (VRP mode - no time windows)
    ga = GeneticAlgorithm(
        problem.depot,
        problem.clients,
        problem.capacity,
        population_size=30,
        generations=30,
        ignore_time_windows=True,  # IGNORE time windows
        minimize_vehicles=False
    )

    print("\nRunning GA (VRP mode)...")
    ga_solution = ga.evolve(verbose=False)
    ga_distance = DistanceCalculator.solution_distance(ga_solution)
    ga_vehicles = ga_solution.get_num_vehicles()

    print(f"  Distance: {ga_distance:.2f}")
    print(f"  Vehicles: {ga_vehicles}")
    print(f"  Note: More feasible solutions expected (no time constraints)")

    # Visualize
    if VISUALIZATION_AVAILABLE:
        viz = RouteVisualizer(figsize=(12, 8))
        viz.plot_solution(
            ga_solution,
            title=f"VRP Solution - {problem.name} (No Time Windows)",
            show_legend=False,
            save_path="results/vrp_example_vrp_mode.png"
        )


def example_minimize_vehicles():
    """
    Example 3: VRP mode + minimize vehicles
    Tries to use fewer vehicles while still minimizing distance
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: VRP Mode + Minimize Vehicles")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"Problem: {problem.name} ({problem.num_clients} clients)")
    print("Objective: Minimize both distance AND number of vehicles")

    # Solve with GA (VRP mode + vehicle minimization)
    ga = GeneticAlgorithm(
        problem.depot,
        problem.clients,
        problem.capacity,
        population_size=30,
        generations=30,
        ignore_time_windows=True,
        minimize_vehicles=True,          # MINIMIZE vehicles
        vehicle_weight=100.0             # Weight for vehicle penalty
    )

    print("\nRunning GA (VRP + vehicle minimization)...")
    ga_solution = ga.evolve(verbose=False)
    ga_distance = DistanceCalculator.solution_distance(ga_solution)
    ga_vehicles = ga_solution.get_num_vehicles()

    print(f"  Distance: {ga_distance:.2f}")
    print(f"  Vehicles: {ga_vehicles}")
    print(f"  Note: Fewer vehicles expected (vehicle cost in objective)")

    # Visualize
    if VISUALIZATION_AVAILABLE:
        viz = RouteVisualizer(figsize=(12, 8))
        viz.plot_solution(
            ga_solution,
            title=f"VRP + Vehicle Minimization - {problem.name}",
            show_legend=False,
            save_path="results/vrp_example_minimize_vehicles.png"
        )


def example_tabu_search_vrp():
    """
    Example 4: Tabu Search in VRP mode with vehicle minimization
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Tabu Search - VRP + Vehicle Minimization")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"Problem: {problem.name} ({problem.num_clients} clients)")

    # Solve with TS (VRP mode + vehicle minimization)
    ts = TabuSearch(
        problem.depot,
        problem.clients,
        problem.capacity,
        max_iterations=500,
        ignore_time_windows=True,
        minimize_vehicles=True,
        vehicle_weight=100.0
    )

    print("\nRunning TS (VRP + vehicle minimization)...")
    ts_solution = ts.search(verbose=False)
    ts_distance = DistanceCalculator.solution_distance(ts_solution)
    ts_vehicles = ts_solution.get_num_vehicles()

    print(f"  Distance: {ts_distance:.2f}")
    print(f"  Vehicles: {ts_vehicles}")

    # Visualize
    if VISUALIZATION_AVAILABLE:
        viz = RouteVisualizer(figsize=(12, 8))
        viz.plot_solution(
            ts_solution,
            title=f"Tabu Search - VRP + Vehicle Minimization - {problem.name}",
            show_legend=False,
            save_path="results/vrp_example_ts_minimize_vehicles.png"
        )


def example_compare_modes():
    """
    Example 5: Compare different modes on the same problem
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Compare VRPTW vs VRP vs VRP+MinVehicles")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"Problem: {problem.name} ({problem.num_clients} clients)\n")

    results = {}

    # Mode 1: Standard VRPTW
    print("[1/3] VRPTW mode (with time windows)...")
    ga1 = GeneticAlgorithm(
        problem.depot, problem.clients, problem.capacity,
        population_size=20, generations=20,
        ignore_time_windows=False, minimize_vehicles=False
    )
    sol1 = ga1.evolve(verbose=False)
    results['VRPTW'] = {
        'distance': DistanceCalculator.solution_distance(sol1),
        'vehicles': sol1.get_num_vehicles(),
        'feasible': SolutionEvaluator.is_feasible(sol1, problem.clients)
    }

    # Mode 2: VRP (no time windows)
    print("[2/3] VRP mode (ignore time windows)...")
    ga2 = GeneticAlgorithm(
        problem.depot, problem.clients, problem.capacity,
        population_size=20, generations=20,
        ignore_time_windows=True, minimize_vehicles=False
    )
    sol2 = ga2.evolve(verbose=False)
    results['VRP'] = {
        'distance': DistanceCalculator.solution_distance(sol2),
        'vehicles': sol2.get_num_vehicles(),
        'feasible': True  # Always feasible in VRP mode (only capacity)
    }

    # Mode 3: VRP + minimize vehicles
    print("[3/3] VRP + Vehicle Minimization...")
    ga3 = GeneticAlgorithm(
        problem.depot, problem.clients, problem.capacity,
        population_size=20, generations=20,
        ignore_time_windows=True, minimize_vehicles=True,
        vehicle_weight=100.0
    )
    sol3 = ga3.evolve(verbose=False)
    results['VRP+MinVeh'] = {
        'distance': DistanceCalculator.solution_distance(sol3),
        'vehicles': sol3.get_num_vehicles(),
        'feasible': True
    }

    # Print comparison
    print("\n" + "-"*70)
    print(f"{'Mode':<20} {'Distance':<15} {'Vehicles':<12} {'Feasible':<10}")
    print("-"*70)
    for mode, result in results.items():
        print(f"{mode:<20} {result['distance']:<15.2f} {result['vehicles']:<12} {str(result['feasible']):<10}")

    print("\nObservations:")
    print("- VRPTW: Respects time windows, may need more vehicles")
    print("- VRP: Ignores time windows, fewer vehicles expected")
    print("- VRP+MinVeh: Actively minimizes vehicles in objective")

    # Visualize comparison
    if VISUALIZATION_AVAILABLE:
        viz = RouteVisualizer(figsize=(14, 6))
        viz.plot_comparison(
            sol2,
            sol3,
            title1="VRP (Distance Only)",
            title2="VRP + Vehicle Minimization",
            save_path="results/vrp_example_mode_comparison.png"
        )


def example_vehicle_weight_tuning():
    """
    Example 6: Effect of vehicle_weight parameter on solution
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Effect of Vehicle Weight Parameter")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"Problem: {problem.name}\n")
    print("Testing different vehicle_weight values:")
    print("(Higher weight = more emphasis on minimizing vehicles)\n")

    weights = [0.0, 50.0, 100.0, 200.0, 500.0]

    print(f"{'Weight':<10} {'Distance':<15} {'Vehicles':<12} {'Score':<15}")
    print("-"*55)

    for weight in weights:
        ga = GeneticAlgorithm(
            problem.depot, problem.clients, problem.capacity,
            population_size=20, generations=20,
            ignore_time_windows=True,
            minimize_vehicles=True,
            vehicle_weight=weight
        )
        solution = ga.evolve(verbose=False)
        distance = DistanceCalculator.solution_distance(solution)
        vehicles = solution.get_num_vehicles()

        # Score shows what the algorithm optimized for
        score = distance + weight * vehicles

        print(f"{weight:<10.0f} {distance:<15.2f} {vehicles:<12} {score:<15.2f}")

    print("\nObservation:")
    print("- Weight=0: Minimize only distance (standard VRP)")
    print("- Weight>0: Trade-off between distance and vehicle count")
    print("- Weight increases: More vehicles are sacrificed for lower total cost")

    # Visualize best and worst solutions from weight tuning
    if VISUALIZATION_AVAILABLE:
        viz = RouteVisualizer(figsize=(14, 6))

        # Find solutions with min and max vehicles
        solutions = []
        for weight in weights:
            ga = GeneticAlgorithm(
                problem.depot, problem.clients, problem.capacity,
                population_size=20, generations=20,
                ignore_time_windows=True,
                minimize_vehicles=True,
                vehicle_weight=weight
            )
            solutions.append(ga.evolve(verbose=False))

        # Compare solution with weight=0 vs weight=500
        viz.plot_comparison(
            solutions[0],
            solutions[-1],
            title1=f"Weight=0 (Distance Only) - {solutions[0].get_num_vehicles()} vehicles",
            title2=f"Weight=500 (Minimize Vehicles) - {solutions[-1].get_num_vehicles()} vehicles",
            save_path="results/vrp_example_weight_comparison.png"
        )


def example_convergence_visualization():
    """
    Example 7: Visualize algorithm convergence history
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Algorithm Convergence Visualization")
    print("="*70)

    problem = DataLoader.load_problem("data/data101.vrp")
    print(f"Problem: {problem.name}\n")

    if not VISUALIZATION_AVAILABLE:
        print("⚠ Visualization module not available")
        return

    viz = RouteVisualizer(figsize=(14, 6))

    # GA convergence
    print("[1/2] Running GA with convergence tracking...")
    ga = GeneticAlgorithm(
        problem.depot,
        problem.clients,
        problem.capacity,
        population_size=30,
        generations=50,
        ignore_time_windows=True,
        minimize_vehicles=True,
        vehicle_weight=100.0
    )
    ga_solution = ga.evolve(verbose=False)

    print("[2/2] Running TS with convergence tracking...")
    ts = TabuSearch(
        problem.depot,
        problem.clients,
        problem.capacity,
        max_iterations=500,
        ignore_time_windows=True,
        minimize_vehicles=True,
        vehicle_weight=100.0
    )
    ts_solution = ts.search(verbose=False)

    # Plot convergence histories
    print("\nGenerating convergence plots...")

    viz.plot_convergence(
        ga.generation_history,
        algorithm_name="Genetic Algorithm",
        save_path="results/vrp_example_ga_convergence.png"
    )

    viz.plot_convergence(
        ts.best_history,
        algorithm_name="Tabu Search",
        save_path="results/vrp_example_ts_convergence.png"
    )

    print("  ✓ GA convergence saved")
    print("  ✓ TS convergence saved")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("VRP/VRPTW Mode Examples - Vehicle Minimization")
    print("="*70)

    try:
        example_vrptw_mode()
        example_vrp_mode()
        example_minimize_vehicles()
        example_tabu_search_vrp()
        example_compare_modes()
        example_vehicle_weight_tuning()
        example_convergence_visualization()

        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70)

        if VISUALIZATION_AVAILABLE:
            print("\n✓ Visualizations Generated:")
            print("  results/vrp_example_vrp_mode.png")
            print("  results/vrp_example_minimize_vehicles.png")
            print("  results/vrp_example_ts_minimize_vehicles.png")
            print("  results/vrp_example_mode_comparison.png")
            print("  results/vrp_example_weight_comparison.png")
            print("  results/vrp_example_ga_convergence.png")
            print("  results/vrp_example_ts_convergence.png")
        else:
            print("\n⚠ Visualizations skipped (matplotlib not installed)")

        print("\nKey Parameters:")
        print("  ignore_time_windows=False  → VRPTW (with time windows)")
        print("  ignore_time_windows=True   → VRP (without time windows)")
        print("  minimize_vehicles=False    → Minimize only distance")
        print("  minimize_vehicles=True     → Minimize distance + vehicles")
        print("  vehicle_weight=X           → Weight for vehicle cost")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
