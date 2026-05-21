#!/usr/bin/env python3
import json
import time
from pathlib import Path

from src.data_loader import DataLoader
from src.genetic_algorithm import GeneticAlgorithm
from src.tabu_search import TabuSearch
from src.distance_utils import DistanceCalculator, SolutionEvaluator


def solve_problem(problem, use_time_windows: bool, verbose: bool = True) -> dict:
    mode_name = "VRPTW" if use_time_windows else "VRP"

    if verbose:
        print(f"\n--- {problem.name} | Mode {mode_name} ---")

    DistanceCalculator.clear_cache()

    # Genetic Algorithm
    ga_start = time.perf_counter()
    ga = GeneticAlgorithm(
        depot=problem.depot,
        clients=problem.clients,
        capacity=problem.capacity,
        use_time_windows=use_time_windows,
    )
    ga_solution = ga.evolve(verbose=verbose)
    ga_time = time.perf_counter() - ga_start

    ga_distance = DistanceCalculator.solution_distance(ga_solution)
    ga_stats = SolutionEvaluator.get_solution_stats(
        ga_solution,
        problem.clients,
        use_time_windows=use_time_windows,
    )

    # Tabu Search
    ts_start = time.perf_counter()
    ts = TabuSearch(
        depot=problem.depot,
        clients=problem.clients,
        capacity=problem.capacity,
        use_time_windows=use_time_windows,
    )
    ts_solution = ts.search(verbose=verbose)
    ts_time = time.perf_counter() - ts_start

    ts_distance = DistanceCalculator.solution_distance(ts_solution)
    ts_stats = SolutionEvaluator.get_solution_stats(
        ts_solution,
        problem.clients,
        use_time_windows=use_time_windows,
    )

    if use_time_windows:
        if ga_stats["feasible"] and not ts_stats["feasible"]:
            winner = "GA (TS infeasible)"
        elif ts_stats["feasible"] and not ga_stats["feasible"]:
            winner = "TS (GA infeasible)"
        elif ga_stats["feasible"] and ts_stats["feasible"]:
            winner = (
                "GA"
                if (ga_solution.get_num_vehicles(), ga_distance)
                < (ts_solution.get_num_vehicles(), ts_distance)
                else "TS"
            )
        else:
            winner = "None (both infeasible)"
    else:
        winner = (
            "GA"
            if (ga_solution.get_num_vehicles(), ga_distance)
            < (ts_solution.get_num_vehicles(), ts_distance)
            else "TS"
        )

    result = {
        "problem_name": problem.name,
        "mode": mode_name,
        "use_time_windows": use_time_windows,
        "num_clients": problem.num_clients,
        "capacity": problem.capacity,
        "genetic_algorithm": {
            "execution_time": ga_time,
            "distance": ga_distance,
            "num_vehicles": ga_solution.get_num_vehicles(),
            "is_feasible": ga_stats["feasible"],
            "solution_stats": ga_stats,
        },
        "tabu_search": {
            "execution_time": ts_time,
            "distance": ts_distance,
            "num_vehicles": ts_solution.get_num_vehicles(),
            "is_feasible": ts_stats["feasible"],
            "solution_stats": ts_stats,
        },
        "winner": winner,
    }

    if verbose:
        print(
            f"GA -> dist={ga_distance:.2f}, "
            f"K={ga_solution.get_num_vehicles()}, "
            f"feasible={ga_stats['feasible']}, "
            f"time={ga_time:.2f}s"
        )
        print(
            f"TS -> dist={ts_distance:.2f}, "
            f"K={ts_solution.get_num_vehicles()}, "
            f"feasible={ts_stats['feasible']}, "
            f"time={ts_time:.2f}s"
        )
        print(f"Winner: {winner}")

    return result


def print_summary_table(title: str, results: dict, use_time_windows: bool) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

    if use_time_windows:
        print(
            f"{'Problem':<12} {'GA Dist':>12} {'GA K':>6} {'GA Feas':>10} "
            f"{'TS Dist':>12} {'TS K':>6} {'TS Feas':>10} {'Winner':>20}"
        )
        for problem_name, result in results.items():
            ga = result["genetic_algorithm"]
            ts = result["tabu_search"]
            print(
                f"{problem_name:<12} "
                f"{ga['distance']:>12.2f} {ga['num_vehicles']:>6} {str(ga['is_feasible']):>10} "
                f"{ts['distance']:>12.2f} {ts['num_vehicles']:>6} {str(ts['is_feasible']):>10} "
                f"{result['winner']:>20}"
            )
    else:
        print(
            f"{'Problem':<12} {'GA Dist':>12} {'GA K':>6} "
            f"{'TS Dist':>12} {'TS K':>6} {'Winner':>12}"
        )
        for problem_name, result in results.items():
            ga = result["genetic_algorithm"]
            ts = result["tabu_search"]
            print(
                f"{problem_name:<12} "
                f"{ga['distance']:>12.2f} {ga['num_vehicles']:>6} "
                f"{ts['distance']:>12.2f} {ts['num_vehicles']:>6} "
                f"{result['winner']:>12}"
            )


def main(problem_limit: int | None = None, verbose: bool = True) -> int:
    project_dir = Path(__file__).resolve().parent
    data_dir = project_dir / "data"
    results_dir = project_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    problems = DataLoader.load_all_problems(data_dir)
    if not problems:
        raise RuntimeError(f"No problems found in {data_dir}")

    if problem_limit is not None:
        problems = problems[:problem_limit]

    comprehensive_results = {
        "vrp_results": {},
        "vrptw_results": {},
    }

    for problem in problems:
        vrp_result = solve_problem(problem, use_time_windows=False, verbose=verbose)
        vrptw_result = solve_problem(problem, use_time_windows=True, verbose=verbose)

        comprehensive_results["vrp_results"][problem.name] = vrp_result
        comprehensive_results["vrptw_results"][problem.name] = vrptw_result

    print_summary_table(
        "TABLEAU 2 : RESULTATS MODE VRP (sans fenetres de temps)",
        comprehensive_results["vrp_results"],
        use_time_windows=False,
    )
    print_summary_table(
        "TABLEAU 3 : RESULTATS MODE VRPTW (avec fenetres de temps)",
        comprehensive_results["vrptw_results"],
        use_time_windows=True,
    )

    output_path = results_dir / "comprehensive_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)

    print(f"\nRésultats sauvegardés dans : {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())