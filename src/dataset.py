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
    """Ajoute lat/lon du centroide de chaque geometrie.

    Le centroide est calcule en projection metrique Lambert-93 (EPSG:2154)
    puis reprojete en WGS84, ce qui est correct geometriquement et evite
    l'avertissement de geopandas sur le calcul en CRS geographique.
    """
    gdf = gdf.copy()
    cent = gdf.geometry.to_crs(2154).centroid.to_crs(4326)
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
