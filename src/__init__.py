"""
VRPTW - Vehicle Routing Problem with Time Windows Solver

This package provides implementations of Genetic Algorithm and Tabu Search
metaheuristics for solving the VRPTW optimization problem.

Main components:
- models: Data structures for the VRPTW problem
- data_loader: Problem file parser
- genetic_algorithm: GA metaheuristic
- tabu_search: TS metaheuristic
- neighborhood: Local search operators
- solution_generator: Initial solution construction heuristics
- distance_utils: Distance calculations and evaluation metrics
"""

__version__ = "1.0.0"
__author__ = "VRPTW Project"

from .models import (
    Location,
    TimeWindow,
    Client,
    Depot,
    Route,
    Solution,
)

from .data_loader import (
    DataLoader,
    VRPTProblem,
)

from .distance_utils import (
    DistanceCalculator,
    SolutionEvaluator,
)

from .solution_generator import (
    SolutionGenerator,
)

from .neighborhood import (
    NeighborhoodOperator,
    TwoOpt,
    OrOpt,
    Relocate,
    CrossExchange,
    TwoOptBetweenRoutes,
    NeighborhoodManager,
)

from .genetic_algorithm import GeneticAlgorithm

from .tabu_search import TabuSearch

__all__ = [
    'Location',
    'TimeWindow',
    'Client',
    'Depot',
    'Route',
    'Solution',
    'DataLoader',
    'VRPTProblem',
    'DistanceCalculator',
    'SolutionEvaluator',
    'SolutionGenerator',
    'NeighborhoodOperator',
    'TwoOpt',
    'OrOpt',
    'Relocate',
    'CrossExchange',
    'TwoOptBetweenRoutes',
    'NeighborhoodManager',
    'GeneticAlgorithm',
    'TabuSearch',
]
