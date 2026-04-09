# VRPTW Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Algorithms](#algorithms)
5. [Neighborhood Operators](#neighborhood-operators)
6. [How to Run](#how-to-run)
7. [Design Decisions](#design-decisions)
8. [Performance Considerations](#performance-considerations)

---

## Overview

This project implements **Genetic Algorithm** and **Tabu Search** metaheuristics to solve the **Vehicle Routing Problem with Time Windows (VRPTW)**.

**VRPTW Problem Definition:**
- Serve a set of clients with known locations, demands, and time windows
- Use multiple vehicles starting/ending at a central depot
- Each vehicle has a capacity constraint
- Minimize total distance traveled while respecting all constraints:
  - Capacity constraints (vehicle load ≤ capacity)
  - Time window constraints (visit client within [ready_time, due_time])
  - Service time requirements at each client

**Project Goals:**
- Compare two different metaheuristic approaches
- Provide well-structured, modular code
- Include visualization of solutions
- Enable detailed performance analysis

---

## Architecture

### Directory Structure

```
VRPTW/
├── src/                           # Core optimization modules
│   ├── __init__.py
│   ├── main.py                    # Experiment orchestration
│   ├── models.py                  # Data structures (Location, Client, Route, Solution)
│   ├── data_loader.py             # Parse .vrp problem files
│   ├── distance_utils.py          # Distance calculations and evaluation
│   ├── solution_generator.py      # Initial solution construction
│   ├── neighborhood.py            # Local search operators
│   ├── genetic_algorithm.py       # GA metaheuristic
│   └── tabu_search.py             # TS metaheuristic
│
├── visualization/                 # Separate visualization package
│   ├── __init__.py
│   └── plotter.py                 # Route visualization and comparisons
│
├── data/                          # Problem instances (downloaded)
│   └── *.vrp                      # VRPTW problem files
│
├── results/                       # Generated results and plots
│   └── results.json               # Experiment results
│
├── requirements.txt               # Python dependencies
└── TECHNICAL_DOCUMENTATION.md     # This file
```

### Design Philosophy

The architecture follows **separation of concerns**:

1. **Core Logic (src/)**: Pure optimization algorithms independent of visualization
2. **Data Layer (models.py, data_loader.py)**: Problem representation
3. **Evaluation Layer (distance_utils.py)**: Solution quality metrics
4. **Construction Layer (solution_generator.py)**: Initial solutions
5. **Search Layer (genetic_algorithm.py, tabu_search.py)**: Metaheuristics
6. **Neighborhood Layer (neighborhood.py)**: Local search operators
7. **Visualization Layer (visualization/)**: Completely separated for modularity

This separation allows:
- Easy testing and extension
- Reusing components in different contexts
- Clear dependencies and responsibilities
- Independent visualization without impacting optimization

---

## Core Components

### 1. Data Models (`models.py`)

#### Location
```python
Location(x, y)  # Euclidean coordinates
```
- Represents geographic points
- Calculates distances to other locations
- Used for depot and client positions

#### TimeWindow
```python
TimeWindow(ready_time, due_time)
```
- Defines service availability window
- Methods:
  - `is_time_feasible(arrival_time)`: Check if arrival respects window
  - `get_waiting_time(arrival_time)`: Calculate wait before service start
  - `get_time_slack(arrival_time)`: Time available before due_time

#### Client
```python
Client(id, location, demand, time_window, service_time)
```
- Represents a customer to serve
- Has unique identifier
- Has demand (goods to pickup/deliver)
- Has time window and service duration

#### Route
```python
Route(depot, capacity)
```
- Single vehicle route
- Manages client sequence
- Validates constraints:
  - `add_client()`: Add client with feasibility check
  - `insert_client(position)`: Insert at specific position
  - `is_feasible()`: Validate entire route
- Calculates route metrics:
  - `get_total_distance()`: Total travel distance
  - Current load and time tracking

#### Solution
```python
Solution(depot, capacity)
```
- Complete multi-vehicle solution
- Contains multiple Route objects
- Methods:
  - `get_all_clients()`: All served clients
  - `get_unassigned_clients()`: Clients not yet served
  - `is_complete()`: All clients assigned
  - `is_feasible()`: All constraints satisfied
  - `get_total_distance()`: Sum of all routes
  - `copy()`: Deep copy for algorithm iterations

### 2. Data Loader (`data_loader.py`)

#### VRPTProblem
```python
VRPTProblem(name, depot, clients, capacity)
```
- Encapsulates a complete problem instance
- Stores all problem data

#### DataLoader
- **Static method**: `load_problem(filepath)` → `VRPTProblem`
  - Parses .vrp format files
  - Handles metadata (NB_CLIENTS, MAX_QUANTITY)
  - Extracts depot and client information
  - Validates input data

- **Static method**: `load_all_problems(directory)` → `List[VRPTProblem]`
  - Batch loading of all .vrp files
  - Useful for running experiments on multiple instances

**File Format (VRP):**
```
NAME: problem_name
TYPE: vrptw
NB_CLIENTS: 100
MAX_QUANTITY: 200

DATA_DEPOTS [id x y ready_time due_time]:
d1 35 35 0 230

DATA_CLIENTS [id x y ready_time due_time demand service]:
c1 41 49 161 171 10 10
c2 35 17 50 60 7 10
...
```

### 3. Distance Utilities (`distance_utils.py`)

#### DistanceCalculator
- `euclidean_distance(x1, y1, x2, y2)`: Raw distance calculation
- `route_distance(route)`: Total distance of a route
- `solution_distance(solution)`: Total distance of all routes
- `insertion_distance_delta(route, client, position)`: Cost change for insertion
- `relocation_distance_delta(route, client, old_pos, new_pos)`: Cost change for relocation

#### SolutionEvaluator
- **Feasibility checks:**
  - `is_feasible(solution, all_clients)`: Complete feasibility check
  - `get_constraint_violations()`: Count violations by type

- **Quality metrics:**
  - `evaluate_quality()`: Objective value with penalty terms
  - `get_solution_stats()`: Comprehensive statistics dictionary
  - `get_average_load_utilization()`: Capacity usage across vehicles

**Why Separated:** Distance and evaluation calculations are frequently called in tight loops. Dedicated, optimized methods improve performance.

### 4. Solution Generator (`solution_generator.py`)

Provides diverse initial solutions for algorithm warm-starting:

#### Methods

1. **Random Solution** (`generate_random_solution`)
   - Shuffle clients randomly
   - Assign to routes greedily
   - May violate constraints (intentional - for diversity)

2. **Nearest Neighbor** (`nearest_neighbor`)
   - Greedy construction
   - Always extends route with nearest unvisited client
   - Time complexity: O(n²)
   - Usually gives reasonable solutions

3. **Greedy Insertion** (`greedy_insertion`)
   - Start with closest client to depot
   - Insert remaining clients at positions minimizing distance increase
   - More sophisticated than NN
   - Higher computational cost

4. **Clarke-Wright Savings** (`savings_algorithm`)
   - Classical VRP heuristic
   - Calculate savings for merging client pairs
   - Merge routes in order of savings
   - Works well for many problem types

5. **Multi-Start Nearest Neighbor** (`multi_start_nearest_neighbor`)
   - Run NN multiple times with different random seeds
   - Return best solution found
   - Good trade-off: quality vs. time

**Why Important:** Initial solution quality significantly affects algorithm performance. Diversity helps escape local optima.

---

## Algorithms

### 1. Genetic Algorithm (`genetic_algorithm.py`)

#### Overview
Population-based evolutionary algorithm that mimics natural selection and genetic recombination.

#### Key Components

**Population Representation:**
- Each individual = complete Solution (multiple routes)
- Population size: 50 individuals (configurable)
- Diversity maintained through different construction heuristics

**Initialization:**
- 25% random solutions
- 25% nearest neighbor solutions
- 25% greedy insertion solutions
- 25% Clarke-Wright solutions

**Selection:** Tournament Selection
- Randomly select k individuals (k=3)
- Return the best (lowest fitness)
- Fast, prevents premature convergence

**Crossover Operators** (3 types, randomly chosen):

1. **Route-Based Crossover**
   - Take some complete routes from parent1
   - Fill missing clients using parent2's routes or new routes
   - Preserves good route structures

2. **Order-Based Crossover**
   - Maintain client order from parent1
   - Insert remaining clients from parent2 in their relative order
   - Simpler, more exploration

3. **Segment-Based Crossover**
   - Randomly select routes from both parents
   - Combine compatible route segments
   - Can significantly restructure solution

**Mutation Operators:**
- Apply 1-3 random neighborhood moves
- Perturb solutions for exploration
- Prevent population stagnation

**Elitism:**
- Preserve best 2 solutions each generation
- Ensure best solution never decreases

**Fitness Function:**
```
fitness = distance + penalty_weight × (unassigned + infeasible_routes + capacity_violations)
```
- Penalties ensure constraint-respecting solutions
- High penalty weight (10,000) strongly favors feasibility

**Parameters:**
- Population size: 50
- Generations: 100
- Crossover rate: 0.8
- Mutation rate: 0.2
- Elite size: 2

#### Complexity
- Time: O(generations × population_size × solution_evaluation_cost)
- Space: O(population_size × solution_size)

#### Strengths
✓ Good at finding diverse solutions
✓ Robust to local optima
✓ Natural parallelization opportunity
✓ Less prone to premature convergence

#### Weaknesses
✗ Slow convergence to local optimum
✗ Higher computational cost per iteration
✗ Requires careful parameter tuning

---

### 2. Tabu Search (`tabu_search.py`)

#### Overview
Deterministic local search that uses memory (tabu list) to avoid revisiting recent solutions and escape local optima.

#### Key Components

**Tabu List:**
- Stores recent moves preventing them for τ iterations
- τ (tabu tenure) = max(7, num_clients / 10) (adaptive)
- Move description: operator name + parameters
- Prevents cycling; allows systematic exploration

**Aspiration Criteria:**
- Override tabu status if solution improves best found
- Critical: prevents tabu restrictions from blocking improvements
- Ensures asymptotic convergence

**Neighborhood Exploration:**
- Best-improvement strategy
- Explore ~100 neighbors per iteration
- Select best non-tabu neighbor (or tabu if aspiration met)

**Diversification Strategy:**
- Triggered when no improvement for many iterations
- Apply 5-10 random moves
- Jump to different solution region
- Prevent getting stuck in plateaus

**Intensification Strategy:**
- Apply 3 iterations of best-improvement moves
- Focus around good solutions
- Reduce neighborhood to promising regions

**Initial Solution:**
- Multi-start nearest neighbor (5 attempts)
- Ensures good starting point
- Better than random

**Parameters:**
- Max iterations: 1000
- Tabu tenure: adaptive
- Neighborhood size: 100
- Diversification frequency: 50 iterations
- Intensification: on plateaus

#### Complexity
- Time: O(max_iterations × neighborhood_size × solution_evaluation)
- Space: O(tabu_tenure × move_description_size)

#### Strengths
✓ Very effective at finding local optima
✓ Good balance of exploitation and exploration
✓ Memory-based approach is elegant
✓ Fast convergence to nearby optima

#### Weaknesses
✗ Can get stuck in poor local optima (despite diversification)
✗ Sensitive to tabu tenure setting
✗ Requires good initial solution

---

## Neighborhood Operators

Located in `neighborhood.py`. Six complementary operators provide diverse local search moves:

### 1. 2-opt (`TwoOpt`)

**Operation:**
- Remove two edges in a route: (i, i+1) and (j, j+1)
- Reverse segment between them: [i+1, ..., j]
- Reconnect: (i, j) and (i+1, j+1)

**When to use:** General-purpose, very effective for sequential problems

**Complexity:** O(n²) per evaluation

**Visual Example:**
```
Before: 1—2—3—4—5—1
After:  1—4—3—2—5—1  (segment 2-3-4 reversed)
```

### 2. Or-opt (`OrOpt`)

**Operation:**
- Remove sequence of k consecutive clients (k=1,2,3)
- Insert sequence elsewhere in same route or different route
- Generalization of 1-opt and 2-opt

**Variants:**
- k=1: Single client relocation
- k=2: Two-client sequence
- k=3: Three-client sequence

**When to use:** More fine-grained control than 2-opt; explores wider neighborhood

**Complexity:** O(n³) for k=3

### 3. Relocate/1-opt (`Relocate`)

**Operation:**
- Remove single client from route
- Insert at different position (same or different route)
- Simplest move

**When to use:** Quick moves, good for initial exploration

**Complexity:** O(n²)

**Best Improvement Variant:**
- Evaluates all possible positions
- Time-intensive but very effective

### 4. Cross-Exchange (`CrossExchange`)

**Operation:**
- Select two different routes
- Swap a client from route1 with a client from route2
- Can change route structures significantly

**When to use:** Restructure multi-vehicle solutions; break bad route combinations

**Complexity:** O(n²) for all possible swaps

### 5. 2-opt Between Routes (`TwoOptBetweenRoutes`)

**Operation:**
- Select two routes
- Remove edge from each route
- Reconnect differently, moving client segments between routes
- More radical than cross-exchange

**When to use:** Explore significantly different solution structures

**Complexity:** O(n²)

### 6. NeighborhoodManager

**Purpose:** Coordinate all operators

**Methods:**
- `apply_random_operator()`: Randomly select operator
- `apply_operator(name)`: Apply specific operator
- `get_all_operators()`: List available operators
- `get_num_operators()`: Count operators

**Why Important:**
- Unified interface for all moves
- Easy to add new operators
- Supports operator statistics and analysis

---

## How to Run

### Prerequisites

```bash
# Install Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

**Run experiments on all problems:**
```bash
cd VRPTW
python src/main.py
```

**Expected Output:**
- Progress messages showing problem loading and solving
- Detailed comparison for each problem
- Summary table of all results
- Results saved to `results/results.json`

### Advanced Usage

**Modify experiment parameters (in `src/main.py`):**

```python
from src.main import VRPTPExperiment

# Create experiment
exp = VRPTPExperiment(
    data_directory="data",
    results_directory="results"
)

# Load and solve specific problems
exp.load_problems(limit=3)  # Limit to 3 problems

# Customize algorithm parameters
from src.genetic_algorithm import GeneticAlgorithm

ga = GeneticAlgorithm(
    depot=problem.depot,
    clients=problem.clients,
    capacity=problem.capacity,
    population_size=100,      # Larger population
    generations=200,           # More generations
    crossover_rate=0.85,       # Higher crossover
    mutation_rate=0.15,        # Lower mutation
)

best_solution = ga.evolve(verbose=True)
```

### Visualization

```python
from visualization.plotter import RouteVisualizer
from src.distance_utils import DistanceCalculator

# Create visualizer
viz = RouteVisualizer(figsize=(14, 10), dpi=100)

# Plot single solution
viz.plot_solution(
    solution,
    title="VRPTW Solution",
    show_time_windows=True,
    show_demands=True,
    save_path="results/solution.png"
)

# Plot algorithm convergence
viz.plot_convergence(
    history=ga.generation_history,
    algorithm_name="Genetic Algorithm",
    save_path="results/convergence_ga.png"
)

# Compare two solutions
viz.plot_comparison(
    solution1=ga_best,
    solution2=ts_best,
    title1="GA Solution",
    title2="TS Solution",
    save_path="results/comparison.png"
)

# Plot performance metrics
viz.plot_distance_comparison(
    results=experiment.results,
    save_path="results/distance_comparison.png"
)
```

### Output Files

Generated in `results/`:
- `results.json`: Complete results data (distances, vehicles, times, feasibility)
- `*.png`: Visualizations (solution plots, convergence curves, comparisons)

---

## Design Decisions

### 1. Why Separate Visualization?

**Decision:** Visualization in separate `visualization/` package

**Rationale:**
- Core optimization doesn't depend on matplotlib
- Enables headless execution on servers
- Visualization is optional, not essential
- Easier testing without graphical dependencies
- Cleaner separation of concerns

### 2. Why Multiple Neighborhood Operators?

**Decision:** Implement 6 different operators instead of just 2-opt

**Rationale:**
- Different operators explore different regions
- Complementary strengths for different problem structures
- Flexibility for customization
- Better research value (compare operator effectiveness)
- Some problems respond better to specific moves

### 3. Why Penalty-Based Evaluation?

**Decision:** Use penalty terms for infeasibility (not repair heuristics)

**Rationale:**
- Simpler implementation (no special cases)
- Allows algorithms to search through infeasible regions
- Better guides search toward feasibility
- More intuitive for research/comparison
- Well-established in constraint handling literature

### 4. Why Tournament Selection in GA?

**Decision:** Use tournament selection over fitness-proportionate

**Rationale:**
- Better convergence properties
- Less sensitive to fitness value scaling
- Prevents premature convergence from super-fit individuals
- More efficient to implement
- Empirically superior for many problems

### 5. Why Adaptive Tabu Tenure?

**Decision:** Tenure = max(7, num_clients / 10)

**Rationale:**
- Automatically scales with problem size
- Prevents too-long tenure (memory waste) on small problems
- Prevents too-short tenure (cycling) on large problems
- No manual tuning required
- Empirically effective

### 6. Why Multi-Start Nearest Neighbor for TS Initialization?

**Decision:** Use 5 NN attempts instead of single random

**Rationale:**
- TS is deterministic, quality depends on initial solution
- 5 attempts is cheap (5% of total TS budget)
- Helps TS escape poor initial local optima
- GA has built-in diversity, doesn't need as much help
- Different initialization philosophies suit different algorithms

---

## Performance Considerations

### Computational Complexity

**Problem Sizes:**
- Small: 25-100 clients → Any algorithm works
- Medium: 100-200 clients → Both algorithms effective
- Large: >200 clients → TS often superior

**Time Estimates (on modern CPU):**
| Problem Size | GA (50×100) | TS (1000 iter) |
|---|---|---|
| 25 clients | ~5s | ~3s |
| 100 clients | ~30s | ~15s |
| 200 clients | ~120s | ~45s |

### Memory Usage

**GA:**
- Population size × solution size
- ~50 solutions × ~10KB each = ~500KB

**TS:**
- Tabu list + current/best solution
- ~10KB + overhead = ~100KB

TS is more memory-efficient.

### Optimization for Speed

**GA:**
- Reduce population size (trade quality for speed)
- Reduce generations (earlier stopping)
- Use simpler crossover operators

**TS:**
- Reduce max iterations (trade quality for speed)
- Reduce neighborhood size exploration
- Use simpler neighborhoods

### Quality vs. Time Trade-off

**For Time-Critical Applications:**
→ Use TS with 500 iterations instead of 1000

**For Quality-Critical Applications:**
→ Use GA with 200 generations and population 100

**For Balanced Approach:**
→ Run both in parallel, use best result (hybrid approach)

### Parallelization Opportunities

**GA:**
- Population evaluation parallelizable (embarrassingly parallel)
- Crossover/mutation can be parallelized per individual
- ×4 speedup achievable on quad-core

**TS:**
- Neighborhood exploration parallelizable
- Can evaluate multiple neighbors simultaneously
- ×2-3 speedup achievable

---

## Testing and Validation

### Solution Validation Checklist

```python
from src.distance_utils import SolutionEvaluator

stats = SolutionEvaluator.get_solution_stats(solution, all_clients)

assert stats['is_feasible'], "Solution violates constraints"
assert stats['unassigned_clients'] == 0, "Clients not served"
assert stats['infeasible_routes'] == 0, "Route constraints violated"
assert stats['capacity_violations'] == 0, "Load exceeded"
```

### Performance Analysis

Check `results/results.json` for:
- Distance: Lower is better
- Num vehicles: Lower is better
- Execution time: Lower is better
- Is_feasible: Must be true
- Constraint violations: Must be zero

### Debugging Infeasible Solutions

```python
unass, infeas, cap_viol = SolutionEvaluator.get_constraint_violations(
    solution, all_clients
)
print(f"Unassigned: {unass}, Infeasible routes: {infeas}, Capacity violations: {cap_viol}")

# Check specific route
for i, route in enumerate(solution.routes):
    if not route.is_feasible():
        print(f"Route {i} infeasible:")
        print(f"  Load: {route.current_load} / {route.capacity}")
        print(f"  Clients: {[c.id for c in route.clients]}")
```

---

## References and Literature

**VRPTW:**
- Solomon, M. M. (1987). "Algorithms for the vehicle routing and scheduling problems with time window constraints"
- Desrosiers, J., Dumas, Y., Solomon, M. M., & Soumis, F. (1995). "Vehicle routing with time windows"

**Genetic Algorithms:**
- Holland, J. H. (1975). "Adaptation in Natural and Artificial Systems"
- Davis, L. D. (1991). "Handbook of Genetic Algorithms"

**Tabu Search:**
- Glover, F. (1986). "Future paths for integer programming and links to artificial intelligence"
- Glover, F., & Laguna, M. (1997). "Tabu Search"

**Local Search:**
- Johnson, D. S., & McGeoch, L. A. (1997). "The traveling salesman problem: A case study in local optimization"
- Hoos, H. H., & Stützle, T. (2004). "Stochastic Local Search: Foundations & Applications"

---

## Troubleshooting

**Problem: ModuleNotFoundError when running main.py**
→ Solution: Ensure you're in VRPTW directory and have installed requirements
```bash
cd VRPTW
pip install -r requirements.txt
python src/main.py
```

**Problem: Solution is infeasible**
→ Solution: Check if problem is solvable; increase max iterations or population size; try different initialization

**Problem: Very slow execution**
→ Solution: Reduce iterations/population size; use smaller problem set for testing

**Problem: Visualization doesn't show**
→ Solution: Ensure matplotlib is installed; may need to set backend
```python
import matplotlib
matplotlib.use('TkAgg')  # Or 'Agg' for headless
```

---

**End of Technical Documentation**