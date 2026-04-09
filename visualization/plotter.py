import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np
from typing import List, Optional, Tuple
import os

from models import Solution, Route, Client, Depot


class RouteVisualizer:
    """
    Visualization module for VRPTW solutions.

    Creates professional visualizations of vehicle routes including:
    - Route paths with depot and client locations
    - Color-coded routes
    - Annotations for time windows and demands
    - Route statistics
    """

    def __init__(self, figsize: Tuple[int, int] = (14, 10), dpi: int = 100):
        """
        Initialize visualizer.

        Args:
            figsize: Figure size (width, height) in inches
            dpi: Resolution in dots per inch
        """
        self.figsize = figsize
        self.dpi = dpi
        self.colors = self._generate_colors(20)

    @staticmethod
    def _generate_colors(num_colors: int) -> List[str]:
        """Generate a list of distinct colors for routes."""
        colors = plt.cm.tab20(np.linspace(0, 1, num_colors))
        return [plt.matplotlib.colors.rgb2hex(c) for c in colors]

    def plot_solution(self, solution: Solution, title: str = "VRPTW Solution",
                      show_time_windows: bool = False, show_demands: bool = False,
                      show_legend: bool = False, save_path: Optional[str] = None) -> None:
        """
        Plot a complete solution with all routes.

        Args:
            solution: The solution to visualize
            title: Title for the plot
            show_time_windows: Whether to display time window information
            show_demands: Whether to display client demand information
            show_legend: Whether to display legend with route information
            save_path: Path to save the figure (None = don't save)
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Plot all routes
        for route_idx, route in enumerate(solution.routes):
            color = self.colors[route_idx % len(self.colors)]
            self._plot_route(ax, route, color, route_idx + 1, show_time_windows, show_demands)

        # Plot depot
        self._plot_depot(ax, solution.depot)

        # Formatting
        ax.set_xlabel("X Coordinate", fontsize=12, fontweight='bold')
        ax.set_ylabel("Y Coordinate", fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_aspect('equal', adjustable='box')

        # Create legend with route information (optional)
        if show_legend:
            self._create_legend(ax, solution)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"Figure saved to: {save_path}")

        plt.show()

    def _plot_route(self, ax, route: Route, color: str, route_number: int,
                   show_time_windows: bool = False, show_demands: bool = False) -> None:
        """Plot a single route."""
        if len(route.clients) == 0:
            return

        # Extract coordinates
        x_coords = [route.depot.location.x]
        y_coords = [route.depot.location.y]

        for client in route.clients:
            x_coords.append(client.location.x)
            y_coords.append(client.location.y)

        x_coords.append(route.depot.location.x)
        y_coords.append(route.depot.location.y)

        # Plot route line
        ax.plot(x_coords, y_coords, color=color, linewidth=2, label=f"Route {route_number}",
                alpha=0.7, zorder=1)

        # Plot client nodes
        for i, client in enumerate(route.clients):
            ax.scatter(client.location.x, client.location.y, color=color, s=150,
                      marker='o', edgecolors='black', linewidth=1.5, zorder=3)

            # Add client ID
            ax.text(client.location.x, client.location.y - 2, client.id,
                   fontsize=9, ha='center', fontweight='bold', zorder=4)

            # Add time window info if requested
            if show_time_windows:
                time_info = f"[{int(client.time_window.ready_time)},{int(client.time_window.due_time)}]"
                ax.text(client.location.x, client.location.y + 2.5, time_info,
                       fontsize=7, ha='center', style='italic', color=color, zorder=4)

            # Add demand info if requested
            if show_demands:
                demand_info = f"d:{int(client.demand)}"
                ax.text(client.location.x + 3, client.location.y, demand_info,
                       fontsize=7, ha='left', color=color, zorder=4)

        # Add arrows to show direction
        for i in range(len(x_coords) - 1):
            dx = x_coords[i + 1] - x_coords[i]
            dy = y_coords[i + 1] - y_coords[i]

            # Only add arrow if there's significant distance
            if dx != 0 or dy != 0:
                ax.annotate('', xy=(x_coords[i + 1], y_coords[i + 1]),
                          xytext=(x_coords[i + 1] - 0.3 * dx, y_coords[i + 1] - 0.3 * dy),
                          arrowprops=dict(arrowstyle='->', color=color, lw=1.5, alpha=0.5),
                          zorder=2)

    def _plot_depot(self, ax, depot: Depot) -> None:
        """Plot the depot as a special marker."""
        ax.scatter(depot.location.x, depot.location.y, color='red', s=400,
                  marker='s', edgecolors='darkred', linewidth=2, zorder=5,
                  label='Depot')
        ax.text(depot.location.x, depot.location.y - 3, depot.id,
               fontsize=11, ha='center', fontweight='bold', color='darkred', zorder=6)

    def _create_legend(self, ax, solution: Solution) -> None:
        """Create a legend with route and solution information."""
        # Route information
        legend_lines = [mpatches.Patch(color='red', label='Depot')]

        for route_idx, route in enumerate(solution.routes):
            color = self.colors[route_idx % len(self.colors)]
            distance = route.get_total_distance()
            num_clients = len(route.clients)
            load = route.current_load
            capacity = route.capacity

            label = f"Route {route_idx + 1}: {num_clients} clients, " \
                   f"dist={distance:.1f}, load={load}/{capacity}"
            legend_lines.append(mpatches.Patch(color=color, label=label))

        # Total statistics
        total_distance = solution.get_total_distance()
        total_vehicles = solution.get_num_vehicles()
        legend_lines.append(mpatches.Patch(color='white',
                                           label=f"\nTotal: {total_vehicles} vehicles, "
                                                f"distance={total_distance:.1f}"))

        ax.legend(handles=legend_lines, loc='upper left', fontsize=9,
                 framealpha=0.95, edgecolor='black')

    def plot_comparison(self, solution1: Solution, solution2: Solution,
                       title1: str = "Solution 1", title2: str = "Solution 2",
                       save_path: Optional[str] = None) -> None:
        """
        Plot two solutions side by side for comparison.

        Args:
            solution1: First solution
            solution2: Second solution
            title1: Title for first solution
            title2: Title for second solution
            save_path: Path to save the figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9), dpi=self.dpi)

        # Plot first solution
        for route_idx, route in enumerate(solution1.routes):
            color = self.colors[route_idx % len(self.colors)]
            self._plot_route_on_axis(ax1, route, color, route_idx + 1)

        self._plot_depot_on_axis(ax1, solution1.depot)
        ax1.set_title(f"{title1}\nDistance: {solution1.get_total_distance():.2f}, "
                     f"Vehicles: {solution1.get_num_vehicles()}",
                     fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')

        # Plot second solution
        for route_idx, route in enumerate(solution2.routes):
            color = self.colors[route_idx % len(self.colors)]
            self._plot_route_on_axis(ax2, route, color, route_idx + 1)

        self._plot_depot_on_axis(ax2, solution2.depot)
        ax2.set_title(f"{title2}\nDistance: {solution2.get_total_distance():.2f}, "
                     f"Vehicles: {solution2.get_num_vehicles()}",
                     fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal')

        plt.suptitle("Solution Comparison", fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"Comparison figure saved to: {save_path}")

        plt.show()

    def _plot_route_on_axis(self, ax, route: Route, color: str, route_number: int) -> None:
        """Helper to plot route on specific axis."""
        if len(route.clients) == 0:
            return

        x_coords = [route.depot.location.x]
        y_coords = [route.depot.location.y]

        for client in route.clients:
            x_coords.append(client.location.x)
            y_coords.append(client.location.y)

        x_coords.append(route.depot.location.x)
        y_coords.append(route.depot.location.y)

        ax.plot(x_coords, y_coords, color=color, linewidth=2, alpha=0.7, zorder=1)

        for client in route.clients:
            ax.scatter(client.location.x, client.location.y, color=color, s=100,
                      marker='o', edgecolors='black', linewidth=1, zorder=3)
            ax.text(client.location.x, client.location.y - 2, client.id,
                   fontsize=8, ha='center', zorder=4)

    def _plot_depot_on_axis(self, ax, depot: Depot) -> None:
        """Helper to plot depot on specific axis."""
        ax.scatter(depot.location.x, depot.location.y, color='red', s=300,
                  marker='s', edgecolors='darkred', linewidth=2, zorder=5)

    def plot_convergence(self, history: List[float], algorithm_name: str = "Algorithm",
                        save_path: Optional[str] = None) -> None:
        """
        Plot convergence history of an algorithm.

        Args:
            history: List of best fitness values per iteration
            algorithm_name: Name of the algorithm
            save_path: Path to save the figure
        """
        fig, ax = plt.subplots(figsize=(12, 7), dpi=self.dpi)

        iterations = range(len(history))
        ax.plot(iterations, history, color='blue', linewidth=2, label='Best Fitness')
        ax.fill_between(iterations, history, alpha=0.3, color='blue')

        ax.set_xlabel("Iteration", fontsize=12, fontweight='bold')
        ax.set_ylabel("Best Fitness Value", fontsize=12, fontweight='bold')
        ax.set_title(f"{algorithm_name} - Convergence History", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=11)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"Convergence plot saved to: {save_path}")

        plt.show()

    def plot_distance_comparison(self, results: dict, save_path: Optional[str] = None) -> None:
        """
        Plot distance comparison between algorithms across multiple problems.

        Args:
            results: Dictionary of results with algorithm distances
            save_path: Path to save the figure
        """
        fig, ax = plt.subplots(figsize=(14, 7), dpi=self.dpi)

        problem_names = list(results.keys())
        ga_distances = [results[p]['genetic_algorithm']['distance'] for p in problem_names]
        ts_distances = [results[p]['tabu_search']['distance'] for p in problem_names]

        x = np.arange(len(problem_names))
        width = 0.35

        bars1 = ax.bar(x - width/2, ga_distances, width, label='Genetic Algorithm',
                      color='steelblue', edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, ts_distances, width, label='Tabu Search',
                      color='coral', edgecolor='black', linewidth=1.5)

        ax.set_xlabel("Problem", fontsize=12, fontweight='bold')
        ax.set_ylabel("Total Distance", fontsize=12, fontweight='bold')
        ax.set_title("Algorithm Performance Comparison - Distance", fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(problem_names, rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"Comparison plot saved to: {save_path}")

        plt.show()

    def plot_vehicles_comparison(self, results: dict, save_path: Optional[str] = None) -> None:
        """
        Plot vehicle count comparison between algorithms.

        Args:
            results: Dictionary of results with vehicle counts
            save_path: Path to save the figure
        """
        fig, ax = plt.subplots(figsize=(14, 7), dpi=self.dpi)

        problem_names = list(results.keys())
        ga_vehicles = [results[p]['genetic_algorithm']['num_vehicles'] for p in problem_names]
        ts_vehicles = [results[p]['tabu_search']['num_vehicles'] for p in problem_names]

        x = np.arange(len(problem_names))
        width = 0.35

        bars1 = ax.bar(x - width/2, ga_vehicles, width, label='Genetic Algorithm',
                      color='steelblue', edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, ts_vehicles, width, label='Tabu Search',
                      color='coral', edgecolor='black', linewidth=1.5)

        ax.set_xlabel("Problem", fontsize=12, fontweight='bold')
        ax.set_ylabel("Number of Vehicles", fontsize=12, fontweight='bold')
        ax.set_title("Algorithm Performance Comparison - Vehicles Used", fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(problem_names, rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"Vehicles comparison plot saved to: {save_path}")

        plt.show()

    def plot_execution_time_comparison(self, results: dict, save_path: Optional[str] = None) -> None:
        """
        Plot execution time comparison between algorithms.

        Args:
            results: Dictionary of results with execution times
            save_path: Path to save the figure
        """
        fig, ax = plt.subplots(figsize=(14, 7), dpi=self.dpi)

        problem_names = list(results.keys())
        ga_times = [results[p]['genetic_algorithm']['execution_time'] for p in problem_names]
        ts_times = [results[p]['tabu_search']['execution_time'] for p in problem_names]

        x = np.arange(len(problem_names))
        width = 0.35

        bars1 = ax.bar(x - width/2, ga_times, width, label='Genetic Algorithm',
                      color='steelblue', edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, ts_times, width, label='Tabu Search',
                      color='coral', edgecolor='black', linewidth=1.5)

        ax.set_xlabel("Problem", fontsize=12, fontweight='bold')
        ax.set_ylabel("Execution Time (seconds)", fontsize=12, fontweight='bold')
        ax.set_title("Algorithm Performance Comparison - Execution Time", fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(problem_names, rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"Execution time comparison plot saved to: {save_path}")

        plt.show()
