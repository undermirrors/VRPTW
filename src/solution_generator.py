import random
from typing import List, Optional
from models import Client, Depot, Route, Solution
from distance_utils import DistanceCalculator


class SolutionGenerator:
    """Generates initial solutions using various construction heuristics."""

    @staticmethod
    def generate_random_solution(depot: Depot, clients: List[Client], capacity: float,
                                ignore_time_windows: bool = False) -> Solution:
        """
        Generate a random solution by randomly assigning clients to routes.
        May produce infeasible solutions.

        Args:
            depot: The depot
            clients: List of all clients
            capacity: Vehicle capacity
            ignore_time_windows: If True, ignore time window constraints

        Returns:
            A Solution with clients randomly distributed among routes
        """
        solution = Solution(depot, capacity, ignore_time_windows=ignore_time_windows)
        shuffled_clients = clients.copy()
        random.shuffle(shuffled_clients)

        for client in shuffled_clients:
            # Try to add to existing route
            added = False
            for route in solution.routes:
                if route.add_client(client):
                    added = True
                    break

            # If not added to any route, create new route
            if not added:
                new_route = solution.create_new_route()
                new_route.add_client(client)

        solution.remove_empty_routes()
        return solution

    @staticmethod
    def nearest_neighbor(depot: Depot, clients: List[Client], capacity: float,
                        start_client: Optional[Client] = None,
                        ignore_time_windows: bool = False) -> Solution:
        """
        Nearest neighbor heuristic: greedily build routes by always adding
        the nearest unvisited client.

        Args:
            depot: The depot
            clients: List of all clients
            capacity: Vehicle capacity
            start_client: Optional starting client (random if not specified)
            ignore_time_windows: If True, ignore time window constraints

        Returns:
            A Solution constructed with nearest neighbor
        """
        solution = Solution(depot, capacity, ignore_time_windows=ignore_time_windows)
        unvisited = set(clients)

        if start_client and start_client in unvisited:
            current_client = start_client
        else:
            current_client = random.choice(list(unvisited))

        unvisited.remove(current_client)

        # Start first route with first client
        current_route = solution.create_new_route()
        current_route.add_client(current_client)

        while unvisited:
            # Find nearest client to current location that can be added
            best_client = None
            best_distance = float('inf')

            for candidate in unvisited:
                distance = current_client.location.distance_to(candidate.location)
                if distance < best_distance:
                    # Try to add it to current route
                    if current_route.capacity >= current_route.current_load + candidate.demand:
                        best_distance = distance
                        best_client = candidate

            if best_client:
                # Add to current route
                if current_route.add_client(best_client):
                    unvisited.remove(best_client)
                    current_client = best_client
                else:
                    # Can't add to current route, start new one
                    current_route = solution.create_new_route()
                    if current_route.add_client(best_client):
                        unvisited.remove(best_client)
                        current_client = best_client
                    else:
                        # Client can't be added even to empty route, skip
                        unvisited.discard(best_client)
            else:
                # No feasible nearest neighbor, start new route
                current_route = solution.create_new_route()
                # Find any unvisited client that fits
                added = False
                for candidate in list(unvisited):
                    if current_route.add_client(candidate):
                        unvisited.remove(candidate)
                        current_client = candidate
                        added = True
                        break
                if not added:
                    break

        solution.remove_empty_routes()
        return solution

    @staticmethod
    def greedy_insertion(depot: Depot, clients: List[Client], capacity: float,
                        ignore_time_windows: bool = False) -> Solution:
        """
        Greedy insertion heuristic: build routes by inserting clients
        at positions that minimize cost increase.

        Args:
            depot: The depot
            clients: List of all clients
            capacity: Vehicle capacity
            ignore_time_windows: If True, ignore time window constraints

        Returns:
            A Solution constructed with greedy insertion
        """
        solution = Solution(depot, capacity, ignore_time_windows=ignore_time_windows)
        unvisited = set(clients)

        # Start with first client
        if not unvisited:
            return solution

        first_client = min(unvisited, key=lambda c: depot.location.distance_to(c.location))
        unvisited.remove(first_client)

        current_route = solution.create_new_route()
        current_route.add_client(first_client)

        while unvisited:
            best_client = None
            best_route = None
            best_position = None
            best_cost_increase = float('inf')

            # For each unvisited client, find best insertion position
            for client in unvisited:
                # Try adding to existing routes
                for route in solution.routes:
                    for pos in range(len(route.clients) + 1):
                        cost_increase = DistanceCalculator.insertion_distance_delta(
                            route, client, pos
                        )
                        if cost_increase < best_cost_increase:
                            # Check feasibility
                            temp_route = Route(depot, capacity)
                            temp_route.clients = route.clients.copy()
                            if temp_route.insert_client(client, pos):
                                best_cost_increase = cost_increase
                                best_client = client
                                best_route = route
                                best_position = pos

                # Try adding to new route
                new_route = Route(depot, capacity)
                cost_increase = DistanceCalculator.insertion_distance_delta(
                    new_route, client, 0
                )
                if cost_increase < best_cost_increase:
                    if new_route.insert_client(client, 0):
                        best_cost_increase = cost_increase
                        best_client = client
                        best_route = new_route
                        best_position = 0

            if best_client:
                unvisited.remove(best_client)
                if best_route not in solution.routes:
                    solution.add_route(best_route)
                    best_route.add_client(best_client)
                else:
                    best_route.insert_client(best_client, best_position)
            else:
                # Can't insert any client, break
                break

        solution.remove_empty_routes()
        return solution

    @staticmethod
    def savings_algorithm(depot: Depot, clients: List[Client], capacity: float,
                         ignore_time_windows: bool = False) -> Solution:
        """
        Clarke-Wright savings algorithm: merge routes based on savings.

        Args:
            depot: The depot
            clients: List of all clients
            capacity: Vehicle capacity
            ignore_time_windows: If True, ignore time window constraints

        Returns:
            A Solution constructed with savings algorithm
        """
        # Use client-to-route mapping instead of list indices to handle merging correctly
        client_to_route = {}
        for client in clients:
            route = Route(depot, capacity, ignore_time_windows=ignore_time_windows)
            route.add_client(client)
            client_to_route[client] = route

        # Calculate savings for all pairs
        savings_list = []
        for i, client_i in enumerate(clients):
            for j, client_j in enumerate(clients):
                if i < j:
                    # Saving from merging: dist(depot, i) + dist(depot, j) - dist(i, j)
                    dist_depot_i = depot.location.distance_to(client_i.location)
                    dist_depot_j = depot.location.distance_to(client_j.location)
                    dist_i_j = client_i.location.distance_to(client_j.location)
                    saving = dist_depot_i + dist_depot_j - dist_i_j

                    # Store clients instead of indices to handle dynamic route changes
                    savings_list.append((saving, client_i, client_j))

        # Sort by savings (descending)
        savings_list.sort(reverse=True, key=lambda x: x[0])

        # Merge routes based on savings
        for saving, client_i, client_j in savings_list:
            if saving <= 0:
                break  # No more beneficial merges

            # Check if both clients still exist in mapping
            if client_i not in client_to_route or client_j not in client_to_route:
                continue

            route_i = client_to_route[client_i]
            route_j = client_to_route[client_j]

            if route_i == route_j:
                continue

            # Try to merge: concatenate route_j to route_i
            temp_route = Route(depot, capacity)
            temp_route.clients = route_i.clients.copy()

            # Add all clients from route_j
            can_merge = True
            for client in route_j.clients:
                if not temp_route.add_client(client):
                    can_merge = False
                    break

            if can_merge:
                route_i.clients = temp_route.clients
                route_i.current_load = temp_route.current_load
                route_i.current_time = temp_route.current_time

                # Update client-to-route mapping for all clients in route_j
                for client in route_j.clients:
                    client_to_route[client] = route_i

        # Create solution from routes (collect unique routes)
        solution = Solution(depot, capacity, ignore_time_windows=ignore_time_windows)
        seen_routes = set()
        for route in client_to_route.values():
            # Avoid adding the same route object multiple times
            if route not in seen_routes and len(route.clients) > 0:
                solution.add_route(route)
                seen_routes.add(route)

        return solution

    @staticmethod
    def multi_start_nearest_neighbor(depot: Depot, clients: List[Client], capacity: float,
                                    num_restarts: int = 5,
                                    ignore_time_windows: bool = False) -> Solution:
        """
        Generate multiple nearest neighbor solutions and return the best.

        Args:
            depot: The depot
            clients: List of all clients
            capacity: Vehicle capacity
            num_restarts: Number of different NN attempts
            ignore_time_windows: If True, ignore time window constraints

        Returns:
            Best solution found
        """
        best_solution = None
        best_distance = float('inf')

        for _ in range(num_restarts):
            solution = SolutionGenerator.nearest_neighbor(depot, clients, capacity,
                                                         ignore_time_windows=ignore_time_windows)
            distance = DistanceCalculator.solution_distance(solution)

            if distance < best_distance:
                best_distance = distance
                best_solution = solution

        return best_solution
