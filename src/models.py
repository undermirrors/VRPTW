"""
Data models for VRPTW problem.
"""

from dataclasses import dataclass
from typing import List, Optional
import math


@dataclass(slots=True)
class Location:
    """Represents a geographical location with coordinates."""
    x: float
    y: float

    def distance_to(self, other: "Location") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


@dataclass(slots=True)
class TimeWindow:
    """Represents time window constraints [ready_time, due_time]."""
    ready_time: float
    due_time: float

    def __post_init__(self):
        if self.ready_time > self.due_time:
            raise ValueError(
                f"Ready time {self.ready_time} cannot be after due time {self.due_time}"
            )

    def is_time_valid(self, arrival_time: float) -> bool:
        return self.ready_time <= arrival_time <= self.due_time


class Client:
    """Represents a client with location, demand, and time window."""

    __slots__ = ("id", "location", "demand", "time_window", "service_time")

    def __init__(
        self,
        id: int,
        location: Location,
        demand: float,
        time_window: TimeWindow,
        service_time: float = 0.0,
    ):
        self.id = id
        self.location = location
        self.demand = demand
        self.time_window = time_window
        self.service_time = service_time

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Client) and self.id == other.id

    def __repr__(self) -> str:
        return (
            f"Client(id={self.id}, demand={self.demand}, "
            f"tw=({self.time_window.ready_time}, {self.time_window.due_time}))"
        )


class Depot:
    """Represents the depot with location and vehicle capacity."""

    __slots__ = ("id", "location", "capacity")

    def __init__(self, id: int, location: Location, capacity: float):
        self.id = id
        self.location = location
        self.capacity = capacity

    def __hash__(self):
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Depot(id={self.id}, capacity={self.capacity})"

class Route:
    """
    Represents a vehicle route with optional time-window feasibility checks.
    """

    __slots__ = (
        "_clients",
        "_depot",
        "_capacity",
        "_current_load",
        "_distance_cache",
        "_cost_cache",
    )

    def __init__(self, depot: Depot, capacity: float):
        self._clients: List[Client] = []
        self._depot = depot
        self._capacity = capacity
        self._current_load = 0.0
        self._distance_cache: Optional[float] = None
        self._cost_cache: Optional[float] = None

    @property
    def clients(self) -> List[Client]:
        return self._clients

    @property
    def depot(self) -> Depot:
        return self._depot

    @property
    def capacity(self) -> float:
        return self._capacity

    @property
    def current_load(self) -> float:
        return self._current_load

    @property
    def available_capacity(self) -> float:
        return self._capacity - self._current_load

    def _invalidate_cache(self) -> None:
        self._distance_cache = None
        self._cost_cache = None

    def _would_respect_time_windows(self, candidate_clients: List[Client]) -> bool:
        current_time = 0.0
        current_location = self._depot.location

        for client in candidate_clients:
            travel_time = current_location.distance_to(client.location)
            arrival_time = current_time + travel_time

            if arrival_time > client.time_window.due_time:
                return False

            service_start = max(arrival_time, client.time_window.ready_time)
            current_time = service_start + client.service_time
            current_location = client.location

        return True

    def can_add_client(self, client: Client, use_time_windows: bool = True) -> bool:
        if client.demand > self.available_capacity:
            return False

        if not use_time_windows:
            return True

        return self._would_respect_time_windows(self._clients + [client])

    def add_client(
        self,
        client: Client,
        invalidate_cache: bool = True,
        use_time_windows: bool = True,
    ) -> None:
        if not self.can_add_client(client, use_time_windows=use_time_windows):
            raise ValueError(f"Cannot add client {client.id}: violates route constraints")

        self._clients.append(client)
        self._current_load += client.demand

        if invalidate_cache:
            self._invalidate_cache()

    def add_clients_batch(
        self,
        clients: List[Client],
        use_time_windows: bool = True,
    ) -> None:
        for client in clients:
            if not self.can_add_client(client, use_time_windows=use_time_windows):
                raise ValueError(f"Cannot add client {client.id}: violates route constraints")
            self._clients.append(client)
            self._current_load += client.demand

        self._invalidate_cache()

    def remove_client(self, client: Client) -> None:
        self._clients.remove(client)
        self._current_load -= client.demand
        self._invalidate_cache()

    def is_empty(self) -> bool:
        return len(self._clients) == 0

    def __len__(self) -> int:
        return len(self._clients)

    def __repr__(self) -> str:
        return f"Route(clients={len(self._clients)}, load={self._current_load:.1f}/{self._capacity})"

class Solution:
    """
    Represents a complete VRPTW/VRP solution.
    """

    __slots__ = ("_routes", "_depot", "_clients", "_distance_cache", "_vehicles_cache")

    def __init__(self, depot: Depot, clients: List[Client], num_vehicles: Optional[int] = None):
        self._depot = depot
        self._clients = clients
        self._routes = [Route(depot, depot.capacity) for _ in range(num_vehicles or len(clients))]
        self._distance_cache: Optional[float] = None
        self._vehicles_cache: Optional[int] = None

    @property
    def depot(self) -> Depot:
        return self._depot

    @property
    def clients(self) -> List[Client]:
        return self._clients

    @property
    def routes(self) -> List[Route]:
        return self._routes

    def get_route(self, index: int) -> Route:
        if index < 0 or index >= len(self._routes):
            raise IndexError(f"Route index {index} out of range")
        return self._routes[index]

    def get_num_vehicles(self) -> int:
        if self._vehicles_cache is None:
            self._vehicles_cache = sum(1 for route in self._routes if not route.is_empty())
        return self._vehicles_cache

    def invalidate_cache(self) -> None:
        self._distance_cache = None
        self._vehicles_cache = None

    def get_total_distance(self) -> float:
        if self._distance_cache is None:
            self._distance_cache = sum(
                self._calculate_route_distance(route) for route in self._routes
            )
        return self._distance_cache

    @staticmethod
    def _calculate_route_distance(route: Route) -> float:
        if route.is_empty():
            return 0.0

        total = 0.0
        current = route.depot.location
        for client in route.clients:
            total += current.distance_to(client.location)
            current = client.location
        total += current.distance_to(route.depot.location)
        return total

    def copy(self) -> "Solution":
        new_solution = Solution(self._depot, self._clients, len(self._routes))
        for old_route, new_route in zip(self._routes, new_solution._routes):
            if not old_route.is_empty():
                new_route.add_clients_batch(old_route.clients[:], use_time_windows=False)
        new_solution.invalidate_cache()
        return new_solution

    def is_feasible(self, use_time_windows: bool = True) -> bool:
        assigned_ids = []

        for route in self._routes:
            if route.current_load > route.capacity:
                return False

            current_time = 0.0
            current_location = route.depot.location

            for client in route.clients:
                assigned_ids.append(client.id)

                if use_time_windows:
                    travel_time = current_location.distance_to(client.location)
                    arrival_time = current_time + travel_time

                    if arrival_time > client.time_window.due_time:
                        return False

                    service_start = max(arrival_time, client.time_window.ready_time)
                    current_time = service_start + client.service_time
                    current_location = client.location

        return (
            len(set(assigned_ids)) == len(self._clients)
            and len(assigned_ids) == len(self._clients)
        )

    def __len__(self) -> int:
        return len(self._routes)

    def __repr__(self) -> str:
        return (
            f"Solution(vehicles={self.get_num_vehicles()}, "
            f"distance={self.get_total_distance():.1f}, "
            f"feasible={self.is_feasible()})"
        )

class VRPTProblem:
    """Represents a complete VRPTW problem instance."""

    __slots__ = ("name", "depot", "clients", "capacity", "num_clients")

    def __init__(self, name: str, depot: Depot, clients: List[Client]):
        self.name = name
        self.depot = depot
        self.clients = clients
        self.capacity = depot.capacity
        self.num_clients = len(clients)

    def __repr__(self) -> str:
        return f"VRPTProblem({self.name}, {self.num_clients} clients, capacity={self.capacity})"