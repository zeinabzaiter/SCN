import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

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
antibiotiques = ["Vancomycin", "Teicoplanin", "Gentamycin", "Oxacilline", "Clindamycin", "Linezolid", "Daptomycin"]
df_scn["DATE_PRELEVEMENT"] = pd.to_datetime(df_scn["DATE_PRELEVEMENT"], dayfirst=True, errors="coerce")
df_scn = df_scn[df_scn["DATE_PRELEVEMENT"].notna()]
df_scn["Semaine"] = df_scn["DATE_PRELEVEMENT"].dt.to_period("W").dt.start_time

weekly_resistance = []
for semaine, group in df_scn.groupby("Semaine"):
    data = {"Semaine": semaine}
    for ab in antibiotiques:
        total = group[ab].notna().sum()
        if total > 0:
            resistant = (group[ab] == "R").sum()
            data["Resistance"] = resistant / total * 100
            data["Antibiotique"] = ab
            weekly_resistance.append(data.copy())

df_weekly_resistance = pd.DataFrame(weekly_resistance)

# Filtrage des antibiotiques selon la sélection de l'utilisateur
df_weekly_resistance = df_weekly_resistance[df_weekly_resistance["Antibiotique"].isin(antibiotiques_selectionnes)]

fig2 = px.line(
    df_weekly_resistance,
    x="Semaine",
    y="Resistance",
    color="Antibiotique",
    markers=True,
    title="Taux de résistance hebdomadaire (%) par antibiotique",
    hover_name="Antibiotique",
    hover_data={"Semaine": True, "Resistance": ".2f"}
)
fig2.update_traces(hovertemplate="Semaine : %{x}<br>%{fullData.name} : %{y:.2f}%")
fig2.update_layout(xaxis_tickangle=45, yaxis_title="% Résistance")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- SECTION 3: Résistances antibiotiques avec seuils d'alerte ---
st.subheader("🦠 Pourcentage de résistance aux antibiotiques (alerte si > moyenne + 2σ)")
alertes = []
resistance_df["Mois"] = pd.to_datetime(resistance_df["Mois"], dayfirst=True, errors="coerce")

for ab in resistance_df.columns[1:]:
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

# --- SECTION 4: Tableau des alertes ---
st.subheader("🚨 Alertes sur les résistances (valeurs > moyenne + 2σ)")
if alertes:
    alert_df = pd.DataFrame(alertes)
    st.dataframe(alert_df.style.applymap(lambda x: 'background-color: red' if isinstance(x, (int, float)) and x > 0 else ''))
else:
    st.success("Aucune alerte actuelle 🎉")

st.markdown("---")

# --- SECTION 5: Détail d’un échantillon par IPP ---
st.subheader("🔍 Détail d’un échantillon par patient (IPP_PASTEL)")

# Sélection du demandeur et de l'IPP
unique_demandeurs = df_scn["LIBELLE_DEMANDEUR"].dropna().unique()
demandeur_selection = st.selectbox("Filtrer par service demandeur :", sorted(unique_demandeurs))
df_filtered = df_scn[df_scn["LIBELLE_DEMANDEUR"] == demandeur_selection]
ipp_selection = st.selectbox("Choisir un patient (IPP_PASTEL) :", df_filtered["IPP_PASTEL"].unique())
df_patient = df_filtered[df_filtered["IPP_PASTEL"] == ipp_selection].copy()

if not df_patient.empty:
    st.markdown("### Informations générales")
    info_cols = ["NUM_SPECIMEN", "DATE_PRELEVEMENT", "LIBELLE_DEMANDEUR", "SEXE", "AGE"] if "SEXE" in df_patient.columns and "AGE" in df_patient.columns else ["NUM_SPECIMEN", "DATE_PRELEVEMENT", "LIBELLE_DEMANDEUR"]
    st.write(df_patient[info_cols].drop_duplicates().reset_index(drop=True))

    st.markdown("### Résultats des antibiotiques")
    ab_cols = ["Vancomycin", "Teicoplanin", "Gentamycin", "Oxacilline", "Clindamycin", "Linezolid", "Daptomycin"]
    ab_results = df_patient[ab_cols].reset_index(drop=True)

    def color_result(val):
        if val == "R":
            return "background-color: red; color: white"
        elif val == "S":
            return "background-color: limegreen; color: white"
        elif pd.isna(val) or val == "-":
            return "background-color: orange; color: white"
        else:
            return ""

    st.dataframe(ab_results.style.applymap(color_result))
else:
    st.info("Aucune donnée trouvée pour cet IPP.")
