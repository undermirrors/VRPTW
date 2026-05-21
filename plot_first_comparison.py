#!/usr/bin/env python3
"""
Generate PNG plots comparing GA and TS on the first VRPTW instance.

- No interactive display
- All outputs saved into results/
"""

from pathlib import Path
import json
import matplotlib

matplotlib.use("Agg")

from src.data_loader import DataLoader
from src.genetic_algorithm import GeneticAlgorithm
from src.tabu_search import TabuSearch
from src.distance_utils import DistanceCalculator, SolutionEvaluator
from visualization.plotter import RouteVisualizer


def main() -> int:
    project_dir = Path(__file__).resolve().parent
    data_dir = project_dir / "data"
    results_dir = project_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    problems = DataLoader.load_all_problems(data_dir)
    if not problems:
        raise RuntimeError(f"No .vrp files found in {data_dir}")

    problem = problems[0]

    print(f"Instance sélectionnée : {problem.name}")
    print(f"Clients : {problem.num_clients}, capacité : {problem.capacity}")

    DistanceCalculator.clear_cache()

    ga = GeneticAlgorithm(
        depot=problem.depot,
        clients=problem.clients,
        capacity=problem.capacity,
    )
    ga_solution = ga.evolve(verbose=True)

    ts = TabuSearch(
        depot=problem.depot,
        clients=problem.clients,
        capacity=problem.capacity,
    )
    ts_solution = ts.search(verbose=True)

    ga_distance = DistanceCalculator.solution_distance(ga_solution)
    ts_distance = DistanceCalculator.solution_distance(ts_solution)

    ga_stats = SolutionEvaluator.get_solution_stats(ga_solution, problem.clients)
    ts_stats = SolutionEvaluator.get_solution_stats(ts_solution, problem.clients)

    summary = {
        "problem_name": problem.name,
        "num_clients": problem.num_clients,
        "capacity": problem.capacity,
        "genetic_algorithm": {
            "distance": ga_distance,
            "num_vehicles": ga_solution.get_num_vehicles(),
            "is_feasible": ga_stats["feasible"],
            "solution_stats": ga_stats,
        },
        "tabu_search": {
            "distance": ts_distance,
            "num_vehicles": ts_solution.get_num_vehicles(),
            "is_feasible": ts_stats["feasible"],
            "solution_stats": ts_stats,
        },
    }

    summary_path = results_dir / f"{problem.name}_comparison_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    viz = RouteVisualizer(figsize=(14, 10), dpi=100)

    ga_png = results_dir / f"{problem.name}_ga_solution.png"
    ts_png = results_dir / f"{problem.name}_ts_solution.png"
    cmp_png = results_dir / f"{problem.name}_comparison.png"

    viz.plot_solution(
        solution=ga_solution,
        title=f"GA Solution for {problem.name}",
        show_time_windows=True,
        show_demands=True,
        save_path=str(ga_png),
    )

    viz.plot_solution(
        solution=ts_solution,
        title=f"TS Solution for {problem.name}",
        show_time_windows=True,
        show_demands=True,
        save_path=str(ts_png),
    )

    viz.plot_comparison(
        solution1=ga_solution,
        solution2=ts_solution,
        title1=f"GA - {problem.name}",
        title2=f"TS - {problem.name}",
        save_path=str(cmp_png),
    )

    print("\nRésumé :")
    print(
        f"GA -> distance={ga_distance:.2f}, "
        f"vehicles={ga_solution.get_num_vehicles()}, "
        f"feasible={ga_stats['feasible']}"
    )
    print(
        f"TS -> distance={ts_distance:.2f}, "
        f"vehicles={ts_solution.get_num_vehicles()}, "
        f"feasible={ts_stats['feasible']}"
    )
    print(f"\nJSON : {summary_path}")
    print(f"PNG  : {ga_png}")
    print(f"PNG  : {ts_png}")
    print(f"PNG  : {cmp_png}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())