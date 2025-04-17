import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

# Chargement des fichiers de données
phenotype_df = pd.read_csv("phenotype_weekly.csv")
resistance_df = pd.read_excel("Tests_Resistances_mensuelles_FINAL.xlsx", engine="openpyxl")
df_scn = pd.read_excel("SCN filtred.xlsx")

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

# --- SECTION 2: Evolution hebdomadaire des résistances par antibiotique (courbes) ---
st.subheader("📈 Evolution hebdomadaire des résistances par antibiotique (%)")

# Sélecteur interactif
tous_les_antibios = ["Vancomycin", "Teicoplanin", "Gentamycin", "Oxacilline", "Clindamycin", "Linezolid", "Daptomycin"]
antibiotiques_selectionnes = st.multiselect("Choisir les antibiotiques à afficher :", tous_les_antibios, default=tous_les_antibios)

# Préparation des données
antibiotiques = tous_les_antibios.copy()
df_scn["DATE_PRELEVEMENT"] = pd.to_datetime(df_scn["DATE_PRELEVEMENT"], dayfirst=True, errors="coerce")
df_scn = df_scn[df_scn["DATE_PRELEVEMENT"].notna()]
df_scn["Semaine"] = df_scn["DATE_PRELEVEMENT"].dt.to_period("W").dt.start_time

weekly_resistance = []
for semaine, group in df_scn.groupby("Semaine"):
    for ab in antibiotiques:
        total = group[ab].notna().sum()
        if total > 0:
            resistant = (group[ab] == "R").sum()
            data = {
                "Semaine": semaine,
                "Antibiotique": ab,
                "Resistance": resistant / total * 100,
                "Total": total,
                "Resistant": resistant
            }
            weekly_resistance.append(data)

df_weekly_resistance = pd.DataFrame(weekly_resistance)
df_weekly_resistance = df_weekly_resistance[df_weekly_resistance["Antibiotique"].isin(antibiotiques_selectionnes)]

fig2 = px.line(
    df_weekly_resistance,
    x="Semaine",
    y="Resistance",
    color="Antibiotique",
    markers=True,
    title="Taux de résistance hebdomadaire (%) par antibiotique",
    hover_name="Antibiotique",
    hover_data={"Semaine": True, "Resistance": ".2f", "Total": True, "Resistant": True}
)
fig2.update_traces(hovertemplate="Semaine : %{x}<br>%{fullData.name} : %{y:.2f}%")
fig2.update_layout(xaxis_tickangle=45, yaxis_title="% Résistance")
st.plotly_chart(fig2, use_container_width=True)

# --- DÉTECTION DE TENDANCE ---
st.markdown("### 📈 Tendance de la résistance par antibiotique")
tendance_messages = []
for ab in antibiotiques_selectionnes:
    df_ab = df_weekly_resistance[df_weekly_resistance["Antibiotique"] == ab].copy()
    if len(df_ab) >= 2:
        x = np.arange(len(df_ab))
        y = df_ab["Resistance"].values
        coef = np.polyfit(x, y, 1)[0]  # pente de la régression linéaire

        if coef > 0.5:
            tendance_messages.append(f"🔺 Résistance en **hausse** pour {ab} (pente : {coef:.2f})")
        elif coef < -0.5:
            tendance_messages.append(f"🔻 Résistance en **baisse** pour {ab} (pente : {coef:.2f})")
        else:
            tendance_messages.append(f"➖ Résistance **stable** pour {ab} (pente : {coef:.2f})")

if tendance_messages:
    for msg in tendance_messages:
        st.markdown(msg)
else:
    st.info("Pas assez de données pour détecter une tendance.")

# --- CO-RÉSISTANCE ---
st.markdown("---")
st.subheader("🔗 Co-résistance entre antibiotiques")
co_resistances = []
semaine_unique = df_weekly_resistance["Semaine"].max()
df_last_week = df_scn[df_scn["Semaine"] == semaine_unique]

for i, ab1 in enumerate(antibiotiques_selectionnes):
    for ab2 in antibiotiques_selectionnes[i+1:]:
        total = df_last_week[[ab1, ab2]].dropna().shape[0]
        if total > 0:
            both_r = df_last_week[(df_last_week[ab1] == "R") & (df_last_week[ab2] == "R")].shape[0]
            pourcentage = both_r / total * 100
            co_resistances.append({"Antibiotique 1": ab1, "Antibiotique 2": ab2, "% Co-résistance": round(pourcentage, 2)})

if co_resistances:
    st.dataframe(pd.DataFrame(co_resistances))
else:
    st.info("Pas de données suffisantes pour la co-résistance.")
