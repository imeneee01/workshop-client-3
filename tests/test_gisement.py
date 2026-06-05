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
