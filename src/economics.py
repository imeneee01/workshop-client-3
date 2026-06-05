"""Modele economique PV. Fonctions pures, parametrees par config.py.

Tous les indicateurs (LCOE, payback, TRI, VAN) sont CALCULES a partir
du gisement (PVGIS, reel) et des hypotheses (config.py).
"""
from src import config


def capex_per_kwc(power_kwc):
    """Cout d'investissement unitaire (EUR/kWc) selon la tranche de taille."""
    brackets = config.CAPEX_BRACKETS
    for i, (low, high, value) in enumerate(brackets):
        if i < len(brackets) - 1:
            # intervalle semi-ouvert [low, high) pour eviter les chevauchements
            if low <= power_kwc < high:
                return value
        else:
            # derniere tranche : intervalle ferme [low, high]
            if low <= power_kwc <= high:
                return value
    # hors bornes : on prend la tranche la plus proche
    if power_kwc < brackets[0][0]:
        return brackets[0][2]
    return brackets[-1][2]


def capex(power_kwc):
    """Investissement initial total (EUR)."""
    return power_kwc * capex_per_kwc(power_kwc)


def vente_tariff(power_kwc):
    """Tarif de vente S21 (EUR/kWh) selon la tranche de puissance."""
    for low, high, value in config.VENTE_TARIFFS:
        if low < power_kwc <= high:
            return value
    return config.VENTE_TARIFFS[-1][2]


def energy_price(power_kwc, regime, taux_autoconso=None):
    """Prix moyen de valorisation de l'energie (EUR/kWh) selon le regime.

    - 'vente'    : vente totale au tarif S21.
    - 'autoconso': autoconsommation avec vente du surplus. La part `taux_autoconso`
      (par defaut config.TAUX_AUTOCONSO) est valorisee au prix evite
      (AUTOCONSO_PRICE), le surplus est vendu au tarif S21.
    """
    if regime == "autoconso":
        taux = config.TAUX_AUTOCONSO if taux_autoconso is None else taux_autoconso
        return taux * config.AUTOCONSO_PRICE + (1 - taux) * vente_tariff(power_kwc)
    if regime == "vente":
        return vente_tariff(power_kwc)
    raise ValueError(f"regime inconnu : {regime!r}")


def annual_production(power_kwc, facteur, year):
    """Production de l'annee `year` (kWh), avec degradation. year >= 1."""
    return power_kwc * facteur * (1 - config.DEGRADATION) ** (year - 1)


def cashflows(power_kwc, facteur, regime, taux_autoconso=None):
    """Flux de tresorerie annuels (EUR), annee 0 a PROJECT_YEARS."""
    invest = capex(power_kwc)
    opex = invest * config.OPEX_RATE
    price = energy_price(power_kwc, regime, taux_autoconso)
    flows = [-invest]  # annee 0
    for year in range(1, config.PROJECT_YEARS + 1):
        revenue = annual_production(power_kwc, facteur, year) * price
        cf = revenue - opex
        if year == config.INVERTER_REPLACEMENT_YEAR:
            cf -= invest * config.INVERTER_REPLACEMENT_RATE
        flows.append(cf)
    return flows


def npv(rate, flows):
    """Valeur actuelle nette d'une serie de flux (annee 0 = flows[0])."""
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(flows))


def irr(flows, low=-0.9, high=1.0, tol=1e-7, max_iter=200):
    """Taux de rendement interne par bisection. None si non trouve."""
    f_low, f_high = npv(low, flows), npv(high, flows)
    if f_low * f_high > 0:
        return None  # pas de changement de signe sur l'intervalle
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


def lcoe(power_kwc, facteur):
    """Cout moyen actualise de l'energie (EUR/kWh)."""
    invest = capex(power_kwc)
    opex = invest * config.OPEX_RATE
    r = config.DISCOUNT_RATE
    disc_costs = invest
    disc_energy = 0.0
    for year in range(1, config.PROJECT_YEARS + 1):
        disc_costs += opex / (1 + r) ** year
        if year == config.INVERTER_REPLACEMENT_YEAR:
            disc_costs += invest * config.INVERTER_REPLACEMENT_RATE / (1 + r) ** year
        disc_energy += annual_production(power_kwc, facteur, year) / (1 + r) ** year
    return disc_costs / disc_energy


def payback(flows, discounted=False):
    """Temps de retour (annees). PROJECT_YEARS + 1 si jamais rembourse."""
    r = config.DISCOUNT_RATE if discounted else 0.0
    cumul = 0.0
    for t, cf in enumerate(flows):
        cumul += cf / (1 + r) ** t
        if t > 0 and cumul >= 0:
            return t
    return config.PROJECT_YEARS + 1
