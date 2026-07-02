"""Couche de preparation des donnees pour le dashboard Streamlit.

Aucune logique UI ici : fonctions pures, testables, qui enrichissent la table
departementale avec les indicateurs economiques calcules.
"""
import pandas as pd
from src import config, economics as eco
from src.assumptions import Assumptions


def compute_indicators(df, power_kwc, regime, a=None):
    """Enrichit `df` (colonne facteur_production requise) avec lcoe, payback,
    tri, van pour la puissance et le regime donnes."""
    a = a or Assumptions.default()
    out = df.copy()
    lcoe_v, pb_v, tri_v, van_v = [], [], [], []
    for facteur in out["facteur_production"]:
        flows = eco.cashflows(power_kwc, facteur, regime, a=a)
        lcoe_v.append(eco.lcoe(power_kwc, facteur, a=a))
        pb_v.append(eco.payback(flows, a=a))
        tri_v.append(eco.irr(flows))
        van_v.append(eco.npv(a.discount_rate, flows))
    out["lcoe"] = lcoe_v
    out["payback"] = pb_v
    out["tri"] = tri_v
    out["van"] = van_v
    return out


def load_departements(csv_path=None):
    """Charge la table departementale processed (sans geometrie)."""
    path = csv_path or config.PROCESSED_CSV
    return pd.read_csv(path, dtype={"code_dept": str})


def load_geodata(geojson_path=None):
    """Charge le GeoJSON des departements en GeoDataFrame (pour les cartes).
    Import geopandas en local pour ne pas alourdir les imports quand inutile."""
    import geopandas as gpd
    path = geojson_path or config.GEOJSON_PATH
    gdf = gpd.read_file(path)
    return gdf.rename(columns={"code": "code_dept", "nom": "nom_dept"})
