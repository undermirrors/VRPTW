"""
Tabu Search implementation for VRPTW / VRP.
"""

import random
from typing import List, Optional, Tuple

from .models import Solution, Depot, Client
from .distance_utils import DistanceCalculator
from .solution_generator import SolutionGenerator

TS_DEFAULT_MAX_ITERATIONS = 1000
TS_DEFAULT_TABU_TENURE = None
TS_DEFAULT_NEIGHBORHOOD_SIZE = 100
TS_DEFAULT_ASPIRATION_CRITERIA = True


class TabuSearch:
    """Tabu Search metaheuristic for VRPTW/VRP."""

    def __init__(
            self,
            depot: Depot,
            clients: List[Client],
            capacity: float,
            max_iterations: int = TS_DEFAULT_MAX_ITERATIONS,
            tabu_tenure: Optional[int] = TS_DEFAULT_TABU_TENURE,
            neighborhood_size: int = TS_DEFAULT_NEIGHBORHOOD_SIZE,
            aspiration_criteria: bool = TS_DEFAULT_ASPIRATION_CRITERIA,
            use_time_windows: bool = True,
    ):
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")
        if neighborhood_size < 1:
            raise ValueError("neighborhood_size must be at least 1")

        self.depot = depot
        self.clients = clients
        self.capacity = capacity
        self.max_iterations = max_iterations
        self.neighborhood_size = neighborhood_size
        self.aspiration_criteria = aspiration_criteria
        self.use_time_windows = use_time_windows
        self.tabu_tenure = (
            tabu_tenure if tabu_tenure is not None else max(10, len(clients) // 2)
        )

        self.tabu_list: List[Tuple[str, int]] = []
        self.iteration_count = 0
        self.best_solution: Optional[Solution] = None

    def search(self, initial_solution: Optional[Solution] = None, verbose: bool = False) -> Solution:
        if initial_solution is None:
            try:
                current_solution = SolutionGenerator.nearest_neighbor(
                    self.depot,
                    self.clients,
                    self.capacity,
                    use_time_windows=self.use_time_windows,
                )
            except RuntimeError:
                current_solution = SolutionGenerator.random_solution(
                    self.depot,
                    self.clients,
                    self.capacity,
                    use_time_windows=self.use_time_windows,
                )
        else:
            current_solution = initial_solution.copy()

        best_solution = current_solution.copy()
        best_key = self._solution_key(best_solution)

        if verbose:
            mode = "VRPTW" if self.use_time_windows else "VRP"
            print(f"TS ({mode}): Starting search from distance {best_key[1]:.2f}")
            print(f"TS: Tabu tenure = {self.tabu_tenure}, neighborhood = {self.neighborhood_size}")

        no_improve_count = 0

        for self.iteration_count in range(self.max_iterations):
            neighbors = self._get_neighbors(current_solution)

            if not neighbors:
                no_improve_count += 1
                continue

            feasible_neighbors = [n for n in neighbors if self._is_feasible(n)]

            candidate_pool = feasible_neighbors if feasible_neighbors else []

            best_neighbor = None
            best_neighbor_key = (float("inf"), float("inf"), float("inf"))

            for neighbor in candidate_pool:
                neighbor_key = self._solution_key(neighbor)
                move_hash = self._hash_solution(neighbor)
                is_tabu = self._is_tabu(move_hash)

                if (not is_tabu) or (
                        self.aspiration_criteria and neighbor_key < best_key
                ):
                    if neighbor_key < best_neighbor_key:
                        best_neighbor = neighbor
                        best_neighbor_key = neighbor_key

            if best_neighbor is None:
                if candidate_pool:
                    best_neighbor = min(candidate_pool, key=self._solution_key)
                    best_neighbor_key = self._solution_key(best_neighbor)
                else:
                    no_improve_count += 1
                    continue

            current_solution = best_neighbor
            self.tabu_list.append(
                (self._hash_solution(current_solution), self.iteration_count + self.tabu_tenure)
            )
            self._clean_tabu_list()

            if best_neighbor_key < best_key:
                best_key = best_neighbor_key
                best_solution = best_neighbor.copy()
                no_improve_count = 0

                if verbose and (self.iteration_count + 1) % max(1, self.max_iterations // 10) == 0:
                    print(
                        f" Iter {self.iteration_count + 1}: "
                        f"New best vehicles = {best_key[0]}, distance = {best_key[1]:.2f}"
                    )
            else:
                no_improve_count += 1

            if no_improve_count > self.max_iterations // 5:
                if verbose:
                    print(
                        f" Iter {self.iteration_count + 1}: "
                        f"No improvement for {no_improve_count} iterations, stopping"
                    )
                break

        self.best_solution = best_solution.copy()

        if verbose:
            print(
                f"TS: Search complete. Best vehicles: {best_key[0]}, "
                f"Best distance: {best_key[1]:.2f}"
            )

        return best_solution

    def _get_neighbors(self, solution: Solution) -> List[Solution]:
        neighbors: List[Solution] = []

        non_empty_route_indices = [
            i for i, route in enumerate(solution.routes) if not route.is_empty()
        ]
        if not non_empty_route_indices:
            return neighbors

        attempts = 0
        max_attempts = max(self.neighborhood_size * 3, 20)

        while len(neighbors) < self.neighborhood_size and attempts < max_attempts:
            attempts += 1
            neighbor = solution.copy()

            mutation_type = random.choice(
                ["swap_in_route", "move_between_routes", "swap_between_routes"]
            )

            try:
                if mutation_type == "swap_in_route":
                    candidate_indices = [
                        i for i in non_empty_route_indices
                        if len(neighbor.routes[i].clients) >= 2
                    ]
                    if not candidate_indices:
                        continue

                    r_idx = random.choice(candidate_indices)
                    route = neighbor.routes[r_idx]
                    i, j = random.sample(range(len(route.clients)), 2)
                    route.clients[i], route.clients[j] = route.clients[j], route.clients[i]

                elif mutation_type == "move_between_routes":
                    src_candidates = [r for r in neighbor.routes if not r.is_empty()]
                    if not src_candidates:
                        continue

                    src_route = random.choice(src_candidates)
                    client = random.choice(src_route.clients)

                    dst_candidates = [
                        r
                        for r in neighbor.routes
                        if r is not src_route
                           and r.can_add_client(
                            client,
                            use_time_windows=self.use_time_windows,
                        )
                    ]
                    if not dst_candidates:
                        continue

                    dst_route = random.choice(dst_candidates)
                    src_route.remove_client(client)
                    dst_route.add_client(
                        client,
                        use_time_windows=self.use_time_windows,
                    )

                elif mutation_type == "swap_between_routes":
                    route_candidates = [r for r in neighbor.routes if not r.is_empty()]
                    if len(route_candidates) < 2:
                        continue

                    r1, r2 = random.sample(route_candidates, 2)
                    c1 = random.choice(r1.clients)
                    c2 = random.choice(r2.clients)

                    new_load_r1 = r1.current_load - c1.demand + c2.demand
                    new_load_r2 = r2.current_load - c2.demand + c1.demand

                    if new_load_r1 <= r1.capacity and new_load_r2 <= r2.capacity:
                        i1 = r1.clients.index(c1)
                        i2 = r2.clients.index(c2)

                        old1 = r1.clients[i1]
                        old2 = r2.clients[i2]

                        r1.clients[i1], r2.clients[i2] = old2, old1
                        r1._current_load = new_load_r1
                        r2._current_load = new_load_r2

                        if self.use_time_windows:
                            if (not neighbor.is_feasible(use_time_windows=True)):
                                r1.clients[i1], r2.clients[i2] = old1, old2
                                r1._current_load = r1.current_load - c2.demand + c1.demand
                                r2._current_load = r2.current_load - c1.demand + c2.demand
                                continue
                    else:
                        continue

                neighbor.invalidate_cache()

                if (
                        self._hash_solution(neighbor) != self._hash_solution(solution)
                        and self._is_feasible(neighbor)
                ):
                    neighbors.append(neighbor)

            except (ValueError, IndexError):
                continue

        return neighbors

    @staticmethod
    def _hash_solution(solution: Solution) -> str:
        route_hashes = []
        for route in solution.routes:
            if not route.is_empty():
                client_ids = tuple(client.id for client in route.clients)
                route_hashes.append(str(client_ids))
        return "|".join(sorted(route_hashes))

    def _is_tabu(self, move_hash: str) -> bool:
        for tabu_hash, expiration in self.tabu_list:
            if tabu_hash == move_hash and expiration > self.iteration_count:
                return True
        return False

    def _clean_tabu_list(self) -> None:
        self.tabu_list = [
            (move_hash, expiration)
            for move_hash, expiration in self.tabu_list
            if expiration > self.iteration_count
        ]

    def _is_feasible(self, solution: Solution) -> bool:
        return solution.is_feasible(use_time_windows=self.use_time_windows)

    def _solution_key(self, solution: Solution):
        feasible = self._is_feasible(solution)
        vehicles = solution.get_num_vehicles()
        distance = DistanceCalculator.solution_distance(solution)
        return (0 if feasible else 1, vehicles, distance)
