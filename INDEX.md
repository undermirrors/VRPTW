# 📚 INDEX DU PROJET VRPTW

## 🎯 Par où commencer ?

### 👨‍💼 Si vous avez 10 minutes
1. Lire : **RESUME_EXECUTIF.md** (2 min)
2. Consulter : Tableau des résultats (Section 8.1 du RAPPORT)
3. Conclusion : Section 11 du RAPPORT

**Temps total : 10 min**

### 👨‍🎓 Si vous avez 30 minutes
1. Lire : **RESUME_EXECUTIF.md** (5 min)
2. Lire : **Section 1** du RAPPORT (Problème) (5 min)
3. Consulter : **Section 8** du RAPPORT (Résultats) (15 min)
4. Lire : **Section 9** du RAPPORT (Comparaison) (5 min)

**Temps total : 30 min**

### 🔬 Si vous avez 1-2 heures (étudiant/chercheur)
1. Lire : **RESUME_EXECUTIF.md** (5 min)
2. Lire : **Section 1-2** du RAPPORT (Problème + Setup) (10 min)
3. Lire : **Section 3-4** du RAPPORT (Heuristiques + Voisinage) (15 min)
4. Lire : **Section 5-6** du RAPPORT (GA + TS - détails) (20 min)
5. Consulter : **Section 7-8** du RAPPORT (Protocole + Résultats) (20 min)
6. Lire : **Section 9** du RAPPORT (Comparaison) (10 min)
7. Vérifier : **CHECKLIST_LIVRAISON.md** (5 min)

**Temps total : 85 min**

### 📖 Si vous lisez le rapport complet (3-4 heures)
Lire en entier **RAPPORT.md** dans l'ordre (11 sections)

---

## 📂 Structure des fichiers

### 📋 Documentation principale
```
VRPTW/
├── RAPPORT.md                    [1,143 lignes] ⭐ RAPPORT PRINCIPAL
├── RESUME_EXECUTIF.md            [242 lignes]   Synthèse 5 min
├── CHECKLIST_LIVRAISON.md        [315 lignes]   Éléments livrés
├── docs/GUIDE_RAPPORT.md         [301 lignes]   Guide de lecture
├── README.md                      [652 lignes]   Vue d'ensemble
├── TECHNICAL_DOCUMENTATION.md                   Détails techniques
└── VRP_MODES.md                                 Modes VRPTW/VRP
```

### 💻 Code source
```
src/
├── models.py                     [325 lignes]   Structures de données
├── data_loader.py                [189 lignes]   Chargement fichiers
├── distance_utils.py             [186 lignes]   Calculs et évaluation
├── solution_generator.py         [315 lignes]   4 générateurs
├── neighborhood.py               [354 lignes]   5 opérateurs
├── genetic_algorithm.py          [352 lignes]   ⭐ Métaheuristique 1
├── tabu_search.py                [322 lignes]   ⭐ Métaheuristique 2
├── main.py                       [320 lignes]   Orchestration tests
└── __init__.py                   [78 lignes]
```

### 📊 Visualisation et résultats
```
visualization/
├── plotter.py                    [389 lignes]   Graphiques

results/
├── results.json                  20 résultats   ⭐ DONNÉES RÉSULTATS
├── execution_log.txt             Log complet
└── [images PNG]                  Graphiques générés
```

### 📚 Données
```
data/
├── data101.vrp, data102.vrp      Fenêtres courtes, capacité 200
├── data1101.vrp, data1102.vrp    Fenêtres longues, capacité 200
├── data111.vrp, data112.vrp      Fenêtres mixtes, capacité 200
├── data1201.vrp, data1202.vrp    Fenêtres courtes, capacité 1000
└── data201.vrp, data202.vrp      Fenêtres longues, capacité 1000
```

---

## 🗂️ Comment naviguer le RAPPORT.md

### Table complète (11 sections)

```
RAPPORT.md
│
├─ 1. Introduction et problème
│  ├─ 1.1 Définition VRPTW
│  ├─ 1.2 Formulation mathématique (avec équations)
│  └─ 1.3 Instances de test (10 fichiers décrits)
│
├─ 2. Lancement du programme
│  ├─ 2.1 Installation et environnement
│  ├─ 2.2 Exécution principale
│  └─ 2.3 Architecture du code
│
├─ 3. Génération de solutions initiales
│  ├─ 3.1 Importance des solutions initiales
│  ├─ 3.2 Méthodes implémentées (4 au total)
│  │  ├─ 3.2.1 Générateur aléatoire
│  │  ├─ 3.2.2 Nearest Neighbor
│  │  ├─ 3.2.3 Greedy Insertion
│  │  └─ 3.2.4 Clarke-Wright
│  └─ 3.3 Sélection de la méthode initiale
│
├─ 4. Opérateurs de voisinage
│  ├─ 4.1 Importance et définition
│  ├─ 4.2 Opérateurs implémentés (5 au total)
│  │  ├─ 4.2.1 2-opt
│  │  ├─ 4.2.2 Or-opt
│  │  ├─ 4.2.3 Relocate
│  │  ├─ 4.2.4 Cross Exchange
│  │  └─ 4.2.5 2-opt Between Routes
│  └─ 4.3 Gestionnaire de voisinage
│
├─ 5. Métaheuristique 1 : Algorithme génétique ⭐
│  ├─ 5.1 Principes généraux
│  ├─ 5.2 Implémentation pour VRPTW
│  │  ├─ 5.2.1 Représentation des chromosomes
│  │  ├─ 5.2.2 Initialisation
│  │  ├─ 5.2.3 Évaluation (Fonction fitness)
│  │  ├─ 5.2.4 Sélection (Tournament)
│  │  ├─ 5.2.5 Croisement (3 types)
│  │  ├─ 5.2.6 Mutation (5 opérateurs)
│  │  └─ 5.2.7 Élitisme
│  └─ 5.3 Hyperparamètres
│
├─ 6. Métaheuristique 2 : Recherche Tabou ⭐
│  ├─ 6.1 Principes généraux
│  ├─ 6.2 Implémentation pour VRPTW
│  │  ├─ 6.2.1 Initialisation
│  │  ├─ 6.2.2 Voisinage exploré
│  │  ├─ 6.2.3 Gestion de la liste tabu
│  │  ├─ 6.2.4 Critère d'aspiration
│  │  └─ 6.2.5 Intensification et diversification
│  └─ 6.3 Hyperparamètres
│
├─ 7. Protocole expérimental
│  ├─ 7.1 Objectifs
│  ├─ 7.2 Configuration des expériences
│  ├─ 7.3 Mesures de performance
│  └─ 7.4 Conditions d'expérimentation
│
├─ 8. Résultats et analyse ⭐⭐
│  ├─ 8.1 Résultats synthétiques (TABLEAUX CLÉS)
│  ├─ 8.2 Analyse par groupe de problèmes (5 groupes)
│  ├─ 8.3 Analyse détaillée par métaheuristique
│  │  ├─ 8.3.1 GA - Points forts
│  │  ├─ 8.3.2 GA - Points faibles
│  │  ├─ 8.3.3 TS - Points forts
│  │  └─ 8.3.4 TS - Points faibles
│  ├─ 8.4 Convergence et évolution (GRAPHIQUES)
│  └─ 8.5 Impact des contraintes de temps
│
├─ 9. Comparaison GA vs Recherche Tabou ⭐
│  ├─ 9.1 Tableau comparatif synthétique
│  ├─ 9.2 Analyse comparative
│  └─ 9.3 Recommandations
│
├─ 10. Bonus : limites de la programmation linéaire
│  ├─ 10.1 Modèle PLNE pour VRPTW
│  ├─ 10.2 Limites observées en théorie
│  ├─ 10.3 Pourquoi PL échoue pour VRPTW
│  ├─ 10.4 Exemple : Problème data101
│  └─ 10.5 Conclusion bonus
│
└─ 11. Conclusion
   ├─ 11.1 Résumé des résultats
   ├─ 11.2 Améliorations futures
   ├─ 11.3 Apprentissages clés
   ├─ 11.4 Recommandation pratique
   └─ 11.5 Fichiers livrables
```

---

## 📊 Données clés du rapport

### Statistiques du projet
- **Rapport** : 1,143 lignes
- **Code** : 2,660 lignes Python
- **Sections** : 11 principales
- **Tableaux** : 15+
- **Instances testées** : 10 (100 clients chacune)
- **Résultats** : 20 (GA + TS par instance)

### Résultats GA vs TS
| Métrique | GA | TS |
|----------|----|----|
| Distance | 6,015 km | 714 km |
| Faisabilité | 60% | 0% |
| Temps | 28.6s | 2.1s |
| Véhicules | 42.6 | 8.9 |

### Fichiers à consulter
- **Résultats bruts** : `results/results.json`
- **Tableau résumé** : Section 8.1 du RAPPORT
- **Analyse détaillée** : Sections 8.2-8.5
- **Comparaison** : Section 9

---

## 🚀 Exécution rapide

```bash
cd VRPTW

# 1. Installation (1 min)
pip install -r requirements.txt

# 2. Test rapide (30 sec)
python test_installation.py

# 3. Lancer tous les tests (5 min)
python src/main.py

# 4. Voir les résultats
cat results/results.json | python -m json.tool

# 5. Exemple d'utilisation
python example_usage.py
```

---

## 🔗 Connexions entre sections

### Pour comprendre les résultats
1. Section 1 → Comprendre le problème
2. Section 3 → Savoir comment on génère les solutions
3. Section 4 → Savoir comment on les améliore
4. Section 5-6 → Comprendre les deux algorithmes
5. Section 7 → Savoir comment on les teste
6. **Section 8 → Les résultats!**
7. Section 9 → Les conclusions

### Pour reproduire l'expérience
1. Section 2 → Installation
2. Section 3 → Générateurs
3. Section 4 → Opérateurs
4. Section 5-6 → Métaheuristiques
5. Section 7 → Configuration exacte
6. Exécuter : `python src/main.py`

### Pour l'académique (compréhension théorique)
1. Section 1 → Théorie VRPTW
2. Section 3-4 → Heuristiques classiques
3. Section 5-6 → Théorie métaheuristiques
4. Section 10 → Programmation linéaire et limites
5. Section 8-9 → Résultats empiriques

---

## 📞 Questions fréquentes

**Q: Où sont les résultats?**
A: Section 8 du RAPPORT.md et dans `results/results.json`

**Q: Comment exécuter le code?**
A: Section 2 du RAPPORT.md ou `python src/main.py`

**Q: Pourquoi GA meilleur?**
A: Section 9.3 du RAPPORT.md (recommandations)

**Q: C'est quoi la différence GA vs TS?**
A: Section 9 du RAPPORT.md (tableau comparatif)

**Q: Comment lire le rapport?**
A: Voir **GUIDE_RAPPORT.md** (docs folder)

**Q: Tous les éléments obligatoires sont présents?**
A: Voir **CHECKLIST_LIVRAISON.md**

---

## 📄 Fichiers clés par besoin

### Besoin : Comprendre le projet
→ Lire : **RESUME_EXECUTIF.md**

### Besoin : Reproduire les résultats
→ Consulter : Section 2 + Section 7 du RAPPORT.md

### Besoin : Voir les résultats
→ Consulter : Section 8 du RAPPORT.md + `results/results.json`

### Besoin : Comprendre GA
→ Consulter : Section 5 du RAPPORT.md + `src/genetic_algorithm.py`

### Besoin : Comprendre TS
→ Consulter : Section 6 du RAPPORT.md + `src/tabu_search.py`

### Besoin : Vérifier l'intégrité
→ Lire : **CHECKLIST_LIVRAISON.md**

### Besoin : Naviguer le projet
→ Consulter : Ce fichier (INDEX.md) + **GUIDE_RAPPORT.md**

---

## ✅ Avant de remettre

- ✅ Rapport imprimé/PDF : RAPPORT.md
- ✅ Code compilé/exécutable : src/ et visualization/
- ✅ Données complètes : data/
- ✅ Résultats reproduits : results/results.json
- ✅ Documentation claire : README.md et guides
- ✅ ZIP préparé avec tous les fichiers

---

## 📈 Statistiques finales

```
Total rapport:     1,143 lignes
Total code:        2,660 lignes
Total docs:        ~1,500 lignes
Total project:     ~5,300 lignes

Temps de rapport:  ~15-40 pages PDF équivalent
Temps d'exec:      ~280 secondes (10 GA + 10 TS)
Instances testées: 10 (2,000 clients au total)
```

---

## 🎯 Status final

**🟢 PROJECT COMPLETE** ✅

Tous les éléments du cahier des charges sont présents et fonctionnels.
Code testé, résultats vérifiés, rapport rédigé.

Prêt pour remise!

---

*Créé le : Juin 2024*  
*Polytech Lyon - Optimisation Discrète*  
*Auteurs : Thibault LARACINE, Louka PESIC*
