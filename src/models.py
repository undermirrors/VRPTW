from dataclasses import dataclass
from typing import List, Optional
import math


@dataclass
class Location:
    """Represents a geographic location with coordinates."""
    x: float
    y: float

    def distance_to(self, other: 'Location') -> float:
        """Calculate Euclidean distance to another location."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class TimeWindow:
    """Represents a time window [ready_time, due_time]."""
    ready_time: float
    due_time: float

    def is_time_feasible(self, arrival_time: float) -> bool:
        """Check if arrival time satisfies the time window constraint."""
        return self.ready_time <= arrival_time <= self.due_time

    def get_waiting_time(self, arrival_time: float) -> float:
        """Calculate waiting time if arriving before ready_time."""
        if arrival_time < self.ready_time:
            return self.ready_time - arrival_time
        return 0.0

    def get_time_slack(self, arrival_time: float) -> float:
        """Calculate how much time is available before due_time."""
        if arrival_time > self.due_time:
            return -1  # Infeasible
        return self.due_time - arrival_time


@dataclass
class Client:
    """Represents a client with location, demand, and time window."""
    id: str
    location: Location
    demand: float
    time_window: TimeWindow
    service_time: float

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Client):
            return False
        return self.id == other.id


@dataclass
class Depot:
    """Represents the central depot."""
    id: str
    location: Location
    time_window: TimeWindow

    def __hash__(self):
        return hash(self.id)


class Route:
    """Represents a single vehicle route."""

    def __init__(self, depot: Depot, capacity: float, ignore_time_windows: bool = False):
        self.depot = depot
        self.capacity = capacity
        self.ignore_time_windows = ignore_time_windows
        self.clients: List[Client] = []
        self.current_load = 0.0
        self.current_time = depot.time_window.ready_time

    def add_client(self, client: Client) -> bool:
        """
        Try to add a client to the route.
        Returns True if feasible (capacity and time window satisfied), False otherwise.
        If ignore_time_windows=True, only checks capacity constraint.
        """
        # Check capacity constraint
        if self.current_load + client.demand > self.capacity:
            return False

        # If ignoring time windows, just add the client
        if self.ignore_time_windows:
            self.clients.append(client)
            self.current_load += client.demand
            return True

        # Calculate arrival time at this client
        if len(self.clients) == 0:
            # First client in route
            arrival_time = self.depot.location.distance_to(client.location)
        else:
            last_client = self.clients[-1]
            arrival_time = self.current_time + last_client.service_time + \
                          last_client.location.distance_to(client.location)

        # Check time window feasibility
        if not client.time_window.is_time_feasible(arrival_time):
            return False

        # Check if we can return to depot by closing time
        return_time = arrival_time + client.service_time + \
                     client.location.distance_to(self.depot.location)
        if return_time > self.depot.time_window.due_time:
            return False

        # All constraints satisfied, add client
        self.clients.append(client)
        self.current_load += client.demand
        self.current_time = max(arrival_time, client.time_window.ready_time) + client.service_time
        return True

    def remove_client(self, client: Client) -> bool:
        """Remove a client from the route. Returns True if removed."""
        if client in self.clients:
            self.clients.remove(client)
            self._recalculate()
            return True
        return False

    def insert_client(self, client: Client, position: int) -> bool:
        """
        Try to insert a client at a specific position in the route.
        Returns True if feasible, False otherwise.
        If ignore_time_windows=True, only checks capacity constraint.
        """
        # Check capacity
        if self.current_load + client.demand > self.capacity:
            return False

        # If ignoring time windows, just insert the client
        if self.ignore_time_windows:
            self.clients.insert(position, client)
            self.current_load += client.demand
            self._recalculate()
            return True

        # Create a temporary route to test insertion
        temp_clients = self.clients.copy()
        temp_clients.insert(position, client)

        # Validate the entire route
        current_time = self.depot.time_window.ready_time
        current_load = 0.0

        for c in temp_clients:
            # Check capacity
            if current_load + c.demand > self.capacity:
                return False

            # Calculate arrival time
            if c == temp_clients[0]:
                arrival_time = self.depot.location.distance_to(c.location)
            else:
                prev_client = temp_clients[temp_clients.index(c) - 1]
                arrival_time = current_time + prev_client.service_time + \
                              prev_client.location.distance_to(c.location)

            # Check time window
            if not c.time_window.is_time_feasible(arrival_time):
                return False

            # Update state
            current_time = max(arrival_time, c.time_window.ready_time) + c.service_time
            current_load += c.demand

        # Check return to depot
        if len(temp_clients) > 0:
            last_client = temp_clients[-1]
            return_time = current_time + last_client.location.distance_to(self.depot.location)
            if return_time > self.depot.time_window.due_time:
                return False

        # Insertion is feasible
        self.clients.insert(position, client)
        self.current_load += client.demand
        self._recalculate()
        return True

    def _recalculate(self):
        """Recalculate current load and time after modifications."""
        self.current_load = sum(c.demand for c in self.clients)
        current_time = self.depot.time_window.ready_time

        for client in self.clients:
            if self.clients.index(client) == 0:
                arrival_time = self.depot.location.distance_to(client.location)
            else:
                prev_client = self.clients[self.clients.index(client) - 1]
                arrival_time = current_time + prev_client.service_time + \
                              prev_client.location.distance_to(client.location)

            current_time = max(arrival_time, client.time_window.ready_time) + client.service_time

        self.current_time = current_time

    def get_total_distance(self) -> float:
        """Calculate total distance traveled in this route."""
        if len(self.clients) == 0:
            return 0.0

        distance = self.depot.location.distance_to(self.clients[0].location)

        for i in range(len(self.clients) - 1):
            distance += self.clients[i].location.distance_to(self.clients[i + 1].location)

        distance += self.clients[-1].location.distance_to(self.depot.location)
        return distance

    def is_feasible(self) -> bool:
        """Check if the entire route is feasible.
        If ignore_time_windows=True, only checks capacity constraint."""
        if len(self.clients) == 0:
            return True

        # If ignoring time windows, just check capacity
        if self.ignore_time_windows:
            total_load = sum(c.demand for c in self.clients)
            return total_load <= self.capacity

        current_time = self.depot.time_window.ready_time
        current_load = 0.0

        for i, client in enumerate(self.clients):
            # Check capacity
            if current_load + client.demand > self.capacity:
                return False

            # Calculate arrival time
            if i == 0:
                arrival_time = self.depot.location.distance_to(client.location)
            else:
                prev_client = self.clients[i - 1]
                arrival_time = current_time + prev_client.service_time + \
                              prev_client.location.distance_to(client.location)

            # Check time window
            if not client.time_window.is_time_feasible(arrival_time):
                return False

            current_time = max(arrival_time, client.time_window.ready_time) + client.service_time
            current_load += client.demand

        # Check return to depot
        last_client = self.clients[-1]
        return_time = current_time + last_client.location.distance_to(self.depot.location)
        return return_time <= self.depot.time_window.due_time

    def __repr__(self):
        client_ids = [c.id for c in self.clients]
        return f"Route({client_ids}, distance={self.get_total_distance():.2f})"


class Solution:
    """Represents a complete solution with multiple routes."""

    def __init__(self, depot: Depot, capacity: float, ignore_time_windows: bool = False):
        self.depot = depot
        self.capacity = capacity
        self.ignore_time_windows = ignore_time_windows
        self.routes: List[Route] = []

    def add_route(self, route: Route) -> None:
        """Add a route to the solution."""
        self.routes.append(route)

    def create_new_route(self) -> Route:
        """Create and add a new empty route."""
        route = Route(self.depot, self.capacity, ignore_time_windows=self.ignore_time_windows)
        self.routes.append(route)
        return route

    def get_all_clients(self) -> List[Client]:
        """Get all clients currently in routes."""
        clients = []
        for route in self.routes:
            clients.extend(route.clients)
        return clients

    def get_unassigned_clients(self, all_clients: List[Client]) -> List[Client]:
        """Get clients not assigned to any route."""
        assigned = set(self.get_all_clients())
        return [c for c in all_clients if c not in assigned]

    def get_total_distance(self) -> float:
        """Calculate total distance for all routes."""
        return sum(route.get_total_distance() for route in self.routes)

    def get_num_vehicles(self) -> int:
        """Get number of vehicles used."""
        return len(self.routes)

    def is_complete(self, all_clients: List[Client]) -> bool:
        """Check if all clients are assigned."""
        return len(self.get_unassigned_clients(all_clients)) == 0

    def is_feasible(self) -> bool:
        """Check if all routes are feasible."""
        return all(route.is_feasible() for route in self.routes)

    def remove_empty_routes(self) -> None:
        """Remove routes with no clients."""
        self.routes = [r for r in self.routes if len(r.clients) > 0]

    def copy(self) -> 'Solution':
        """Create a deep copy of the solution."""
        new_solution = Solution(self.depot, self.capacity, ignore_time_windows=self.ignore_time_windows)
        for route in self.routes:
            new_route = Route(self.depot, self.capacity, ignore_time_windows=self.ignore_time_windows)
            new_route.clients = route.clients.copy()
            new_route.current_load = route.current_load
            new_route.current_time = route.current_time
            new_solution.add_route(new_route)
        return new_solution

    def __repr__(self):
        return f"Solution(vehicles={self.get_num_vehicles()}, distance={self.get_total_distance():.2f})"
