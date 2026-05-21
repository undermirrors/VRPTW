# Results
 
## TEST_1

```
GA_DEFAULT_POPULATION_SIZE = 50
GA_DEFAULT_GENERATIONS = 100
GA_DEFAULT_CROSSOVER_RATE = 0.8
GA_DEFAULT_MUTATION_RATE = 0.2
GA_DEFAULT_ELITE_SIZE = 2
GA_DEFAULT_TOURNAMENT_SIZE = 3
TS_DEFAULT_MAX_ITERATIONS = 1000
TS_DEFAULT_TABU_TENURE = None
TS_DEFAULT_NEIGHBORHOOD_SIZE = 100
TS_DEFAULT_ASPIRATION_CRITERIA = True
```

====================================================================================================
TABLEAU 2 : RESULTATS MODE VRP (sans fenetres de temps)
====================================================================================================
Problem           GA Dist   GA K      TS Dist   TS K       Winner
data101           1090.93      8      1005.67      8           TS
data102           1100.40      8      1003.37      8           TS
data1101          1231.42      9      1239.33      9           GA
data1102          1224.81      9      1234.05      9           GA
data111           1097.97      8       955.41      8           TS
data112           1104.71      8       928.88      8           TS
data1201           758.30      2       827.50      2           GA
data1202           776.91      2       832.01      2           GA
data201            800.91      2       802.73      2           GA
data202            801.18      2       802.73      2           GA

====================================================================================================
TABLEAU 3 : RESULTATS MODE VRPTW (avec fenetres de temps)
====================================================================================================
Problem           GA Dist   GA K    GA Feas      TS Dist   TS K    TS Feas               Winner
data101           2478.84     33       True      1886.31     23       True                   TS
data102           2279.57     27       True      1704.22     22       True                   TS
data1101          2459.94     25       True      1933.59     20       True                   TS
data1102          2479.21     22       True      1867.03     21       True                   TS
data111           1579.93     17       True      1317.30     17       True                   TS
data112           1232.12     12       True      1193.64     13       True                   GA
data1201          2411.84     12       True      1838.08     13       True                   GA
data1202          2050.96     11       True      1554.82     11       True                   TS
data201           2194.04     12       True      1465.96     13       True                   GA
data202           1791.14     12       True      1395.96     13       True                   GA

## TEST_2

```
GA_DEFAULT_POPULATION_SIZE = 200
GA_DEFAULT_GENERATIONS = 1000
GA_DEFAULT_CROSSOVER_RATE = 0.90
GA_DEFAULT_MUTATION_RATE = 0.05
GA_DEFAULT_ELITE_SIZE = 1
GA_DEFAULT_TOURNAMENT_SIZE = 3
TS_DEFAULT_MAX_ITERATIONS = 2500
TS_DEFAULT_TABU_TENURE = 15
TS_DEFAULT_NEIGHBORHOOD_SIZE = 250
TS_DEFAULT_ASPIRATION_CRITERIA = True
```

Blocage trop rapide : 
--- data101 | Mode VRP ---
GA (VRP): Starting evolution with 200 individuals for 1000 generations
 Gen 100: best vehicles = 8, best distance = 1091.33
 Gen 200: best vehicles = 8, best distance = 1079.41
 Gen 300: best vehicles = 8, best distance = 1075.57
 Gen 400: best vehicles = 8, best distance = 1075.57
 Gen 500: best vehicles = 8, best distance = 1075.44
 Gen 600: best vehicles = 8, best distance = 1075.44
 Gen 700: best vehicles = 8, best distance = 1075.44
 Gen 800: best vehicles = 8, best distance = 1075.44
 Gen 900: best vehicles = 8, best distance = 1075.44
 Gen 1000: best vehicles = 8, best distance = 1075.44

Donc modification des hyperparamètres pour essayer de casser la convergence prématurée :

```
GA_DEFAULT_POPULATION_SIZE = 400
GA_DEFAULT_GENERATIONS = 1000
GA_DEFAULT_CROSSOVER_RATE = 0.90
GA_DEFAULT_MUTATION_RATE = 0.08
GA_DEFAULT_ELITE_SIZE = 1
GA_DEFAULT_TOURNAMENT_SIZE = 2
TS_DEFAULT_MAX_ITERATIONS = 2500
TS_DEFAULT_TABU_TENURE = 15
TS_DEFAULT_NEIGHBORHOOD_SIZE = 250
TS_DEFAULT_ASPIRATION_CRITERIA = True
```

Le passage à population = 400 et tournament = 2 aide souvent à casser la convergence prématurée, tandis que mutation = 0.08 réinjecte un peu plus de nouveauté sans rendre l’évolution chaotique.
Côté TS, neighborhood = 500 te donne plus d’options locales sans aller directement au coût maximal de 1000.
Cependant, ça dure trop longtemps pour les deux méthodes, on va modifier les hyperparamètres pour réduire le temps d’exécution tout en essayant de maintenir une bonne qualité de solution :
```
GA_DEFAULT_POPULATION_SIZE = 400
GA_DEFAULT_GENERATIONS = 500
GA_DEFAULT_CROSSOVER_RATE = 0.90
GA_DEFAULT_MUTATION_RATE = 0.08
GA_DEFAULT_ELITE_SIZE = 1
GA_DEFAULT_TOURNAMENT_SIZE = 2
TS_DEFAULT_MAX_ITERATIONS = 2000
TS_DEFAULT_TABU_TENURE = 10
TS_DEFAULT_NEIGHBORHOOD_SIZE = 150
TS_DEFAULT_ASPIRATION_CRITERIA = True
```


## TEST_3

GA: Evolution complete. Best vehicles: 11, Best distance: 1605.25
TS (VRPTW): Starting search from distance 14.00
TS: Tabu tenure = 10, neighborhood = 150
 Iter 1634: No improvement for 401 iterations, stopping
TS: Search complete. Feasible : True, Best vehicles: 12, Best distance: 1266.23
GA -> dist=1605.25, K=11, feasible=True, time=157.01s
TS -> dist=1266.23, K=12, feasible=True, time=100.29s
Winner: GA

====================================================================================================
TABLEAU 2 : RESULTATS MODE VRP (sans fenetres de temps)
====================================================================================================
Problem           GA Dist   GA K      TS Dist   TS K       Winner
data101           1072.26      8       936.11      8           TS
data102           1064.82      8       943.98      8           TS
data1101          1191.41      9      1185.48      9           TS
data1102          1185.23      9      1252.44      9           GA
data111           1067.70      8       937.50      8           TS
data112           1064.89      8       910.91      8           TS
data1201           744.49      2       792.95      2           GA
data1202           745.48      2       762.43      2           GA
data201            764.20      2       795.73      2           GA
data202            764.80      2       800.66      2           GA

====================================================================================================
TABLEAU 3 : RESULTATS MODE VRPTW (avec fenetres de temps)
====================================================================================================
Problem           GA Dist   GA K    GA Feas      TS Dist   TS K    TS Feas               Winner
data101           2043.60     26       True      1792.60     24       True                   TS
data102           1958.14     22       True      1669.74     22       True                   TS
data1101          2298.05     23       True      1877.52     21       True                   TS
data1102          2216.75     20       True      1817.41     20       True                   TS
data111           1511.41     18       True      1342.16     17       True                   TS
data112           1165.72     12       True      1118.34     13       True                   GA
data1201          2242.06     12       True      1795.48     13       True                   GA
data1202          1948.61     10       True      1638.55     12       True                   GA
data201           1977.78     12       True      1516.68     14       True                   GA
data202           1605.25     11       True      1266.23     12       True                   GA

Résultats sauvegardés dans : C:\Users\louka\Documents\2 - Ecole\4A\opti discrète\VRPTW\results\comprehensive_results.json
Graphes sauvegardés dans : C:\Users\louka\Documents\2 - Ecole\4A\opti discrète\VRPTW\results\plots
Images des solutions sauvegardées dans : C:\Users\louka\Documents\2 - Ecole\4A\opti discrète\VRPTW\results\solutions

GA_DEFAULT_POPULATION_SIZE = 400
GA_DEFAULT_GENERATIONS = 500
GA_DEFAULT_CROSSOVER_RATE = 0.90
GA_DEFAULT_MUTATION_RATE = 0.08
GA_DEFAULT_ELITE_SIZE = 1
GA_DEFAULT_TOURNAMENT_SIZE = 2
TS_DEFAULT_MAX_ITERATIONS = 2000
TS_DEFAULT_TABU_TENURE = 10
TS_DEFAULT_NEIGHBORHOOD_SIZE = 150
TS_DEFAULT_ASPIRATION_CRITERIA = True