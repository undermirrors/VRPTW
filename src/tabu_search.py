import random
import time
from typing import List, Tuple, Optional, Set
from models import Client, Depot, Solution
from distance_utils import DistanceCalculator, SolutionEvaluator
from solution_generator import SolutionGenerator
from neighborhood import NeighborhoodManager, TwoOpt, OrOpt, Relocate, CrossExchange, TwoOptBetweenRoutes


class TabuAttribute:
    """Represents an attribute (move) in the tabu list."""

    def __init__(self, move_description: str, tabu_tenure: int):
        """
        Args:
            move_description: Description of the move (e.g., "relocate_c1_to_route_2")
            tabu_tenure: Number of iterations this move remains tabu
        """
        self.move_description = move_description
        self.tabu_tenure = tabu_tenure
        self.iteration_added = 0


class TabuSearch:
    """
    Tabu Search metaheuristic for VRPTW.

    Uses:
    - Tabu list to avoid cycling and revisiting recent solutions
    - Aspiration criteria to override tabu status for improving solutions
    - Best improvement neighborhood exploration strategy
    - Adaptive tabu tenure based on problem size
    - Diversification and intensification strategies
    - Multiple neighborhood operators for rich search space exploration
    """

    def __init__(self, depot: Depot, clients: List[Client], capacity: float,
                 max_iterations: int = 1000, tabu_tenure: int = None,
                 neighborhood_size: int = 100, diversification_freq: int = 50,
                 ignore_time_windows: bool = False, minimize_vehicles: bool = False,
                 vehicle_weight: float = 100.0):
        """
        Initialize Tabu Search.

        Args:
            depot: The depot
            clients: All clients to serve
            capacity: Vehicle capacity
            max_iterations: Maximum number of iterations
            tabu_tenure: Number of iterations a move stays tabu (auto-calculated if None)
            neighborhood_size: Size of neighborhood to explore per iteration
            diversification_freq: Frequency of diversification moves (in iterations)
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

        self.max_iterations = max_iterations
        # Auto-calculate tabu tenure based on problem size
        self.tabu_tenure = tabu_tenure or max(7, len(clients) // 10)
        self.neighborhood_size = neighborhood_size
        self.diversification_freq = diversification_freq

        self.current_solution: Solution = None
        self.best_solution: Solution = None
        self.best_fitness: float = float('inf')
        self.current_fitness: float = float('inf')

        self.tabu_list: List[TabuAttribute] = []
        self.iteration = 0
        self.neighborhood_manager = NeighborhoodManager()

        self.iteration_history = []
        self.best_history = []

    def initialize(self) -> None:
        """Initialize with a good initial solution using multi-start nearest neighbor."""
        # Use multi-start nearest neighbor to get good initial solution
        self.current_solution = SolutionGenerator.multi_start_nearest_neighbor(
            self.depot, self.clients, self.capacity, num_restarts=5,
            ignore_time_windows=self.ignore_time_windows
        )

        self.best_solution = self.current_solution.copy()
        self.best_fitness = SolutionEvaluator.evaluate_quality(
            self.best_solution, self.clients,
            minimize_vehicles=self.minimize_vehicles,
            vehicle_weight=self.vehicle_weight
        )
        self.current_fitness = self.best_fitness

    def _update_tabu_list(self) -> None:
        """Remove expired tabu attributes (those whose tenure has expired)."""
        self.tabu_list = [attr for attr in self.tabu_list
                         if self.iteration - attr.iteration_added < attr.tabu_tenure]

    def _is_tabu(self, move_description: str) -> bool:
        """Check if a move is currently in the tabu list."""
        for attr in self.tabu_list:
            if attr.move_description == move_description:
                return True
        return False

    def _add_to_tabu(self, move_description: str) -> None:
        """Add a move to the tabu list with specified tenure."""
        # Check if already in list and update its iteration
        for attr in self.tabu_list:
            if attr.move_description == move_description:
                attr.iteration_added = self.iteration
                return

        # Add new tabu attribute
        tabu_attr = TabuAttribute(move_description, self.tabu_tenure)
        tabu_attr.iteration_added = self.iteration
        self.tabu_list.append(tabu_attr)

    def _aspiration_criteria(self, candidate_fitness: float) -> bool:
        """
        Check if aspiration criteria is met.
        Override tabu status if solution is better than best found so far.
        This prevents tabu restrictions from preventing finding new best solutions.
        """
        return candidate_fitness < self.best_fitness

    def _explore_neighborhood(self, solution: Solution) -> Tuple[Optional[Solution], Optional[str], float]:
        """
        Explore neighborhood using best improvement strategy.
        Returns the best neighbor found that is not tabu (or meets aspiration criteria).
        """
        best_neighbor = None
        best_move_desc = None
        best_candidate_fitness = float('inf')

        # Apply multiple random moves to explore different neighbors
        for _ in range(min(self.neighborhood_size, 50)):
            # Generate random move
            neighbor, move_desc = self.neighborhood_manager.apply_random_operator(solution)

            if neighbor is None:
                continue

            # Evaluate neighbor
            neighbor_fitness = SolutionEvaluator.evaluate_quality(
                neighbor, self.clients,
                minimize_vehicles=self.minimize_vehicles,
                vehicle_weight=self.vehicle_weight
            )

            # Check tabu status
            is_tabu = self._is_tabu(move_desc)

            # Accept if: not tabu, or tabu but meets aspiration criteria, and improves best found
            if not is_tabu or self._aspiration_criteria(neighbor_fitness):
                if neighbor_fitness < best_candidate_fitness:
                    best_candidate_fitness = neighbor_fitness
                    best_neighbor = neighbor
                    best_move_desc = move_desc

        delta = best_candidate_fitness - self.current_fitness if best_neighbor else 0.0
        return best_neighbor, best_move_desc, delta

    def _diversification(self, solution: Solution) -> Solution:
        """
        Apply diversification strategy to escape local optima.
        Applies multiple random moves to create a significantly different solution.
        """
        new_solution = solution.copy()
        num_moves = random.randint(5, 10)

        for _ in range(num_moves):
            new_solution, _ = self.neighborhood_manager.apply_random_operator(new_solution)

        return new_solution

    def _intensification(self, solution: Solution) -> Solution:
        """
        Apply intensification strategy to improve current good solutions.
        Uses best-improvement moves multiple times.
        """
        current = solution.copy()

        for _ in range(3):
            # Temporarily disable diversification
            old_freq = self.diversification_freq
            self.diversification_freq = float('inf')

            neighbor, move_desc, delta = self._explore_neighborhood(current)

            self.diversification_freq = old_freq

            if neighbor and delta < 0:
                current = neighbor
            else:
                break

        return current

    def search(self, verbose: bool = False) -> Solution:
        """
        Run tabu search algorithm for specified number of iterations.

        Args:
            verbose: Print progress information every 50 iterations

        Returns:
            Best solution found during search
        """
        self.initialize()

        if verbose:
            distance = DistanceCalculator.solution_distance(self.best_solution)
            vehicles = self.best_solution.get_num_vehicles()
            mode = "VRP" if self.ignore_time_windows else "VRPTW"
            obj = f"distance + vehicles" if self.minimize_vehicles else "distance"
            print(f"Tabu Search initialized:")
            print(f"  Mode: {mode}")
            print(f"  Objective: minimize {obj}")
            print(f"  Initial distance: {distance:.2f}")
            print(f"  Initial vehicles: {vehicles}")
            print(f"  Tabu tenure: {self.tabu_tenure}")
            print(f"  Max iterations: {self.max_iterations}")

        no_improvement_counter = 0

        for self.iteration in range(self.max_iterations):
            # Update tabu list (remove expired entries)
            self._update_tabu_list()

            # Decide on exploration strategy
            if no_improvement_counter > 0 and self.iteration % self.diversification_freq == 0:
                # Apply diversification when stuck
                self.current_solution = self._diversification(self.current_solution)
                self.current_fitness = SolutionEvaluator.evaluate_quality(
                    self.current_solution, self.clients
                )
                no_improvement_counter = 0

                if verbose and (self.iteration + 1) % 50 == 0:
                    print(f"  [Iteration {self.iteration + 1}] Diversification applied")

            elif no_improvement_counter > 0 and no_improvement_counter % 2 == 0:
                # Apply intensification to improve good solutions
                self.current_solution = self._intensification(self.current_solution)
                self.current_fitness = SolutionEvaluator.evaluate_quality(
                    self.current_solution, self.clients
                )

                if verbose and (self.iteration + 1) % 50 == 0:
                    print(f"  [Iteration {self.iteration + 1}] Intensification applied")

            else:
                # Explore neighborhood normally
                neighbor, move_desc, delta = self._explore_neighborhood(self.current_solution)

                if neighbor is not None:
                    self.current_solution = neighbor
                    self.current_fitness = SolutionEvaluator.evaluate_quality(
                        self.current_solution, self.clients,
                        minimize_vehicles=self.minimize_vehicles,
                        vehicle_weight=self.vehicle_weight
                    )

                    # Add move to tabu list
                    if move_desc:
                        self._add_to_tabu(move_desc)

                    # Update best if improved
                    if self.current_fitness < self.best_fitness:
                        self.best_fitness = self.current_fitness
                        self.best_solution = self.current_solution.copy()
                        no_improvement_counter = 0
                    else:
                        no_improvement_counter += 1
                else:
                    no_improvement_counter += 1

            # Record iteration history
            self.iteration_history.append(self.current_fitness)
            self.best_history.append(self.best_fitness)

            if verbose and (self.iteration + 1) % 50 == 0:
                distance = DistanceCalculator.solution_distance(self.best_solution)
                vehicles = self.best_solution.get_num_vehicles()
                print(f"Iteration {self.iteration + 1}/{self.max_iterations}:")
                print(f"  Best Distance: {distance:.2f}")
                print(f"  Best Vehicles: {vehicles}")
                print(f"  Current Fitness: {self.current_fitness:.2f}")
                print(f"  Tabu List Size: {len(self.tabu_list)}")
                print(f"  No Improvement: {no_improvement_counter} iterations")

        if verbose:
            distance = DistanceCalculator.solution_distance(self.best_solution)
            vehicles = self.best_solution.get_num_vehicles()
            print(f"\nTabu Search completed:")
            print(f"  Final best distance: {distance:.2f}")
            print(f"  Final vehicles: {vehicles}")

        return self.best_solution

    def get_statistics(self) -> dict:
        """Get comprehensive statistics about the search run."""
        stats = {
            'best_fitness': self.best_fitness,
            'best_solution': self.best_solution,
            'iteration_history': self.iteration_history,
            'best_history': self.best_history,
            'final_tabu_list_size': len(self.tabu_list),
            'iterations_run': self.iteration + 1,
            'tabu_tenure_used': self.tabu_tenure,
        }

        if self.best_solution:
            stats['best_distance'] = DistanceCalculator.solution_distance(self.best_solution)
            stats['best_vehicles'] = self.best_solution.get_num_vehicles()

        return stats
