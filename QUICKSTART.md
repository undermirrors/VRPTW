# VRPTW - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
cd VRPTW
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Run Experiments
```bash
python src/main.py
```

This will:
- Load all problems from `data/` directory
- Solve each with Genetic Algorithm and Tabu Search
- Print comparison results
- Save results to `results/results.json`

---

## 📝 Common Commands

### Run Full Experiment
```bash
python src/main.py
```

### Run Quick Demo (first 3 problems only)
```bash
python example_usage.py
```

### Solve Single Problem Programmatically
```python
from src.data_loader import DataLoader
from src.genetic_algorithm import GeneticAlgorithm
from src.distance_utils import DistanceCalculator

# Load problem
problem = DataLoader.load_problem("data/data101.vrp")

# Solve with GA
ga = GeneticAlgorithm(problem.depot, problem.clients, problem.capacity)
solution = ga.evolve(verbose=True)

# Check result
distance = DistanceCalculator.solution_distance(solution)
print(f"Distance: {distance:.2f}")
print(f"Vehicles: {solution.get_num_vehicles()}")
```

### Visualize Solution
```python
from visualization.plotter import RouteVisualizer

viz = RouteVisualizer()
viz.plot_solution(solution, "My Solution", save_path="results/solution.png")
```

---

## 📊 Understanding Results

Results are printed to console and saved to `results/results.json`

**Key Metrics:**
- **distance**: Total travel distance (lower = better)
- **num_vehicles**: Number of vehicles used (lower = better)  
- **execution_time**: Runtime in seconds
- **is_feasible**: Whether all constraints are satisfied

**Example Output:**
```
Problem: data101
Clients: 100, Capacity: 200
=====================================
Metric                GA               TS              
Total Distance        1234.56          1198.34         
Number of Vehicles    10               9               
Feasible              True             True            
Execution Time (s)    45.32            28.15           

Winner: Tabu Search (by distance)
```

---

## ⚙️ Customize Algorithm Parameters

### Genetic Algorithm
```python
ga = GeneticAlgorithm(
    depot=problem.depot,
    clients=problem.clients,
    capacity=problem.capacity,
    population_size=100,    # Larger = better quality, slower
    generations=200,        # More = better quality, slower
    crossover_rate=0.85,    # 0-1: probability of crossover
    mutation_rate=0.15,     # 0-1: probability of mutation
    elite_size=3            # Keep best N solutions
)
solution = ga.evolve(verbose=True)
```

### Tabu Search
```python
ts = TabuSearch(
    depot=problem.depot,
    clients=problem.clients,
    capacity=problem.capacity,
    max_iterations=2000,        # More iterations = better quality
    tabu_tenure=None,           # Auto-calculated, or set manually
    neighborhood_size=100,      # Neighbors to explore per iteration
    diversification_freq=50     # Diversify every N iterations
)
solution = ts.search(verbose=True)
```

---

## 🎨 Quality vs Speed Trade-off

### Fast (< 30 seconds)
```python
ga = GeneticAlgorithm(..., population_size=30, generations=30)
ts = TabuSearch(..., max_iterations=300)
```

### Balanced (30-120 seconds)
```python
ga = GeneticAlgorithm(..., population_size=50, generations=100)
ts = TabuSearch(..., max_iterations=1000)
```

### High Quality (> 2 minutes)
```python
ga = GeneticAlgorithm(..., population_size=100, generations=200)
ts = TabuSearch(..., max_iterations=2000)
```

---

## 🔍 Solve Multiple Problems

```python
from src.data_loader import DataLoader
from src.tabu_search import TabuSearch
from src.distance_utils import DistanceCalculator

# Load all problems
problems = DataLoader.load_all_problems("data")

# Solve first 5
for problem in problems[:5]:
    ts = TabuSearch(problem.depot, problem.clients, problem.capacity)
    solution = ts.search(verbose=False)
    distance = DistanceCalculator.solution_distance(solution)
    print(f"{problem.name}: {distance:.2f}")
```

---

## 📈 Compare GA vs TS

```python
from src.genetic_algorithm import GeneticAlgorithm
from src.tabu_search import TabuSearch
from src.distance_utils import DistanceCalculator

problem = DataLoader.load_problem("data/data101.vrp")

# GA
ga = GeneticAlgorithm(problem.depot, problem.clients, problem.capacity)
ga_sol = ga.evolve(verbose=False)
ga_dist = DistanceCalculator.solution_distance(ga_sol)

# TS
ts = TabuSearch(problem.depot, problem.clients, problem.capacity)
ts_sol = ts.search(verbose=False)
ts_dist = DistanceCalculator.solution_distance(ts_sol)

print(f"GA: {ga_dist:.2f}")
print(f"TS: {ts_dist:.2f}")
print(f"Winner: {'GA' if ga_dist < ts_dist else 'TS'}")
```

---

## 📁 Project Structure

```
VRPTW/
├── src/                    # Optimization algorithms
│   ├── main.py            # Run experiments
│   ├── genetic_algorithm.py
│   ├── tabu_search.py
│   ├── neighborhood.py    # Local search operators
│   └── ...
├── visualization/          # Plotting module
│   └── plotter.py
├── data/                  # Problem instances (.vrp files)
├── results/               # Output (results.json, plots)
├── TECHNICAL_DOCUMENTATION.md
└── example_usage.py
```

---

## 🎯 Next Steps

1. **Run experiments**: `python src/main.py`
2. **Check results**: Look at `results/results.json`
3. **Visualize**: Use `RouteVisualizer` to plot solutions
4. **Tune**: Modify GA/TS parameters for better results
5. **Extend**: Add new neighborhood operators or algorithms
6. **Read**: See `TECHNICAL_DOCUMENTATION.md` for deep dive

---

## ❓ Common Issues

**ModuleNotFoundError**
```bash
cd VRPTW
source .venv/bin/activate
python src/main.py
```

**FileNotFoundError for data**
- Make sure you're in the VRPTW directory
- Check data files exist: `ls data/*.vrp`

**Very slow?**
- Reduce iterations: `generations=50` instead of 100
- Reduce population: `population_size=30` instead of 50
- Test on fewer problems: `problem_limit=1`

**Solution infeasible?**
- Increase iterations (algorithm didn't run long enough)
- Try different initial solution method
- Check if problem is solvable

---

## 📚 Documentation

- **README.md** - Full project overview
- **TECHNICAL_DOCUMENTATION.md** - Algorithm details, design decisions, complexity analysis
- **example_usage.py** - 8 detailed examples you can run
- **Code docstrings** - Every class and function documented

---

## 🏃 Ultra-Quick Test

```bash
cd VRPTW
source .venv/bin/activate
python -c "
from src.data_loader import DataLoader
from src.genetic_algorithm import GeneticAlgorithm
from src.distance_utils import DistanceCalculator

problem = DataLoader.load_problem('data/data101.vrp')
ga = GeneticAlgorithm(problem.depot, problem.clients, problem.capacity, 
                     population_size=20, generations=10)
sol = ga.evolve()
print(f'Distance: {DistanceCalculator.solution_distance(sol):.2f}')
"
```

---

**Ready to solve VRPTW problems? Start with `python src/main.py`! 🚀**