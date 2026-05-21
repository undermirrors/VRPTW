"""
Genetic Algorithm implementation for VRPTW / VRP.
"""

import random
from typing import List, Optional

from .models import Solution, Depot, Client
from .distance_utils import DistanceCalculator
from .solution_generator import SolutionGenerator
from . import hyperparameters as hp


class GeneticAlgorithm:
    """Genetic Algorithm for VRPTW/VRP optimization."""

    def __init__(
            self,
            depot: Depot,
            clients: List[Client],
            capacity: float,
            population_size: int = hp.GA_DEFAULT_POPULATION_SIZE,
            generations: int = hp.GA_DEFAULT_GENERATIONS,
            crossover_rate: float = hp.GA_DEFAULT_CROSSOVER_RATE,
            mutation_rate: float = hp.GA_DEFAULT_MUTATION_RATE,
            elite_size: int = hp.GA_DEFAULT_ELITE_SIZE,
            tournament_size: int = hp.GA_DEFAULT_TOURNAMENT_SIZE,
            use_time_windows: bool = True,
    ):
        if population_size < 4:
            raise ValueError("population_size must be at least 4")
        if not 0 <= crossover_rate <= 1:
            raise ValueError("crossover_rate must be between 0 and 1")
        if not 0 <= mutation_rate <= 1:
            raise ValueError("mutation_rate must be between 0 and 1")
        if tournament_size < 2:
            raise ValueError("tournament_size must be at least 2")

        self.depot = depot
        self.clients = clients
        self.capacity = capacity
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = min(elite_size, population_size // 2)
        self.tournament_size = tournament_size
        self.use_time_windows = use_time_windows

        self.population: List[Solution] = []
        self.best_solution: Optional[Solution] = None

    def evolve(self, verbose: bool = False) -> Solution:
        self._initialize_population()

        best_solution = min(self.population, key=self._solution_key).copy()

        if verbose:
            mode = "VRPTW" if self.use_time_windows else "VRP"
            print(
                f"GA ({mode}): Starting evolution with {self.population_size} individuals "
                f"for {self.generations} generations"
            )

        for gen in range(self.generations):
            sorted_pop = sorted(self.population, key=self._solution_key)
            current_best = sorted_pop[0]
            current_best_distance = DistanceCalculator.solution_distance(current_best)

            if self._solution_key(current_best) < self._solution_key(best_solution):
                best_solution = current_best.copy()

            if verbose and (gen + 1) % max(1, self.generations // 10) == 0:
                print(
                    f" Gen {gen + 1}: best vehicles = {current_best.get_num_vehicles()}, "
                    f"best distance = {current_best_distance:.2f}"
                )

            new_population = [sol.copy() for sol in sorted_pop[:self.elite_size]]

            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection()
                parent2 = self._tournament_selection()

                try:
                    if random.random() < self.crossover_rate:
                        child = self._crossover(parent1, parent2)
                    else:
                        child = parent1.copy()

                    if random.random() < self.mutation_rate:
                        child = self._mutate(child)

                    if not self._is_feasible(child):
                        raise RuntimeError("Generated infeasible child")

                    new_population.append(child)

                except RuntimeError:
                    fallback = parent1.copy()
                    if self._is_feasible(fallback):
                        new_population.append(fallback)
                    else:
                        repaired = min(self.population, key=self._solution_key).copy()
                        new_population.append(repaired)

            self.population = new_population[:self.population_size]

        self.best_solution = best_solution.copy()

        if verbose:
            print(
                f"GA: Evolution complete. Best vehicles: {best_solution.get_num_vehicles()}, "
                f"Best distance: {DistanceCalculator.solution_distance(best_solution):.2f}"
            )

        return best_solution

    def _initialize_population(self) -> None:
        self.population = []

        constructors = [
            SolutionGenerator.random_solution,
            SolutionGenerator.nearest_neighbor,
            SolutionGenerator.greedy_insertion,
            SolutionGenerator.multi_start_nearest_neighbor,
        ]

        for i in range(self.population_size):
            builder = constructors[i % len(constructors)]
            try:
                solution = builder(
                    self.depot,
                    self.clients,
                    self.capacity,
                    use_time_windows=self.use_time_windows,
                )
            except TypeError:
                solution = builder(
                    depot=self.depot,
                    clients=self.clients,
                    capacity=self.capacity,
                    use_time_windows=self.use_time_windows,
                )
            except RuntimeError:
                solution = SolutionGenerator.random_solution(
                    self.depot,
                    self.clients,
                    self.capacity,
                    use_time_windows=self.use_time_windows,
                )

            self.population.append(solution)

    def _fitness(self, solution: Solution) -> float:
        feasible = self._is_feasible(solution)
        vehicles = solution.get_num_vehicles()
        distance = DistanceCalculator.solution_distance(solution)

        if not feasible:
            return 1e-12 / (1.0 + vehicles + distance)

        return 1.0 / (1.0 + vehicles * 1_000_000 + distance)

    def _tournament_selection(self) -> Solution:
        tournament = random.sample(
            self.population,
            min(self.tournament_size, len(self.population)),
        )
        return max(tournament, key=self._fitness)

    def _crossover(self, parent1: Solution, parent2: Solution) -> Solution:
        child = parent1.copy()

        for i in range(min(len(child.routes), len(parent2.routes))):
            if random.random() < 0.5:
                p2_route = parent2.routes[i]
                c_route = child.routes[i]

                c_route.clients.clear()
                c_route._current_load = 0.0

                for client in p2_route.clients:
                    if c_route.can_add_client(
                            client,
                            use_time_windows=self.use_time_windows,
                    ):
                        c_route.add_client(
                            client,
                            use_time_windows=self.use_time_windows,
                        )

        self._repair_solution(child)
        child.invalidate_cache()
        return child

    def _mutate(self, solution: Solution) -> Solution:
        mutated = solution.copy()

        mutation_type = random.choice(["swap_clients", "move_client", "swap_routes"])

        try:
            if mutation_type == "swap_clients":
                non_empty_routes = [r for r in mutated.routes if len(r.clients) >= 2]
                if non_empty_routes:
                    route = random.choice(non_empty_routes)
                    i, j = random.sample(range(len(route.clients)), 2)
                    route.clients[i], route.clients[j] = route.clients[j], route.clients[i]

            elif mutation_type == "move_client":
                non_empty_routes = [r for r in mutated.routes if not r.is_empty()]
                target_routes = [r for r in mutated.routes]

                if non_empty_routes:
                    src_route = random.choice(non_empty_routes)
                    client = random.choice(src_route.clients)

                    candidate_routes = [
                        r
                        for r in target_routes
                        if r is not src_route
                           and r.can_add_client(
                            client,
                            use_time_windows=self.use_time_windows,
                        )
                    ]
                    if candidate_routes:
                        dst_route = random.choice(candidate_routes)
                        src_route.remove_client(client)
                        dst_route.add_client(
                            client,
                            use_time_windows=self.use_time_windows,
                        )

            elif mutation_type == "swap_routes":
                if len(mutated.routes) >= 2:
                    i, j = random.sample(range(len(mutated.routes)), 2)
                    mutated.routes[i], mutated.routes[j] = mutated.routes[j], mutated.routes[i]

        except (ValueError, IndexError):
            pass

        self._repair_solution(mutated)
        mutated.invalidate_cache()
        return mutated

    def _repair_solution(self, solution: Solution) -> None:
        seen = set()
        duplicates = []

        for route in solution.routes:
            unique_clients = []
            load = 0.0

            for client in route.clients:
                if client.id in seen:
                    duplicates.append(client)
                else:
                    seen.add(client.id)
                    unique_clients.append(client)
                    load += client.demand

            route.clients[:] = unique_clients
            route._current_load = load

        missing = [client for client in self.clients if client.id not in seen]

        for client in duplicates + missing:
            placed = False
            for route in solution.routes:
                if route.can_add_client(
                        client,
                        use_time_windows=self.use_time_windows,
                ):
                    route.add_client(
                        client,
                        use_time_windows=self.use_time_windows,
                    )
                    placed = True
                    break
            if not placed:
                raise RuntimeError(f"Unable to repair solution for client {client.id}")

        solution.invalidate_cache()

        if not self._is_feasible(solution):
            raise RuntimeError("Repair produced an infeasible solution")

    def _is_feasible(self, solution: Solution) -> bool:
        return solution.is_feasible(use_time_windows=self.use_time_windows)

    def _solution_key(self, solution: Solution):
        feasible = self._is_feasible(solution)
        vehicles = solution.get_num_vehicles()
        distance = DistanceCalculator.solution_distance(solution)
        return (0 if feasible else 1, vehicles, distance)
