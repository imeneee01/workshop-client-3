# Potentiel PV tertiaire en France — Workshop Oxand

Analyse exploratoire du potentiel photovoltaïque des toitures tertiaires
(9–500 kWc) par département, focus rentabilité (LCOE, payback, TRI, VAN).

Projet d'une semaine visant à *caractériser le terrain de jeu* en vue d'un
futur volet « production locale » dans l'outil Simeo. Ne constitue pas ce module.

## Installation

```powershell
python -m pip install -r requirements.txt
```

## Utilisation

1. Construire le jeu de données (PVGIS, ~96 appels, mis en cache la 1ʳᵉ fois) :
   ```powershell
   python -c "from src.dataset import build_dataset; build_dataset()"
   ```
2. Générer le notebook :
   ```powershell
   python scripts/build_notebook.py
   ```
3. Ouvrir `notebooks/analyse_pv_france.ipynb` dans Jupyter (ou l'exécuter :
   `python -m jupyter nbconvert --to notebook --execute --inplace notebooks/analyse_pv_france.ipynb`).

## Dashboard interactif

Local :
```powershell
python -m streamlit run streamlit_app.py
```

En ligne : déployé sur Streamlit Community Cloud — <URL_A_COMPLETER_APRES_DEPLOIEMENT>.
Le dashboard présente, pour des hypothèses économiques fixes (celles de la note
de cadrage), les indicateurs LCOE / payback / TRI / VAN et les cartes par
département. L'utilisateur choisit le régime de valorisation (autoconsommation /
vente) et la puissance de l'installation.

## Tests

```powershell
python -m pytest -v
```

## Structure

- `src/config.py` — toutes les hypothèses (CAPEX, OPEX, tarifs, taux d'autoconso…)
- `src/gisement.py` — gisement PVGIS + cache + fallback synthétique
- `src/economics.py` — modèle économique (LCOE, payback, TRI, VAN)
- `src/dataset.py` — pipeline de données départementales
- `src/viz.py` — cartes choroplèthes et graphiques
- `scripts/build_notebook.py` — génère le notebook (reproductible)
- `notebooks/` — le livrable
- `tests/` — tests du modèle (TDD)

## Nature des données (transparence)

| Catégorie | Source | Nature |
|---|---|---|
| Facteur de production, irradiance | **PVGIS** (JRC) | **Récupérée, fiable** |
| Contours / centroïdes départements | GeoJSON officiel | **Récupérée, fiable** |
| CAPEX, OPEX, tarifs S21, taux | Note de cadrage (Annexe A) | **Hypothèses** explicites |
| LCOE, payback, TRI, VAN | Modèle `economics.py` | **Calculées** (reproductibles) |

## Régimes de valorisation

- **Autoconsommation avec vente du surplus** (scénario principal) — taux
  d'autoconsommation par défaut **65 %** ; la part consommée est valorisée au
  prix évité (~20 c/kWh), le surplus vendu au tarif S21. Le TRI ressort élevé,
  cohérent avec le constat de rentabilité de la note (§1.2). Une analyse de
  sensibilité (40/65/90 %) est fournie dans le notebook.
- **Vente totale** — au tarif S21 ; payback 9–15 ans, recoupe le benchmark
  conservateur de la note.

## Limites

Analyse territoriale **agrégée** (pas d'étude bâtiment par bâtiment = rôle de
Simeo). France métropolitaine uniquement. Hypothèses économiques indicatives,
à recouper/dater pour un usage opérationnel.
