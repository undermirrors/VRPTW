"""
Distance calculation and solution evaluation utilities.
"""

from typing import List, Dict, Any, Tuple
import math

from .models import Solution, Route, Client, Location


class DistanceCalculator:
    """Calculate distances with optional caching."""

    _distance_cache: Dict[Tuple[Tuple[float, float], Tuple[float, float]], float] = {}
    _cache_enabled = True

    @classmethod
    def enable_cache(cls) -> None:
        cls._cache_enabled = True

    @classmethod
    def disable_cache(cls) -> None:
        cls._cache_enabled = False

    @classmethod
    def clear_cache(cls) -> None:
        cls._distance_cache.clear()

    @classmethod
    def get_distance(cls, loc1: Location, loc2: Location) -> float:
        if not cls._cache_enabled:
            return cls._calculate_distance_uncached(loc1, loc2)

        key = ((loc1.x, loc1.y), (loc2.x, loc2.y))
        rev_key = ((loc2.x, loc2.y), (loc1.x, loc1.y))

        if key in cls._distance_cache:
            return cls._distance_cache[key]
        if rev_key in cls._distance_cache:
            return cls._distance_cache[rev_key]

        dist = cls._calculate_distance_uncached(loc1, loc2)
        cls._distance_cache[key] = dist
        return dist

    @staticmethod
    def _calculate_distance_uncached(loc1: Location, loc2: Location) -> float:
        dx = loc1.x - loc2.x
        dy = loc1.y - loc2.y
        return math.sqrt(dx * dx + dy * dy)

    @classmethod
    def route_distance(cls, route: Route) -> float:
        if route.is_empty():
            return 0.0

        total = 0.0
        current = route.depot.location

        for client in route.clients:
            total += cls.get_distance(current, client.location)
            current = client.location

        total += cls.get_distance(current, route.depot.location)
        return total

    @classmethod
    def solution_distance(cls, solution: Solution) -> float:
        return sum(cls.route_distance(route) for route in solution.routes if not route.is_empty())

    @classmethod
    def insertion_distance_delta(cls, route: Route, client: Client, position: int) -> float:
        if position < 0 or position > len(route.clients):
            raise ValueError(f"Invalid position {position} for route with {len(route.clients)} clients")

        clients = route.clients

        if len(clients) == 0:
            return (
                cls.get_distance(route.depot.location, client.location)
                + cls.get_distance(client.location, route.depot.location)
            )

        if position == 0:
            old_dist = cls.get_distance(route.depot.location, clients[0].location)
            new_dist = (
                cls.get_distance(route.depot.location, client.location)
                + cls.get_distance(client.location, clients[0].location)
            )
            return new_dist - old_dist

        if position == len(clients):
            last_client = clients[-1]
            old_dist = cls.get_distance(last_client.location, route.depot.location)
            new_dist = (
                cls.get_distance(last_client.location, client.location)
                + cls.get_distance(client.location, route.depot.location)
            )
            return new_dist - old_dist

        prev_client = clients[position - 1]
        next_client = clients[position]
        old_dist = cls.get_distance(prev_client.location, next_client.location)
        new_dist = (
            cls.get_distance(prev_client.location, client.location)
            + cls.get_distance(client.location, next_client.location)
        )
        return new_dist - old_dist

    @classmethod
    def removal_distance_delta(cls, route: Route, position: int) -> float:
        if position < 0 or position >= len(route.clients):
            raise ValueError(f"Invalid position {position} for route with {len(route.clients)} clients")

        clients = route.clients

        if len(clients) == 1:
            return -(
                cls.get_distance(route.depot.location, clients[0].location)
                + cls.get_distance(clients[0].location, route.depot.location)
            )

        if position == 0:
            old_dist = (
                cls.get_distance(route.depot.location, clients[0].location)
                + cls.get_distance(clients[0].location, clients[1].location)
            )
            new_dist = cls.get_distance(route.depot.location, clients[1].location)
            return new_dist - old_dist

        if position == len(clients) - 1:
            old_dist = (
                cls.get_distance(clients[-2].location, clients[-1].location)
                + cls.get_distance(clients[-1].location, route.depot.location)
            )
            new_dist = cls.get_distance(clients[-2].location, route.depot.location)
            return new_dist - old_dist

        old_dist = (
            cls.get_distance(clients[position - 1].location, clients[position].location)
            + cls.get_distance(clients[position].location, clients[position + 1].location)
        )
        new_dist = cls.get_distance(clients[position - 1].location, clients[position + 1].location)
        return new_dist - old_dist


class SolutionEvaluator:
    """Evaluate solution quality and feasibility."""

    @staticmethod
    def evaluate_route(route: Route, use_time_windows: bool = True) -> Dict[str, float]:
        if route.is_empty():
            return {
                "feasible": True,
                "total_distance": 0.0,
                "end_time": 0.0,
                "late_clients": 0,
            }

        current_time = 0.0
        current_location = route.depot.location
        total_distance = 0.0
        late_clients = 0

        for client in route.clients:
            travel_time = DistanceCalculator.get_distance(current_location, client.location)
            arrival_time = current_time + travel_time
            total_distance += travel_time

            if use_time_windows:
                if arrival_time > client.time_window.due_time:
                    late_clients += 1
                service_start = max(arrival_time, client.time_window.ready_time)
                current_time = service_start + client.service_time
            else:
                current_time = arrival_time + client.service_time

            current_location = client.location

        back_distance = DistanceCalculator.get_distance(current_location, route.depot.location)
        total_distance += back_distance
        current_time += back_distance

        return {
            "feasible": (late_clients == 0) and (route.current_load <= route.capacity),
            "total_distance": total_distance,
            "end_time": current_time,
            "late_clients": late_clients,
        }

    @staticmethod
    def is_feasible(
        solution: Solution,
        clients: List[Client],
        use_time_windows: bool = True
    ) -> bool:
        assigned_ids = []

        for route in solution.routes:
            route_eval = SolutionEvaluator.evaluate_route(route, use_time_windows=use_time_windows)
            if not route_eval["feasible"]:
                return False

            for client in route.clients:
                assigned_ids.append(client.id)

        return len(set(assigned_ids)) == len(clients) and len(assigned_ids) == len(clients)

    @staticmethod
    def get_solution_stats(
        solution: Solution,
        clients: List[Client],
        use_time_windows: bool = True
    ) -> Dict[str, float]:
        total_distance = DistanceCalculator.solution_distance(solution)
        num_vehicles = solution.get_num_vehicles()

        route_distances = []
        route_loads = []
        route_clients = []
        infeasible_routes = 0
        late_clients = 0
        capacity_violations = 0

        assigned_ids = []
        for route in solution.routes:
            if not route.is_empty():
                route_eval = SolutionEvaluator.evaluate_route(route, use_time_windows=use_time_windows)
                route_distances.append(route_eval["total_distance"])
                route_loads.append(route.current_load)
                route_clients.append(len(route.clients))
                late_clients += route_eval["late_clients"]

                if not route_eval["feasible"]:
                    infeasible_routes += 1

                if route.current_load > route.capacity:
                    capacity_violations += 1

                assigned_ids.extend(client.id for client in route.clients)

        avg_distance = sum(route_distances) / num_vehicles if num_vehicles > 0 else 0.0
        avg_load = sum(route_loads) / num_vehicles if num_vehicles > 0 else 0.0
        avg_clients = sum(route_clients) / num_vehicles if num_vehicles > 0 else 0.0

        max_load = max(route_loads) if route_loads else 0.0
        min_load = min(route_loads) if route_loads else 0.0

        total_demand = sum(c.demand for c in clients)
        capacity_utilization = (
            total_demand / (solution.routes[0].capacity * num_vehicles)
            if num_vehicles > 0
            else 0.0
        )

        unique_assigned = len(set(assigned_ids))
        unassigned_clients = len(clients) - unique_assigned
        duplicate_assignments = len(assigned_ids) - unique_assigned

        return {
            "total_distance": total_distance,
            "num_vehicles": num_vehicles,
            "avg_distance_per_vehicle": avg_distance,
            "avg_load_per_vehicle": avg_load,
            "avg_clients_per_vehicle": avg_clients,
            "max_load": max_load,
            "min_load": min_load,
            "capacity_utilization": capacity_utilization,
            "unassigned_clients": unassigned_clients,
            "duplicate_assignments": duplicate_assignments,
            "infeasible_routes": infeasible_routes,
            "capacity_violations": capacity_violations,
            "late_clients": late_clients if use_time_windows else 0,
            "use_time_windows": use_time_windows,
            "feasible": SolutionEvaluator.is_feasible(
                solution,
                clients,
                use_time_windows=use_time_windows
            ),
        }

    @staticmethod
    def get_route_load_distribution(solution: Solution) -> List[float]:
        distribution = []
        for route in solution.routes:
            if route.capacity > 0:
                distribution.append(route.current_load / route.capacity)
            else:
                distribution.append(0.0)
        return distribution

    @staticmethod
    def compare_solutions(
        solution1: Solution,
        solution2: Solution,
        clients: List[Client],
        use_time_windows: bool = True
    ) -> Dict[str, any]:
        stats1 = SolutionEvaluator.get_solution_stats(
            solution1, clients, use_time_windows=use_time_windows
        )
        stats2 = SolutionEvaluator.get_solution_stats(
            solution2, clients, use_time_windows=use_time_windows
        )

        return {
            "solution1": stats1,
            "solution2": stats2,
            "distance_diff": stats1["total_distance"] - stats2["total_distance"],
            "vehicle_diff": stats1["num_vehicles"] - stats2["num_vehicles"],
            "solution1_better": (
                stats1["num_vehicles"], stats1["total_distance"]
            ) < (
                stats2["num_vehicles"], stats2["total_distance"]
            ),
        }