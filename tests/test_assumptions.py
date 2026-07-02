from src.assumptions import Assumptions
from src import config


def test_default_reflects_config():
    a = Assumptions.default()
    assert a.discount_rate == config.DISCOUNT_RATE
    assert a.project_years == config.PROJECT_YEARS
    assert a.opex_rate == config.OPEX_RATE
    assert a.autoconso_price == config.AUTOCONSO_PRICE
    assert a.taux_autoconso == config.TAUX_AUTOCONSO


def test_capex_brackets_copied_as_tuple():
    a = Assumptions.default()
    assert tuple(a.capex_brackets) == tuple(config.CAPEX_BRACKETS)
    assert tuple(a.vente_tariffs) == tuple(config.VENTE_TARIFFS)


def test_frozen_is_immutable():
    a = Assumptions.default()
    try:
        a.opex_rate = 0.5
        assert False, "devrait etre immuable"
    except Exception:
        pass
