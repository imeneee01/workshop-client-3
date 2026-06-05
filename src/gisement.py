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
