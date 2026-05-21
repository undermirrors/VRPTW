#!/usr/bin/env python3
"""
Algorithm Comparison Example.

Demonstrates how to compare different solution generation methods
on VRPTW problems.

Usage:
    python examples/compare_algorithms.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Location, TimeWindow, Client, Depot
from solution_generator import SolutionGenerator
from distance_utils import DistanceCalculator
import time


def create_test_problem(num_clients=10):
    """Create a test VRPTW problem."""
    depot = Depot(0, Location(0, 0), 100)

    clients = []
    for i in range(1, num_clients + 1):
        x = 10 + (i % 5) * 20
        y = 10 + (i // 5) * 20
        clients.append(
            Client(
                id=i,
                location=Location(x, y),
                demand=10,
                time_window=TimeWindow(0, 1000),
                service_time=5
            )
        )

    return depot, clients


def compare_solution_methods(depot, clients, num_runs=5):
    """Compare different solution generation methods."""

    print("\n" + "=" * 80)
    print("SOLUTION GENERATION METHOD COMPARISON")
    print("=" * 80)
    print(f"Problem: {len(clients)} clients, Capacity: {depot.capacity}")
    print(f"Runs: {num_runs} per method\n")

    methods = [
        ('Random', SolutionGenerator.generate_random_solution),
        ('Nearest Neighbor', SolutionGenerator.nearest_neighbor),
        ('Greedy Insertion', SolutionGenerator.greedy_insertion),
    ]

    results = {}

    for method_name, method_func in methods:
        print(f"Running {method_name}...")
        method_results = []

        for run in range(num_runs):
            try:
                start = time.time()
                solution = method_func(depot, clients, depot.capacity)
                elapsed = time.time() - start

                distance = DistanceCalculator.solution_distance(solution)
                vehicles = solution.get_num_vehicles()
                feasible = solution.is_feasible()

                method_results.append({
                    'distance': distance,
                    'vehicles': vehicles,
                    'time': elapsed,
                    'feasible': feasible
                })

                status = "✓" if feasible else "✗"
                print(f"  Run {run+1}: {status} Distance={distance:.2f}, Vehicles={vehicles}, Time={elapsed:.3f}s")

            except Exception as e:
                print(f"  Run {run+1}: ERROR - {e}")

        if method_results:
            results[method_name] = method_results
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    for method_name, method_results in results.items():
        if not method_results:
            continue

        avg_dist = sum(r['distance'] for r in method_results) / len(method_results)
        avg_vehicles = sum(r['vehicles'] for r in method_results) / len(method_results)
        avg_time = sum(r['time'] for r in method_results) / len(method_results)
        feasible_pct = sum(1 for r in method_results if r['feasible']) / len(method_results) * 100

        print(f"\n{method_name}:")
        print(f"  Avg Distance: {avg_dist:.2f}")
        print(f"  Avg Vehicles: {avg_vehicles:.1f}")
        print(f"  Avg Time: {avg_time:.3f}s")
        print(f"  Feasibility: {feasible_pct:.0f}%")

    # Best method by distance
    print(f"\n{'─' * 80}")
    best_method = min(results.items(),
                      key=lambda x: sum(r['distance'] for r in x[1]) / len(x[1]))
    print(f"Best method (by avg distance): {best_method[0]}")

    best_time = min(results.items(),
                   key=lambda x: sum(r['time'] for r in x[1]) / len(x[1]))
    print(f"Fastest method (by avg time): {best_time[0]}")

    print("\n" + "=" * 80 + "\n")


def main():
    """Main execution."""
    try:
        # Create test problem
        depot, clients = create_test_problem(num_clients=20)

        # Compare methods
        compare_solution_methods(depot, clients, num_runs=5)

        print("✓ Comparison complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
