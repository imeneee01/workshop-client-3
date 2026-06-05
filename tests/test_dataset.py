import geopandas as gpd
from shapely.geometry import Polygon
from src import dataset


def test_centroids_from_geodataframe():
    # Carre centre sur (lon=2, lat=47), en France metropolitaine, ou la
    # projection Lambert-93 (EPSG:2154) utilisee par add_centroids est valide.
    poly = Polygon([(1.8, 46.8), (1.8, 47.2), (2.2, 47.2), (2.2, 46.8)])
    gdf = gpd.GeoDataFrame(
        {"code": ["01"], "nom": ["Test"]},
        geometry=[poly], crs="EPSG:4326",
    )
    out = dataset.add_centroids(gdf)
    assert abs(out.loc[0, "lat"] - 47.0) < 0.01
    assert abs(out.loc[0, "lon"] - 2.0) < 0.01
