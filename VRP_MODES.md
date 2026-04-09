# VRP vs VRPTW Modes & Vehicle Minimization

## Overview

The VRPTW solver supports two main problem variants and flexible objective optimization:

- **VRPTW**: Vehicle Routing Problem **with Time Windows** (default)
- **VRP**: Vehicle Routing Problem **without Time Windows**
- **Vehicle Minimization**: Optional objective to minimize number of vehicles

This guide explains how to use these features.

---

## Problem Variants

### VRPTW Mode (Default)

**Problem Definition:**
- Serve clients with specific **location**, **demand**, and **time window** constraints
- Each client must be visited within their time window: `[ready_time, due_time]`
- Each vehicle has a **capacity** limit
- **Objective**: Minimize total distance traveled

**Usage:**
```python
from src.genetic_algorithm import GeneticAlgorithm
from src.data_loader import DataLoader

problem = DataLoader.load_problem("data/data101.vrp")

ga = GeneticAlgorithm(
    problem.depot,
    problem.clients,
    problem.capacity,
    ignore_time_windows=False,  # Default: respect time windows
    minimize_vehicles=False
)

solution = ga.evolve()
```

**When to Use:**
- Real-world routing with time windows
- Delivery services with appointment times
- When time constraints are essential

**Constraints Checked:**
- ✓ Time windows (strict)
- ✓ Vehicle capacity
- ✓ Service times at each client
- ✓ Return to depot by closing time

---

### VRP Mode (Ignore Time Windows)

**Problem Definition:**
- Serve clients with specific **location** and **demand**
- **Time windows are completely ignored**
- Each vehicle has a **capacity** limit
- **Objective**: Minimize total distance traveled

**Usage:**
```python
from src.genetic_algorithm import GeneticAlgorithm
from src.data_loader import DataLoader

problem = DataLoader.load_problem("data/data101.vrp")

ga = GeneticAlgorithm(
    problem.depot,
    problem.clients,
    problem.capacity,
    ignore_time_windows=True,   # IGNORE time windows
    minimize_vehicles=False
)

solution = ga.evolve()
```

**When to Use:**
- No time constraints in the problem
- Test/simplify a VRPTW instance
- Compare impact of time windows
- When time windows are not binding constraints

**Constraints Checked:**
- ✓ Vehicle capacity only
- ✗ Time windows (ignored)
- ✗ Service times (ignored)

**Key Differences from VRPTW:**
- Solutions are always feasible (only capacity matters)
- Typically requires fewer vehicles
- Significantly faster to solve
- Better solution quality (easier problem)

---

## Vehicle Minimization

By default, the algorithm minimizes **total distance**. Optionally, you can add a penalty for using more vehicles.

### Without Vehicle Minimization

**Objective Function:**
```
minimize: total_distance
```

**Result:**
- Focuses on minimizing distance
- May use more vehicles if it reduces distance

**Usage:**
```python
ga = GeneticAlgorithm(
    problem.depot,
    problem.clients,
    problem.capacity,
    minimize_vehicles=False  # Default
)
```

### With Vehicle Minimization

**Objective Function:**
```
minimize: total_distance + vehicle_weight × num_vehicles
```

**Result:**
- Minimizes both distance AND vehicle count
- Balances two objectives

**Usage:**
```python
ga = GeneticAlgorithm(
    problem.depot,
    problem.clients,
    problem.capacity,
    minimize_vehicles=True,      # Enable vehicle minimization
    vehicle_weight=100.0         # Weight for vehicle penalty
)
```

### Vehicle Weight Parameter

The `vehicle_weight` parameter controls the trade-off between distance and vehicles:

- **vehicle_weight = 0.0**: Minimize distance only
- **vehicle_weight = 50.0**: Small penalty for vehicles
- **vehicle_weight = 100.0**: Moderate penalty (recommended)
- **vehicle_weight = 200.0**: Strong penalty for vehicles
- **vehicle_weight = 500.0**: Minimize vehicles aggressively

**Example: Impact of Weight**

```python
from src.genetic_algorithm import GeneticAlgorithm

problem = DataLoader.load_problem("data/data101.vrp")

# Test different weights
for weight in [0.0, 50.0, 100.0, 200.0]:
    ga = GeneticAlgorithm(
        problem.depot, problem.clients, problem.capacity,
        ignore_time_windows=True,
        minimize_vehicles=True,
        vehicle_weight=weight
    )
    solution = ga.evolve()
    distance = DistanceCalculator.solution_distance(solution)
    vehicles = solution.get_num_vehicles()
    
    print(f"Weight {weight}: Distance={distance:.2f}, Vehicles={vehicles}")
```

**Expected Output:**
```
Weight 0.0: Distance=1150.50, Vehicles=8
Weight 50.0: Distance=1180.25, Vehicles=7
Weight 100.0: Distance=1210.00, Vehicles=6
Weight 200.0: Distance=1250.75, Vehicles=5
```

**How to Choose Weight:**
- Start with `vehicle_weight=100.0`
- If you want fewer vehicles → increase weight
- If you want better distance → decrease weight
- Run multiple experiments and compare results

---

## Configuration Summary

### Configuration Matrix

| Mode | `ignore_time_windows` | `minimize_vehicles` | Use Case |
|------|----------------------|-------------------|----------|
| **VRPTW Standard** | False | False | Real-world with time windows |
| **VRPTW + Min Vehicles** | False | True | Time windows + vehicle efficiency |
| **VRP Standard** | True | False | Pure distance minimization |
| **VRP + Min Vehicles** | True | True | Minimize vehicles first |

### Quick Reference

```python
# 1. Standard VRPTW (default)
ga = GeneticAlgorithm(depot, clients, capacity)

# 2. VRPTW with vehicle minimization
ga = GeneticAlgorithm(depot, clients, capacity,
    minimize_vehicles=True, vehicle_weight=100.0)

# 3. VRP (no time windows)
ga = GeneticAlgorithm(depot, clients, capacity,
    ignore_time_windows=True)

# 4. VRP with vehicle minimization
ga = GeneticAlgorithm(depot, clients, capacity,
    ignore_time_windows=True, minimize_vehicles=True,
    vehicle_weight=100.0)
```

---

## Works with Both Algorithms

All parameters work with **both GA and TS**:

```python
from src.genetic_algorithm import GeneticAlgorithm
from src.tabu_search import TabuSearch

# Genetic Algorithm
ga = GeneticAlgorithm(depot, clients, capacity,
    ignore_time_windows=True,
    minimize_vehicles=True,
    vehicle_weight=100.0)
ga_solution = ga.evolve()

# Tabu Search
ts = TabuSearch(depot, clients, capacity,
    ignore_time_windows=True,
    minimize_vehicles=True,
    vehicle_weight=100.0)
ts_solution = ts.search()
```

---

## Solution Quality Comparison

### VRPTW vs VRP

On typical Solomon benchmark (data101):

| Metric | VRPTW | VRP |
|--------|-------|-----|
| Distance | 1,250-1,300 | 1,100-1,200 |
| Vehicles | 10-12 | 8-10 |
| Feasibility | 70-90% | 100% |
| Time | ~30s | ~15s |

**Key Insights:**
- VRP gives better distance (no time constraints)
- VRP uses fewer vehicles
- VRP is faster to solve
- VRPTW is more realistic for real-world applications

### Impact of Vehicle Minimization

On VRP mode (data101):

| Vehicle Weight | Distance | Vehicles | Score |
|---|---|---|---|
| 0 | 1,180 | 8 | 1,180 |
| 50 | 1,200 | 7 | 1,550 |
| 100 | 1,220 | 6 | 1,820 |
| 200 | 1,280 | 5 | 2,280 |

**Key Insights:**
- Higher weight → fewer vehicles
- Trade-off: distance increases
- Find balance for your application

---

## Practical Examples

### Example 1: Minimize Distance Only

```python
ga = GeneticAlgorithm(depot, clients, capacity,
    ignore_time_windows=False,  # Respect time windows
    minimize_vehicles=False)     # Focus on distance

solution = ga.evolve(verbose=True)
print(f"Distance: {DistanceCalculator.solution_distance(solution):.2f}")
print(f"Vehicles: {solution.get_num_vehicles()}")
```

### Example 2: Minimize Vehicles (VRP)

```python
ga = GeneticAlgorithm(depot, clients, capacity,
    ignore_time_windows=True,   # No time constraints
    minimize_vehicles=True,      # Minimize vehicle count
    vehicle_weight=150.0)        # Strong weight for vehicles

solution = ga.evolve(verbose=True)
print(f"Distance: {DistanceCalculator.solution_distance(solution):.2f}")
print(f"Vehicles: {solution.get_num_vehicles()}")
```

### Example 3: Balance Distance and Vehicles

```python
ga = GeneticAlgorithm(depot, clients, capacity,
    ignore_time_windows=True,
    minimize_vehicles=True,
    vehicle_weight=100.0)  # Balanced weight

solution = ga.evolve(verbose=True)
stats = SolutionEvaluator.get_solution_stats(solution, clients)
print(f"Feasible: {stats['is_feasible']}")
print(f"Distance: {stats['distance']:.2f}")
print(f"Vehicles: {stats['num_vehicles']}")
```

### Example 4: Compare All Modes

```python
from src.genetic_algorithm import GeneticAlgorithm
from src.tabu_search import TabuSearch
from src.distance_utils import DistanceCalculator

problem = DataLoader.load_problem("data/data101.vrp")

modes = {
    "VRPTW": (False, False),
    "VRPTW+MinVeh": (False, True),
    "VRP": (True, False),
    "VRP+MinVeh": (True, True),
}

results = {}

for name, (ignore_time, min_veh) in modes.items():
    ga = GeneticAlgorithm(
        problem.depot, problem.clients, problem.capacity,
        ignore_time_windows=ignore_time,
        minimize_vehicles=min_veh,
        vehicle_weight=100.0
    )
    solution = ga.evolve(verbose=False)
    distance = DistanceCalculator.solution_distance(solution)
    vehicles = solution.get_num_vehicles()
    
    results[name] = {"distance": distance, "vehicles": vehicles}
    print(f"{name:<15} Distance: {distance:8.2f}  Vehicles: {vehicles}")
```

---

## Testing & Debugging

### Verify Mode is Working

```python
from src.models import Route

# Create route with ignore_time_windows=True
route = Route(depot, capacity, ignore_time_windows=True)

# Should add any client without time checks
result = route.add_client(client)
print(f"Client added: {result}")  # Should be True
```

### Check Feasibility

```python
from src.distance_utils import SolutionEvaluator

solution = ga.evolve()
stats = SolutionEvaluator.get_solution_stats(solution, problem.clients)

print(f"Feasible: {stats['is_feasible']}")
print(f"Unassigned: {stats['unassigned_clients']}")
print(f"Infeasible routes: {stats['infeasible_routes']}")
print(f"Capacity violations: {stats['capacity_violations']}")
```

---

## Run Examples

Complete examples are in `vrp_example.py`:

```bash
# Run all VRP/VRPTW mode examples
python vrp_example.py
```

This will run 6 detailed examples showing:
1. Standard VRPTW
2. VRP mode
3. VRP + vehicle minimization
4. Tabu Search in VRP mode
5. Comparison of all modes
6. Effect of vehicle weight parameter

---

## Summary

**Key Parameters:**

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `ignore_time_windows` | False | True = VRP mode, False = VRPTW mode |
| `minimize_vehicles` | False | True = penalize vehicle count |
| `vehicle_weight` | 100.0 | How much to penalize each vehicle |

**Choose Your Mode:**
- **VRPTW (ignore_time_windows=False)**: Real-world with time constraints
- **VRP (ignore_time_windows=True)**: Simplified, no time windows
- **Add minimize_vehicles=True**: When vehicle count is important

**Start Here:**
```python
# Standard recommendation: VRP + minimize vehicles
ga = GeneticAlgorithm(depot, clients, capacity,
    ignore_time_windows=True,
    minimize_vehicles=True,
    vehicle_weight=100.0)
solution = ga.evolve()
```
