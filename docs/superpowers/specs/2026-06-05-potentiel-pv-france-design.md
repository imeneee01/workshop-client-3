# Potentiel PV France — Spécification de conception

> **Statut** : validé — 2026-06-05
> **Contexte** : workshop client Oxand, projet exploratoire d'une semaine.
> **Note de cadrage source** : [potentiel-pv-france-note-cadrage.md](../../../potentiel-pv-france-note-cadrage.md)

## 1. Objectif

Produire un **notebook Python d'analyse** caractérisant le potentiel photovoltaïque
des toitures tertiaires (9–500 kWc) en France métropolitaine, à granularité
**départementale**, avec un focus sur la **rentabilité économique** (LCOE, payback,
TRI, VAN). Le projet « caractérise le terrain de jeu » pour une future intégration
dans l'outil Simeo — il ne construit pas ce module.

## 2. Livrable

Un notebook Jupyter narratif (`notebooks/analyse_pv_france.ipynb`) qui :
contexte → données → modèle → résultats → cartes/graphiques → limites & hypothèses.
Le code lourd vit dans des modules `src/` testables ; le notebook orchestre et raconte.

## 3. Nature des données (transparence)

| Catégorie | Source | Nature |
|---|---|---|
| Facteur de production, irradiance | **PVGIS** (JRC) | Récupérée, fiable |
| Contours/centroïdes départements | GeoJSON officiel | Récupérée, fiable |
| CAPEX, OPEX, tarifs S21, taux | Annexe A de la note | **Hypothèses** explicites, étiquetées |
| LCOE, payback, TRI, VAN | Modèle `economics.py` | Calculées (reproductibles) |

Décision : on **s'en tient aux ordres de grandeur de l'Annexe A** pour l'économique,
étiquetés comme hypothèses dans `config.py`. Sourcing ADEME/CRE renforcé = hors-scope
de cette semaine.

## 4. Architecture

```
workshop/
├─ potentiel-pv-france-note-cadrage.md
├─ data/
│  ├─ raw/          GeoJSON départements, cache PVGIS
│  └─ processed/    CSV consolidé (1 ligne = 1 département)
├─ src/
│  ├─ config.py     TOUTES les hypothèses (aucune valeur en dur ailleurs)
│  ├─ gisement.py   récupération PVGIS + cache CSV + fallback synthétique
│  ├─ economics.py  fonctions pures : production, CAPEX, OPEX, cash-flows, LCOE, payback, TRI, VAN
│  └─ viz.py        cartes choroplèthes + graphiques
├─ notebooks/
│  └─ analyse_pv_france.ipynb
└─ tests/           tests du modèle économique
```

**Principe** : séparation données → calcul → analyse → visualisation. Chaque module a
un rôle unique, une interface claire, testable isolément.

## 5. Modèle de données

Table consolidée `data/processed/departements_pv.csv`, ~96 lignes :

| Colonne | Source |
|---|---|
| `code_dept`, `nom_dept` | GeoJSON |
| `lat`, `lon` | centroïde |
| `facteur_production` (kWh/kWc/an) | PVGIS (ou fallback) |
| `irradiance` (kWh/m²/an) | PVGIS |
| `geometry` | GeoJSON (pour cartes) |

Le gisement est récupéré **une fois** et mis en cache dans `data/raw/pvgis_cache.csv`.
Si le cache existe, pas de nouvel appel API. Installation de référence pour PVGIS :
inclinaison ~30°, orientation Sud, pertes système ~14 % (PR ~0,86) — paramètres dans `config.py`.

**Fallback** : si PVGIS est indisponible, gradient synthétique Nord→Sud (~900→~1500
kWh/kWc/an) basé sur la latitude. **Étiqueté visiblement** dans le notebook
(« données synthétiques — PVGIS indisponible »).

## 6. Modèle économique (`economics.py`)

Fonctions pures, entrée = facteur de production + hypothèses `config.py` :

- **Production annuelle** = `puissance_kWc × facteur × (1 − dégradation)^année`
- **CAPEX** = `puissance × coût_kWc` (barème par tranche : 9–36 / 36–100 / 100–500 kWc, Annexe A)
- **OPEX** = `% CAPEX/an` + provision remplacement onduleur (~année 12, ~10–15 % CAPEX)
- **Cash-flows** sur 25 ans selon **régime de valorisation** :
  - Autoconsommation (~15–25 c€/kWh évités)
  - Vente totale (tarif S21 par tranche, ~7–11 c€/kWh)
- **Indicateurs** : LCOE (€/kWh), Payback brut + actualisé (ans), TRI (%), VAN (€)

Aucune valeur en dur : tout paramètre (taux d'actualisation, durée 25 ans, dégradation,
barèmes CAPEX/OPEX, tarifs) vit dans `config.py`.

## 7. Cas de référence & sensibilité

- **Cas type cartographié** : toiture tertiaire **100 kWc** (cité dans la note), indicateurs
  calculés par département.
- **Analyse de sensibilité** : tailles 9 / 100 / 500 kWc pour illustrer l'effet d'échelle CAPEX,
  et comparaison autoconso vs vente.

## 8. Visualisations (`viz.py`)

- **Cartes choroplèthes** par département (geopandas + matplotlib, statiques) :
  facteur de production, LCOE, payback, TRI.
- **Graphiques** : effet d'échelle CAPEX, autoconso vs vente, distribution Nord/Sud.

## 9. Tests (`tests/`)

Vérifient `economics.py` sur cas connus :
- VAN à taux 0 = somme des cash-flows nets
- Payback cohérent (revenus cumulés = CAPEX)
- LCOE dans la fourchette 6–10 c€/kWh (Annexe A) pour un cas central
- Monotonie : plus de gisement → meilleur TRI (toutes choses égales)

## 10. Stack technique

Python 3.11 (env `myenv` existant). Dépendances : `pandas`, `numpy`, `numpy-financial`
(TRI/VAN), `geopandas`, `matplotlib`, `requests` (PVGIS), `jupyter`.

## 11. Hors-scope (YAGNI)

- Pas d'analyse bâtiment par bâtiment (rôle de Simeo).
- Pas de dashboard interactif (notebook statique suffit).
- Pas de sourcing ADEME/CRE renforcé cette semaine.
- DROM exclus (spécificités tarifaires distinctes).
- Parc PV installé / comparaison européenne = nice-to-have, hors-scope initial.
