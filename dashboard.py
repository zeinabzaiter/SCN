import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Chargement des fichiers de données
phenotype_df = pd.read_csv("phenotype_weekly.csv")
resistance_df = pd.read_excel("Tests_Resistances_mensuelles_FINAL.xlsx", engine="openpyxl")

# Titre du Dashboard
st.title("📊 Dashboard de Suivi des Phénotypes et Résistances Antibiotiques")

st.markdown("---")

# --- SECTION 1: Evolution hebdomadaire des phénotypes ---
st.subheader("🕰️ Evolution hebdomadaire des phénotypes")

# Transformation pour graphe interactif
df_long = phenotype_df.melt(id_vars="Semaine", var_name="Phénotype", value_name="Nombre de cas")
fig1 = px.line(
    df_long,
    x="Semaine",
    y="Nombre de cas",
    color="Phénotype",
    markers=True,
    title="Evolution des phénotypes par semaine",
    hover_name="Phénotype",
    hover_data={"Semaine": True, "Nombre de cas": True}
)
fig1.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# --- SECTION 2: Résistances antibiotiques avec seuils d'alerte ---
st.subheader("🦠 Pourcentage de résistance aux antibiotiques (alerte si > moyenne + 2σ)")
alertes = []
resistance_df["Mois"] = pd.to_datetime(resistance_df["Mois"])
antibiotiques = resistance_df.columns[1:]

for ab in antibiotiques:
    st.markdown(f"### {ab}")
    values = resistance_df[ab]
    dates = resistance_df["Mois"]
    moyenne = values.mean()
    ecart_type = values.std()
    seuil = moyenne + 2 * ecart_type

    df_ab = pd.DataFrame({"Date": dates, "Valeur": values})
    fig = px.line(df_ab, x="Date", y="Valeur", markers=True, title=f"{ab} - Résistance mensuelle")
    fig.add_hline(y=seuil, line_dash="dash", line_color="red", annotation_text=f"Seuil Alerte ({seuil:.1f})")
    st.plotly_chart(fig, use_container_width=True)

    if values.iloc[-1] > seuil:
        alertes.append({"Antibiotique": ab, "Valeur": values.iloc[-1], "Seuil": seuil})

st.markdown("---")

# --- SECTION 3: Tableau des alertes ---
st.subheader("🚨 Alertes sur les résistances (valeurs > moyenne + 2σ)")
if alertes:
    alert_df = pd.DataFrame(alertes)
    st.dataframe(alert_df.style.applymap(lambda x: 'background-color: red' if isinstance(x, (int, float)) and x > 0 else ''))
else:
    st.success("Aucune alerte actuelle 🎉")
