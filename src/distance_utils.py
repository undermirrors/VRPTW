import math
from typing import List, Tuple
from models import Client, Route, Solution, Depot


class DistanceCalculator:
    """Utilities for calculating distances and metrics."""

    @staticmethod
    def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @staticmethod
    def route_distance(route: Route) -> float:
        """Calculate total distance for a route (optimized version)."""
        if len(route.clients) == 0:
            return 0.0

        distance = route.depot.location.distance_to(route.clients[0].location)

        for i in range(len(route.clients) - 1):
            distance += route.clients[i].location.distance_to(route.clients[i + 1].location)

        distance += route.clients[-1].location.distance_to(route.depot.location)
        return distance

    @staticmethod
    def solution_distance(solution: Solution) -> float:
        """Calculate total distance for entire solution."""
        return sum(DistanceCalculator.route_distance(route) for route in solution.routes)

    @staticmethod
    def insertion_distance_delta(route: Route, client: Client, position: int) -> float:
        """
        Calculate the change in route distance if client is inserted at position.
        Positive value means increase in distance, negative means decrease.
        """
        if position < 0 or position > len(route.clients):
            return float('inf')

        # Distance if we don't insert
        current_distance = DistanceCalculator.route_distance(route)

        # Distance if we insert
        temp_clients = route.clients.copy()
        temp_clients.insert(position, client)

        new_distance = 0.0
        if len(temp_clients) > 0:
            new_distance = route.depot.location.distance_to(temp_clients[0].location)
            for i in range(len(temp_clients) - 1):
                new_distance += temp_clients[i].location.distance_to(temp_clients[i + 1].location)
            new_distance += temp_clients[-1].location.distance_to(route.depot.location)

        return new_distance - current_distance

    @staticmethod
    def relocation_distance_delta(route: Route, client: Client, old_pos: int, new_pos: int) -> float:
        """
        Calculate change in distance when moving a client from old_pos to new_pos.
        """
        if old_pos == new_pos:
            return 0.0

        # Create route without the client
        temp_clients = route.clients.copy()
        temp_clients.pop(old_pos)

        # Insert at new position
        adjusted_new_pos = new_pos if new_pos < old_pos else new_pos - 1
        temp_clients.insert(adjusted_new_pos, client)

        # Calculate new distance
        new_distance = route.depot.location.distance_to(temp_clients[0].location)
        for i in range(len(temp_clients) - 1):
            new_distance += temp_clients[i].location.distance_to(temp_clients[i + 1].location)
        new_distance += temp_clients[-1].location.distance_to(route.depot.location)

        old_distance = DistanceCalculator.route_distance(route)
        return new_distance - old_distance


class SolutionEvaluator:
    """Evaluates solution quality and feasibility."""

    @staticmethod
    def is_feasible(solution: Solution, all_clients: List[Client]) -> bool:
        """Check if solution is feasible (all constraints satisfied)."""
        # All routes must be feasible
        if not all(route.is_feasible() for route in solution.routes):
            return False

        # All clients must be assigned
        if not solution.is_complete(all_clients):
            return False

        return True

    @staticmethod
    def get_constraint_violations(solution: Solution, all_clients: List[Client]) -> Tuple[int, int, int]:
        """
        Get number of constraint violations.
        Returns: (unassigned_clients, infeasible_routes, capacity_violations)
        """
        unassigned = len(solution.get_unassigned_clients(all_clients))
        infeasible_routes = sum(1 for route in solution.routes if not route.is_feasible())

        # Check capacity violations
        capacity_violations = 0
        for route in solution.routes:
            if route.current_load > route.capacity:
                capacity_violations += 1

        return unassigned, infeasible_routes, capacity_violations

    @staticmethod
    def get_route_load_distribution(solution: Solution) -> List[float]:
        """Get capacity utilization for each route (0-1 scale)."""
        return [route.current_load / route.capacity for route in solution.routes]

    @staticmethod
    def get_average_load_utilization(solution: Solution) -> float:
        """Get average capacity utilization across all routes."""
        if len(solution.routes) == 0:
            return 0.0
        distribution = SolutionEvaluator.get_route_load_distribution(solution)
        return sum(distribution) / len(distribution)

    @staticmethod
    def get_num_empty_routes(solution: Solution) -> int:
        """Get number of empty routes."""
        return sum(1 for route in solution.routes if len(route.clients) == 0)

    @staticmethod
    def evaluate_quality(solution: Solution, all_clients: List[Client],
                        penalty_weight: float = 10000.0, minimize_vehicles: bool = False,
                        vehicle_weight: float = 100.0) -> float:
        """
        Evaluate solution quality with penalties for infeasibility.
        Lower is better.

        Args:
            solution: The solution to evaluate
            all_clients: All clients in the problem
            penalty_weight: Weight for penalty terms
            minimize_vehicles: If True, penalize number of vehicles
            vehicle_weight: Weight for vehicle count in objective

        Returns:
            Objective value (distance + penalties + vehicle_cost)
        """
        distance = DistanceCalculator.solution_distance(solution)

        # Add penalties for infeasibility
        unassigned, infeasible_routes, capacity_violations = \
            SolutionEvaluator.get_constraint_violations(solution, all_clients)

        penalty = penalty_weight * (unassigned + infeasible_routes + capacity_violations)

        # Add vehicle minimization cost if requested
        vehicle_cost = 0.0
        if minimize_vehicles:
            num_vehicles = solution.get_num_vehicles()
            vehicle_cost = vehicle_weight * num_vehicles

        return distance + penalty + vehicle_cost

    @staticmethod
    def get_solution_stats(solution: Solution, all_clients: List[Client]) -> dict:
        """Get comprehensive statistics about a solution."""
        distance = DistanceCalculator.solution_distance(solution)
        unassigned, infeasible_routes, capacity_violations = \
            SolutionEvaluator.get_constraint_violations(solution, all_clients)

        stats = {
            'distance': distance,
            'num_vehicles': solution.get_num_vehicles(),
            'num_empty_vehicles': SolutionEvaluator.get_num_empty_routes(solution),
            'avg_load_utilization': SolutionEvaluator.get_average_load_utilization(solution),
            'unassigned_clients': unassigned,
            'infeasible_routes': infeasible_routes,
            'capacity_violations': capacity_violations,
            'is_feasible': SolutionEvaluator.is_feasible(solution, all_clients),
        }
        return stats
