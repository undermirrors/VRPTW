import random
from typing import List, Tuple, Optional
from models import Client, Route, Solution, Depot
from distance_utils import DistanceCalculator


class LargeNeighborhoodSearch:
    """
    Large Neighborhood Search (LNS) operator.
    Destroys part of a solution and repairs it to find new, potentially better solutions.
    This is a more powerful operator than simple local search moves.
    """

    def __init__(self, destruction_rate: float = 0.3, num_iterations: int = 10):
        """
        Args:
            destruction_rate: Percentage of clients to remove (0-1).
            num_iterations: Number of repair attempts.
        """
        self.destruction_rate = destruction_rate
        self.num_iterations = num_iterations

    def apply(self, solution: Solution) -> Solution:
        """
        Apply the LNS operator.

        1. **Destroy**: Remove a fraction of clients from the solution.
        2. **Repair**: Re-insert the removed clients using a greedy heuristic.
        """
        solution_copy = solution.copy()

        # 1. Destruction Phase
        num_clients_to_remove = int(len(solution.get_all_clients()) * self.destruction_rate)
        if num_clients_to_remove == 0:
            return solution_copy

        # Select clients to remove (randomly for simplicity)
        all_clients = solution_copy.get_all_clients()
        clients_to_remove = random.sample(all_clients, num_clients_to_remove)

        # Create a set for faster lookups
        clients_to_remove_set = set(c.client_id for c in clients_to_remove)

        # Remove clients from their routes
        for route in solution_copy.routes:
            route.clients = [c for c in route.clients if c.client_id not in clients_to_remove_set]
            route._recalculate()

        solution_copy.remove_empty_routes()

        # 2. Repair Phase
        # Use a greedy insertion heuristic to re-insert the removed clients
        unvisited = clients_to_remove
        random.shuffle(unvisited)

        for client in unvisited:
            best_route = None
            best_position = -1
            min_cost_increase = float('inf')

            # Find the best insertion position across all routes
            for route in solution_copy.routes:
                for pos in range(len(route.clients) + 1):
                    # Check if insertion is feasible
                    if route.can_insert_client(client, pos):
                        cost_increase = DistanceCalculator.insertion_distance_delta(route, client, pos)
                        if cost_increase < min_cost_increase:
                            min_cost_increase = cost_increase
                            best_route = route
                            best_position = pos

            # Also consider creating a new route
            new_route_cost = DistanceCalculator.insertion_distance_delta(Route(solution.depot, solution.capacity), client, 0)
            if new_route_cost < min_cost_increase:
                best_route = None # Sentinel for new route
                min_cost_increase = new_route_cost

            # Perform the insertion
            if best_route is not None:
                best_route.insert_client(client, best_position)
            elif best_position != -1: # New route
                new_route = solution_copy.create_new_route()
                new_route.add_client(client)

        solution_copy.remove_empty_routes()
        return solution_copy


class FeasibilityRestorer:
    """
    An operator specifically designed to restore feasibility to a solution.
    It focuses on inserting unassigned clients, even if it increases the total distance.
    """

    @staticmethod
    def restore(solution: Solution, all_clients: List[Client]) -> Solution:
        """
        Attempts to insert all unassigned clients into the solution.

        Args:
            solution: The potentially infeasible solution.
            all_clients: The complete list of clients for the problem.

        Returns:
            A new solution, hopefully more feasible.
        """
        solution_copy = solution.copy()

        assigned_client_ids = {c.client_id for c in solution_copy.get_all_clients()}
        unassigned_clients = [c for c in all_clients if c.client_id not in assigned_client_ids]

        if not unassigned_clients:
            return solution_copy # Already feasible

        random.shuffle(unassigned_clients)

        for client in unassigned_clients:
            inserted = False
            # Try to insert into an existing route
            for route in solution_copy.routes:
                for pos in range(len(route.clients) + 1):
                    if route.can_insert_client(client, pos):
                        route.insert_client(client, pos)
                        inserted = True
                        break
                if inserted:
                    break

            # If not inserted, create a new route for it
            if not inserted:
                new_route = solution_copy.create_new_route()
                if new_route.can_add_client(client):
                    new_route.add_client(client)

        return solution_copy
