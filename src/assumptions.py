"""Hypotheses economiques regroupees en objet immuable et modifiable a chaud.

Les valeurs par defaut proviennent de config.py (source unique). Le dashboard
injecte des instances modifiees ; le reste du code peut ignorer ce parametre
(defaut = Assumptions.default()), ce qui garde la retrocompatibilite.
"""
from dataclasses import dataclass
from src import config


@dataclass(frozen=True)
class Assumptions:
    discount_rate: float
    project_years: int
    degradation: float
    capex_brackets: tuple
    opex_rate: float
    inverter_replacement_year: int
    inverter_replacement_rate: float
    autoconso_price: float
    taux_autoconso: float
    vente_tariffs: tuple

    @staticmethod
    def default():
        return Assumptions(
            discount_rate=config.DISCOUNT_RATE,
            project_years=config.PROJECT_YEARS,
            degradation=config.DEGRADATION,
            capex_brackets=tuple(config.CAPEX_BRACKETS),
            opex_rate=config.OPEX_RATE,
            inverter_replacement_year=config.INVERTER_REPLACEMENT_YEAR,
            inverter_replacement_rate=config.INVERTER_REPLACEMENT_RATE,
            autoconso_price=config.AUTOCONSO_PRICE,
            taux_autoconso=config.TAUX_AUTOCONSO,
            vente_tariffs=tuple(config.VENTE_TARIFFS),
        )
