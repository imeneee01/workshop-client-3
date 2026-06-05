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
