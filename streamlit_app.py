"""Dashboard interactif du potentiel PV tertiaire par departement.

Reutilise src/ (aucune logique metier ici). Les hypotheses sont modifiables
via la barre laterale ; tous les indicateurs se recalculent en direct.
Lancement local : streamlit run streamlit_app.py
"""
from dataclasses import replace
import pandas as pd
import streamlit as st

from src.assumptions import Assumptions
from src import dashboard_data as dd
from src import economics as eco
from src import viz

st.set_page_config(page_title="Potentiel photovoltaïque tertiaire — France", layout="wide")


@st.cache_data
def _base_table():
    return dd.load_departements()


@st.cache_data
def _geo():
    return dd.load_geodata()


st.title("Potentiel photovoltaïque tertiaire en France")
st.caption("Toitures 9-500 kWc — données PVGIS (réelles) + hypothèses ajustables")

# --- Barre laterale : hypotheses ---
base = Assumptions.default()
with st.sidebar:
    st.header("Hypothèses")
    regime = st.selectbox("Régime de valorisation", ["autoconso", "vente"])
    power = st.select_slider("Puissance (kWc)", options=[9.0, 36.0, 100.0, 250.0, 500.0], value=100.0)
    opex = st.slider("OPEX (% du CAPEX/an)", 0.5, 3.0, base.opex_rate * 100, 0.1) / 100
    autoconso_price = st.slider("Prix évité autoconso (c/kWh)", 10.0, 30.0, base.autoconso_price * 100, 0.5) / 100
    taux = st.slider("Taux d'autoconsommation (%)", 30, 100, int(base.taux_autoconso * 100)) / 100
    discount = st.slider("Taux d'actualisation (%)", 0.0, 10.0, base.discount_rate * 100, 0.5) / 100
    capex_mult = st.slider("CAPEX (multiplicateur)", 0.6, 1.6, 1.0, 0.05)

scaled_capex = tuple((lo, hi, val * capex_mult) for lo, hi, val in base.capex_brackets)
a = replace(
    base, opex_rate=opex, autoconso_price=autoconso_price,
    taux_autoconso=taux, discount_rate=discount, capex_brackets=scaled_capex,
)

df = dd.compute_indicators(_base_table(), power, regime, a=a)

# --- Vue nationale : KPI ---
st.subheader("Synthèse nationale")
c1, c2, c3, c4 = st.columns(4)
c1.metric("LCOE moyen", f"{df['lcoe'].mean()*100:.1f} c/kWh")
c2.metric("Payback moyen", f"{df['payback'].mean():.1f} ans")
c3.metric("TRI moyen", f"{df['tri'].mean()*100:.1f} %")
c4.metric("VAN moyenne", f"{df['van'].mean()/1000:.0f} k EUR")

# --- Carte choroplethe ---
st.subheader("Cartographie")
indic = st.selectbox("Indicateur cartographie", ["facteur_production", "lcoe", "payback", "tri"])
gdf = _geo().drop(columns=["nom_dept"], errors="ignore").merge(df, on="code_dept", how="left")
labels = {"facteur_production": "kWh/kWc/an", "lcoe": "EUR/kWh", "payback": "annees", "tri": "TRI"}
fig = viz.choropleth(gdf, indic, f"{indic} par département", legend_label=labels[indic])
st.pyplot(fig)

# --- Vue departement ---
st.subheader("Détail par département")
choix = st.selectbox("Département", df["nom_dept"] if "nom_dept" in df else df["code_dept"])
key = "nom_dept" if "nom_dept" in df else "code_dept"
row = df[df[key] == choix].iloc[0]
d1, d2, d3, d4 = st.columns(4)
d1.metric("LCOE", f"{row['lcoe']*100:.1f} c/kWh")
d2.metric("Payback", f"{row['payback']:.0f} ans")
d3.metric("TRI", f"{row['tri']*100:.1f} %")
d4.metric("VAN", f"{row['van']/1000:.0f} k EUR")

flows = eco.cashflows(power, row["facteur_production"], regime, a=a)
cumul = pd.Series(flows).cumsum()
st.line_chart(pd.DataFrame({"Cash-flow cumulé (EUR)": cumul}))

# --- Sensibilite ---
st.subheader("Sensibilité au taux d'autoconsommation")
rows = []
for t in [0.40, 0.65, 0.90]:
    at = replace(a, taux_autoconso=t)
    dt = dd.compute_indicators(_base_table(), power, "autoconso", a=at)
    rows.append({"taux_autoconso": f"{int(t*100)} %", "TRI moyen (%)": dt["tri"].mean() * 100})
st.bar_chart(pd.DataFrame(rows).set_index("taux_autoconso"))

# --- Donnees + telechargement ---
st.subheader("Données")
st.dataframe(df)
st.download_button("Télécharger le CSV", df.to_csv(index=False), "departements_pv_indicateurs.csv")
