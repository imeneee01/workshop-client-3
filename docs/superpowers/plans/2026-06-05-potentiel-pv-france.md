# Potentiel PV France — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construire un notebook Python d'analyse caractérisant le potentiel PV tertiaire (9–500 kWc) par département français, avec calcul de rentabilité (LCOE, payback, TRI, VAN) et cartes choroplèthes.

**Architecture:** Données → calcul → analyse → visualisation. Le code testable vit dans `src/` (config, gisement, economics, dataset, viz) ; le notebook orchestre et raconte. Gisement solaire récupéré via PVGIS (réel) + cache CSV + fallback synthétique. Hypothèses économiques centralisées dans `config.py`.

**Tech Stack:** Python 3.11 (env `myenv`), pandas, numpy, geopandas, matplotlib, requests, pytest. NPV/IRR implémentés maison (pas de numpy_financial).

**Spec source:** [docs/superpowers/specs/2026-06-05-potentiel-pv-france-design.md](../specs/2026-06-05-potentiel-pv-france-design.md)

**Note Windows / commandes:** Toutes les commandes supposent le venv actif. Si besoin : `& C:\Users\ImeneBELHOCINE\myenv\Scripts\Activate.ps1`. `pytest` se lance avec `python -m pytest`.

---

## Task 1: Scaffolding du projet, dépendances et configuration

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Initialiser git et l'arborescence**

```powershell
git init
New-Item -ItemType Directory -Force src, tests, "data/raw", "data/processed", notebooks | Out-Null
```

- [ ] **Step 2: Créer `.gitignore`**

```
__pycache__/
*.pyc
.ipynb_checkpoints/
data/raw/pvgis_cache.csv
.pytest_cache/
```

- [ ] **Step 3: Créer `requirements.txt`**

```
pandas
numpy
geopandas
matplotlib
requests
pytest
jupyter
```

- [ ] **Step 4: Installer geopandas (les autres sont déjà présents)**

Run: `python -m pip install geopandas`
Expected: installation réussie de geopandas, shapely, pyproj, pyogrio.

- [ ] **Step 5: Créer les fichiers `__init__.py` vides**

`src/__init__.py` et `tests/__init__.py` : fichiers vides.

- [ ] **Step 6: Créer `src/config.py` — TOUTES les hypothèses**

```python
"""Hypotheses centrales du projet. AUCUNE valeur en dur ailleurs.

Sources : Annexe A de la note de cadrage (ordres de grandeur indicatifs).
Etiquetees comme HYPOTHESES, distinctes des donnees PVGIS recuperees (reelles).
"""

# --- Parametres financiers ---
DISCOUNT_RATE = 0.04          # taux d'actualisation
PROJECT_YEARS = 25            # duree de vie analysee (modules)
DEGRADATION = 0.005           # perte de production annuelle (0.5 %/an)

# --- Installation de reference (pour PVGIS et cartographie) ---
REF_POWER_KWC = 100.0         # toiture tertiaire type
TILT = 30                     # inclinaison (degres)
AZIMUTH = 0                   # orientation Sud (PVGIS: aspect=0)
SYSTEM_LOSS = 14              # pertes systeme PVGIS (%) -> PR ~0.86

# --- Tailles pour l'analyse de sensibilite ---
SENSITIVITY_SIZES_KWC = [9.0, 100.0, 500.0]

# --- CAPEX par tranche de taille (EUR/kWc) ---
# Valeurs representatives (milieu de fourchette Annexe A).
CAPEX_BRACKETS = [
    (9, 36, 1850.0),    # 9-36 kWc : 1500-2200
    (36, 100, 1400.0),  # 36-100 kWc : 1200-1600
    (100, 500, 1100.0), # 100-500 kWc : 900-1300
]

# --- OPEX ---
OPEX_RATE = 0.015             # 1.5 % du CAPEX/an (fourchette 1-2 %)
INVERTER_REPLACEMENT_YEAR = 12
INVERTER_REPLACEMENT_RATE = 0.12  # 12 % du CAPEX (fourchette 10-15 %)

# --- Valorisation de l'energie (EUR/kWh) ---
AUTOCONSO_PRICE = 0.20        # prix evite reseau tertiaire (15-25 c)
# Tarif de vente S21 par tranche de puissance (EUR/kWh)
VENTE_TARIFFS = [
    (0, 9, 0.13),
    (9, 100, 0.10),
    (100, 500, 0.08),
]

# --- PVGIS ---
PVGIS_URL = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
PVGIS_CACHE = "data/raw/pvgis_cache.csv"

# --- Donnees geographiques ---
GEOJSON_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/"
    "france-geojson/master/departements-version-simplifiee.geojson"
)
GEOJSON_PATH = "data/raw/departements.geojson"
PROCESSED_CSV = "data/processed/departements_pv.csv"

# --- Fallback synthetique (si PVGIS indisponible) ---
# Gradient lineaire du facteur de production selon la latitude.
FALLBACK_LAT_SOUTH = 42.5     # ~Perpignan
FALLBACK_LAT_NORTH = 51.0     # ~Lille
FALLBACK_FACTEUR_SOUTH = 1500.0
FALLBACK_FACTEUR_NORTH = 900.0
```

- [ ] **Step 7: Commit**

```powershell
git add .gitignore requirements.txt src tests
git commit -m "chore: scaffolding, dependances et configuration"
```

---

## Task 2: Modèle économique (`src/economics.py`) — TDD

**Files:**
- Create: `src/economics.py`
- Test: `tests/test_economics.py`

- [ ] **Step 1: Écrire les tests d'abord**

`tests/test_economics.py` :

```python
import numpy as np
from src import economics as eco
from src import config


def test_capex_per_kwc_brackets():
    assert eco.capex_per_kwc(20) == 1850.0
    assert eco.capex_per_kwc(50) == 1400.0
    assert eco.capex_per_kwc(300) == 1100.0


def test_capex_total():
    # 100 kWc tombe dans la tranche 100-500 -> 1100 EUR/kWc
    assert eco.capex(100) == 100 * 1100.0


def test_vente_tariff_brackets():
    assert eco.vente_tariff(50) == 0.10
    assert eco.vente_tariff(300) == 0.08


def test_annual_production_degrades():
    p0 = eco.annual_production(100, 1200, year=1)
    p2 = eco.annual_production(100, 1200, year=2)
    assert p0 == 100 * 1200  # annee 1 : pas de degradation
    assert p2 < p0           # annee 2 : degrade


def test_npv_at_zero_rate_equals_sum():
    cf = [-100.0, 30.0, 30.0, 30.0, 30.0]
    assert abs(eco.npv(0.0, cf) - sum(cf)) < 1e-9


def test_npv_discounts_future():
    cf = [-100.0, 110.0]
    # a 10 %, le flux de 110 a l'annee 1 vaut exactement 100 -> NPV = 0
    assert abs(eco.npv(0.10, cf)) < 1e-9


def test_irr_recovers_known_rate():
    cf = [-100.0, 110.0]
    assert abs(eco.irr(cf) - 0.10) < 1e-4


def test_cashflows_structure():
    cf = eco.cashflows(100, 1200, regime="autoconso")
    assert len(cf) == config.PROJECT_YEARS + 1
    assert cf[0] < 0  # annee 0 : investissement
    assert cf[1] > 0  # annee 1 : revenu net positif


def test_inverter_replacement_dips_cashflow():
    cf = eco.cashflows(100, 1200, regime="autoconso")
    y = config.INVERTER_REPLACEMENT_YEAR
    # l'annee de remplacement onduleur a un flux inferieur a l'annee precedente
    assert cf[y] < cf[y - 1]


def test_lcoe_in_plausible_range():
    # cas central : 100 kWc, facteur 1100 -> LCOE attendu ~6-10 c (Annexe A)
    lcoe = eco.lcoe(100, 1100)
    assert 0.04 < lcoe < 0.12


def test_better_gisement_improves_irr():
    low = eco.irr(eco.cashflows(100, 900, regime="autoconso"))
    high = eco.irr(eco.cashflows(100, 1500, regime="autoconso"))
    assert high > low


def test_payback_returns_year_within_horizon():
    pb = eco.payback(eco.cashflows(100, 1300, regime="autoconso"))
    assert 1 <= pb <= config.PROJECT_YEARS
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `python -m pytest tests/test_economics.py -v`
Expected: FAIL — `module 'src.economics' has no attribute ...` (le module n'existe pas encore).

- [ ] **Step 3: Implémenter `src/economics.py`**

```python
"""Modele economique PV. Fonctions pures, parametrees par config.py.

Tous les indicateurs (LCOE, payback, TRI, VAN) sont CALCULES a partir
du gisement (PVGIS, reel) et des hypotheses (config.py).
"""
from src import config


def capex_per_kwc(power_kwc):
    """Cout d'investissement unitaire (EUR/kWc) selon la tranche de taille."""
    for low, high, value in config.CAPEX_BRACKETS:
        if low <= power_kwc <= high:
            return value
    # hors bornes : on prend la tranche la plus proche
    if power_kwc < config.CAPEX_BRACKETS[0][0]:
        return config.CAPEX_BRACKETS[0][2]
    return config.CAPEX_BRACKETS[-1][2]


def capex(power_kwc):
    """Investissement initial total (EUR)."""
    return power_kwc * capex_per_kwc(power_kwc)


def vente_tariff(power_kwc):
    """Tarif de vente S21 (EUR/kWh) selon la tranche de puissance."""
    for low, high, value in config.VENTE_TARIFFS:
        if low < power_kwc <= high:
            return value
    return config.VENTE_TARIFFS[-1][2]


def energy_price(power_kwc, regime):
    """Prix de valorisation de l'energie (EUR/kWh) selon le regime."""
    if regime == "autoconso":
        return config.AUTOCONSO_PRICE
    if regime == "vente":
        return vente_tariff(power_kwc)
    raise ValueError(f"regime inconnu : {regime!r}")


def annual_production(power_kwc, facteur, year):
    """Production de l'annee `year` (kWh), avec degradation. year >= 1."""
    return power_kwc * facteur * (1 - config.DEGRADATION) ** (year - 1)


def cashflows(power_kwc, facteur, regime):
    """Flux de tresorerie annuels (EUR), annee 0 a PROJECT_YEARS."""
    invest = capex(power_kwc)
    opex = invest * config.OPEX_RATE
    price = energy_price(power_kwc, regime)
    flows = [-invest]  # annee 0
    for year in range(1, config.PROJECT_YEARS + 1):
        revenue = annual_production(power_kwc, facteur, year) * price
        cf = revenue - opex
        if year == config.INVERTER_REPLACEMENT_YEAR:
            cf -= invest * config.INVERTER_REPLACEMENT_RATE
        flows.append(cf)
    return flows


def npv(rate, flows):
    """Valeur actuelle nette d'une serie de flux (annee 0 = flows[0])."""
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(flows))


def irr(flows, low=-0.9, high=1.0, tol=1e-7, max_iter=200):
    """Taux de rendement interne par bisection. None si non trouve."""
    f_low, f_high = npv(low, flows), npv(high, flows)
    if f_low * f_high > 0:
        return None  # pas de changement de signe sur l'intervalle
    for _ in range(max_iter):
        mid = (low + high) / 2
        f_mid = npv(mid, flows)
        if abs(f_mid) < tol:
            return mid
        if f_low * f_mid < 0:
            high, f_high = mid, f_mid
        else:
            low, f_low = mid, f_mid
    return (low + high) / 2


def lcoe(power_kwc, facteur):
    """Cout moyen actualise de l'energie (EUR/kWh)."""
    invest = capex(power_kwc)
    opex = invest * config.OPEX_RATE
    r = config.DISCOUNT_RATE
    disc_costs = invest
    disc_energy = 0.0
    for year in range(1, config.PROJECT_YEARS + 1):
        disc_costs += opex / (1 + r) ** year
        if year == config.INVERTER_REPLACEMENT_YEAR:
            disc_costs += invest * config.INVERTER_REPLACEMENT_RATE / (1 + r) ** year
        disc_energy += annual_production(power_kwc, facteur, year) / (1 + r) ** year
    return disc_costs / disc_energy


def payback(flows, discounted=False):
    """Temps de retour (annees). PROJECT_YEARS + 1 si jamais rembourse."""
    r = config.DISCOUNT_RATE if discounted else 0.0
    cumul = 0.0
    for t, cf in enumerate(flows):
        cumul += cf / (1 + r) ** t
        if t > 0 and cumul >= 0:
            return t
    return config.PROJECT_YEARS + 1
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `python -m pytest tests/test_economics.py -v`
Expected: PASS (12 tests).

- [ ] **Step 5: Commit**

```powershell
git add src/economics.py tests/test_economics.py
git commit -m "feat: modele economique PV (LCOE, payback, TRI, VAN) avec tests"
```

---

## Task 3: Récupération du gisement PVGIS (`src/gisement.py`)

**Files:**
- Create: `src/gisement.py`
- Test: `tests/test_gisement.py`

- [ ] **Step 1: Écrire les tests (fallback testable sans réseau)**

`tests/test_gisement.py` :

```python
from src import gisement
from src import config


def test_fallback_south_is_sunnier_than_north():
    sud = gisement.fallback_facteur(config.FALLBACK_LAT_SOUTH)
    nord = gisement.fallback_facteur(config.FALLBACK_LAT_NORTH)
    assert sud > nord


def test_fallback_endpoints():
    assert abs(gisement.fallback_facteur(config.FALLBACK_LAT_SOUTH)
               - config.FALLBACK_FACTEUR_SOUTH) < 1.0
    assert abs(gisement.fallback_facteur(config.FALLBACK_LAT_NORTH)
               - config.FALLBACK_FACTEUR_NORTH) < 1.0


def test_fallback_in_range():
    f = gisement.fallback_facteur(46.0)  # centre France
    assert config.FALLBACK_FACTEUR_NORTH < f < config.FALLBACK_FACTEUR_SOUTH
```

- [ ] **Step 2: Lancer les tests pour vérifier qu'ils échouent**

Run: `python -m pytest tests/test_gisement.py -v`
Expected: FAIL — module inexistant.

- [ ] **Step 3: Implémenter `src/gisement.py`**

```python
"""Recuperation du gisement solaire via PVGIS, avec cache et fallback.

PVGIS (JRC, Commission europeenne) = donnees REELLES.
Le fallback synthetique n'est utilise QUE si PVGIS est indisponible,
et est etiquete comme tel (colonne `source`).
"""
import os
import pandas as pd
import requests
from src import config


def fallback_facteur(lat):
    """Facteur de production synthetique (kWh/kWc/an) par interpolation
    lineaire selon la latitude. Filet de securite si PVGIS echoue."""
    lat_s, lat_n = config.FALLBACK_LAT_SOUTH, config.FALLBACK_LAT_NORTH
    f_s, f_n = config.FALLBACK_FACTEUR_SOUTH, config.FALLBACK_FACTEUR_NORTH
    # clamp
    lat = max(lat_s, min(lat_n, lat))
    ratio = (lat - lat_s) / (lat_n - lat_s)
    return f_s + ratio * (f_n - f_s)


def fetch_pvgis(lat, lon, timeout=20):
    """Interroge PVGIS pour 1 kWc. Retourne (facteur, irradiance, 'pvgis').
    Leve une exception en cas d'echec (geree par l'appelant)."""
    params = {
        "lat": lat, "lon": lon,
        "peakpower": 1, "loss": config.SYSTEM_LOSS,
        "angle": config.TILT, "aspect": config.AZIMUTH,
        "mountingplace": "building", "outputformat": "json",
    }
    resp = requests.get(config.PVGIS_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    fixed = resp.json()["outputs"]["totals"]["fixed"]
    facteur = fixed["E_y"]          # kWh/an pour 1 kWc = kWh/kWc/an
    irradiance = fixed["H(i)_y"]    # kWh/m2/an sur le plan des modules
    return facteur, irradiance, "pvgis"


def get_gisement(lat, lon):
    """Tente PVGIS, retombe sur le fallback synthetique si echec.
    Retourne (facteur, irradiance_ou_None, source)."""
    try:
        return fetch_pvgis(lat, lon)
    except Exception as exc:  # reseau, API, parsing
        print(f"  [fallback] PVGIS indisponible ({exc}) -> synthetique")
        return fallback_facteur(lat), None, "synthetique"


def load_cache():
    """Charge le cache PVGIS s'il existe, sinon None."""
    if os.path.exists(config.PVGIS_CACHE):
        return pd.read_csv(config.PVGIS_CACHE, dtype={"code_dept": str})
    return None


def save_cache(df):
    """Persiste le cache PVGIS."""
    os.makedirs(os.path.dirname(config.PVGIS_CACHE), exist_ok=True)
    df.to_csv(config.PVGIS_CACHE, index=False)
```

- [ ] **Step 4: Lancer les tests pour vérifier qu'ils passent**

Run: `python -m pytest tests/test_gisement.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```powershell
git add src/gisement.py tests/test_gisement.py
git commit -m "feat: recuperation gisement PVGIS avec cache et fallback synthetique"
```

---

## Task 4: Construction du jeu de données départemental (`src/dataset.py`)

**Files:**
- Create: `src/dataset.py`
- Test: `tests/test_dataset.py`

- [ ] **Step 1: Écrire un test léger (logique de centroïde, sans réseau)**

`tests/test_dataset.py` :

```python
import geopandas as gpd
from shapely.geometry import Polygon
from src import dataset


def test_centroids_from_geodataframe():
    poly = Polygon([(0, 0), (0, 2), (2, 2), (2, 0)])
    gdf = gpd.GeoDataFrame(
        {"code": ["01"], "nom": ["Test"]},
        geometry=[poly], crs="EPSG:4326",
    )
    out = dataset.add_centroids(gdf)
    assert abs(out.loc[0, "lat"] - 1.0) < 1e-6
    assert abs(out.loc[0, "lon"] - 1.0) < 1e-6
```

- [ ] **Step 2: Lancer le test pour vérifier qu'il échoue**

Run: `python -m pytest tests/test_dataset.py -v`
Expected: FAIL — module inexistant.

- [ ] **Step 3: Implémenter `src/dataset.py`**

```python
"""Construit la table consolidee : 1 ligne = 1 departement.

Etapes : telecharger le GeoJSON officiel -> centroides -> gisement (PVGIS/cache)
-> CSV consolide dans data/processed/.
"""
import os
import geopandas as gpd
import pandas as pd
import requests
from src import config, gisement


def download_geojson():
    """Telecharge le GeoJSON des departements s'il n'est pas deja en local."""
    if os.path.exists(config.GEOJSON_PATH):
        return
    os.makedirs(os.path.dirname(config.GEOJSON_PATH), exist_ok=True)
    resp = requests.get(config.GEOJSON_URL, timeout=60)
    resp.raise_for_status()
    with open(config.GEOJSON_PATH, "wb") as f:
        f.write(resp.content)


def add_centroids(gdf):
    """Ajoute lat/lon du centroide de chaque geometrie (EPSG:4326)."""
    gdf = gdf.copy()
    cent = gdf.geometry.centroid
    gdf["lat"] = cent.y
    gdf["lon"] = cent.x
    return gdf


def build_gisement_table(gdf):
    """Retourne un DataFrame (code_dept, facteur, irradiance, source),
    en utilisant le cache PVGIS si disponible."""
    cached = gisement.load_cache()
    if cached is not None:
        print(f"  Cache PVGIS trouve ({len(cached)} departements).")
        return cached

    rows = []
    n = len(gdf)
    for i, row in enumerate(gdf.itertuples(), start=1):
        code = row.code
        print(f"  PVGIS {i}/{n} - dept {code}...")
        facteur, irradiance, source = gisement.get_gisement(row.lat, row.lon)
        rows.append({
            "code_dept": code, "facteur_production": facteur,
            "irradiance": irradiance, "source": source,
        })
    out = pd.DataFrame(rows)
    gisement.save_cache(out)
    return out


def build_dataset():
    """Pipeline complet -> ecrit data/processed/departements_pv.csv et
    retourne le GeoDataFrame consolide (avec geometrie pour les cartes)."""
    download_geojson()
    gdf = gpd.read_file(config.GEOJSON_PATH)
    gdf = gdf.rename(columns={"code": "code_dept", "nom": "nom_dept"})
    gdf["code"] = gdf["code_dept"]  # alias pour build_gisement_table
    gdf = add_centroids(gdf)

    gis = build_gisement_table(gdf)
    merged = gdf.merge(gis, on="code_dept", how="left")

    # CSV sans geometrie (pour partage / inspection)
    os.makedirs(os.path.dirname(config.PROCESSED_CSV), exist_ok=True)
    cols = ["code_dept", "nom_dept", "lat", "lon",
            "facteur_production", "irradiance", "source"]
    merged[cols].to_csv(config.PROCESSED_CSV, index=False)
    return merged
```

- [ ] **Step 4: Lancer le test pour vérifier qu'il passe**

Run: `python -m pytest tests/test_dataset.py -v`
Expected: PASS (1 test).

- [ ] **Step 5: Construire réellement le jeu de données (appels PVGIS, ~96)**

Run: `python -c "from src.dataset import build_dataset; df = build_dataset(); print(df[['code_dept','nom_dept','facteur_production','source']].head(10)); print('Total:', len(df))"`
Expected: ~96 lignes, `source` = `pvgis` (ou `synthetique` si réseau indisponible), facteurs entre ~900 et ~1500. Crée `data/raw/pvgis_cache.csv` et `data/processed/departements_pv.csv`.

- [ ] **Step 6: Commit**

```powershell
git add src/dataset.py tests/test_dataset.py data/processed/departements_pv.csv
git commit -m "feat: pipeline de construction du jeu de donnees departemental"
```

---

## Task 5: Visualisations (`src/viz.py`)

**Files:**
- Create: `src/viz.py`
- Test: `tests/test_viz.py`

- [ ] **Step 1: Écrire un test (les fonctions renvoient un objet figure)**

`tests/test_viz.py` :

```python
import matplotlib
matplotlib.use("Agg")  # backend sans affichage
import geopandas as gpd
from shapely.geometry import Polygon
from src import viz


def _toy_gdf():
    polys = [Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
             Polygon([(1, 0), (1, 1), (2, 1), (2, 0)])]
    return gpd.GeoDataFrame(
        {"nom_dept": ["A", "B"], "valeur": [1.0, 2.0]},
        geometry=polys, crs="EPSG:4326",
    )


def test_choropleth_returns_figure():
    fig = viz.choropleth(_toy_gdf(), "valeur", "Titre test")
    assert fig is not None
    assert len(fig.axes) >= 1


def test_bar_chart_returns_figure():
    fig = viz.bar_chart(["a", "b"], [1, 2], "Titre", "x", "y")
    assert fig is not None
```

- [ ] **Step 2: Lancer le test pour vérifier qu'il échoue**

Run: `python -m pytest tests/test_viz.py -v`
Expected: FAIL — module inexistant.

- [ ] **Step 3: Implémenter `src/viz.py`**

```python
"""Visualisations : cartes choroplethes departementales et graphiques."""
import matplotlib.pyplot as plt


def choropleth(gdf, column, title, cmap="viridis", legend_label=None):
    """Carte choroplethe de la France par departement sur `column`."""
    fig, ax = plt.subplots(figsize=(8, 8))
    gdf.plot(
        column=column, ax=ax, cmap=cmap, legend=True,
        edgecolor="white", linewidth=0.3,
        legend_kwds={"label": legend_label or column, "shrink": 0.6},
        missing_kwds={"color": "lightgrey", "label": "n/d"},
    )
    ax.set_title(title, fontsize=13)
    ax.axis("off")
    fig.tight_layout()
    return fig


def bar_chart(labels, values, title, xlabel, ylabel, color="#2c7fb8"):
    """Diagramme en barres simple."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([str(l) for l in labels], values, color=color)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    return fig


def grouped_bar(labels, series_dict, title, xlabel, ylabel):
    """Barres groupees : series_dict = {nom_serie: [valeurs]}."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(labels))
    n = len(series_dict)
    width = 0.8 / n
    for i, (name, vals) in enumerate(series_dict.items()):
        ax.bar(x + i * width, vals, width, label=name)
    ax.set_xticks(x + width * (n - 1) / 2)
    ax.set_xticklabels([str(l) for l in labels])
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    fig.tight_layout()
    return fig
```

- [ ] **Step 4: Lancer le test pour vérifier qu'il passe**

Run: `python -m pytest tests/test_viz.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```powershell
git add src/viz.py tests/test_viz.py
git commit -m "feat: module de visualisation (choroplethes + graphiques)"
```

---

## Task 6: Notebook narratif (`notebooks/analyse_pv_france.ipynb`)

**Files:**
- Create: `scripts/build_notebook.py` (génère le .ipynb via nbformat)
- Create: `notebooks/analyse_pv_france.ipynb` (produit par le script)

**Note:** on génère le notebook par script (reproductible) plutôt qu'à la main.

- [ ] **Step 1: Créer le générateur de notebook `scripts/build_notebook.py`**

```python
"""Genere notebooks/analyse_pv_france.ipynb via nbformat.

Le notebook charge le jeu de donnees (cache), applique le modele economique
par departement, et produit cartes + graphiques. Narratif :
contexte -> donnees -> modele -> resultats -> limites.
"""
import os
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text): cells.append(nbf.v4.new_markdown_cell(text))
def code(src): cells.append(nbf.v4.new_code_cell(src))

md("""# Potentiel photovoltaique tertiaire en France

**Workshop client Oxand** — analyse exploratoire du potentiel PV des toitures
tertiaires (9-500 kWc) a l'echelle departementale, focus rentabilite economique.

> Donnees de gisement : **PVGIS** (JRC, reelles). Hypotheses economiques :
> ordres de grandeur de la note de cadrage (Annexe A), explicitees dans `config.py`.
""")

md("## 1. Chargement des donnees et du modele")
code("""import sys, os
sys.path.insert(0, os.path.abspath(".."))
import pandas as pd
import geopandas as gpd
from src import config, economics as eco, viz
from src.dataset import build_dataset

# Reconstruit (utilise le cache PVGIS si present) et renvoie le GeoDataFrame
gdf = build_dataset()
print("Departements :", len(gdf))
print("Source gisement :", gdf["source"].value_counts().to_dict())
gdf[["code_dept", "nom_dept", "facteur_production", "source"]].head()""")

md("""## 2. Calcul des indicateurs economiques par departement

Installation de reference : **100 kWc**, regime **autoconsommation**
(le plus rentable pour le tertiaire selon la note).""")
code("""P = config.REF_POWER_KWC
REGIME = "autoconso"

def indicateurs(facteur):
    if pd.isna(facteur):
        return pd.Series({"production_MWh": None, "LCOE": None,
                          "payback": None, "TRI": None, "VAN": None})
    cf = eco.cashflows(P, facteur, REGIME)
    irr = eco.irr(cf)
    return pd.Series({
        "production_MWh": eco.annual_production(P, facteur, 1) / 1000,
        "LCOE": eco.lcoe(P, facteur),
        "payback": eco.payback(cf),
        "TRI": irr * 100 if irr is not None else None,
        "VAN": eco.npv(config.DISCOUNT_RATE, cf),
    })

ind = gdf["facteur_production"].apply(indicateurs)
gdf = gdf.join(ind)
gdf[["nom_dept", "facteur_production", "LCOE", "payback", "TRI", "VAN"]].describe()""")

md("## 3. Cartes du potentiel")
code("""viz.choropleth(gdf, "facteur_production",
    "Facteur de production PV (kWh/kWc/an)", legend_label="kWh/kWc/an");""")
code("""viz.choropleth(gdf, "LCOE", "LCOE (EUR/kWh)",
    cmap="viridis_r", legend_label="EUR/kWh");""")
code("""viz.choropleth(gdf, "payback", "Temps de retour (annees)",
    cmap="RdYlGn_r", legend_label="annees");""")
code("""viz.choropleth(gdf, "TRI", "TRI sur 25 ans (%)",
    cmap="RdYlGn", legend_label="%");""")

md("""## 4. Analyse de sensibilite

### 4.1 Effet d'echelle du CAPEX (EUR/kWc) selon la taille""")
code("""sizes = config.SENSITIVITY_SIZES_KWC
capex_unit = [eco.capex_per_kwc(s) for s in sizes]
viz.bar_chart(sizes, capex_unit,
    "Effet d'echelle du CAPEX", "Puissance (kWc)", "EUR/kWc");""")

md("### 4.2 Autoconsommation vs vente — payback pour un departement median")
code("""fac_med = gdf["facteur_production"].median()
pb = {r: [eco.payback(eco.cashflows(s, fac_med, r)) for s in sizes]
      for r in ("autoconso", "vente")}
viz.grouped_bar(sizes, pb,
    f"Payback selon regime (facteur median = {fac_med:.0f})",
    "Puissance (kWc)", "Payback (annees)");""")

md("### 4.3 Dispersion Nord / Sud du facteur de production")
code("""nord = gdf.nsmallest(5, "facteur_production")[["nom_dept", "facteur_production"]]
sud = gdf.nlargest(5, "facteur_production")[["nom_dept", "facteur_production"]]
print("5 plus faibles (Nord) :"); print(nord.to_string(index=False))
print("\\n5 plus eleves (Sud) :"); print(sud.to_string(index=False))""")

md("""## 5. Limites et hypotheses

- **Gisement** : PVGIS, installation type (30 deg, Sud, pertes 14 %). Reel.
- **Couts/tarifs** : hypotheses (Annexe A), non specifiques au batiment.
- **Analyse agregee** : pas d'etude batiment par batiment (= role de Simeo).
- **Indicateurs** : calcules par le modele, reproductibles, auditables via `config.py`.

Ce notebook caracterise le *terrain de jeu* ; il ne constitue pas un module Simeo.
""")

nb["cells"] = cells
os.makedirs("notebooks", exist_ok=True)
with open("notebooks/analyse_pv_france.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("Notebook ecrit : notebooks/analyse_pv_france.ipynb")
```

- [ ] **Step 2: Générer le notebook**

Run: `python scripts/build_notebook.py`
Expected: `Notebook ecrit : notebooks/analyse_pv_france.ipynb`.

- [ ] **Step 3: Exécuter le notebook de bout en bout (validation)**

Run: `python -m jupyter nbconvert --to notebook --execute --inplace notebooks/analyse_pv_france.ipynb`
Expected: exécution sans erreur ; le notebook contient les cartes et graphiques.

- [ ] **Step 4: Lancer toute la suite de tests**

Run: `python -m pytest -v`
Expected: PASS (tous les tests des Tasks 2–5).

- [ ] **Step 5: Commit**

```powershell
git add scripts/build_notebook.py notebooks/analyse_pv_france.ipynb
git commit -m "feat: notebook narratif d'analyse du potentiel PV"
```

---

## Task 7: README et finalisation

**Files:**
- Create: `README.md`

- [ ] **Step 1: Créer `README.md`**

```markdown
# Potentiel PV tertiaire en France — Workshop Oxand

Analyse exploratoire du potentiel photovoltaique des toitures tertiaires
(9-500 kWc) par departement, focus rentabilite (LCOE, payback, TRI, VAN).

## Installation
```
python -m pip install -r requirements.txt
```

## Utilisation
1. Construire le jeu de donnees (PVGIS, ~96 appels, mis en cache) :
   `python -c "from src.dataset import build_dataset; build_dataset()"`
2. Generer le notebook : `python scripts/build_notebook.py`
3. Ouvrir `notebooks/analyse_pv_france.ipynb` dans Jupyter.

## Tests
```
python -m pytest -v
```

## Structure
- `src/config.py` — toutes les hypotheses (CAPEX, OPEX, tarifs...)
- `src/gisement.py` — gisement PVGIS + cache + fallback
- `src/economics.py` — modele economique
- `src/dataset.py` — pipeline de donnees departementales
- `src/viz.py` — cartes et graphiques
- `notebooks/` — le livrable

## Donnees
- Gisement : **PVGIS** (JRC) — reel.
- Couts/tarifs : hypotheses (note de cadrage, Annexe A).
```

- [ ] **Step 2: Commit final**

```powershell
git add README.md
git commit -m "docs: README du projet"
```

---

## Self-review (couverture spec)

- §4 Architecture → Tasks 1–6 (config, gisement, economics, dataset, viz, notebook). ✅
- §5 Modèle de données → Task 4 (centroïdes, merge, CSV consolidé). ✅
- §6 Modèle économique → Task 2 (production, CAPEX/OPEX, cash-flows, LCOE, payback, TRI, VAN, 2 régimes). ✅
- §7 Cas de référence + sensibilité → Task 6 (100 kWc cartographié ; sensibilité 9/100/500 ; autoconso vs vente). ✅
- §8 Visualisations → Task 5 + Task 6 (choroplèthes + barres). ✅
- §9 Tests → Tasks 2–5 (TDD), exécution complète Task 6. ✅
- §10 Stack → Task 1 (deps ; NPV/IRR maison, pas de numpy_financial). ✅
- §3 Transparence données → étiquetage `source`, README, cellule limites. ✅
```
