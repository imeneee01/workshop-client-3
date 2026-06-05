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
