"""Modele economique PV. Fonctions pures, parametrees par Assumptions.

Tous les indicateurs (LCOE, payback, TRI, VAN) sont CALCULES a partir
du gisement (PVGIS, reel) et des hypotheses (Assumptions / config.py).
Le parametre `a` est optionnel : par defaut Assumptions.default().
"""
from src.assumptions import Assumptions


def _bracket_value(power_kwc, brackets):
    """Valeur de la tranche contenant power_kwc. Intervalles [low, high),
    derniere tranche fermee [low, high]. Hors bornes : tranche la plus proche."""
    for i, (low, high, value) in enumerate(brackets):
        if i < len(brackets) - 1:
            if low <= power_kwc < high:
                return value
        else:
            if low <= power_kwc <= high:
                return value
    if power_kwc < brackets[0][0]:
        return brackets[0][2]
    return brackets[-1][2]


def capex_per_kwc(power_kwc, a=None):
    """Cout d'investissement unitaire (EUR/kWc) selon la tranche de taille."""
    a = a or Assumptions.default()
    return _bracket_value(power_kwc, a.capex_brackets)


def capex(power_kwc, a=None):
    """Investissement initial total (EUR)."""
    return power_kwc * capex_per_kwc(power_kwc, a)


def vente_tariff(power_kwc, a=None):
    """Tarif de vente S21 (EUR/kWh) selon la tranche de puissance."""
    a = a or Assumptions.default()
    return _bracket_value(power_kwc, a.vente_tariffs)


def energy_price(power_kwc, regime, taux_autoconso=None, a=None):
    """Prix moyen de valorisation de l'energie (EUR/kWh) selon le regime.

    - 'vente'    : vente totale au tarif S21.
    - 'autoconso': part `taux_autoconso` valorisee au prix evite (autoconso_price),
      surplus vendu au tarif S21.
    """
    a = a or Assumptions.default()
    if regime == "autoconso":
        taux = a.taux_autoconso if taux_autoconso is None else taux_autoconso
        return taux * a.autoconso_price + (1 - taux) * vente_tariff(power_kwc, a)
    if regime == "vente":
        return vente_tariff(power_kwc, a)
    raise ValueError(f"regime inconnu : {regime!r}")


def annual_production(power_kwc, facteur, year, a=None):
    """Production de l'annee `year` (kWh), avec degradation. year >= 1."""
    a = a or Assumptions.default()
    return power_kwc * facteur * (1 - a.degradation) ** (year - 1)


def cashflows(power_kwc, facteur, regime, taux_autoconso=None, a=None):
    """Flux de tresorerie annuels (EUR), annee 0 a project_years."""
    a = a or Assumptions.default()
    invest = capex(power_kwc, a)
    opex = invest * a.opex_rate
    price = energy_price(power_kwc, regime, taux_autoconso, a)
    flows = [-invest]
    for year in range(1, a.project_years + 1):
        revenue = annual_production(power_kwc, facteur, year, a) * price
        cf = revenue - opex
        if year == a.inverter_replacement_year:
            cf -= invest * a.inverter_replacement_rate
        flows.append(cf)
    return flows


def npv(rate, flows):
    """Valeur actuelle nette d'une serie de flux (annee 0 = flows[0])."""
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(flows))


def irr(flows, low=-0.9, high=1.0, tol=1e-7, max_iter=200):
    """Taux de rendement interne par bisection. None si non trouve."""
    f_low, f_high = npv(low, flows), npv(high, flows)
    if f_low * f_high > 0:
        return None
    for _ in range(max_iter):
        mid = (low + high) / 2
        f_mid = npv(mid, flows)
        if abs(f_mid) < tol:
            return mid
        if f_low * f_mid < 0:
            high, f_high = mid, f_mid
        else:
            low, f_low = mid, f_mid
    return (low + high) / 2


def lcoe(power_kwc, facteur, a=None):
    """Cout moyen actualise de l'energie (EUR/kWh)."""
    a = a or Assumptions.default()
    invest = capex(power_kwc, a)
    opex = invest * a.opex_rate
    r = a.discount_rate
    disc_costs = invest
    disc_energy = 0.0
    for year in range(1, a.project_years + 1):
        disc_costs += opex / (1 + r) ** year
        if year == a.inverter_replacement_year:
            disc_costs += invest * a.inverter_replacement_rate / (1 + r) ** year
        disc_energy += annual_production(power_kwc, facteur, year, a) / (1 + r) ** year
    return disc_costs / disc_energy


def payback(flows, discounted=False, a=None):
    """Temps de retour (annees). project_years + 1 si jamais rembourse."""
    a = a or Assumptions.default()
    r = a.discount_rate if discounted else 0.0
    cumul = 0.0
    for t, cf in enumerate(flows):
        cumul += cf / (1 + r) ** t
        if t > 0 and cumul >= 0:
            return t
    return a.project_years + 1
