"""
Initial solution generation heuristics for VRPTW / VRP.
"""

import random
from typing import List, Optional

from .models import Solution, Depot, Client
from .distance_utils import DistanceCalculator


class SolutionGenerator:
    """Generate initial solutions using various construction heuristics."""

    @staticmethod
    def generate_empty_solution(depot: Depot, clients: List[Client]) -> Solution:
        return Solution(depot, clients, num_vehicles=len(clients))

    @staticmethod
    def random_solution(
        depot: Depot,
        clients: List[Client],
        capacity: float,
        use_time_windows: bool = True,
    ) -> Solution:
        solution = SolutionGenerator.generate_empty_solution(depot, clients)
        shuffled = clients[:]
        random.shuffle(shuffled)

        route_idx = 0
        for client in shuffled:
            placed = False
            while route_idx < len(solution.routes):
                route = solution.get_route(route_idx)
                if route.can_add_client(client, use_time_windows=use_time_windows):
                    route.add_client(client, use_time_windows=use_time_windows)
                    placed = True
                    break
                route_idx += 1

            if not placed:
                raise RuntimeError("Not enough vehicles to accommodate all clients")

        solution.invalidate_cache()
        return solution

    @staticmethod
    def nearest_neighbor(
        depot: Depot,
        clients: List[Client],
        capacity: float,
        start_client: Optional[Client] = None,
        use_time_windows: bool = True,
    ) -> Solution:
        solution = SolutionGenerator.generate_empty_solution(depot, clients)
        unassigned = set(clients)
        route_idx = 0

        while unassigned:
            if route_idx >= len(solution.routes):
                raise RuntimeError("Not enough vehicles for nearest neighbor construction")

            route = solution.get_route(route_idx)

            feasible_candidates = [
                c for c in unassigned
                if route.can_add_client(c, use_time_windows=use_time_windows)
            ]

            if not feasible_candidates:
                route_idx += 1
                continue

            if route.is_empty():
                if (
                    start_client is not None
                    and start_client in unassigned
                    and route.can_add_client(
                        start_client,
                        use_time_windows=use_time_windows,
                    )
                ):
                    chosen = start_client
                    start_client = None
                else:
                    chosen = min(
                        feasible_candidates,
                        key=lambda c: DistanceCalculator.get_distance(
                            depot.location,
                            c.location,
                        ),
                    )
            else:
                current_location = route.clients[-1].location
                chosen = min(
                    feasible_candidates,
                    key=lambda c: DistanceCalculator.get_distance(
                        current_location,
                        c.location,
                    ),
                )

            route.add_client(chosen, use_time_windows=use_time_windows)
            unassigned.remove(chosen)

        solution.invalidate_cache()
        return solution

    @staticmethod
    def greedy_insertion(
        depot: Depot,
        clients: List[Client],
        capacity: float,
        use_time_windows: bool = True,
    ) -> Solution:
        solution = SolutionGenerator.generate_empty_solution(depot, clients)
        unassigned = set(clients)
        route_idx = 0

        while unassigned:
            if route_idx >= len(solution.routes):
                raise RuntimeError("Not enough vehicles for greedy insertion")

            route = solution.get_route(route_idx)

            best_client = None
            best_position = 0
            best_delta = float("inf")

            for client in unassigned:
                if not route.can_add_client(client, use_time_windows=use_time_windows):
                    continue

                for position in range(len(route.clients) + 1):
                    trial_clients = route.clients[:]
                    trial_clients.insert(position, client)

                    if use_time_windows and not route._would_respect_time_windows(trial_clients):
                        continue

                    delta = DistanceCalculator.insertion_distance_delta(route, client, position)
                    if delta < best_delta:
                        best_delta = delta
                        best_client = client
                        best_position = position

            if best_client is None:
                route_idx += 1
                continue

            route.clients.insert(best_position, best_client)
            route._current_load += best_client.demand
            route._invalidate_cache()
            unassigned.remove(best_client)

        solution.invalidate_cache()
        return solution

    @staticmethod
    def savings_algorithm(
        depot: Depot,
        clients: List[Client],
        capacity: float,
        use_time_windows: bool = True,
    ) -> Solution:
        return SolutionGenerator.nearest_neighbor(
            depot=depot,
            clients=clients,
            capacity=capacity,
            use_time_windows=use_time_windows,
        )

    @staticmethod
    def multi_start_nearest_neighbor(
        depot: Depot,
        clients: List[Client],
        capacity: float,
        num_starts: int = 5,
        use_time_windows: bool = True,
    ) -> Solution:
        best_solution = None
        best_key = (float("inf"), float("inf"))

        if not clients:
            return SolutionGenerator.generate_empty_solution(depot, clients)

        starts = random.sample(clients, min(num_starts, len(clients)))

        for start in starts:
            try:
                solution = SolutionGenerator.nearest_neighbor(
                    depot=depot,
                    clients=clients,
                    capacity=capacity,
                    start_client=start,
                    use_time_windows=use_time_windows,
                )
                key = (
                    solution.get_num_vehicles(),
                    DistanceCalculator.solution_distance(solution),
                )
                if key < best_key:
                    best_key = key
                    best_solution = solution
            except RuntimeError:
                continue

        if best_solution is None:
            return SolutionGenerator.random_solution(
                depot,
                clients,
                capacity,
                use_time_windows=use_time_windows,
            )

        return best_solution