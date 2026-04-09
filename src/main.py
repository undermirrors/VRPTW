import time
import os
import sys
from typing import List, Tuple
import json

from data_loader import DataLoader, VRPTProblem
from genetic_algorithm import GeneticAlgorithm
from tabu_search import TabuSearch
from distance_utils import DistanceCalculator, SolutionEvaluator
from models import Solution


class VRPTPExperiment:
    """
    Manages VRPTW problem solving experiments.
    Compares performance of Genetic Algorithm and Tabu Search.
    """

    def __init__(self, data_directory: str = "data", results_directory: str = "results"):
        """
        Initialize experiment.

        Args:
            data_directory: Directory containing .vrp problem files
            results_directory: Directory to save results
        """
        self.data_directory = data_directory
        self.results_directory = results_directory
        self.problems: List[VRPTProblem] = []
        self.results = {}

        # Create results directory if it doesn't exist
        os.makedirs(results_directory, exist_ok=True)

    def load_problems(self, limit: int = None) -> None:
        """
        Load all problems from data directory.

        Args:
            limit: Maximum number of problems to load (None = all)
        """
        print("=" * 70)
        print("LOADING PROBLEMS")
        print("=" * 70)

        self.problems = DataLoader.load_all_problems(self.data_directory)

        if limit:
            self.problems = self.problems[:limit]

        print(f"\nLoaded {len(self.problems)} problems")
        print("-" * 70)

    def solve_with_genetic_algorithm(self, problem: VRPTProblem,
                                    population_size: int = 50,
                                    generations: int = 100,
                                    verbose: bool = False) -> Tuple[Solution, dict, float]:
        """
        Solve problem using Genetic Algorithm.

        Returns:
            (best_solution, statistics, execution_time)
        """
        ga = GeneticAlgorithm(
            depot=problem.depot,
            clients=problem.clients,
            capacity=problem.capacity,
            population_size=population_size,
            generations=generations,
            crossover_rate=0.8,
            mutation_rate=0.2,
            elite_size=2
        )

        start_time = time.time()
        best_solution = ga.evolve(verbose=verbose)
        exec_time = time.time() - start_time

        stats = ga.get_statistics()
        stats['execution_time'] = exec_time

        return best_solution, stats, exec_time

    def solve_with_tabu_search(self, problem: VRPTProblem,
                              max_iterations: int = 1000,
                              verbose: bool = False) -> Tuple[Solution, dict, float]:
        """
        Solve problem using Tabu Search.

        Returns:
            (best_solution, statistics, execution_time)
        """
        ts = TabuSearch(
            depot=problem.depot,
            clients=problem.clients,
            capacity=problem.capacity,
            max_iterations=max_iterations,
            tabu_tenure=None,  # Auto-calculate
            neighborhood_size=100,
            diversification_freq=50
        )

        start_time = time.time()
        best_solution = ts.search(verbose=verbose)
        exec_time = time.time() - start_time

        stats = ts.get_statistics()
        stats['execution_time'] = exec_time

        return best_solution, stats, exec_time

    def solve_problem(self, problem: VRPTProblem, verbose: bool = False) -> dict:
        """
        Solve a single problem with both algorithms and compare.

        Args:
            problem: The problem to solve
            verbose: Print detailed information

        Returns:
            Dictionary with results for both algorithms
        """
        problem_result = {
            'problem_name': problem.name,
            'num_clients': problem.num_clients,
            'capacity': problem.capacity,
        }

        if verbose:
            print(f"\n{'=' * 70}")
            print(f"PROBLEM: {problem.name}")
            print(f"{'=' * 70}")
            print(f"Clients: {problem.num_clients}, Capacity: {problem.capacity}")
            print(f"{'-' * 70}")

        # Solve with Genetic Algorithm
        if verbose:
            print("\n[1/2] Running Genetic Algorithm...")
        ga_solution, ga_stats, ga_time = self.solve_with_genetic_algorithm(
            problem, verbose=verbose
        )
        problem_result['genetic_algorithm'] = {
            'execution_time': ga_time,
            'distance': DistanceCalculator.solution_distance(ga_solution),
            'num_vehicles': ga_solution.get_num_vehicles(),
            'is_feasible': SolutionEvaluator.is_feasible(ga_solution, problem.clients),
            'solution_stats': SolutionEvaluator.get_solution_stats(ga_solution, problem.clients),
            'algorithm_stats': ga_stats,
        }

        # Solve with Tabu Search
        if verbose:
            print("\n[2/2] Running Tabu Search...")
        ts_solution, ts_stats, ts_time = self.solve_with_tabu_search(
            problem, verbose=verbose
        )
        problem_result['tabu_search'] = {
            'execution_time': ts_time,
            'distance': DistanceCalculator.solution_distance(ts_solution),
            'num_vehicles': ts_solution.get_num_vehicles(),
            'is_feasible': SolutionEvaluator.is_feasible(ts_solution, problem.clients),
            'solution_stats': SolutionEvaluator.get_solution_stats(ts_solution, problem.clients),
            'algorithm_stats': ts_stats,
        }

        if verbose:
            self._print_comparison(problem_result)

        return problem_result

    def _print_comparison(self, problem_result: dict) -> None:
        """Print comparison between algorithms for a problem."""
        print(f"\n{'=' * 70}")
        print("RESULTS COMPARISON")
        print(f"{'=' * 70}")

        ga_result = problem_result['genetic_algorithm']
        ts_result = problem_result['tabu_search']

        print(f"\n{'Metric':<30} {'GA':<20} {'TS':<20}")
        print(f"{'-' * 70}")

        print(f"{'Total Distance':<30} {ga_result['distance']:<20.2f} {ts_result['distance']:<20.2f}")
        print(f"{'Number of Vehicles':<30} {ga_result['num_vehicles']:<20} {ts_result['num_vehicles']:<20}")
        print(f"{'Feasible':<30} {str(ga_result['is_feasible']):<20} {str(ts_result['is_feasible']):<20}")
        print(f"{'Execution Time (s)':<30} {ga_result['execution_time']:<20.3f} {ts_result['execution_time']:<20.3f}")

        # Calculate winner
        ga_feasible = ga_result['is_feasible']
        ts_feasible = ts_result['is_feasible']

        if ga_feasible and ts_feasible:
            if ga_result['distance'] < ts_result['distance']:
                winner = "Genetic Algorithm (by distance)"
            elif ts_result['distance'] < ga_result['distance']:
                winner = "Tabu Search (by distance)"
            else:
                winner = "Tie (same distance)"
        elif ga_feasible:
            winner = "Genetic Algorithm (TS not feasible)"
        elif ts_feasible:
            winner = "Tabu Search (GA not feasible)"
        else:
            winner = "Neither (both infeasible)"

        print(f"\nWinner: {winner}")

    def run_experiments(self, verbose: bool = True, problem_limit: int = None) -> None:
        """
        Run experiments on all loaded problems.

        Args:
            verbose: Print detailed information
            problem_limit: Maximum number of problems to solve
        """
        self.load_problems(limit=problem_limit)

        self.results = {}

        for i, problem in enumerate(self.problems):
            print(f"\n[Problem {i + 1}/{len(self.problems)}]", end=" ")
            result = self.solve_problem(problem, verbose=verbose)
            self.results[problem.name] = result

        self.print_summary()
        self.save_results()

    def print_summary(self) -> None:
        """Print summary of all experiments."""
        print(f"\n\n{'=' * 100}")
        print("EXPERIMENTAL SUMMARY")
        print(f"{'=' * 100}")

        print(f"\n{'Problem':<20} {'GA Distance':<15} {'TS Distance':<15} {'Winner':<20} {'GA Time':<12} {'TS Time':<12}")
        print(f"{'-' * 100}")

        for problem_name, result in self.results.items():
            ga_result = result['genetic_algorithm']
            ts_result = result['tabu_search']

            ga_dist = ga_result['distance']
            ts_dist = ts_result['distance']

            if ga_dist < ts_dist:
                winner = "GA"
            elif ts_dist < ga_dist:
                winner = "TS"
            else:
                winner = "Tie"

            print(f"{problem_name:<20} {ga_dist:<15.2f} {ts_dist:<15.2f} {winner:<20} "
                  f"{ga_result['execution_time']:<12.3f} {ts_result['execution_time']:<12.3f}")

        # Calculate overall winner
        ga_wins = sum(1 for r in self.results.values()
                     if r['genetic_algorithm']['distance'] < r['tabu_search']['distance'])
        ts_wins = sum(1 for r in self.results.values()
                     if r['tabu_search']['distance'] < r['genetic_algorithm']['distance'])

        print(f"\n{'Overall:':<20} GA Wins: {ga_wins}, TS Wins: {ts_wins}")

    def save_results(self) -> None:
        """Save results to JSON file."""
        results_file = os.path.join(self.results_directory, "results.json")

        # Convert results to serializable format
        serializable_results = {}
        for problem_name, result in self.results.items():
            serializable_result = {
                'problem_name': result['problem_name'],
                'num_clients': result['num_clients'],
                'capacity': result['capacity'],
                'genetic_algorithm': {
                    'execution_time': result['genetic_algorithm']['execution_time'],
                    'distance': result['genetic_algorithm']['distance'],
                    'num_vehicles': result['genetic_algorithm']['num_vehicles'],
                    'is_feasible': result['genetic_algorithm']['is_feasible'],
                    'solution_stats': result['genetic_algorithm']['solution_stats'],
                },
                'tabu_search': {
                    'execution_time': result['tabu_search']['execution_time'],
                    'distance': result['tabu_search']['distance'],
                    'num_vehicles': result['tabu_search']['num_vehicles'],
                    'is_feasible': result['tabu_search']['is_feasible'],
                    'solution_stats': result['tabu_search']['solution_stats'],
                },
            }
            serializable_results[problem_name] = serializable_result

        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)

        print(f"\nResults saved to: {results_file}")


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("VRPTW - Vehicle Routing Problem with Time Windows")
    print("Genetic Algorithm + Tabu Search Comparison")
    print("=" * 70 + "\n")

    # Create experiment
    experiment = VRPTPExperiment(
        data_directory="data",
        results_directory="results"
    )

    # Run experiments
    # Use problem_limit to test on fewer problems quickly
    experiment.run_experiments(verbose=True, problem_limit=None)

    print("\n" + "=" * 70)
    print("Experiments completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
