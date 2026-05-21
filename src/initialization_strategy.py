"""
Initialization strategies for VRPTW solving.

Optimizations:
- Simplified initialization logic
- Removed dead code
- Better error handling
"""

from typing import List, Tuple, Dict
from models import Solution, Depot, Client
from distance_utils import DistanceCalculator
from solution_generator import SolutionGenerator


class InitializationStrategy:
    """Provide various initialization strategies for VRPTW."""

    @staticmethod
    def nearest_neighbor_init(
        depot: Depot,
        clients: List[Client],
        capacity: float
    ) -> Solution:
        """
        Simple nearest neighbor initialization.

        Args:
            depot: The depot
            clients: Clients to serve
            capacity: Vehicle capacity

        Returns:
            Initial solution
        """
        try:
            return SolutionGenerator.nearest_neighbor(depot, clients, capacity)
        except RuntimeError:
            # Fallback
            return SolutionGenerator.random_solution(depot, clients, capacity)

    @staticmethod
    def greedy_init(
        depot: Depot,
        clients: List[Client],
        capacity: float
    ) -> Solution:
        """
        Greedy insertion initialization.

        Args:
            depot: The depot
            clients: Clients to serve
            capacity: Vehicle capacity

        Returns:
            Initial solution
        """
        try:
            return SolutionGenerator.greedy_insertion(depot, clients, capacity)
        except RuntimeError:
            # Fallback
            return SolutionGenerator.random_solution(depot, clients, capacity)

    @staticmethod
    def savings_init(
        depot: Depot,
        clients: List[Client],
        capacity: float
    ) -> Solution:
        """
        Savings algorithm initialization.

        Args:
            depot: The depot
            clients: Clients to serve
            capacity: Vehicle capacity

        Returns:
            Initial solution
        """
        try:
            return SolutionGenerator.savings_algorithm(depot, clients, capacity)
        except RuntimeError:
            # Fallback
            return SolutionGenerator.random_solution(depot, clients, capacity)

    @staticmethod
    def multi_start_best(
        depot: Depot,
        clients: List[Client],
        capacity: float,
        num_attempts: int = 3
    ) -> Solution:
        """
        Generate multiple initial solutions and return the best.

        Args:
            depot: The depot
            clients: Clients to serve
            capacity: Vehicle capacity
            num_attempts: Number of different strategies to try

        Returns:
            Best solution found
        """
        methods = [
            InitializationStrategy.nearest_neighbor_init,
            InitializationStrategy.greedy_init,
            InitializationStrategy.savings_init,
        ]

        best_solution = None
        best_distance = float('inf')

        for i in range(min(num_attempts, len(methods))):
            try:
                solution = methods[i](depot, clients, capacity)
                distance = DistanceCalculator.solution_distance(solution)

                if distance < best_distance:
                    best_distance = distance
                    best_solution = solution
            except Exception:
                continue

        if best_solution is None:
            best_solution = SolutionGenerator.random_solution(depot, clients, capacity)

        return best_solution

    @staticmethod
    def get_initialization_stats(
        solutions: List[Solution],
        clients: List[Client]
    ) -> Dict[str, float]:
        """
        Get statistics about a set of initial solutions.

        Args:
            solutions: List of solutions to analyze
            clients: All clients

        Returns:
            Dictionary of statistics
        """
        if not solutions:
            return {}

        distances = [DistanceCalculator.solution_distance(s) for s in solutions]
        vehicles = [s.get_num_vehicles() for s in solutions]

        return {
            "num_solutions": len(solutions),
            "best_distance": min(distances),
            "worst_distance": max(distances),
            "avg_distance": sum(distances) / len(distances),
            "best_vehicles": min(vehicles),
            "worst_vehicles": max(vehicles),
            "avg_vehicles": sum(vehicles) / len(vehicles),
        }
