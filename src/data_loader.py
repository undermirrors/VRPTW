from typing import List
from models import Client, Depot, Location, TimeWindow
import os


class VRPTProblem:
    """Represents a complete VRPTW problem instance."""

    def __init__(self, name: str, depot: Depot, clients: List[Client], capacity: float):
        self.name = name
        self.depot = depot
        self.clients = clients
        self.capacity = capacity
        self.num_clients = len(clients)
        self.num_depots = 1

    def __repr__(self):
        return f"VRPTProblem({self.name}, clients={self.num_clients}, capacity={self.capacity})"


class DataLoader:
    """Loads and parses VRPTW problem files in .vrp format."""

    @staticmethod
    def load_problem(filepath: str) -> VRPTProblem:
        """
        Load a VRPTW problem from a .vrp file.

        Args:
            filepath: Path to the .vrp file

        Returns:
            VRPTProblem instance with all data loaded
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Problem file not found: {filepath}")

        with open(filepath, 'r') as f:
            lines = f.readlines()

        # Parse metadata
        name = None
        num_clients = None
        max_quantity = None

        depot = None
        clients = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith('COMMENT'):
                i += 1
                continue

            # Parse NAME
            if line.startswith('NAME:'):
                name = line.split(':', 1)[1].strip()

            # Parse NB_CLIENTS
            elif line.startswith('NB_CLIENTS:'):
                num_clients = int(line.split(':', 1)[1].strip())

            # Parse MAX_QUANTITY (vehicle capacity)
            elif line.startswith('MAX_QUANTITY:'):
                max_quantity = int(line.split(':', 1)[1].strip())

            # Parse DEPOT section
            elif line.startswith('DATA_DEPOTS'):
                i += 1
                # Read depot line (next non-empty line)
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    depot_line = lines[i].strip()
                    if depot_line and not depot_line.startswith('DATA_'):
                        depot = DataLoader._parse_depot_line(depot_line)

            # Parse CLIENTS section
            elif line.startswith('DATA_CLIENTS'):
                i += 1
                # Read all client lines until end of file or next section
                while i < len(lines):
                    client_line = lines[i].strip()
                    if not client_line:
                        i += 1
                        continue
                    if client_line.startswith('DATA_'):
                        break
                    if not client_line.startswith('['):  # Skip header
                        client = DataLoader._parse_client_line(client_line)
                        if client:
                            clients.append(client)
                    i += 1
                i -= 1  # Adjust for outer loop increment

            i += 1

        if depot is None or len(clients) == 0:
            raise ValueError(f"Invalid problem file: missing depot or clients")

        return VRPTProblem(
            name=name or os.path.basename(filepath),
            depot=depot,
            clients=clients,
            capacity=max_quantity or 200
        )

    @staticmethod
    def _parse_depot_line(line: str) -> Depot:
        """
        Parse a depot line: d1 35 35 0 230
        Format: id x y ready_time due_time
        """
        parts = line.split()
        if len(parts) < 5:
            raise ValueError(f"Invalid depot format: {line}")

        depot_id = parts[0]
        x = float(parts[1])
        y = float(parts[2])
        ready_time = float(parts[3])
        due_time = float(parts[4])

        location = Location(x=x, y=y)
        time_window = TimeWindow(ready_time=ready_time, due_time=due_time)

        return Depot(id=depot_id, location=location, time_window=time_window)

    @staticmethod
    def _parse_client_line(line: str) -> Client:
        """
        Parse a client line: c1 41 49 161 171 10 10
        Format: id x y ready_time due_time demand service_time
        """
        parts = line.split()
        if len(parts) < 7:
            return None

        client_id = parts[0]
        x = float(parts[1])
        y = float(parts[2])
        ready_time = float(parts[3])
        due_time = float(parts[4])
        demand = float(parts[5])
        service_time = float(parts[6])

        location = Location(x=x, y=y)
        time_window = TimeWindow(ready_time=ready_time, due_time=due_time)

        return Client(
            id=client_id,
            location=location,
            demand=demand,
            time_window=time_window,
            service_time=service_time
        )

    @staticmethod
    def load_all_problems(directory: str) -> List[VRPTProblem]:
        """
        Load all .vrp files from a directory.

        Args:
            directory: Path to directory containing .vrp files

        Returns:
            List of VRPTProblem instances sorted by filename
        """
        problems = []

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Directory not found: {directory}")

        vrp_files = [f for f in os.listdir(directory) if f.endswith('.vrp')]
        vrp_files.sort()

        for vrp_file in vrp_files:
            filepath = os.path.join(directory, vrp_file)
            try:
                problem = DataLoader.load_problem(filepath)
                problems.append(problem)
                print(f"Loaded: {problem.name} ({problem.num_clients} clients)")
            except Exception as e:
                print(f"Error loading {vrp_file}: {e}")

        return problems
