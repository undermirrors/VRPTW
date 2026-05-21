# RAPPORT - Optimisation Discrète : VRP / VRPTW

**Auteurs :** Thibaut LARACINE, Louka PESIC  
**Date :** Juin 2024  
**Cours :** Optimisation Discrète - Filière Informatique  
**Professeur :** Stéphane Bonnevay - Polytech Lyon  

## 1. Introduction

Le Vehicle Routing Problem with Time Windows (VRPTW) est un problème d'optimisation combinatoire dans lequel une flotte de véhicules doit servir un ensemble de clients en minimisant la distance totale, tout en respectant des contraintes de capacité et des fenêtres de temps associées à chaque client [cite:20]. Cette étude compare deux métaheuristiques, l'Algorithme Génétique (GA) et la Recherche Tabou (TS), sur 10 instances de benchmark Solomon, d'abord en mode VRP sans fenêtres de temps, puis en mode VRPTW avec fenêtres de temps actives [cite:20].

L'objectif est double : mesurer l'impact des fenêtres de temps sur la difficulté du problème et comparer la qualité des solutions produites par les deux approches [cite:20]. Les expériences ont été conduites sur les instances data101, data102, data1101, data1102, data111, data112, data1201, data1202, data201 et data202, qui couvrent des cas à capacité 200 et 1000, avec fenêtres courtes, longues ou mixtes [cite:20].

## 2. Protocole expérimental

Les expériences suivent le protocole du rapport initial : une phase VRP où les fenêtres de temps sont ignorées, puis une phase VRPTW où elles sont prises en compte, avec comparaison de la distance, du nombre de véhicules, de la faisabilité et du temps d'exécution [cite:20]. La faisabilité est un critère de validité indispensable en mode VRPTW, car une solution infaisable n'a pas de valeur opérationnelle même si sa distance est faible [cite:20].

Le critère de comparaison retenu est le suivant : priorité à la faisabilité, puis au nombre de véhicules, puis à la distance totale [cite:20]. Cette hiérarchie est cohérente avec le rôle central de la faisabilité dans le protocole et avec l'analyse méthodologique du rapport initial, qui insiste sur la nécessité de traiter les contraintes temporelles comme des contraintes dures [cite:20].

## 3. Résultats en mode VRP

En mode VRP, les résultats sont relativement équilibrés entre GA et TS, avec des victoires réparties selon la structure des instances. TS gagne sur data101, data102, data111 et data112, tandis que GA l'emporte sur data1101, data1102, data1201, data1202, data201 et data202.

| Problem | GA Dist | GA K | TS Dist | TS K | Winner |
|---|---:|---:|---:|---:|---|
| data101 | 1099.55 | 8 | 971.88 | 8 | TS |
| data102 | 1111.67 | 8 | 953.13 | 8 | TS |
| data1101 | 1212.16 | 9 | 1288.66 | 9 | GA |
| data1102 | 1236.53 | 9 | 1237.05 | 9 | GA |
| data111 | 1098.85 | 8 | 974.53 | 8 | TS |
| data112 | 1091.73 | 8 | 970.24 | 8 | TS |
| data1201 | 768.65 | 2 | 864.62 | 2 | GA |
| data1202 | 779.91 | 2 | 861.14 | 2 | GA |
| data201 | 792.74 | 2 | 801.16 | 2 | GA |
| data202 | 794.16 | 2 | 802.73 | 2 | GA |

Le bilan global en VRP est donc de 6 victoires pour GA contre 4 pour TS. TS est particulièrement performant sur plusieurs instances à capacité 200, alors que GA se montre meilleur sur les instances à forte capacité, en particulier lorsque seulement 2 véhicules suffisent.

## 4. Résultats en mode VRPTW

En mode VRPTW, les deux algorithmes produisent des solutions faisables sur les 10 instances, ce qui constitue un résultat important au regard de l'objectif de validité expérimentale [cite:20]. En revanche, l'activation des fenêtres de temps augmente fortement le nombre de véhicules et la distance totale sur la plupart des instances, ce qui confirme que les contraintes temporelles réduisent fortement la liberté de routage [cite:20].

| Problem | GA Dist | GA K | GA Feas | TS Dist | TS K | TS Feas | Winner |
|---|---:|---:|---|---:|---:|---|---|
| data101 | 2493.15 | 33 | True | 1910.07 | 24 | True | TS |
| data102 | 2228.48 | 27 | True | 1721.81 | 23 | True | TS |
| data1101 | 2540.35 | 25 | True | 2010.86 | 21 | True | TS |
| data1102 | 2495.57 | 22 | True | 1863.16 | 21 | True | TS |
| data111 | 1627.57 | 18 | True | 1393.13 | 17 | True | TS |
| data112 | 1179.48 | 12 | True | 1128.20 | 13 | True | GA |
| data1201 | 2394.63 | 12 | True | 2011.19 | 14 | True | GA |
| data1202 | 2079.93 | 11 | True | 1591.31 | 12 | True | GA |
| data201 | 2134.75 | 12 | True | 1454.04 | 14 | True | GA |
| data202 | 1853.78 | 12 | True | 1374.12 | 14 | True | GA |

Le bilan est parfaitement partagé : 5 victoires pour TS et 5 pour GA. TS domine sur les cinq premières instances, tandis que GA l'emporte sur les cinq dernières, ce qui montre qu'aucune des deux métaheuristiques n'est universellement supérieure en présence de contraintes temporelles.

## 5. Impact des fenêtres de temps

Le passage du mode VRP au mode VRPTW augmente très fortement le nombre de véhicules utilisés sur presque toutes les instances. Par exemple, data101 passe de 8 véhicules à 33 pour GA et 24 pour TS, tandis que data201 passe de 2 véhicules à 12 pour GA et 14 pour TS.

Cette hausse confirme l'hypothèse de départ du rapport, selon laquelle les fenêtres de temps réduisent fortement les possibilités de mutualisation des clients dans une même tournée [cite:20]. En pratique, l'algorithme ne peut plus seulement optimiser la géométrie des trajets ; il doit aussi préserver la compatibilité temporelle entre les visites, ce qui fragmente les routes et augmente la distance totale [cite:20].

## 6. Analyse comparative GA vs TS

### 6.1 Mode VRP

En VRP, TS obtient souvent de meilleures distances sur les instances à capacité 200, ce qui suggère que sa recherche locale est très efficace lorsque le problème reste structuré principalement par la distance. À l'inverse, GA est meilleur sur les instances à grande capacité, où la structure globale des routes semble plus stable et mieux exploitée par une approche populationnelle.

### 6.2 Mode VRPTW

En VRPTW, les deux algorithmes restent faisables sur l'ensemble des cas testés, ce qui montre qu'un traitement strict de la faisabilité permet d'éviter les dérives décrites dans le rapport initial pour la Recherche Tabou [cite:20]. Les performances se scindent néanmoins en deux groupes : TS domine clairement sur data101 à data111, tandis que GA devient meilleur sur data112 à data202.

Ce résultat nuance fortement les hypothèses initiales du rapport, qui anticipaient une supériorité nette de GA en faisabilité et une fréquence plus élevée de solutions infaisables pour TS [cite:20]. Dans l'état actuel de l'implémentation, ce n'est plus la faisabilité qui différencie les algorithmes, mais surtout leur capacité à réduire simultanément distance et nombre de véhicules selon le type d'instance.

## 7. Interprétation par familles d'instances

### 7.1 Instances à capacité 200

Les instances data101, data102, data1101, data1102, data111 et data112 montrent une forte sensibilité à la structure spatio-temporelle. TS domine sur cinq de ces six instances en VRPTW, ce qui laisse penser que sa recherche locale est très performante lorsque les améliorations viennent principalement du réordonnancement fin des tournées.

### 7.2 Instances à capacité 1000

Sur data1201, data1202, data201 et data202, GA est systématiquement meilleur en VRPTW. Cela suggère qu'avec une capacité élevée, la difficulté ne vient plus seulement du placement local des clients mais aussi de l'organisation globale des grandes tournées, terrain sur lequel GA semble mieux se comporter.

### 7.3 Observations générales

Le comportement des deux algorithmes dépend donc fortement des caractéristiques de l'instance. TS n'est pas simplement un algorithme plus rapide mais plus fragile ; dans ces résultats, il est compétitif et même meilleur sur plusieurs familles d'instances, à condition que la faisabilité soit correctement filtrée et maintenue [cite:20].

## 8. Discussion méthodologique

Le rapport initial prévoyait une forte asymétrie entre GA et TS en matière de faisabilité, avec un besoin potentiel de mécanismes de restauration pour TS [cite:20]. Les résultats obtenus ici montrent qu'après correction des opérateurs et mise en place d'une logique feasibility-first, les deux méthodes peuvent conserver une faisabilité complète sur les 10 instances.

Cette évolution change l'interprétation globale : la question n'est plus seulement de savoir quel algorithme évite les solutions infaisables, mais lequel exploite le mieux la structure du problème sous contraintes temporelles. Les résultats actuels indiquent donc une confrontation plus équilibrée et plus intéressante scientifiquement que celle envisagée dans la version initiale du rapport [cite:20].

## 9. Conclusion

Les expériences menées sur 10 instances montrent que l'Algorithme Génétique et la Recherche Tabou sont tous deux capables de produire des solutions faisables en mode VRPTW, ce qui valide l'approche expérimentale choisie [cite:20]. En mode VRP, GA remporte 6 instances contre 4 pour TS, tandis qu'en mode VRPTW le bilan est parfaitement équilibré avec 5 victoires chacun.

Le principal enseignement est que l'effet des fenêtres de temps est massif : augmentation du nombre de véhicules, hausse importante des distances et changement de hiérarchie entre les algorithmes selon les familles d'instances [cite:20]. Il n'existe donc pas de métaheuristique universellement dominante ; le choix entre GA et TS dépend de la structure de l'instance, en particulier de la capacité des véhicules et de la rigidité temporelle des visites.

Une perspective naturelle serait d'explorer une approche hybride, combinant l'exploration globale de GA et l'exploitation locale de TS, comme le suggérait déjà le rapport initial [cite:20]. Une telle combinaison pourrait permettre de conserver la robustesse de GA tout en profitant de la capacité de raffinement local de TS sur les instances où celui-ci est particulièrement performant [cite:20].
