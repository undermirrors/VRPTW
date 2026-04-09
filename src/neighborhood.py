import random
from typing import List, Tuple, Optional
from models import Client, Route, Solution, Depot
from distance_utils import DistanceCalculator


class NeighborhoodOperator:
    """Base class for neighborhood operators."""

    @staticmethod
    def apply(solution: Solution) -> Solution:
        """Apply the operator and return a new solution."""
        raise NotImplementedError


class TwoOpt(NeighborhoodOperator):
    """
    2-opt operator: Remove two edges and reconnect.
    Classic local search move for TSP-like problems.

    Within a single route, removes edges (i, i+1) and (j, j+1),
    then reconnects by reversing the segment between them.
    """

    @staticmethod
    def apply(solution: Solution) -> Solution:
        """Apply 2-opt move to a random route."""
        if len(solution.routes) == 0:
            return solution

        solution_copy = solution.copy()
        route = random.choice(solution_copy.routes)

        # Need at least 4 clients for valid 2-opt move
        # (so i + 2 <= len(route.clients) - 1)
        if len(route.clients) < 4:
            return solution_copy

        # Random positions
        i = random.randint(0, len(route.clients) - 3)
        j = random.randint(i + 2, len(route.clients) - 1)

        # Reverse segment between i and j
        route.clients[i + 1:j + 1] = reversed(route.clients[i + 1:j + 1])
        route._recalculate()

        return solution_copy

    @staticmethod
    def apply_best(solution: Solution) -> Tuple[Solution, float]:
        """Apply best 2-opt move and return improvement."""
        best_solution = solution.copy()
        best_improvement = 0.0

        for route in best_solution.routes:
            if len(route.clients) < 3:
                continue

            for i in range(len(route.clients) - 2):
                for j in range(i + 2, len(route.clients)):
                    # Calculate delta
                    current_dist = route.get_total_distance()

                    # Reverse segment
                    route.clients[i + 1:j + 1] = reversed(route.clients[i + 1:j + 1])
                    new_dist = route.get_total_distance()
                    delta = new_dist - current_dist

                    if delta < best_improvement:
                        best_improvement = delta
                        # Keep this move
                        route._recalculate()
                    else:
                        # Revert
                        route.clients[i + 1:j + 1] = reversed(route.clients[i + 1:j + 1])

        route._recalculate() if best_solution.routes else None
        return best_solution, best_improvement


class OrOpt(NeighborhoodOperator):
    """
    Or-opt operator: Remove a sequence of k consecutive clients and insert elsewhere.
    Generalization of 1-opt (relocate) and 2-opt.

    Can operate within same route or move to different routes.
    """

    def __init__(self, sequence_length: int = 1):
        """
        Args:
            sequence_length: Length of sequence to move (1, 2, or 3)
        """
        self.sequence_length = max(1, min(3, sequence_length))

    def apply(self, solution: Solution) -> Solution:
        """Apply Or-opt move with random sequence length."""
        if len(solution.routes) == 0:
            return solution

        solution_copy = solution.copy()

        # Choose random route and sequence
        route = random.choice(solution_copy.routes)
        if len(route.clients) < self.sequence_length:
            return solution_copy

        start_pos = random.randint(0, len(route.clients) - self.sequence_length)
        sequence = route.clients[start_pos:start_pos + self.sequence_length]

        # Remove sequence from route
        for client in sequence:
            route.remove_client(client)

        # Try to insert in random position
        if random.random() < 0.5 and len(solution_copy.routes) > 1:
            # Insert in different route
            target_route = random.choice([r for r in solution_copy.routes if r != route])
            for i, client in enumerate(sequence):
                pos = random.randint(0, len(target_route.clients))
                target_route.insert_client(client, pos)
        else:
            # Insert back in same route
            for i, client in enumerate(sequence):
                pos = random.randint(0, len(route.clients))
                route.insert_client(client, pos)

        solution_copy.remove_empty_routes()
        return solution_copy


class Relocate(NeighborhoodOperator):
    """
    Relocate (1-opt) operator: Move a single client to another position.
    Simplest local search move - move one client to a different location.

    Can move within same route or to different route.
    """

    @staticmethod
    def apply(solution: Solution) -> Solution:
        """Apply relocate move."""
        if len(solution.routes) == 0:
            return solution

        solution_copy = solution.copy()
        route = random.choice(solution_copy.routes)

        if len(route.clients) == 0:
            return solution_copy

        # Choose random client to relocate
        client = random.choice(route.clients)
        route.remove_client(client)

        # Try inserting in random position
        if random.random() < 0.3 and len(solution_copy.routes) > 1:
            # Move to different route
            target_route = random.choice([r for r in solution_copy.routes if r != route])
            pos = random.randint(0, len(target_route.clients))
            if not target_route.insert_client(client, pos):
                # If insertion fails, put back in original route
                route.insert_client(client, random.randint(0, len(route.clients)))
        else:
            # Move within same route
            pos = random.randint(0, len(route.clients))
            if not route.insert_client(client, pos):
                # Should not happen if client was in route initially
                route.clients.insert(pos, client)
                route._recalculate()

        solution_copy.remove_empty_routes()
        return solution_copy

    @staticmethod
    def apply_best(solution: Solution) -> Tuple[Solution, float]:
        """Apply best relocate move and return improvement."""
        best_solution = solution.copy()
        best_improvement = 0.0
        best_move = None

        for route_idx, route in enumerate(best_solution.routes):
            for client_idx, client in enumerate(route.clients):
                current_dist = DistanceCalculator.route_distance(route)

                # Try removing and reinserting at all positions in same route
                for new_pos in range(len(route.clients)):
                    if new_pos == client_idx or new_pos == client_idx + 1:
                        continue

                    # Calculate delta
                    delta = DistanceCalculator.relocation_distance_delta(
                        route, client, client_idx, new_pos
                    )

                    if delta < best_improvement:
                        best_improvement = delta
                        best_move = (route_idx, client_idx, new_pos, 'same')

                # Try moving to different routes
                for target_route_idx, target_route in enumerate(best_solution.routes):
                    if target_route_idx == route_idx:
                        continue

                    for target_pos in range(len(target_route.clients) + 1):
                        # Check if move is feasible
                        if route.capacity >= route.current_load - client.demand and \
                           target_route.capacity >= target_route.current_load + client.demand:
                            # Rough estimate of delta (simplified)
                            best_move = (route_idx, client_idx, target_pos, 'different')
                            best_improvement = -client.demand  # Placeholder

        # Apply best move if found
        if best_move and best_improvement < 0:
            route_idx, client_idx, new_pos, move_type = best_move
            client = best_solution.routes[route_idx].clients[client_idx]
            best_solution.routes[route_idx].remove_client(client)

            if move_type == 'same':
                best_solution.routes[route_idx].insert_client(client, new_pos)
            else:
                best_solution.routes[new_pos].insert_client(client, new_pos)

        return best_solution, best_improvement


class CrossExchange(NeighborhoodOperator):
    """
    Cross-exchange operator: Swap clients between two routes.
    Exchanges a client from route A with a client from route B.
    """

    @staticmethod
    def apply(solution: Solution) -> Solution:
        """Apply cross-exchange move."""
        if len(solution.routes) < 2:
            return solution

        solution_copy = solution.copy()

        # Choose two different routes
        route1, route2 = random.sample(solution_copy.routes, 2)

        if len(route1.clients) == 0 or len(route2.clients) == 0:
            return solution_copy

        # Choose clients to exchange
        client1 = random.choice(route1.clients)
        client2 = random.choice(route2.clients)

        # Try swap
        pos1 = route1.clients.index(client1)
        pos2 = route2.clients.index(client2)

        route1.clients[pos1] = client2
        route2.clients[pos2] = client1

        # Update loads
        route1.current_load = route1.current_load - client1.demand + client2.demand
        route2.current_load = route2.current_load - client2.demand + client1.demand

        # Recalculate times
        route1._recalculate()
        route2._recalculate()

        # Check feasibility, revert if needed
        if not (route1.is_feasible() and route2.is_feasible()):
            route1.clients[pos1] = client1
            route2.clients[pos2] = client2
            route1._recalculate()
            route2._recalculate()

        return solution_copy


class TwoOptBetweenRoutes(NeighborhoodOperator):
    """
    2-opt between routes: Remove edges between routes and reconnect differently.
    Can transform the solution structure by moving clients between routes.
    """

    @staticmethod
    def apply(solution: Solution) -> Solution:
        """Apply 2-opt between routes."""
        if len(solution.routes) < 2:
            return solution

        solution_copy = solution.copy()
        route1, route2 = random.sample(solution_copy.routes, 2)

        if len(route1.clients) == 0 or len(route2.clients) == 0:
            return solution_copy

        # Choose split points
        split1 = random.randint(0, len(route1.clients) - 1)
        split2 = random.randint(0, len(route2.clients) - 1)

        # Exchange segments
        segment1 = route1.clients[split1:]
        segment2 = route2.clients[split2:]

        route1.clients = route1.clients[:split1] + segment2
        route2.clients = route2.clients[:split2] + segment1

        # Recalculate and check feasibility
        route1._recalculate()
        route2._recalculate()

        if not (route1.is_feasible() and route2.is_feasible()):
            # Revert
            route1.clients = route1.clients[:split1] + segment1
            route2.clients = route2.clients[:split2] + segment2
            route1._recalculate()
            route2._recalculate()

        solution_copy.remove_empty_routes()
        return solution_copy


class NeighborhoodManager:
    """Manages multiple neighborhood operators."""

    def __init__(self):
        """Initialize all available neighborhood operators."""
        self.operators = [
            ('2-opt', TwoOpt()),
            ('Or-opt-1', OrOpt(sequence_length=1)),
            ('Or-opt-2', OrOpt(sequence_length=2)),
            ('Or-opt-3', OrOpt(sequence_length=3)),
            ('Relocate', Relocate()),
            ('Cross-Exchange', CrossExchange()),
            ('2-opt-Routes', TwoOptBetweenRoutes()),
        ]

    def apply_random_operator(self, solution: Solution) -> Tuple[Solution, str]:
        """Apply a randomly selected neighborhood operator."""
        operator_name, operator = random.choice(self.operators)
        new_solution = operator.apply(solution)
        return new_solution, operator_name

    def apply_operator(self, solution: Solution, operator_name: str) -> Solution:
        """Apply a specific neighborhood operator by name."""
        for name, operator in self.operators:
            if name == operator_name:
                return operator.apply(solution)
        raise ValueError(f"Unknown operator: {operator_name}")

    def get_all_operators(self) -> List[str]:
        """Get list of all available operator names."""
        return [name for name, _ in self.operators]

    def get_num_operators(self) -> int:
        """Get number of available operators."""
        return len(self.operators)
