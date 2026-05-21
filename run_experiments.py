#!/usr/bin/env python3
import json
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.data_loader import DataLoader
from src.genetic_algorithm import GeneticAlgorithm
from src.tabu_search import TabuSearch
from src.distance_utils import DistanceCalculator, SolutionEvaluator


def ensure_plot_dir(project_dir: Path) -> Path:
    plot_dir = project_dir / "results" / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    return plot_dir


def ensure_dataset_dir(project_dir: Path, dataset_name: str) -> Path:
    dataset_dir = project_dir / "results" / "solutions" / dataset_name
    dataset_dir.mkdir(parents=True, exist_ok=True)
    return dataset_dir


def plot_solution_routes(problem, solution, title: str, output_path: Path, use_time_windows: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(10, 8), constrained_layout=True)

    depot_x = problem.depot.location.x
    depot_y = problem.depot.location.y

    ax.scatter(
        [depot_x],
        [depot_y],
        c="red",
        s=180,
        marker="s",
        label="Dépôt",
        edgecolors="black",
        linewidths=1.0,
        zorder=5,
    )

    all_client_x = [client.location.x for client in problem.clients]
    all_client_y = [client.location.y for client in problem.clients]
    ax.scatter(
        all_client_x,
        all_client_y,
        c="lightgray",
        s=30,
        alpha=0.7,
        label="Clients",
        zorder=1,
    )

    non_empty_routes = [route for route in solution.routes if not route.is_empty()]
    cmap = plt.get_cmap("tab20", max(len(non_empty_routes), 1))

    for idx, route in enumerate(non_empty_routes):
        color = cmap(idx)
        xs = [depot_x] + [client.location.x for client in route.clients] + [depot_x]
        ys = [depot_y] + [client.location.y for client in route.clients] + [depot_y]

        ax.plot(xs, ys, color=color, linewidth=2.0, alpha=0.95, label=f"Route {idx + 1}", zorder=2)
        ax.scatter(xs[1:-1], ys[1:-1], color=[color], s=40, zorder=3)

        for client in route.clients:
            ax.annotate(
                str(client.id),
                (client.location.x, client.location.y),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=7,
                alpha=0.8,
            )

    distance = DistanceCalculator.solution_distance(solution)
    vehicles = solution.get_num_vehicles()
    mode = "VRPTW" if use_time_windows else "VRP"

    ax.set_title(
        f"{title}\n{problem.name} | {mode} | Distance={distance:.2f} | Véhicules={vehicles}"
    )
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, linestyle="--", alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    ax.set_aspect("equal", adjustable="box")

    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_first_comparison(results_by_problem: dict, mode_name: str, output_path: Path) -> None:
    datasets = list(results_by_problem.keys())
    ga_dist = [results_by_problem[d]["genetic_algorithm"]["distance"] for d in datasets]
    ts_dist = [results_by_problem[d]["tabu_search"]["distance"] for d in datasets]
    ga_k = [results_by_problem[d]["genetic_algorithm"]["num_vehicles"] for d in datasets]
    ts_k = [results_by_problem[d]["tabu_search"]["num_vehicles"] for d in datasets]

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), constrained_layout=True)
    x = list(range(len(datasets)))

    axes[0].plot(x, ga_dist, marker="o", linewidth=2, label="GA distance")
    axes[0].plot(x, ts_dist, marker="s", linewidth=2, label="TS distance")
    axes[0].set_title(f"Comparaison des distances - {mode_name}")
    axes[0].set_ylabel("Distance")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(datasets, rotation=45, ha="right")
    axes[0].grid(True, linestyle="--", alpha=0.35)
    axes[0].legend()

    axes[1].plot(x, ga_k, marker="o", linewidth=2, label="GA véhicules")
    axes[1].plot(x, ts_k, marker="s", linewidth=2, label="TS véhicules")
    axes[1].set_title(f"Comparaison du nombre de véhicules - {mode_name}")
    axes[1].set_ylabel("Nombre de véhicules")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(datasets, rotation=45, ha="right")
    axes[1].grid(True, linestyle="--", alpha=0.35)
    axes[1].legend()

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_result_table_evolution(vrp_results: dict, vrptw_results: dict, output_path: Path) -> None:
    datasets = list(vrp_results.keys())

    ga_vrp = [vrp_results[d]["genetic_algorithm"]["distance"] for d in datasets]
    ts_vrp = [vrp_results[d]["tabu_search"]["distance"] for d in datasets]
    ga_vrptw = [vrptw_results[d]["genetic_algorithm"]["distance"] for d in datasets]
    ts_vrptw = [vrptw_results[d]["tabu_search"]["distance"] for d in datasets]

    fig, ax = plt.subplots(figsize=(15, 7), constrained_layout=True)
    x = list(range(len(datasets)))

    ax.plot(x, ga_vrp, marker="o", linewidth=2, label="GA VRP")
    ax.plot(x, ts_vrp, marker="s", linewidth=2, label="TS VRP")
    ax.plot(x, ga_vrptw, marker="o", linestyle="--", linewidth=2, label="GA VRPTW")
    ax.plot(x, ts_vrptw, marker="s", linestyle="--", linewidth=2, label="TS VRPTW")

    ax.set_title("Évolution des performances GA vs TS par dataset")
    ax.set_ylabel("Distance")
    ax.set_xticks(x)
    ax.set_xticklabels(datasets, rotation=45, ha="right")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(ncol=2)

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_ga_learning_curve(history: list, dataset_name: str, mode_name: str, output_path: Path) -> None:
    if not history:
        return

    generations = list(range(1, len(history) + 1))
    best_so_far = []
    current_best = float("inf")

    for value in history:
        current_best = min(current_best, value)
        best_so_far.append(current_best)

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    ax.plot(generations, history, alpha=0.45, linewidth=1.5, label="Best génération")
    ax.plot(generations, best_so_far, linewidth=2.5, label="Best cumulé")
    ax.set_title(f"Courbe d'apprentissage GA - {dataset_name} ({mode_name})")
    ax.set_xlabel("Génération")
    ax.set_ylabel("Distance")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend()

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def solve_problem(problem, use_time_windows: bool, verbose: bool = True) -> dict:
    mode_name = "VRPTW" if use_time_windows else "VRP"

    if verbose:
        print(f"\n--- {problem.name} | Mode {mode_name} ---")

    DistanceCalculator.clear_cache()

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
            "generation_history": list(getattr(ga, "generation_history", [])),
            "solution": ga_solution,
        },
        "tabu_search": {
            "execution_time": ts_time,
            "distance": ts_distance,
            "num_vehicles": ts_solution.get_num_vehicles(),
            "is_feasible": ts_stats["feasible"],
            "solution_stats": ts_stats,
            "solution": ts_solution,
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


def strip_solution_objects(results: dict) -> dict:
    serializable = {"vrp_results": {}, "vrptw_results": {}, "generated_plots": {}}

    for mode_key in ["vrp_results", "vrptw_results"]:
        for problem_name, result in results[mode_key].items():
            cleaned = dict(result)
            cleaned["genetic_algorithm"] = dict(result["genetic_algorithm"])
            cleaned["tabu_search"] = dict(result["tabu_search"])
            cleaned["genetic_algorithm"].pop("solution", None)
            cleaned["tabu_search"].pop("solution", None)
            serializable[mode_key][problem_name] = cleaned

    serializable["generated_plots"] = results.get("generated_plots", {})
    return serializable


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
        dataset_dir = ensure_dataset_dir(project_dir, problem.name)

        vrp_result = solve_problem(problem, use_time_windows=False, verbose=verbose)
        vrptw_result = solve_problem(problem, use_time_windows=True, verbose=verbose)

        plot_solution_routes(
            problem,
            vrp_result["genetic_algorithm"]["solution"],
            title="Solution GA",
            output_path=dataset_dir / "ga_vrp_solution.png",
            use_time_windows=False,
        )
        plot_solution_routes(
            problem,
            vrp_result["tabu_search"]["solution"],
            title="Solution TS",
            output_path=dataset_dir / "ts_vrp_solution.png",
            use_time_windows=False,
        )
        plot_solution_routes(
            problem,
            vrptw_result["genetic_algorithm"]["solution"],
            title="Solution GA",
            output_path=dataset_dir / "ga_vrptw_solution.png",
            use_time_windows=True,
        )
        plot_solution_routes(
            problem,
            vrptw_result["tabu_search"]["solution"],
            title="Solution TS",
            output_path=dataset_dir / "ts_vrptw_solution.png",
            use_time_windows=True,
        )

        vrp_result["generated_images"] = {
            "ga_solution": str(dataset_dir / "ga_vrp_solution.png"),
            "ts_solution": str(dataset_dir / "ts_vrp_solution.png"),
        }
        vrptw_result["generated_images"] = {
            "ga_solution": str(dataset_dir / "ga_vrptw_solution.png"),
            "ts_solution": str(dataset_dir / "ts_vrptw_solution.png"),
        }

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

    plot_dir = ensure_plot_dir(project_dir)

    plot_first_comparison(
        comprehensive_results["vrp_results"],
        mode_name="VRP",
        output_path=plot_dir / "vrp_comparison.png",
    )
    plot_first_comparison(
        comprehensive_results["vrptw_results"],
        mode_name="VRPTW",
        output_path=plot_dir / "vrptw_comparison.png",
    )
    plot_result_table_evolution(
        comprehensive_results["vrp_results"],
        comprehensive_results["vrptw_results"],
        output_path=plot_dir / "ga_ts_evolution_by_dataset.png",
    )

    first_problem_name = problems[0].name
    first_vrp_history = comprehensive_results["vrp_results"][first_problem_name]["genetic_algorithm"].get("generation_history", [])
    first_vrptw_history = comprehensive_results["vrptw_results"][first_problem_name]["genetic_algorithm"].get("generation_history", [])

    plot_ga_learning_curve(
        first_vrp_history,
        dataset_name=first_problem_name,
        mode_name="VRP",
        output_path=plot_dir / f"ga_learning_curve_{first_problem_name}_vrp.png",
    )
    plot_ga_learning_curve(
        first_vrptw_history,
        dataset_name=first_problem_name,
        mode_name="VRPTW",
        output_path=plot_dir / f"ga_learning_curve_{first_problem_name}_vrptw.png",
    )

    comprehensive_results["generated_plots"] = {
        "vrp_comparison": str(plot_dir / "vrp_comparison.png"),
        "vrptw_comparison": str(plot_dir / "vrptw_comparison.png"),
        "ga_ts_evolution_by_dataset": str(plot_dir / "ga_ts_evolution_by_dataset.png"),
        "ga_learning_curve_vrp": str(plot_dir / f"ga_learning_curve_{first_problem_name}_vrp.png"),
        "ga_learning_curve_vrptw": str(plot_dir / f"ga_learning_curve_{first_problem_name}_vrptw.png"),
    }

    output_path = results_dir / "comprehensive_results.json"
    serializable_results = strip_solution_objects(comprehensive_results)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)

    print(f"\nRésultats sauvegardés dans : {output_path}")
    print(f"Graphes sauvegardés dans : {plot_dir}")
    print(f"Images des solutions sauvegardées dans : {results_dir / 'solutions'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())