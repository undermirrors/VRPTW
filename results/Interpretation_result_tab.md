Oui — tes résultats montrent surtout que le réglage actuel favorise trop peu l’exploration pour le GA, et que le TS gagnerait probablement à être rendu plus adaptatif. En pratique, pour viser des résultats “exceptionnels”, il faut surtout élargir la recherche sur les hyperparamètres au lieu de rester sur un seul réglage fixe, ce qui est justement l’idée du tuning par grille, aléatoire ou bayésien. [larevueia](https://larevueia.fr/3-methodes-pour-optimiser-les-hyperparametres-de-vos-modeles-de-machine-learning/)

## Lecture rapide de tes résultats

Dans le VRP sans fenêtres de temps, le TS bat souvent le GA sur la distance, mais pas toujours sur le nombre de véhicules, et les écarts restent modestes sur certains cas. [thescipub](https://thescipub.com/pdf/ajassp.2010.95.101.pdf)
Dans le VRPTW, le TS semble globalement meilleur sur la distance, tandis que le GA obtient parfois moins de véhicules, ce qui suggère un compromis objectif-contraintes différent selon les instances. [sciencedirect](https://www.sciencedirect.com/science/article/abs/pii/S156849462401367X)
Autrement dit, ton problème n’est pas seulement “augmenter la performance”, mais choisir si tu optimises surtout la distance, le nombre de véhicules, ou un score combiné pénalisé. [dialoguesreview](https://dialoguesreview.com/index.php/2/article/download/1048/1023)

## Réglages GA à tester

Pour le GA, tes valeurs actuelles sont probablement un peu conservatrices pour un problème combinatoire dur comme le VRPTW, où la diversité de population et la pression de sélection jouent beaucoup. [mii](https://www.mii.lt/files/doc/lt/doktorantura/apgintos_disertacijos/mii_dis_2014_vaira.pdf)
Je testerais d’abord :

- Population size : 100, 200, 400.
- Generations : 300, 500, 1000.
- Crossover rate : 0.85 à 0.95.
- Mutation rate : 0.05 à 0.15, puis éventuellement mutation adaptative.
- Elite size : 1 ou 2, rarement plus.
- Tournament size : 2 ou 3, pas trop grand pour éviter une convergence prématurée.

La logique est simple : plus de population et plus de générations pour explorer, mais mutation un peu plus faible et sélection pas trop agressive pour éviter de bloquer le GA dans un optimum local. [ebrary.free](http://ebrary.free.fr/Genetic%20Algorithms%20Handbook/The_Practical_Handbook_of_GA,_v3_Complex_Coding_Systems,1999/2539ch9.pdf)

## Réglages TS à tester

Pour le Tabu Search, ton `tabu_tenure=None` est le point le plus suspect : il faut presque toujours une tenure explicite ou adaptative pour contrôler le retour cyclique. [pubsonline.informs](https://pubsonline.informs.org/doi/10.1287/ijoc.9.4.417)
Je testerais :

- Max iterations : 2000, 5000, 10000.
- Tabu tenure : 10, 15, 20, 30, ou adaptative.
- Neighborhood size : 200, 500, 1000.
- Aspiration criteria : True, à garder.
- Diversification : redémarrages, mémoire à long terme, ou tenure réactive.

Les travaux sur le TS pour VRPTW insistent justement sur la diversification, l’intensification et la variation dynamique de la tenure pour éviter les cycles et améliorer la qualité finale. [pubsonline.informs](https://pubsonline.informs.org/doi/10.1287/trsc.31.2.170)

## Stratégie de tuning efficace

Le plus rentable n’est pas un grid search exhaustif sur tout, mais un tuning en deux étages : d’abord large et peu coûteux, ensuite fin et ciblé. [aws.amazon](https://aws.amazon.com/fr/what-is/hyperparameter-tuning/)
Vu ton cas, une bonne stratégie serait :

1. Fixer une métrique unique d’évaluation, par exemple `distance + λ * nb_vehicules + pénalité_infeasibilité`.
2. Lancer un random search large sur 30 à 100 configurations.
3. Garder les 5 à 10 meilleures configurations.
4. Relancer avec plus d’itérations et plusieurs seeds.
5. Valider sur plusieurs instances et pas seulement sur une seule.

C’est souvent bien plus efficace que d’augmenter aveuglément le nombre de générations, même si tu acceptes 30 h d’exécution. [docs.cloud.google](https://docs.cloud.google.com/vertex-ai/docs/training/hyperparameter-tuning-overview?hl=fr)

## Recommandation concrète

Si tu veux un réglage “fort” pour commencer, je prendrais :

| Algorithme | Paramètres de départ |
|---|---|
| GA | population 200, générations 500, crossover 0.9, mutation 0.1, elite 1, tournament 2 ou 3 |
| TS | iterations 5000, tabu tenure 15 ou adaptative, neighborhood 500, aspiration True |

Pour le VRPTW, je ferais aussi deux versions du score : une qui favorise la distance, une autre qui pénalise fortement le nombre de véhicules, parce que tes résultats montrent que les deux algorithmes n’optimisent pas exactement la même chose. [dialoguesreview](https://dialoguesreview.com/index.php/2/article/download/1048/1023)
Si ton but est vraiment d’obtenir des résultats exceptionnels, la meilleure amélioration viendra probablement d’un **hybride** : GA pour explorer grossièrement, puis TS pour raffiner la meilleure solution. [leria-info.univ-angers](https://leria-info.univ-angers.fr/~jinkao.hao/papers/HeHaoWuJOC2025.pdf)

## Ce que je ferais ensuite

Je lancerais un plan d’expérimentation avec 20 à 50 seeds par configuration, puis je comparerais les distributions de résultats au lieu d’une seule exécution. [ibm](https://www.ibm.com/fr-fr/think/topics/hyperparameter-tuning)
Je peux te proposer juste après une grille de test précise, par exemple 24 ou 48 configurations, pensée pour tenir dans 30 heures d’exécution.