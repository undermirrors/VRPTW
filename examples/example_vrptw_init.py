"""
Example demonstrating the new VRPTW initialization strategy.

This shows how to:
1. Use the Progressive Vehicle Reduction strategy for VRPTW
2. Pass use_vrptw_init=True to Genetic Algorithm and Tabu Search
3. See the difference in results

The new strategy ensures that solutions start feasible and are progressively improved.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader
from genetic_algorithm import GeneticAlgorithm
from tabu_search import TabuSearch
from distance_utils import DistanceCalculator, SolutionEvaluator
from initialization_strategy import InitializationStrategy
import time


def demonstrate_initialization_strategies():
    """Show different initialization strategies."""
    print("\n" + "=" * 80)
    print("VRPTW INITIALIZATION STRATEGIES DEMONSTRATION")
    print("=" * 80)

    # Load a problem
    problems = DataLoader.load_all_problems("data", limit=1)
    if not problems:
        print("No problems found in data directory. Please add .vrp files to the data folder.")
        return

    problem = problems[0]
    print(f"\nProblem: {problem.name}")
    print(f"  Clients: {problem.num_clients}")
    print(f"  Capacity: {problem.capacity}")

    # Strategy 1: Progressive Vehicle Reduction
    print("\n" + "-" * 80)
    print("Strategy 1: Progressive Vehicle Reduction (VRPTW-specific)")
    print("-" * 80)
    start_time = time.time()
    solution, min_vehicles = InitializationStrategy.progressive_vehicle_reduction(
        problem.depot, problem.clients, problem.capacity,
        ignore_time_windows=False, verbose=True
    )
    elapsed = time.time() - start_time
    distance = DistanceCalculator.solution_distance(solution)
    feasible = SolutionEvaluator.is_feasible(solution, problem.clients)
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Distance: {distance:.2f}")
    print(f"  Vehicles: {solution.get_num_vehicles()}")
    print(f"  Feasible: {feasible}")

    # Strategy 2: Best Construction Heuristic
    print("\n" + "-" * 80)
    print("Strategy 2: Best Construction Heuristic (Fast, but may need fallback)")
    print("-" * 80)
    start_time = time.time()
    solution2 = InitializationStrategy.best_construction_heuristic(
        problem.depot, problem.clients, problem.capacity,
        ignore_time_windows=False, verbose=True
    )
    elapsed = time.time() - start_time
    distance2 = DistanceCalculator.solution_distance(solution2)
    feasible2 = SolutionEvaluator.is_feasible(solution2, problem.clients)
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Distance: {distance2:.2f}")
    print(f"  Vehicles: {solution2.get_num_vehicles()}")
    print(f"  Feasible: {feasible2}")

    # Strategy 3: Hybrid Approach
    print("\n" + "-" * 80)
    print("Strategy 3: Hybrid Approach (Fast with fallback to progressive reduction)")
    print("-" * 80)
    start_time = time.time()
    solution3, stats = InitializationStrategy.hybrid_approach(
        problem.depot, problem.clients, problem.capacity,
        ignore_time_windows=False, verbose=True
    )
    elapsed = time.time() - start_time
    distance3 = DistanceCalculator.solution_distance(solution3)
    feasible3 = SolutionEvaluator.is_feasible(solution3, problem.clients)
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Distance: {distance3:.2f}")
    print(f"  Vehicles: {solution3.get_num_vehicles()}")
    print(f"  Feasible: {feasible3}")
    print(f"  Strategy Used: {stats['strategy_used']}")
    print(f"  Reason: {stats['reason']}")


def demonstrate_algorithm_with_vrptw_init():
    """Show how to use VRPTW initialization with GA and TS."""
    print("\n" + "=" * 80)
    print("VRPTW INITIALIZATION IN GENETIC ALGORITHM & TABU SEARCH")
    print("=" * 80)

    # Load a problem
    problems = DataLoader.load_all_problems("data", limit=1)
    if not problems:
        print("No problems found in data directory. Please add .vrp files to the data folder.")
        return

    problem = problems[0]
    print(f"\nProblem: {problem.name}")
    print(f"  Clients: {problem.num_clients}")
    print(f"  Capacity: {problem.capacity}")

    # Test Genetic Algorithm with VRPTW initialization
    print("\n" + "-" * 80)
    print("Genetic Algorithm with VRPTW Initialization (use_vrptw_init=True)")
    print("-" * 80)

    ga_vrptw = GeneticAlgorithm(
        depot=problem.depot,
        clients=problem.clients,
        capacity=problem.capacity,
        population_size=30,
        generations=50,
        use_vrptw_init=True
    )

    start_time = time.time()
    solution_ga = ga_vrptw.evolve(verbose=True)
    elapsed_ga = time.time() - start_time

    print(f"\n  Time: {elapsed_ga:.2f}s")
    print(f"  Final Distance: {DistanceCalculator.solution_distance(solution_ga):.2f}")
    print(f"  Final Vehicles: {solution_ga.get_num_vehicles()}")
    print(f"  Feasible: {SolutionEvaluator.is_feasible(solution_ga, problem.clients)}")
    print(f"  Initialization Strategy: {ga_vrptw.initialization_stats.get('strategy_used', 'N/A')}")

    # Test Tabu Search with VRPTW initialization
    print("\n" + "-" * 80)
    print("Tabu Search with VRPTW Initialization (use_vrptw_init=True)")
    print("-" * 80)

    ts_vrptw = TabuSearch(
        depot=problem.depot,
        clients=problem.clients,
        capacity=problem.capacity,
        max_iterations=500,
        use_vrptw_init=True
    )

    start_time = time.time()
    solution_ts = ts_vrptw.search(verbose=True)
    elapsed_ts = time.time() - start_time

    print(f"\n  Time: {elapsed_ts:.2f}s")
    print(f"  Final Distance: {DistanceCalculator.solution_distance(solution_ts):.2f}")
    print(f"  Final Vehicles: {solution_ts.get_num_vehicles()}")
    print(f"  Feasible: {SolutionEvaluator.is_feasible(solution_ts, problem.clients)}")
    print(f"  Initialization Strategy: {ts_vrptw.initialization_stats.get('strategy_used', 'N/A')}")


if __name__ == "__main__":
    demonstrate_initialization_strategies()
    demonstrate_algorithm_with_vrptw_init()

    print("\n" + "=" * 80)
    print("KEY BENEFITS OF NEW VRPTW INITIALIZATION")
    print("=" * 80)
    print("""
1. GUARANTEED FEASIBILITY: Solutions start feasible by using one vehicle per client,
   then intelligently reducing vehicles while maintaining feasibility.

2. BETTER STARTING POINT: The progressive reduction finds the minimum viable
   configuration, giving optimization algorithms a better foundation.

3. TIME WINDOWS AWARE: The initialization respects time window constraints from
   the start, unlike generic heuristics that may struggle with VRPTW.

4. FALLBACK STRATEGY: If fast heuristics fail, the system automatically uses
   progressive reduction as a safety net.

5. HYBRID APPROACH: The hybrid strategy tries fast methods first, then falls back
   to guaranteed methods if needed.

Usage:
  - Set use_vrptw_init=True when creating GA or TS for VRPTW problems
  - The algorithms will automatically use progressive vehicle reduction
  - This ensures your solutions are always feasible and well-optimized
    """)
    print("=" * 80 + "\n")
