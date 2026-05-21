"""
Custom VRPTW .vrp loader for the project dataset format.

Expected format example:
NAME: data111.vrp
COMMENT:
TYPE: vrptw
COORDINATES: cartesian
NB_DEPOTS: 1
NB_CLIENTS: 100
MAX_QUANTITY: 200

DATA_DEPOTS [idName x y readyTime dueTime]:
d1 35 35 0 230

DATA_CLIENTS [idName x y readyTime dueTime demand service]:
c1 41 49 15 204 10 10
...
"""

from pathlib import Path
from typing import List

from .models import Location, TimeWindow, Client, Depot, VRPTProblem


class DataLoader:
    @staticmethod
    def _parse_numeric_id(raw_id: str) -> int:
        digits = "".join(ch for ch in raw_id if ch.isdigit())
        if digits:
            return int(digits)
        raise ValueError(f"Unable to parse numeric id from {raw_id!r}")

    @staticmethod
    def load_problem(file_path: str | Path) -> VRPTProblem:
        file_path = Path(file_path)
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()

        name = file_path.stem
        capacity = None
        depot = None
        clients: List[Client] = []

        in_depots = False
        in_clients = False

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            upper = line.upper()

            if upper.startswith("NAME:"):
                name_value = line.split(":", 1)[1].strip()
                if name_value:
                    name = Path(name_value).stem
                continue

            if upper.startswith("MAX_QUANTITY:"):
                capacity = float(line.split(":", 1)[1].strip())
                continue

            if upper.startswith("DATA_DEPOTS"):
                in_depots = True
                in_clients = False
                continue

            if upper.startswith("DATA_CLIENTS"):
                in_clients = True
                in_depots = False
                continue

            parts = line.split()

            if in_depots:
                # d1 35 35 0 230
                if len(parts) >= 5:
                    depot_id = DataLoader._parse_numeric_id(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    ready_time = float(parts[3])
                    due_time = float(parts[4])

                    if capacity is None:
                        raise ValueError(f"MAX_QUANTITY missing before depot section in {file_path}")

                    depot = Depot(
                        id=depot_id,
                        location=Location(x, y),
                        capacity=capacity,
                    )
                continue

            if in_clients:
                # c1 41 49 15 204 10 10
                if len(parts) >= 7:
                    client_id = DataLoader._parse_numeric_id(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    ready_time = float(parts[3])
                    due_time = float(parts[4])
                    demand = float(parts[5])
                    service_time = float(parts[6])

                    clients.append(
                        Client(
                            id=client_id,
                            location=Location(x, y),
                            demand=demand,
                            time_window=TimeWindow(ready_time, due_time),
                            service_time=service_time,
                        )
                    )

        if capacity is None:
            raise ValueError(f"Unable to detect MAX_QUANTITY in {file_path}")

        if depot is None:
            raise ValueError(f"Unable to parse depot in {file_path}")

        if not clients:
            raise ValueError(f"No clients parsed in {file_path}")

        return VRPTProblem(name, depot, clients)

    @staticmethod
    def load_all_problems(data_dir: str | Path) -> List[VRPTProblem]:
        data_dir = Path(data_dir)
        return [DataLoader.load_problem(path) for path in sorted(data_dir.glob("*.vrp"))]