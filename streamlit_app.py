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
from src import viz

st.set_page_config(page_title="Potentiel photovoltaïque tertiaire — France", layout="wide")


@st.cache_data
def _base_table():
    return dd.load_departements()


@st.cache_data
def _geo():
    return dd.load_geodata()


st.title("Potentiel photovoltaïque tertiaire en France")
st.caption("Toitures 9-500 kWc — données PVGIS (réelles) + hypothèses économiques fixes")

# --- Barre laterale : choix du scenario (hypotheses figees) ---
a = Assumptions.default()
with st.sidebar:
    st.header("Scénario")
    regime = st.selectbox("Régime de valorisation", ["autoconso", "vente"])
    power = st.select_slider("Puissance (kWc)", options=[9.0, 36.0, 100.0, 250.0, 500.0], value=100.0)
    st.divider()
    st.caption(
        "Hypothèses économiques fixes (note de cadrage) : "
        "CAPEX 1100-1850 EUR/kWc selon la taille, OPEX 1,5 %/an, "
        "onduleur remplacé en année 12, autoconsommation 65 % valorisée à 0,20 EUR/kWh, "
        "actualisation 4 %, durée 25 ans."
    )

df = dd.compute_indicators(_base_table(), power, regime, a=a)

# --- Vue nationale : KPI ---
st.subheader("Synthèse nationale")
c1, c2, c3, c4 = st.columns(4)
c1.metric("LCOE moyen", f"{df['lcoe'].mean()*100:.1f} c/kWh")
c2.metric("Payback moyen", f"{df['payback'].mean():.1f} ans")
c3.metric("TRI moyen", f"{df['tri'].mean()*100:.1f} %")
c4.metric("VAN moyenne", f"{df['van'].mean()/1000:.0f} k EUR")

if regime == "vente":
    st.caption(
        "⚠️ En vente totale, l'électricité est revendue à bas tarif (8-13 c/kWh) : "
        "la rentabilité est faible. L'autoconsommation est nettement plus rentable "
        "— changez de régime pour comparer."
    )
else:
    st.caption(
        "Scénario autoconsommation : 65 % de la production est consommée sur place "
        "(prix évité ~20 c/kWh), le surplus est revendu."
    )

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
tri_txt = f"{row['tri']*100:.1f} %" if pd.notna(row["tri"]) else "n/d"
d1, d2, d3, d4 = st.columns(4)
d1.metric("LCOE", f"{row['lcoe']*100:.1f} c/kWh")
d2.metric("Payback", f"{row['payback']:.0f} ans")
d3.metric("TRI", tri_txt)
d4.metric("VAN", f"{row['van']/1000:.0f} k EUR")

# Verdict clair, en langage simple
if row["van"] > 0:
    st.success(
        f"Rentable : investissement remboursé en {row['payback']:.0f} ans, "
        f"pour un gain net d'environ {row['van']/1000:.0f} k EUR sur 25 ans."
    )
else:
    st.warning(
        f"Peu rentable dans ce scénario (régime « {regime} ») : la VAN est négative "
        f"({row['van']/1000:.0f} k EUR). En autoconsommation, ce département redevient rentable."
    )

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
table = pd.DataFrame({
    "Département": df["nom_dept"] if "nom_dept" in df else df["code_dept"],
    "Production (kWh/kWc/an)": df["facteur_production"].round(0).astype("Int64"),
    "LCOE (c/kWh)": (df["lcoe"] * 100).round(1),
    "Payback (ans)": df["payback"].round(0).astype("Int64"),
    "TRI (%)": (df["tri"] * 100).round(1),
    "VAN (k EUR)": (df["van"] / 1000).round(0).astype("Int64"),
})
st.dataframe(table, hide_index=True, use_container_width=True)
st.download_button("Télécharger le CSV", df.to_csv(index=False), "departements_pv_indicateurs.csv")
