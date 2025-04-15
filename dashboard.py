
import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
df_resistance = pd.read_csv("data/weekly_resistance.csv")
df_phenotypes = pd.read_csv("data/phenotype_weekly.csv")

st.title("Dashboard de Résistance Antibiotique - SCN (hors aureus)")

# ----- Section 1 : Résistance hebdomadaire -----
st.header("Évolution hebdomadaire de la résistance")

ab_selected = st.selectbox("Choisir un antibiotique :", df_resistance["Antibiotique"].unique())
df_ab = df_resistance[df_resistance["Antibiotique"] == ab_selected]

fig = px.line(df_ab, x="Semaine", y="%R", title=f"% de Résistance à {ab_selected} par semaine",
              markers=True, color_discrete_sequence=["#EF553B"])

# Ajouter les alertes
alertes = df_ab[df_ab["Alerte"] == True]
fig.add_scatter(x=alertes["Semaine"], y=alertes["%R"],
                mode="markers", marker=dict(color='red', size=10),
                name="Alerte")

st.plotly_chart(fig, use_container_width=True)

# ----- Section 2 : Phénotypes -----
st.header("Phénotypes SCN par semaine")

df_phenotypes = df_phenotypes.set_index("Semaine")
fig2 = px.area(df_phenotypes, title="Distribution des phénotypes SCN (SRM, SRV, Wild, Other)")
st.plotly_chart(fig2, use_container_width=True)
