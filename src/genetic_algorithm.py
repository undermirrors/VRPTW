import random
import copy
from typing import List, Tuple
from models import Client, Depot, Route, Solution
from distance_utils import DistanceCalculator, SolutionEvaluator
from solution_generator import SolutionGenerator
from neighborhood import NeighborhoodManager


class GeneticAlgorithm:
    """
    Genetic Algorithm metaheuristic for VRPTW.

    Uses a population-based approach with:
    - Multiple crossover operators (route-based, order-based, segment-based)
    - Multiple mutation operators (using neighborhood operators)
    - Tournament selection
    - Elitism to preserve best solutions
    - Adaptive fitness evaluation with penalties for infeasibility
    """

    def __init__(self, depot: Depot, clients: List[Client], capacity: float,
                 population_size: int = 50, generations: int = 100,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.2,
                 elite_size: int = 2, tournament_size: int = 3,
                 ignore_time_windows: bool = False, minimize_vehicles: bool = False,
                 vehicle_weight: float = 100.0):
        """
        Initialize Genetic Algorithm.

        Args:
            depot: The depot
            clients: All clients to serve
            capacity: Vehicle capacity
            population_size: Size of population (individuals per generation)
            generations: Number of generations to evolve
            crossover_rate: Probability of applying crossover (0-1)
            mutation_rate: Probability of applying mutation (0-1)
            elite_size: Number of best solutions to preserve (elitism)
            tournament_size: Size of tournament for parent selection
            ignore_time_windows: If True, ignore time window constraints (VRP instead of VRPTW)
            minimize_vehicles: If True, penalize number of vehicles in objective
            vehicle_weight: Weight for vehicle count penalty (if minimize_vehicles=True)
        """
        self.depot = depot
        self.clients = clients
        self.capacity = capacity
        self.ignore_time_windows = ignore_time_windows
        self.minimize_vehicles = minimize_vehicles
        self.vehicle_weight = vehicle_weight

        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = min(elite_size, population_size // 2)
        self.tournament_size = tournament_size

        self.population: List[Solution] = []
        self.fitness_values: List[float] = []
        self.best_solution: Solution = None
        self.best_fitness: float = float('inf')

        self.neighborhood_manager = NeighborhoodManager()
        self.generation_history = []

    def initialize_population(self) -> None:
        """Initialize population with diverse solutions using different heuristics."""
        self.population = []

        # Create solutions using different construction heuristics for diversity
        for i in range(self.population_size):
            if i < self.population_size // 4:
                # Random solutions
                solution = SolutionGenerator.generate_random_solution(
                    self.depot, self.clients, self.capacity,
                    ignore_time_windows=self.ignore_time_windows
                )
            elif i < self.population_size // 2:
                # Nearest neighbor heuristic
                solution = SolutionGenerator.nearest_neighbor(
                    self.depot, self.clients, self.capacity,
                    ignore_time_windows=self.ignore_time_windows
                )
            elif i < 3 * self.population_size // 4:
                # Greedy insertion heuristic
                solution = SolutionGenerator.greedy_insertion(
                    self.depot, self.clients, self.capacity,
                    ignore_time_windows=self.ignore_time_windows
                )
            else:
                # Savings algorithm (Clarke-Wright)
                solution = SolutionGenerator.savings_algorithm(
                    self.depot, self.clients, self.capacity,
                    ignore_time_windows=self.ignore_time_windows
                )

            self.population.append(solution)

        self._evaluate_population()

    def _evaluate_population(self) -> None:
        """Evaluate fitness of entire population."""
        self.fitness_values = []
        for solution in self.population:
            fitness = SolutionEvaluator.evaluate_quality(
                solution, self.clients, penalty_weight=10000.0,
                minimize_vehicles=self.minimize_vehicles,
                vehicle_weight=self.vehicle_weight
            )
            self.fitness_values.append(fitness)

            # Track best solution found so far
            if fitness < self.best_fitness:
                self.best_fitness = fitness
                self.best_solution = solution.copy()

    def _tournament_selection(self) -> Solution:
        """
        Select a solution using tournament selection.
        Randomly selects tournament_size individuals and returns the best.
        """
        tournament_indices = random.sample(range(self.population_size), self.tournament_size)
        best_idx = min(tournament_indices, key=lambda i: self.fitness_values[i])
        return self.population[best_idx].copy()

    def _crossover_route_based(self, parent1: Solution, parent2: Solution) -> Solution:
        """
        Route-based crossover: Exchange complete routes between parents.

        Takes some routes from parent1 and some from parent2,
        then fills missing clients using available routes or creating new ones.
        """
        offspring = Solution(self.depot, self.capacity)

        # Add some routes from parent1
        num_routes_p1 = random.randint(1, max(1, len(parent1.routes)))
        if parent1.routes:
            selected_routes = random.sample(parent1.routes,
                                           min(num_routes_p1, len(parent1.routes)))

            for route in selected_routes:
                new_route = Route(self.depot, self.capacity)
                new_route.clients = route.clients.copy()
                new_route._recalculate()
                offspring.add_route(new_route)

        # Add clients from parent2 that are not yet in offspring
        assigned_clients = set(offspring.get_all_clients())
        unassigned = [c for c in self.clients if c not in assigned_clients]

        for client in unassigned:
            # Try to add to existing routes
            added = False
            for route in offspring.routes:
                if route.add_client(client):
                    added = True
                    break

            # If not added, create new route
            if not added:
                new_route = offspring.create_new_route()
                new_route.add_client(client)

        offspring.remove_empty_routes()
        return offspring

    def _crossover_order_based(self, parent1: Solution, parent2: Solution) -> Solution:
        """
        Order-based crossover: Preserve relative order of clients from parent1.

        Takes client ordering from parent1 and inserts remaining clients
        from parent2 in their relative order.
        """
        offspring = Solution(self.depot, self.capacity)

        # Get all clients in order from parent1
        parent1_order = []
        for route in parent1.routes:
            parent1_order.extend(route.clients)

        # Create merged order: parent1 clients first, then remaining from parent2
        merged_order = []
        for client in parent1_order:
            if client in self.clients:
                merged_order.append(client)

        for client in self.clients:
            if client not in merged_order:
                merged_order.append(client)

        # Reconstruct routes with this client order
        current_route = offspring.create_new_route()
        for client in merged_order:
            if not current_route.add_client(client):
                current_route = offspring.create_new_route()
                if not current_route.add_client(client):
                    # If client can't fit in new route, skip
                    pass

        offspring.remove_empty_routes()
        return offspring

    def _crossover_segment_based(self, parent1: Solution, parent2: Solution) -> Solution:
        """
        Segment-based crossover: Randomly select segments (routes) from both parents.

        Combines routes from both parents and reconstructs the solution.
        """
        offspring = Solution(self.depot, self.capacity)

        # Collect all routes from both parents
        all_routes = parent1.routes + parent2.routes

        if not all_routes:
            return offspring

        # Randomly select routes
        selected_routes = []
        assigned_clients = set()

        for _ in range(len(all_routes)):
            if not all_routes:
                break

            route = random.choice(all_routes)
            new_route = Route(self.depot, self.capacity)
            new_route.clients = route.clients.copy()
            new_route._recalculate()

            if new_route.is_feasible():
                offspring.add_route(new_route)
                assigned_clients.update(new_route.clients)
                selected_routes.append(route)

            all_routes.remove(route)

        # Add unassigned clients
        unassigned = [c for c in self.clients if c not in assigned_clients]

        for client in unassigned:
            added = False
            for route in offspring.routes:
                if route.add_client(client):
                    added = True
                    break
            if not added:
                new_route = offspring.create_new_route()
                new_route.add_client(client)

        offspring.remove_empty_routes()
        return offspring

    def _mutate(self, solution: Solution) -> Solution:
        """
        Apply mutation using multiple neighborhood operators.
        Applies 1-3 random neighborhood moves to the solution.
        """
        num_moves = random.randint(1, 3)
        for _ in range(num_moves):
            solution, _ = self.neighborhood_manager.apply_random_operator(solution)

        return solution

    def evolve(self, verbose: bool = False) -> Solution:
        """
        Run genetic algorithm evolution for specified number of generations.

        Args:
            verbose: Print progress information every 10 generations

        Returns:
            Best solution found during evolution
        """
        self.initialize_population()

        if verbose:
            distance = DistanceCalculator.solution_distance(self.best_solution)
            print(f"GA initialized. Best initial distance: {distance:.2f}, "
                  f"vehicles: {self.best_solution.get_num_vehicles()}")

        for generation in range(self.generations):
            # Create new generation
            new_population = []

            # Elitism: keep best solutions unchanged
            elite_indices = sorted(range(self.population_size),
                                  key=lambda i: self.fitness_values[i])[:self.elite_size]
            for idx in elite_indices:
                new_population.append(self.population[idx].copy())

            # Generate offspring through selection, crossover, and mutation
            while len(new_population) < self.population_size:
                # Selection (tournament)
                parent1 = self._tournament_selection()
                parent2 = self._tournament_selection()

                # Crossover
                if random.random() < self.crossover_rate:
                    crossover_type = random.choice(['route', 'order', 'segment'])
                    if crossover_type == 'route':
                        offspring = self._crossover_route_based(parent1, parent2)
                    elif crossover_type == 'order':
                        offspring = self._crossover_order_based(parent1, parent2)
                    else:
                        offspring = self._crossover_segment_based(parent1, parent2)
                else:
                    offspring = random.choice([parent1, parent2]).copy()

                # Mutation
                if random.random() < self.mutation_rate:
                    offspring = self._mutate(offspring)

                new_population.append(offspring)

            # Replace population with new generation
            self.population = new_population[:self.population_size]
            self._evaluate_population()

            # Record best fitness for this generation
            min_fitness = min(self.fitness_values)
            self.generation_history.append(min_fitness)

            if verbose and (generation + 1) % 10 == 0:
                distance = DistanceCalculator.solution_distance(self.best_solution)
                print(f"Generation {generation + 1}/{self.generations}, "
                      f"Best Distance: {distance:.2f}, "
                      f"Best Fitness: {self.best_fitness:.2f}, "
                      f"Vehicles: {self.best_solution.get_num_vehicles()}")

        if verbose:
            distance = DistanceCalculator.solution_distance(self.best_solution)
            print(f"GA completed. Final best distance: {distance:.2f}, "
                  f"vehicles: {self.best_solution.get_num_vehicles()}")

        return self.best_solution

    def get_statistics(self) -> dict:
        """Get statistics about the algorithm run."""
        stats = {
            'best_fitness': self.best_fitness,
            'best_solution': self.best_solution,
            'generation_history': self.generation_history,
            'final_population_size': len(self.population),
            'num_generations_run': len(self.generation_history),
        }

        if self.best_solution:
            stats['best_distance'] = DistanceCalculator.solution_distance(self.best_solution)
            stats['best_vehicles'] = self.best_solution.get_num_vehicles()

        return stats
