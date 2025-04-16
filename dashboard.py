import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Chargement des fichiers de données
phenotype_df = pd.read_csv("phenotype_weekly.csv")
resistance_df = pd.read_excel("Tests_Resistances_mensuelles_FINAL.xlsx")

# Titre du Dashboard
st.title("📊 Dashboard de Suivi des Phénotypes et Résistances Antibiotiques")

st.markdown("---")

# --- SECTION 1: Evolution hebdomadaire des phénotypes ---
st.subheader("🕰️ Evolution hebdomadaire des phénotypes")
fig1, ax1 = plt.subplots()
for col in ["SRM", "SRV", "Wild", "Other"]:
    ax1.plot(phenotype_df["Semaine"], phenotype_df[col], marker="o", label=col)
ax1.set_xlabel("Semaine")
ax1.set_ylabel("Nombre de cas")
ax1.set_title("Evolution des phénotypes par semaine")
plt.xticks(rotation=45)
ax1.legend()
st.pyplot(fig1)

st.markdown("---")

# --- SECTION 2: Résistances antibiotiques avec seuils d'alerte ---
st.subheader("🦠 Pourcentage de résistance aux antibiotiques (alerte si > moyenne + 2σ)")
alertes = []
resistance_df["Mois"] = pd.to_datetime(resistance_df["Mois"])
antibiotiques = resistance_df.columns[1:]

for ab in antibiotiques:
    st.markdown(f"### {ab}")
    fig, ax = plt.subplots()
    values = resistance_df[ab]
    dates = resistance_df["Mois"]
    moyenne = values.mean()
    ecart_type = values.std()
    seuil = moyenne + 2 * ecart_type
    ax.plot(dates, values, marker='o')
    ax.axhline(seuil, color='red', linestyle='--', label=f'Seuil Alerte ({seuil:.1f})')
    ax.set_title(f"{ab} - Résistance mensuelle")
    ax.set_ylabel("Nombre de cas")
    ax.legend()
    st.pyplot(fig)

    # Ajout aux alertes si dernière valeur > seuil
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

