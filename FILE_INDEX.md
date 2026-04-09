# VRPTW Project - File Index & Navigation Guide

## 📌 Quick Navigation

**Getting Started:**
- `README.md` - Start here! Full project overview
- `QUICKSTART.md` - 5-minute setup guide
- `test_installation.py` - Verify installation works

**Run Code:**
- `src/main.py` - Full experiment runner
- `example_usage.py` - 8 detailed examples
- `test_installation.py` - Installation verification

**Learn More:**
- `TECHNICAL_DOCUMENTATION.md` - Deep dive into algorithms
- `IMPLEMENTATION_SUMMARY.md` - What was built and why

---

## 📁 Project Structure & File Descriptions

### Root Level Files

```
VRPTW/
├── README.md (650 lines)
│   └─ Full project overview, quick start, examples, troubleshooting
│
├── QUICKSTART.md (278 lines)
│   └─ 5-minute setup, common commands, parameters, examples
│
├── TECHNICAL_DOCUMENTATION.md (807 lines)
│   └─ Algorithm details, design decisions, complexity analysis
│
├── IMPLEMENTATION_SUMMARY.md (624 lines)
│   └─ What was built, architecture decisions, performance metrics
│
├── FILE_INDEX.md (this file)
│   └─ Navigation guide and file reference
│
├── requirements.txt
│   └─ Python package dependencies (numpy, matplotlib, pandas, scipy, folium)
│
├── test_installation.py (284 lines)
│   └─ Automated verification of installation (6 comprehensive tests)
│
└── example_usage.py (364 lines)
    └─ 8 detailed usage examples (basic to advanced)
```

### Source Code: `src/` Directory

```
src/
├── __init__.py (78 lines)
│   └─ Package initialization, exports all classes/functions
│
├── models.py (302 lines) ⭐ CORE DATA STRUCTURES
│   ├─ Location: Geographic coordinates
│   ├─ TimeWindow: Service availability [ready_time, due_time]
│   ├─ Client: Customer with demand & time window
│   ├─ Depot: Central facility
│   ├─ Route: Single vehicle route with feasibility checking
│   └─ Solution: Multi-vehicle solution container
│
├── data_loader.py (189 lines) ⭐ PROBLEM LOADING
│   ├─ VRPTProblem: Problem instance container
│   └─ DataLoader: Parse .vrp files and load problems
│
├── distance_utils.py (177 lines) ⭐ SOLUTION EVALUATION
│   ├─ DistanceCalculator: Distance computations & delta evaluation
│   └─ SolutionEvaluator: Feasibility checking, quality metrics
│
├── solution_generator.py (293 lines) ⭐ INITIAL SOLUTIONS
│   ├─ SolutionGenerator.generate_random_solution()
│   ├─ SolutionGenerator.nearest_neighbor()
│   ├─ SolutionGenerator.greedy_insertion()
│   ├─ SolutionGenerator.savings_algorithm()
│   └─ SolutionGenerator.multi_start_nearest_neighbor()
│
├── neighborhood.py (352 lines) ⭐ LOCAL SEARCH OPERATORS
│   ├─ NeighborhoodOperator: Base class
│   ├─ TwoOpt: 2-edge exchange
│   ├─ OrOpt: Sequence relocation (1, 2, 3 clients)
│   ├─ Relocate: Single client movement with best-improvement
│   ├─ CrossExchange: Inter-route client swap
│   ├─ TwoOptBetweenRoutes: Segment exchange between routes
│   └─ NeighborhoodManager: Unified operator interface
│
├── genetic_algorithm.py (338 lines) 🧬 METAHEURISTIC #1
│   ├─ GeneticAlgorithm: Population-based evolutionary algorithm
│   ├─ Components:
│   │  ├─ Tournament selection
│   │  ├─ 3 crossover types (route, order, segment)
│   │  ├─ Neighborhood-based mutation
│   │  ├─ Elitism (keep best solutions)
│   │  └─ Convergence tracking
│   └─ Customizable: pop size, generations, crossover/mutation rates
│
├── tabu_search.py (301 lines) 🔍 METAHEURISTIC #2
│   ├─ TabuSearch: Memory-enhanced local search
│   ├─ TabuAttribute: Move memory management
│   ├─ Components:
│   │  ├─ Adaptive tabu tenure (auto-calculated)
│   │  ├─ Aspiration criteria
│   │  ├─ Best-improvement neighborhood exploration
│   │  ├─ Diversification (escape local optima)
│   │  ├─ Intensification (improve good solutions)
│   │  └─ Search history tracking
│   └─ Customizable: iterations, neighborhood size, diversification frequency
│
└── main.py (320 lines) ⭐ EXPERIMENT ORCHESTRATION
    ├─ VRPTPExperiment: Batch problem solving & comparison
    ├─ Features:
    │  ├─ Load all problems from data/ directory
    │  ├─ Solve with both GA and TS
    │  ├─ Detailed result comparisons
    │  ├─ Summary statistics
    │  ├─ JSON export
    │  └─ Problem limiting for quick tests
    └─ Functions:
        ├─ load_problems()
        ├─ solve_with_genetic_algorithm()
        ├─ solve_with_tabu_search()
        ├─ solve_problem()
        ├─ run_experiments()
        └─ save_results()
```

### Visualization: `visualization/` Directory

```
visualization/
├── __init__.py (12 lines)
│   └─ Package initialization
│
└── plotter.py (387 lines) 🎨 VISUALIZATION MODULE
    ├─ RouteVisualizer: Professional route & performance visualization
    ├─ Route Visualization:
    │  ├─ plot_solution(): Single solution with all routes
    │  ├─ plot_comparison(): Two solutions side-by-side
    │  ├─ Color-coded routes, client markers, direction arrows
    │  └─ Optional time window & demand annotations
    ├─ Algorithm Analysis:
    │  ├─ plot_convergence(): Fitness history over iterations
    │  └─ plot_execution_time_comparison(): Speed comparison
    ├─ Performance Comparison:
    │  ├─ plot_distance_comparison(): Distance by problem
    │  ├─ plot_vehicles_comparison(): Vehicle count by problem
    │  └─ plot_execution_time_comparison(): Time by problem
    └─ Features:
        ├─ Custom figure sizes and resolution
        ├─ Automatic color generation for routes
        ├─ Legend with route statistics
        └─ Save to file option
```

### Data Directory: `data/`

```
data/
├── data101.vrp (100 clients, capacity 200)
├── data102.vrp (100 clients, capacity 200)
├── data111.vrp (100 clients, capacity 200)
├── data112.vrp (100 clients, capacity 200)
├── data201.vrp (200 clients, capacity 200)
├── data202.vrp (200 clients, capacity 200)
├── data1101.vrp (100 clients, capacity 1000)
├── data1102.vrp (100 clients, capacity 1000)
├── data1201.vrp (200 clients, capacity 1000)
└── data1202.vrp (200 clients, capacity 1000)

Format: Solomon VRPTW benchmark format (.vrp)
- Problem metadata (name, client count, vehicle capacity)
- Depot location and time window
- Client locations, demands, and time windows
```

### Results Directory: `results/`

```
results/
├── results.json (auto-generated)
│   └─ Complete experiment results in JSON format
│       ├─ Per-problem results
│       ├─ GA performance metrics
│       ├─ TS performance metrics
│       ├─ Feasibility status
│       └─ Solution statistics
│
├── *.png (auto-generated, optional)
│   ├─ solution_*.png: Route visualizations
│   ├─ convergence_*.png: Algorithm convergence curves
│   ├─ comparison_*.png: Algorithm comparisons
│   ├─ distance_comparison.png: Distance across problems
│   ├─ vehicles_comparison.png: Vehicle count across problems
│   └─ time_comparison.png: Execution time across problems
```

---

## 📊 Code Statistics

### Lines of Code
| Component | Lines | Purpose |
|-----------|-------|---------|
| models.py | 302 | Data structures |
| data_loader.py | 189 | Problem loading |
| distance_utils.py | 177 | Solution evaluation |
| solution_generator.py | 293 | Initial solutions |
| neighborhood.py | 352 | Local search moves |
| genetic_algorithm.py | 338 | GA metaheuristic |
| tabu_search.py | 301 | TS metaheuristic |
| main.py | 320 | Experiment orchestration |
| visualization/plotter.py | 387 | Route visualization |
| **Total Core** | **2,659** | **Algorithms & logic** |
| example_usage.py | 364 | Examples |
| test_installation.py | 284 | Installation tests |
| **Total Utilities** | **648** | **Testing & examples** |

### Documentation
| File | Lines | Purpose |
|------|-------|---------|
| README.md | 650 | Full overview & guide |
| TECHNICAL_DOCUMENTATION.md | 807 | Deep technical details |
| QUICKSTART.md | 278 | Quick start guide |
| IMPLEMENTATION_SUMMARY.md | 624 | Design & implementation |
| FILE_INDEX.md | this | Navigation guide |

### Total Project
- **Code:** ~3,300 LOC
- **Documentation:** ~2,400 LOC
- **Tests:** 6 comprehensive tests
- **Examples:** 8 detailed scenarios

---

## 🚀 How to Use This Index

### If You Want To...

**Get Started Immediately**
→ Read: `QUICKSTART.md`
→ Run: `python test_installation.py`
→ Execute: `python src/main.py`

**Understand the Project**
→ Read: `README.md` (overview)
→ Read: `IMPLEMENTATION_SUMMARY.md` (what was built)

**Learn Algorithm Details**
→ Read: `TECHNICAL_DOCUMENTATION.md`
→ Browse: `src/genetic_algorithm.py`, `src/tabu_search.py`

**See Code Examples**
→ Run: `python example_usage.py`
→ Browse: `example_usage.py` (8 scenarios)

**Understand Data Structures**
→ Read: `src/models.py` (commented, ~10 lines per class)
→ Read: `src/data_loader.py` (understand VRP format)

**Learn Neighborhood Operators**
→ Read: `src/neighborhood.py` (6 operators documented)

**Visualize Solutions**
→ See: `visualization/plotter.py` (10+ visualization types)
→ Example: `example_usage.py` → example_8_visualize_solution()

**Modify Parameters**
→ See: `QUICKSTART.md` → "Customize Algorithm Parameters"
→ Edit: `src/main.py` or create custom script

**Extend the Project**
→ Read: `IMPLEMENTATION_SUMMARY.md` → "Extension Opportunities"
→ Add new operator: Inherit from `NeighborhoodOperator` in `src/neighborhood.py`
→ Add new heuristic: Add method to `SolutionGenerator` in `src/solution_generator.py`

---

## 🔍 Key Classes & Their Locations

| Class | File | Purpose |
|-------|------|---------|
| **Data Models** | | |
| Location | models.py | Geographic coordinates |
| TimeWindow | models.py | Time constraints |
| Client | models.py | Customer representation |
| Depot | models.py | Central facility |
| Route | models.py | Single vehicle route |
| Solution | models.py | Multi-vehicle solution |
| **Problem Loading** | | |
| VRPTProblem | data_loader.py | Problem instance |
| DataLoader | data_loader.py | File parsing |
| **Evaluation** | | |
| DistanceCalculator | distance_utils.py | Distance metrics |
| SolutionEvaluator | distance_utils.py | Quality assessment |
| **Construction** | | |
| SolutionGenerator | solution_generator.py | Initial solutions (5 methods) |
| **Local Search** | | |
| TwoOpt | neighborhood.py | 2-opt operator |
| OrOpt | neighborhood.py | Or-opt operator (1, 2, 3) |
| Relocate | neighborhood.py | 1-opt with best-improvement |
| CrossExchange | neighborhood.py | Inter-route swap |
| TwoOptBetweenRoutes | neighborhood.py | Segment exchange |
| NeighborhoodManager | neighborhood.py | Operator interface |
| **Algorithms** | | |
| GeneticAlgorithm | genetic_algorithm.py | GA solver |
| TabuSearch | tabu_search.py | TS solver |
| **Orchestration** | | |
| VRPTPExperiment | main.py | Batch runner |
| **Visualization** | | |
| RouteVisualizer | visualization/plotter.py | Plotting utilities |

---

## 📋 Common Tasks & File References

### Running Experiments
```
python src/main.py                    # Full experiments
python test_installation.py           # Verify setup
python example_usage.py               # See 8 examples
```

### Modifying GA Parameters
**File:** `src/main.py`
**Lines:** ~60-75 (solve_with_genetic_algorithm method)
**Or:** Create custom script using `GeneticAlgorithm` from `src/genetic_algorithm.py`

### Modifying TS Parameters
**File:** `src/main.py`
**Lines:** ~79-95 (solve_with_tabu_search method)
**Or:** Create custom script using `TabuSearch` from `src/tabu_search.py`

### Adding New Neighborhood Operator
**File:** `src/neighborhood.py`
**Lines:** Inherit from `NeighborhoodOperator` at end of file
**Register:** Add to `NeighborhoodManager.operators` list

### Adding New Construction Heuristic
**File:** `src/solution_generator.py`
**Lines:** Add static method to `SolutionGenerator` class
**Use:** Call from `GeneticAlgorithm.initialize_population()` or directly

### Creating Visualizations
**File:** `visualization/plotter.py`
**Class:** `RouteVisualizer`
**Methods:** `plot_solution()`, `plot_comparison()`, `plot_convergence()`, etc.
**Example:** `example_usage.py` lines 290-330

### Checking Solution Feasibility
**File:** `src/distance_utils.py`
**Class:** `SolutionEvaluator`
**Method:** `is_feasible()`, `get_constraint_violations()`, `get_solution_stats()`

---

## 🎓 Learning Path

**For Complete Beginners:**
1. Read: `README.md`
2. Run: `python test_installation.py`
3. Run: `python src/main.py` (first problem only)
4. Read: `QUICKSTART.md`

**For Algorithm Understanding:**
1. Read: `TECHNICAL_DOCUMENTATION.md`
2. Read: `src/genetic_algorithm.py` (with full docstrings)
3. Read: `src/tabu_search.py` (with full docstrings)
4. Read: `src/neighborhood.py` (understand operators)

**For Code Extension:**
1. Read: `IMPLEMENTATION_SUMMARY.md` → Extension Opportunities
2. Study: `src/neighborhood.py` (add new operator)
3. Study: `src/solution_generator.py` (add new heuristic)
4. Study: `src/main.py` (customize experiment runner)

**For Performance Optimization:**
1. Read: `TECHNICAL_DOCUMENTATION.md` → Performance Considerations
2. Modify: `src/main.py` algorithm parameters
3. Run: `example_usage.py` example 7 (quality vs speed)
4. Profile: Use Python's cProfile on your custom scripts

---

## ✅ Verification Checklist

- [ ] Virtual environment activated: `source .venv/bin/activate`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Installation verified: `python test_installation.py`
- [ ] Can load problems: `data/*.vrp` files present
- [ ] Can run experiments: `python src/main.py`
- [ ] Results saved: `results/results.json` created
- [ ] Examples work: `python example_usage.py`
- [ ] Documentation clear: Read `README.md` and `QUICKSTART.md`

---

## 📞 Quick Reference

| Need | File | Lines |
|------|------|-------|
| Overview | README.md | All |
| Quick Start | QUICKSTART.md | All |
| Deep Dive | TECHNICAL_DOCUMENTATION.md | All |
| Architecture | IMPLEMENTATION_SUMMARY.md | All |
| Data Structures | src/models.py | All |
| Problem Loading | src/data_loader.py | All |
| Solution Evaluation | src/distance_utils.py | All |
| Initial Solutions | src/solution_generator.py | All |
| Local Search | src/neighborhood.py | All |
| GA Algorithm | src/genetic_algorithm.py | All |
| TS Algorithm | src/tabu_search.py | All |
| Run Experiments | src/main.py | All |
| Visualizations | visualization/plotter.py | All |
| Examples | example_usage.py | All |
| Tests | test_installation.py | All |

---

**End of File Index**

This document provides complete navigation of the VRPTW project. For any specific task, find it in the "How to Use This Index" section and follow the references.