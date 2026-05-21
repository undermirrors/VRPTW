"""
Neighborhood operators for local search.

Optimizations:
- Efficient move operations with delta calculations
- Early termination checks
- Minimal solution copying
"""

import random
from typing import List, Optional, Tuple
from models import Solution, Route, Client
from distance_utils import DistanceCalculator


class NeighborhoodOperator:
    """Base class for neighborhood operators."""

    @staticmethod
    def apply_move(solution: Solution, move: Tuple) -> Solution:
        """Apply a move to create a new solution."""
        raise NotImplementedError


class TwoOptOperator(NeighborhoodOperator):
    """2-opt neighborhood operator: reverse segment of route."""

    @staticmethod
    def generate_moves(solution: Solution, sample_size: Optional[int] = None) -> List[Tuple]:
        """
        Generate 2-opt moves.

        Args:
            solution: Current solution
            sample_size: If specified, return random sample of moves

        Returns:
            List of (route_idx, i, j) tuples for 2-opt swaps
        """
        moves = []
        for route_idx, route in enumerate(solution.routes):
            if len(route.clients) < 2:
                continue

            for i in range(len(route.clients) - 1):
                for j in range(i + 2, len(route.clients)):
                    moves.append((route_idx, i, j))

        if sample_size and len(moves) > sample_size:
            moves = random.sample(moves, sample_size)

        return moves

    @staticmethod
    def apply_move(solution: Solution, move: Tuple) -> Solution:
        """Apply 2-opt move: reverse segment between positions i and j."""
        route_idx, i, j = move
        new_solution = solution.copy()
        route = new_solution.get_route(route_idx)

        # Reverse segment
        segment = route.clients[i:j+1]
        segment.reverse()
        route._clients[i:j+1] = segment
        route._invalidate_cache()

        new_solution.invalidate_cache()
        return new_solution

    @staticmethod
    def get_move_delta(solution: Solution, move: Tuple) -> float:
        """Calculate distance change for 2-opt move."""
        route_idx, i, j = move
        route = solution.get_route(route_idx)

        if i >= len(route.clients) - 1 or j >= len(route.clients):
            return float('inf')

        clients = route.clients

        # Current edges: (i-1,i), (i,i+1),...,(j-1,j), (j,j+1)
        # After: (i-1,j), (j,j-1),...,(i+1,i), (i,j+1)

        if i == 0:
            # First segment
            old_dist = DistanceCalculator.get_distance(route.depot.location, clients[0].location)
            new_dist = DistanceCalculator.get_distance(route.depot.location, clients[j].location)
        else:
            old_dist = DistanceCalculator.get_distance(clients[i-1].location, clients[i].location)
            new_dist = DistanceCalculator.get_distance(clients[i-1].location, clients[j].location)

        if j == len(clients) - 1:
            # Last segment
            old_dist += DistanceCalculator.get_distance(clients[j].location, route.depot.location)
            new_dist += DistanceCalculator.get_distance(clients[i].location, route.depot.location)
        else:
            old_dist += DistanceCalculator.get_distance(clients[j].location, clients[j+1].location)
            new_dist += DistanceCalculator.get_distance(clients[i].location, clients[j+1].location)

        # Account for reversed segment
        for k in range(i, j):
            old_dist += DistanceCalculator.get_distance(clients[k].location, clients[k+1].location)
            new_dist += DistanceCalculator.get_distance(clients[j-k+i].location, clients[j-k+i-1].location)

        return new_dist - old_dist


class OrOptOperator(NeighborhoodOperator):
    """Or-opt operator: move sequence of clients to new position."""

    @staticmethod
    def generate_moves(solution: Solution, seq_length: int = 1, sample_size: Optional[int] = None) -> List[Tuple]:
        """
        Generate Or-opt moves.

        Args:
            solution: Current solution
            seq_length: Length of sequence to move (1, 2, or 3)
            sample_size: If specified, return random sample of moves

        Returns:
            List of moves (route_idx, start, length, target_route, target_pos)
        """
        moves = []

        for route_idx, route in enumerate(solution.routes):
            if len(route.clients) < seq_length:
                continue

            for start in range(len(route.clients) - seq_length + 1):
                # Try inserting in same route
                for target_pos in range(len(route.clients) - seq_length + 1):
                    if target_pos < start or target_pos > start + seq_length:
                        moves.append((route_idx, start, seq_length, route_idx, target_pos))

                # Try inserting in other routes
                for other_route_idx, other_route in enumerate(solution.routes):
                    if other_route_idx == route_idx:
                        continue

                    for target_pos in range(len(other_route.clients) + 1):
                        moves.append((route_idx, start, seq_length, other_route_idx, target_pos))

        if sample_size and len(moves) > sample_size:
            moves = random.sample(moves, sample_size)

        return moves

    @staticmethod
    def apply_move(solution: Solution, move: Tuple) -> Solution:
        """Apply Or-opt move: relocate sequence of clients."""
        src_route_idx, start, length, dst_route_idx, target_pos = move
        new_solution = solution.copy()

        src_route = new_solution.get_route(src_route_idx)
        dst_route = new_solution.get_route(dst_route_idx)

        # Extract sequence
        sequence = src_route.clients[start:start+length]

        # Check capacity
        if dst_route.current_load + sum(c.demand for c in sequence) > dst_route.capacity:
            return solution  # Infeasible move

        # Remove sequence from source
        for client in sequence:
            src_route.remove_client(client)

        # Add sequence to destination
        for i, client in enumerate(sequence):
            dst_route._clients.insert(target_pos + i, client)
            dst_route._current_load += client.demand

        dst_route._invalidate_cache()
        new_solution.invalidate_cache()

        return new_solution


class RelocateOperator(NeighborhoodOperator):
    """Relocate operator: move single client to different route or position."""

    @staticmethod
    def generate_moves(solution: Solution, sample_size: Optional[int] = None) -> List[Tuple]:
        """
        Generate relocation moves.

        Args:
            solution: Current solution
            sample_size: If specified, return random sample of moves

        Returns:
            List of (src_route, src_pos, dst_route, dst_pos) tuples
        """
        moves = []

        for src_idx, src_route in enumerate(solution.routes):
            for src_pos in range(len(src_route.clients)):
                client = src_route.clients[src_pos]

                # Try all destination positions
                for dst_idx, dst_route in enumerate(solution.routes):
                    if not dst_route.can_add_client(client):
                        continue

                    for dst_pos in range(len(dst_route.clients) + 1):
                        if src_idx == dst_idx and (dst_pos == src_pos or dst_pos == src_pos + 1):
                            continue  # Skip trivial moves

                        moves.append((src_idx, src_pos, dst_idx, dst_pos))

        if sample_size and len(moves) > sample_size:
            moves = random.sample(moves, sample_size)

        return moves

    @staticmethod
    def apply_move(solution: Solution, move: Tuple) -> Solution:
        """Apply relocation move."""
        src_idx, src_pos, dst_idx, dst_pos = move
        new_solution = solution.copy()

        src_route = new_solution.get_route(src_idx)
        dst_route = new_solution.get_route(dst_idx)

        client = src_route.clients[src_pos]

        # Check capacity
        if src_idx != dst_idx and not dst_route.can_add_client(client):
            return solution  # Infeasible

        # Remove from source
        src_route.remove_client(client)

        # Add to destination
        if src_idx == dst_idx:
            # Adjust position if removing and inserting in same route
            if dst_pos > src_pos:
                dst_pos -= 1

        dst_route._clients.insert(dst_pos, client)
        dst_route._current_load += client.demand
        dst_route._invalidate_cache()

        new_solution.invalidate_cache()
        return new_solution


class CrossExchangeOperator(NeighborhoodOperator):
    """Cross-exchange operator: swap clients between routes."""

    @staticmethod
    def generate_moves(solution: Solution, sample_size: Optional[int] = None) -> List[Tuple]:
        """
        Generate cross-exchange moves.

        Args:
            solution: Current solution
            sample_size: If specified, return random sample of moves

        Returns:
            List of (route1_idx, pos1, route2_idx, pos2) tuples
        """
        moves = []

        for r1_idx in range(len(solution.routes)):
            for r2_idx in range(r1_idx + 1, len(solution.routes)):
                r1 = solution.get_route(r1_idx)
                r2 = solution.get_route(r2_idx)

                for p1 in range(len(r1.clients)):
                    for p2 in range(len(r2.clients)):
                        c1 = r1.clients[p1]
                        c2 = r2.clients[p2]

                        # Check if exchange is feasible
                        if (r1.current_load - c1.demand + c2.demand <= r1.capacity and
                            r2.current_load - c2.demand + c1.demand <= r2.capacity):
                            moves.append((r1_idx, p1, r2_idx, p2))

        if sample_size and len(moves) > sample_size:
            moves = random.sample(moves, sample_size)

        return moves

    @staticmethod
    def apply_move(solution: Solution, move: Tuple) -> Solution:
        """Apply cross-exchange move."""
        r1_idx, p1, r2_idx, p2 = move
        new_solution = solution.copy()

        r1 = new_solution.get_route(r1_idx)
        r2 = new_solution.get_route(r2_idx)

        c1 = r1.clients[p1]
        c2 = r2.clients[p2]

        # Swap
        r1._clients[p1] = c2
        r2._clients[p2] = c1

        # Update loads
        r1._current_load = r1._current_load - c1.demand + c2.demand
        r2._current_load = r2._current_load - c2.demand + c1.demand

        r1._invalidate_cache()
        r2._invalidate_cache()
        new_solution.invalidate_cache()

        return new_solution
