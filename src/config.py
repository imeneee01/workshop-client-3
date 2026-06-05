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
