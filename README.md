# VRPTW - Vehicle Routing Problem with Time Windows Solver

## 📋 Project Overview

This project implements advanced metaheuristic algorithms to solve the **Vehicle Routing Problem with Time Windows (VRPTW)**, a classic optimization problem in operations research.

**Problem Statement:**
- Route a fleet of vehicles to serve a set of customers (clients)
- Each customer has a location, demand, and time window for service
- Each vehicle has a capacity constraint and must start/end at the depot
- **Objective:** Minimize total distance traveled while satisfying all constraints

**This Implementation:**
- ✅ Genetic Algorithm (GA) - population-based evolutionary approach
- ✅ Tabu Search (TS) - memory-enhanced local search
- ✅ 6 different neighborhood operators for diverse local search
- ✅ 4 initial solution construction heuristics
- ✅ Comprehensive visualization module
- ✅ Detailed performance comparison framework
- ✅ Modular, well-documented codebase

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

```bash
# 1. Navigate to the project directory
cd VRPTW

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run experiments
python src/main.py
```

### Expected Output
- Progress messages showing algorithm execution
- Summary tables comparing GA and TS performance
- Results saved to `results/results.json`
- Solution statistics (distance, vehicles, feasibility)

---

## 📁 Project Structure

```
VRPTW/
├── src/                              # Core optimization modules
│   ├── __init__.py
│   ├── main.py                       # Experiment orchestrator
│   ├── models.py                     # Data structures (Location, Client, Route, Solution)
│   ├── data_loader.py                # Parse .vrp problem files
│   ├── distance_utils.py             # Distance calculations & evaluation metrics
│   ├── solution_generator.py         # Initial solution construction heuristics
│   ├── neighborhood.py               # Local search operators (2-opt, Or-opt, etc.)
│   ├── genetic_algorithm.py          # GA metaheuristic implementation
│   └── tabu_search.py                # TS metaheuristic implementation
│
├── visualization/                    # Visualization package (separated from core)
│   ├── __init__.py
│   └── plotter.py                    # Route visualization and performance plots
│
├── data/                             # Problem instances
│   └── *.vrp                         # VRPTW benchmark problems
│
├── results/                          # Generated results
│   └── results.json                  # Experiment results data
│
├── requirements.txt                  # Python dependencies
├── TECHNICAL_DOCUMENTATION.md        # Detailed technical documentation
└── README.md                         # This file
```

---

## 🔧 Installation & Setup

### Step 1: Clone or Extract Project
```bash
# If you have a zip file, extract it first
unzip VRPTW.zip
cd VRPTW
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies:**
- numpy (1.24.3) - Numerical computations
- matplotlib (3.7.1) - Visualization
- pandas (2.0.2) - Data handling
- scipy (1.10.1) - Scientific computing
- folium (0.14.0) - Interactive maps (optional for advanced visualization)

---

## ▶️ Running the Code

### Basic Execution
```bash
cd VRPTW
python src/main.py
```

This will:
1. Load all problems from `data/` directory
2. Solve each problem with both GA and TS
3. Print detailed results and comparisons
4. Save results to `results/results.json`

### Advanced Usage - Modify Parameters

Create a script to customize execution:

```python
from src.main import VRPTPExperiment
from src.data_loader import DataLoader

# Create experiment
exp = VRPTPExperiment(
    data_directory="data",
    results_directory="results"
)

# Load specific problems
problems = DataLoader.load_all_problems("data")
problem = problems[0]  # First problem

# Solve with custom GA parameters
from src.genetic_algorithm import GeneticAlgorithm

ga = GeneticAlgorithm(
    depot=problem.depot,
    clients=problem.clients,
    capacity=problem.capacity,
    population_size=100,      # Larger population
    generations=200,          # More generations
    crossover_rate=0.85,      # Higher crossover rate
    mutation_rate=0.15,       # Lower mutation rate
    elite_size=3              # Keep more best solutions
)

best_solution = ga.evolve(verbose=True)
print(f"Distance: {ga.best_fitness:.2f}")
print(f"Vehicles: {best_solution.get_num_vehicles()}")
```

### Solve Only First 3 Problems
```python
exp = VRPTPExperiment("data", "results")
exp.run_experiments(verbose=True, problem_limit=3)
```

---

## 📊 Understanding Results

### Output Format

Results are saved as JSON in `results/results.json`:

```json
{
  "data101": {
    "problem_name": "data101",
    "num_clients": 100,
    "capacity": 200,
    "genetic_algorithm": {
      "execution_time": 45.32,
      "distance": 1234.56,
      "num_vehicles": 10,
      "is_feasible": true,
      "solution_stats": {
        "unassigned_clients": 0,
        "infeasible_routes": 0,
        "capacity_violations": 0
      }
    },
    "tabu_search": {
      "execution_time": 28.15,
      "distance": 1198.34,
      "num_vehicles": 9,
      "is_feasible": true,
      ...
    }
  }
}
```

### Key Metrics

1. **distance**: Total travel distance (lower is better)
2. **num_vehicles**: Number of vehicles used (lower is better)
3. **execution_time**: Algorithm runtime in seconds
4. **is_feasible**: Whether solution satisfies all constraints (must be true)
5. **unassigned_clients**: Number of unserved clients (must be 0)
6. **infeasible_routes**: Routes violating constraints
7. **capacity_violations**: Vehicles exceeding capacity

### Interpreting Comparisons

- **GA wins on distance**: Better solution quality, slower to compute
- **TS wins on distance**: Better local optimization, good balance
- **TS faster**: More time-efficient for large problems
- **GA slower**: Population overhead, but more robust

---

## 🎨 Visualization

The visualization module is completely separated from the core optimization code.

### Plot a Solution

```python
from visualization.plotter import RouteVisualizer
from src.data_loader import DataLoader
from src.genetic_algorithm import GeneticAlgorithm

# Load problem
problem = DataLoader.load_problem("data/data101.vrp")

# Solve it
ga = GeneticAlgorithm(problem.depot, problem.clients, problem.capacity)
solution = ga.evolve(verbose=True)

# Visualize
viz = RouteVisualizer(figsize=(14, 10), dpi=100)
viz.plot_solution(
    solution,
    title="GA Solution for data101",
    show_time_windows=True,
    show_demands=True,
    save_path="results/solution_ga.png"
)
```

### Plot Convergence History

```python
viz.plot_convergence(
    history=ga.generation_history,
    algorithm_name="Genetic Algorithm",
    save_path="results/convergence_ga.png"
)
```

### Compare Two Solutions

```python
from src.tabu_search import TabuSearch

ts = TabuSearch(problem.depot, problem.clients, problem.capacity)
ts_solution = ts.search(verbose=True)

viz.plot_comparison(
    solution1=ga.best_solution,
    solution2=ts_solution,
    title1="Genetic Algorithm",
    title2="Tabu Search",
    save_path="results/comparison.png"
)
```

### Plot Performance Metrics Across Problems

```python
# After running experiments
viz.plot_distance_comparison(
    results=exp.results,
    save_path="results/distance_comparison.png"
)

viz.plot_vehicles_comparison(
    results=exp.results,
    save_path="results/vehicles_comparison.png"
)

viz.plot_execution_time_comparison(
    results=exp.results,
    save_path="results/time_comparison.png"
)
```

---

## 🔍 Component Overview

### 1. Data Models (`src/models.py`)

**Location**: Represents geographic coordinates
```python
Location(x=35.0, y=45.0)
```

**Client**: Represents a customer to serve
```python
Client(
    id="c1",
    location=Location(41, 49),
    demand=10,
    time_window=TimeWindow(161, 171),
    service_time=10
)
```

**Route**: Single vehicle route
```python
route = Route(depot, capacity=200)
route.add_client(client)
route.get_total_distance()
```

**Solution**: Complete multi-vehicle solution
```python
solution = Solution(depot, capacity=200)
solution.create_new_route()
solution.get_total_distance()
solution.is_feasible()
```

### 2. Solution Generators (`src/solution_generator.py`)

Four construction heuristics for initial solutions:

1. **Random Solution**: Quick, diverse starting points
2. **Nearest Neighbor**: Greedy, usually reasonable
3. **Greedy Insertion**: More sophisticated construction
4. **Clarke-Wright Savings**: Classical VRP algorithm
5. **Multi-Start NN**: Best of multiple NN attempts

### 3. Neighborhood Operators (`src/neighborhood.py`)

Six local search moves:

1. **2-opt**: Remove and reconnect two edges (classic)
2. **Or-opt-1**: Relocate single client
3. **Or-opt-2**: Relocate pair of clients
4. **Or-opt-3**: Relocate triplet of clients
5. **Cross-Exchange**: Swap clients between routes
6. **2-opt Between Routes**: Exchange route segments

### 4. Genetic Algorithm (`src/genetic_algorithm.py`)

Population-based evolutionary algorithm:
- **Selection**: Tournament (select best from random group)
- **Crossover**: Route-based, Order-based, Segment-based
- **Mutation**: Random neighborhood moves
- **Elitism**: Preserve best solutions
- **Parameters**: 50 pop, 100 gen, 0.8 crossover, 0.2 mutation

### 5. Tabu Search (`src/tabu_search.py`)

Memory-enhanced local search:
- **Tabu List**: Forbid recent moves
- **Tabu Tenure**: Adaptive (based on problem size)
- **Aspiration**: Override tabu for improving solutions
- **Diversification**: Escape local optima
- **Intensification**: Improve good solutions
- **Parameters**: 1000 iterations, auto tabu tenure

---

## 💡 Key Design Decisions

### Why Separate Visualization?
- ✅ Optimization works without graphics (headless servers)
- ✅ Cleaner separation of concerns
- ✅ No graphical dependencies for core code
- ✅ Easier testing and debugging

### Why Multiple Neighborhood Operators?
- ✅ Different operators suit different problem structures
- ✅ Diversify search space exploration
- ✅ Compare operator effectiveness
- ✅ Flexibility for problem customization

### Why Both GA and TS?
- ✅ GA excels at robust exploration (less stuck in local optima)
- ✅ TS excels at focused exploitation (fast convergence)
- ✅ Different strengths for different problem types
- ✅ Educational value (compare paradigms)

### Why Penalty-Based Constraint Handling?
- ✅ Simpler implementation
- ✅ Allows search through infeasible regions
- ✅ Better guides toward feasibility
- ✅ Well-established in literature

---

## 📈 Performance Guide

### Recommended Parameters by Problem Size

**Small (≤50 clients):**
- GA: population=30, generations=50
- TS: iterations=500

**Medium (50-150 clients):**
- GA: population=50, generations=100
- TS: iterations=1000

**Large (>150 clients):**
- GA: population=50, generations=200 (or reduce pop to 30)
- TS: iterations=1500

### Time Estimates (on typical CPU)

| Clients | GA | TS |
|---------|-----|-----|
| 25      | 5s  | 3s  |
| 100     | 30s | 15s |
| 200     | 2m  | 1m  |

### Quality vs. Speed Trade-off

**Fast (priority: speed):**
```python
ga = GeneticAlgorithm(..., population_size=30, generations=50)
ts = TabuSearch(..., max_iterations=500)
```

**Balanced:**
```python
ga = GeneticAlgorithm(..., population_size=50, generations=100)
ts = TabuSearch(..., max_iterations=1000)
```

**High-quality (priority: solution quality):**
```python
ga = GeneticAlgorithm(..., population_size=100, generations=200)
ts = TabuSearch(..., max_iterations=2000)
```

---

## 🐛 Troubleshooting

### Problem: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'src'
```
**Solution:**
```bash
cd VRPTW
python src/main.py
```
Ensure you're in the right directory.

### Problem: FileNotFoundError for data
```
FileNotFoundError: Problem file not found: data/...
```
**Solution:** Check that you have data files in `VRPTW/data/` directory.

### Problem: Solution is infeasible
**Possible causes:**
- Problem is overconstrained (impossible to solve)
- Algorithm didn't run long enough

**Solutions:**
- Increase iterations/generations
- Try different initial solution
- Check constraint values (time windows, capacity)

### Problem: Very slow execution
**Solutions:**
- Test on fewer problems: `exp.run_experiments(problem_limit=1)`
- Reduce algorithm iterations
- Reduce population size
- Use a faster computer

### Problem: Visualization not showing
```python
import matplotlib
matplotlib.use('TkAgg')  # Use interactive backend
plt.show()
```

---

## 📚 Files and Their Purposes

| File | Purpose |
|------|---------|
| `src/models.py` | Data structures (Location, Client, Route, Solution) |
| `src/data_loader.py` | Parse .vrp files and load problems |
| `src/distance_utils.py` | Calculate distances and evaluate solutions |
| `src/solution_generator.py` | Create initial solutions (4 heuristics) |
| `src/neighborhood.py` | Local search moves (6 operators) |
| `src/genetic_algorithm.py` | GA metaheuristic |
| `src/tabu_search.py` | TS metaheuristic |
| `src/main.py` | Experiment orchestrator and comparator |
| `visualization/plotter.py` | Create plots and visualizations |
| `TECHNICAL_DOCUMENTATION.md` | Detailed algorithm documentation |

---

## 🎓 Educational Use

This codebase is ideal for learning:

1. **Optimization**: How different metaheuristics work
2. **Python**: Well-structured, modular code with docstrings
3. **Software Engineering**: Clean architecture, separation of concerns
4. **Algorithm Analysis**: Compare GA vs TS empirically
5. **VRPTW**: Understand the problem deeply

Each class and function is documented with:
- Purpose and behavior
- Parameters and return types
- Time/space complexity
- Example usage

---

## 📝 Example: Complete Workflow

```python
from src.data_loader import DataLoader
from src.genetic_algorithm import GeneticAlgorithm
from src.tabu_search import TabuSearch
from src.distance_utils import DistanceCalculator, SolutionEvaluator
from visualization.plotter import RouteVisualizer

# 1. Load problem
problem = DataLoader.load_problem("data/data101.vrp")
print(f"Problem: {problem.name}")
print(f"Clients: {problem.num_clients}, Capacity: {problem.capacity}")

# 2. Solve with GA
print("\nSolving with Genetic Algorithm...")
ga = GeneticAlgorithm(
    problem.depot,
    problem.clients,
    problem.capacity,
    population_size=50,
    generations=100
)
ga_solution = ga.evolve(verbose=True)

# 3. Solve with TS
print("\nSolving with Tabu Search...")
ts = TabuSearch(
    problem.depot,
    problem.clients,
    problem.capacity,
    max_iterations=1000
)
ts_solution = ts.search(verbose=True)

# 4. Evaluate and compare
print("\n" + "="*60)
print("COMPARISON")
print("="*60)

ga_distance = DistanceCalculator.solution_distance(ga_solution)
ts_distance = DistanceCalculator.solution_distance(ts_solution)

ga_feasible = SolutionEvaluator.is_feasible(ga_solution, problem.clients)
ts_feasible = SolutionEvaluator.is_feasible(ts_solution, problem.clients)

print(f"GA: Distance={ga_distance:.2f}, Vehicles={ga_solution.get_num_vehicles()}, Feasible={ga_feasible}")
print(f"TS: Distance={ts_distance:.2f}, Vehicles={ts_solution.get_num_vehicles()}, Feasible={ts_feasible}")

winner = "GA" if ga_distance < ts_distance else "TS"
print(f"Winner: {winner}")

# 5. Visualize
viz = RouteVisualizer()
viz.plot_comparison(
    ga_solution,
    ts_solution,
    "GA Solution",
    "TS Solution",
    "results/comparison.png"
)

# 6. Analyze convergence
viz.plot_convergence(ga.generation_history, "GA", "results/ga_convergence.png")
viz.plot_convergence(ts.best_history, "TS", "results/ts_convergence.png")
```

---

## 📞 Support

**For technical questions**, see `TECHNICAL_DOCUMENTATION.md` which contains:
- Detailed algorithm explanations
- Design decisions and rationale
- Complexity analysis
- Performance optimization tips
- Troubleshooting guide

**For code questions**, check docstrings in source files:
```python
from src.genetic_algorithm import GeneticAlgorithm
help(GeneticAlgorithm)  # Print class documentation
help(GeneticAlgorithm.evolve)  # Print method documentation
```

---

## 📄 License

This project is provided for educational purposes.

---

## 🙏 Acknowledgments

This implementation is based on:
- Solomon's VRPTW benchmarks
- Classical GA and TS literature
- Best practices in metaheuristic optimization

---

## 🎯 Next Steps

1. **Try different problems**: Explore `data/` directory
2. **Tune parameters**: Experiment with GA/TS settings
3. **Extend code**: Add new neighborhood operators or selection methods
4. **Analyze results**: Study what works best for different problem types
5. **Parallelize**: Implement parallel population evaluation in GA
6. **Hybrid approaches**: Combine GA and TS for better results

---

**Happy solving! 🚀**