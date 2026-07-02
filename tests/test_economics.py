import numpy as np
from src import economics as eco
from src import config


def test_capex_per_kwc_brackets():
    assert eco.capex_per_kwc(20) == 1850.0
    assert eco.capex_per_kwc(50) == 1400.0
    assert eco.capex_per_kwc(300) == 1100.0


def test_capex_total():
    # 100 kWc tombe dans la tranche 100-500 -> 1100 EUR/kWc
    assert eco.capex(100) == 100 * 1100.0


def test_vente_tariff_brackets():
    assert eco.vente_tariff(50) == 0.10
    assert eco.vente_tariff(300) == 0.08


def test_annual_production_degrades():
    p0 = eco.annual_production(100, 1200, year=1)
    p2 = eco.annual_production(100, 1200, year=2)
    assert p0 == 100 * 1200  # annee 1 : pas de degradation
    assert p2 < p0           # annee 2 : degrade


def test_npv_at_zero_rate_equals_sum():
    cf = [-100.0, 30.0, 30.0, 30.0, 30.0]
    assert abs(eco.npv(0.0, cf) - sum(cf)) < 1e-9


def test_npv_discounts_future():
    cf = [-100.0, 110.0]
    # a 10 %, le flux de 110 a l'annee 1 vaut exactement 100 -> NPV = 0
    assert abs(eco.npv(0.10, cf)) < 1e-9


def test_irr_recovers_known_rate():
    cf = [-100.0, 110.0]
    assert abs(eco.irr(cf) - 0.10) < 1e-4


def test_cashflows_structure():
    cf = eco.cashflows(100, 1200, regime="autoconso")
    assert len(cf) == config.PROJECT_YEARS + 1
    assert cf[0] < 0  # annee 0 : investissement
    assert cf[1] > 0  # annee 1 : revenu net positif


def test_inverter_replacement_dips_cashflow():
    cf = eco.cashflows(100, 1200, regime="autoconso")
    y = config.INVERTER_REPLACEMENT_YEAR
    # l'annee de remplacement onduleur a un flux inferieur a l'annee precedente
    assert cf[y] < cf[y - 1]


def test_lcoe_in_plausible_range():
    # cas central : 100 kWc, facteur 1100 -> LCOE attendu ~6-10 c (Annexe A)
    lcoe = eco.lcoe(100, 1100)
    assert 0.04 < lcoe < 0.12


def test_better_gisement_improves_irr():
    low = eco.irr(eco.cashflows(100, 900, regime="autoconso"))
    high = eco.irr(eco.cashflows(100, 1500, regime="autoconso"))
    assert high > low


def test_payback_returns_year_within_horizon():
    pb = eco.payback(eco.cashflows(100, 1300, regime="autoconso"))
    assert 1 <= pb <= config.PROJECT_YEARS


def test_autoconso_price_is_blend_between_vente_and_avoided():
    p = eco.energy_price(100, "autoconso")
    assert eco.vente_tariff(100) < p < config.AUTOCONSO_PRICE


def test_higher_autoconso_rate_increases_price():
    low = eco.energy_price(100, "autoconso", taux_autoconso=0.4)
    high = eco.energy_price(100, "autoconso", taux_autoconso=0.9)
    assert high > low


from src.assumptions import Assumptions


def test_assumptions_default_matches_config_behaviour():
    # passer default() doit donner exactement le meme resultat qu'avant
    a = Assumptions.default()
    assert eco.capex_per_kwc(50, a=a) == eco.capex_per_kwc(50)
    assert eco.lcoe(100, 1100, a=a) == eco.lcoe(100, 1100)


def test_custom_capex_changes_payback():
    base = Assumptions.default()
    from dataclasses import replace
    pricey = replace(base, capex_brackets=((9, 36, 3000.0), (36, 100, 3000.0), (100, 500, 3000.0)))
    pb_base = eco.payback(eco.cashflows(100, 1200, "autoconso", a=base), a=base)
    pb_pricey = eco.payback(eco.cashflows(100, 1200, "autoconso", a=pricey), a=pricey)
    assert pb_pricey > pb_base
