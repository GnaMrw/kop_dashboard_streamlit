# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 12:29:05 2025

@author: gnaou
"""
# Prompt : cd "C:\Users\gnaou\Bureau\Alternance 2025\KOP Media\Script_client" 
# bokeh serve --show viz_dashboard_kop.py



import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, Select, Div, HoverTool
from bokeh.layouts import column
from bokeh.transform import factor_cmap

# === 1. Charger les données ===
df = pd.read_csv("instagram_kop_vs_client_clean.csv")
df["mois_annee"] = df["Année post"].astype(str) + "-" + df["Mois post"].astype(str).str.zfill(2)
annees = sorted(df["Année post"].dropna().unique().astype(str))

# === 2. Sources ===
source_bar = ColumnDataSource(data=dict(x=[], y=[]))
source_line = ColumnDataSource(data=dict(x=[], y=[]))
select_annee = Select(title="Choisir une année :", value=annees[-1], options=annees)

# === 3. Graphique 1 : Vues moyennes par producteur ===
p1 = figure(x_range=[], title="Vues moyennes par producteur", height=350, toolbar_location=None, tools="")

hover_bar = HoverTool(tooltips=[
    ("Producteur", "@x"),
    ("Vues moyennes", "@y"),
    ("Commentaires", "@comments"),
    ("Likes", "@likes"),
    ("Engagement (%)", "@engagement")
])
p1.add_tools(hover_bar)

p1.vbar(x='x', top='y', width=0.5, source=source_bar,
        fill_color=factor_cmap('x', palette=["#FFA500", "#1F77B4"], factors=["KOP", "Client"]))

p1.yaxis.axis_label = "Vues moyennes"
p1.xgrid.grid_line_color = None
p1.title.text_font_size = "16px"

# === 4. Graphique 2 : Évolution des vues dans le temps ===
p2 = figure(x_range=[], title="Évolution des vues par mois", height=350, toolbar_location="above", tools="pan,wheel_zoom,reset")

hover_line = HoverTool(tooltips=[
    ("Mois", "@x"),
    ("Vues", "@y")
])
p2.add_tools(hover_line)

p2.line(x='x', y='y', source=source_line, line_width=3, color="#6a0dad")
p2.circle(x='x', y='y', source=source_line, size=6, color="#6a0dad")

p2.xaxis.major_label_orientation = 0.7
p2.yaxis.axis_label = "Total des vues"
p2.title.text_font_size = "16px"


# === 5. Analyse écrite ===
texte = Div(text="""
<div style='padding:10px; background-color:#f5f5f5; border-left:5px solid #ffa500; font-size:14px'>
<b>Analyse :</b><br>
Depuis 2025, les vidéos produites par <b style='color:#FFA500'>KOP</b> affichent un meilleur engagement que celles du client.<br>
Elles suscitent plus de commentaires, malgré un volume de production inférieur.<br>
Cette tendance est visible dans l’évolution des vues mensuelles.
</div>
""", width=900)


# === 6. Fonction de mise à jour ===
def update(attr, old, new):
    annee = int(select_annee.value)

    df_annee = df[df["Année post"] == annee]
    grouped = df_annee.groupby("Producer (Kop/Client)").agg({
        "videoViewCount": "mean",
        "commentsCount": "mean",
        "likesCount": "mean",
        "engagement_rate": "mean"
    }).round(2).reset_index()

    source_bar.data = {
        "x": list(grouped["Producer (Kop/Client)"]),
        "y": list(grouped["videoViewCount"]),
        "comments": list(grouped["commentsCount"]),
        "likes": list(grouped["likesCount"]),
        "engagement": list(grouped["engagement_rate"])
    }
    p1.x_range.factors = list(grouped["Producer (Kop/Client)"])
    p1.title.text = f"Vues moyennes par producteur – {annee}"

    # Line chart
    df_group = df[df["Année post"] <= annee]
    line_data = df_group.groupby("mois_annee")["videoViewCount"].sum().reset_index()
    source_line.data = {"x": list(line_data["mois_annee"]), "y": list(line_data["videoViewCount"])}
    p2.x_range.factors = list(line_data["mois_annee"])
    p2.title.text = f"Évolution des vues jusqu’en {annee}"

select_annee.on_change("value", update)
update(None, None, None)

# === 7. Affichage final ===
curdoc().add_root(column(select_annee, p1, p2, texte))
curdoc().title = "Dashboard Instagram – KOP"
















import streamlit as st
import pandas as pd
import plotly.express as px

# === 1. Chargement des données ===
df = pd.read_csv("instagram_kop_vs_client_clean.csv")
df["mois_annee"] = df["Année post"].astype(str) + "-" + df["Mois post"].astype(str).str.zfill(2)

# === 2. Sidebar : filtres ===
st.sidebar.title("Filtres")
annee = st.sidebar.selectbox("Choisir une année :", sorted(df["Année post"].unique(), reverse=True))
df_annee = df[df["Année post"] == annee]

# === 3. KPI ===
vue_totale = int(df_annee["videoViewCount"].sum())
engagement_moy = round(df_annee["engagement_rate"].mean(), 2)
nb_videos = df_annee.shape[0]

st.title("📊 Dashboard Instagram – KOP vs Client")
st.markdown(f"### Année sélectionnée : {annee}")
col1, col2, col3 = st.columns(3)
col1.metric("🎥 Vidéos publiées", nb_videos)
col2.metric("👁️ Vues totales", f"{vue_totale:,}")
col3.metric("📈 Engagement moyen", f"{engagement_moy}%")

# === 4. Graphique barres (moyennes par producteur) ===
grouped = df_annee.groupby("Producer (Kop/Client)").agg({
    "videoViewCount": "mean",
    "commentsCount": "mean",
    "likesCount": "mean",
    "engagement_rate": "mean"
}).reset_index()

fig_bar = px.bar(
    grouped,
    x="Producer (Kop/Client)",
    y="videoViewCount",
    color="Producer (Kop/Client)",
    title="Vues moyennes par producteur",
    hover_data=["commentsCount", "likesCount", "engagement_rate"],
    labels={"videoViewCount": "Vues moyennes"}
)
st.plotly_chart(fig_bar, use_container_width=True)

# === 5. Graphique évolution temporelle ===
df_evol = df[df["Année post"] <= annee]
evol = df_evol.groupby(["mois_annee", "Producer (Kop/Client)"])["videoViewCount"].sum().reset_index()

fig_line = px.line(
    evol,
    x="mois_annee",
    y="videoViewCount",
    color="Producer (Kop/Client)",
    title="Évolution des vues dans le temps",
    markers=True,
    labels={"videoViewCount": "Vues", "mois_annee": "Mois"}
)
st.plotly_chart(fig_line, use_container_width=True)

# === 6. Analyse ===
st.markdown("""
<div style='background-color:#f5f5f5; padding:10px; border-left:5px solid #FFA500'>
<b>Analyse :</b><br>
Depuis 2025, les vidéos produites par <b style='color:#FFA500'>KOP</b> génèrent plus d'engagement et de commentaires que celles du client.<br>
Cette tendance est confirmée par l’évolution des vues mensuelles ci-dessus.
</div>
""", unsafe_allow_html=True)



















