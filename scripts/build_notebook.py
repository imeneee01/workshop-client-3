"""Genere notebooks/analyse_pv_france.ipynb via nbformat.

Le notebook charge le jeu de donnees (cache), applique le modele economique
par departement, et produit cartes + graphiques. Narratif :
contexte -> donnees -> modele -> resultats -> limites.
"""
import os
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text): cells.append(nbf.v4.new_markdown_cell(text))
def code(src): cells.append(nbf.v4.new_code_cell(src))

md("""# Potentiel photovoltaique tertiaire en France

**Workshop client Oxand** — analyse exploratoire du potentiel PV des toitures
tertiaires (9-500 kWc) a l'echelle departementale, focus rentabilite economique.

> Donnees de gisement : **PVGIS** (JRC, reelles). Hypotheses economiques :
> ordres de grandeur de la note de cadrage (Annexe A), explicitees dans `config.py`.
""")

md("## 1. Chargement des donnees et du modele")
code("""import sys, os
# Se placer a la racine du projet pour que les imports et les chemins
# relatifs de config.py (data/...) fonctionnent, quel que soit le dossier de lancement.
_here = os.getcwd()
if os.path.basename(_here) == "notebooks":
    os.chdir("..")
sys.path.insert(0, os.path.abspath("."))
import pandas as pd
import geopandas as gpd
from src import config, economics as eco, viz
from src.dataset import build_dataset

# Reconstruit (utilise le cache PVGIS si present) et renvoie le GeoDataFrame
gdf = build_dataset()
print("Departements :", len(gdf))
print("Source gisement :", gdf["source"].value_counts().to_dict())
gdf[["code_dept", "nom_dept", "facteur_production", "source"]].head()""")

md("""## 2. Calcul des indicateurs economiques par departement

Installation de reference : **100 kWc**, regime **autoconsommation avec vente
du surplus** (taux d'autoconso = 65 %, le plus rentable pour le tertiaire
selon la note). Voir la sensibilite a ce taux en section 4.4.""")
code("""P = config.REF_POWER_KWC
REGIME = "autoconso"

def indicateurs(facteur):
    if pd.isna(facteur):
        return pd.Series({"production_MWh": None, "LCOE": None,
                          "payback": None, "TRI": None, "VAN": None})
    cf = eco.cashflows(P, facteur, REGIME)
    irr = eco.irr(cf)
    return pd.Series({
        "production_MWh": eco.annual_production(P, facteur, 1) / 1000,
        "LCOE": eco.lcoe(P, facteur),
        "payback": eco.payback(cf),
        "TRI": irr * 100 if irr is not None else None,
        "VAN": eco.npv(config.DISCOUNT_RATE, cf),
    })

ind = gdf["facteur_production"].apply(indicateurs)
gdf = gdf.join(ind)
gdf[["nom_dept", "facteur_production", "LCOE", "payback", "TRI", "VAN"]].describe()""")

md("## 3. Cartes du potentiel")
code("""viz.choropleth(gdf, "facteur_production",
    "Facteur de production PV (kWh/kWc/an)", legend_label="kWh/kWc/an");""")
code("""viz.choropleth(gdf, "LCOE", "LCOE (EUR/kWh)",
    cmap="viridis_r", legend_label="EUR/kWh");""")
code("""viz.choropleth(gdf, "payback", "Temps de retour (annees)",
    cmap="RdYlGn_r", legend_label="annees");""")
code("""viz.choropleth(gdf, "TRI", "TRI sur 25 ans (%)",
    cmap="RdYlGn", legend_label="%");""")

md("""## 4. Analyse de sensibilite

### 4.1 Effet d'echelle du CAPEX (EUR/kWc) selon la taille""")
code("""sizes = config.SENSITIVITY_SIZES_KWC
capex_unit = [eco.capex_per_kwc(s) for s in sizes]
viz.bar_chart(sizes, capex_unit,
    "Effet d'echelle du CAPEX", "Puissance (kWc)", "EUR/kWc");""")

md("### 4.2 Autoconsommation vs vente — payback pour un departement median")
code("""fac_med = gdf["facteur_production"].median()
pb = {r: [eco.payback(eco.cashflows(s, fac_med, r)) for s in sizes]
      for r in ("autoconso", "vente")}
viz.grouped_bar(sizes, pb,
    f"Payback selon regime (facteur median = {fac_med:.0f})",
    "Puissance (kWc)", "Payback (annees)");""")

md("### 4.3 Dispersion Nord / Sud du facteur de production")
code("""nord = gdf.nsmallest(5, "facteur_production")[["nom_dept", "facteur_production"]]
sud = gdf.nlargest(5, "facteur_production")[["nom_dept", "facteur_production"]]
print("5 plus faibles (Nord) :"); print(nord.to_string(index=False))
print("\\n5 plus eleves (Sud) :"); print(sud.to_string(index=False))""")

md("""### 4.4 Sensibilite au taux d'autoconsommation

Le TRI en autoconsommation depend fortement de la part reellement consommee
sur place. On fait varier ce taux pour un departement median.""")
code('''fac_med = gdf["facteur_production"].median()
rows = []
for taux in config.AUTOCONSO_RATES:
    cf = eco.cashflows(config.REF_POWER_KWC, fac_med, "autoconso", taux_autoconso=taux)
    irr = eco.irr(cf)
    rows.append({"taux_autoconso": f"{taux:.0%}",
                 "TRI_%": round(irr * 100, 1) if irr else None,
                 "payback_ans": eco.payback(cf)})
import pandas as pd
sensib = pd.DataFrame(rows)
print(sensib.to_string(index=False))
viz.bar_chart(sensib["taux_autoconso"], sensib["TRI_%"],
    f"Sensibilite du TRI au taux d'autoconsommation (facteur median = {fac_med:.0f})",
    "Taux d'autoconsommation", "TRI (%)");''')

md("""## 5. Limites et hypotheses

- **Gisement** : PVGIS, installation type (30 deg, Sud, pertes 14 %). Reel.
- **Couts/tarifs** : hypotheses (Annexe A), non specifiques au batiment.
- **Autoconsommation** : modelisee avec un taux de 65 % (surplus vendu au tarif S21).
  Le TRI y est eleve, ce qui rejoint le constat de rentabilite de la note (section 1.2) ;
  la vente totale (payback 9-15 ans) recoupe le benchmark conservateur.
- **Sensibilite** : le taux d'autoconsommation est le parametre le plus influent (section 4.4).
- **Analyse agregee** : pas d'etude batiment par batiment (= role de Simeo).
- **Indicateurs** : calcules par le modele, reproductibles, auditables via `config.py`.

Ce notebook caracterise le *terrain de jeu* ; il ne constitue pas un module Simeo.
""")

nb["cells"] = cells
os.makedirs("notebooks", exist_ok=True)
with open("notebooks/analyse_pv_france.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("Notebook ecrit : notebooks/analyse_pv_france.ipynb")
