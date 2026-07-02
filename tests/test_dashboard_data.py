import pandas as pd
from dataclasses import replace
from src.dashboard_data import compute_indicators
from src.assumptions import Assumptions


def _df():
    return pd.DataFrame({"code_dept": ["01", "06"], "facteur_production": [1050.0, 1400.0]})


def test_adds_indicator_columns():
    out = compute_indicators(_df(), 100.0, "autoconso")
    for col in ("lcoe", "payback", "tri", "van"):
        assert col in out.columns
    assert len(out) == 2


def test_higher_gisement_higher_van():
    out = compute_indicators(_df(), 100.0, "autoconso").set_index("code_dept")
    assert out.loc["06", "van"] > out.loc["01", "van"]


def test_higher_capex_increases_lcoe():
    base = Assumptions.default()
    pricey = replace(base, capex_brackets=((9, 36, 3000.0), (36, 100, 3000.0), (100, 500, 3000.0)))
    lo = compute_indicators(_df(), 100.0, "autoconso", a=base)["lcoe"].mean()
    hi = compute_indicators(_df(), 100.0, "autoconso", a=pricey)["lcoe"].mean()
    assert hi > lo
