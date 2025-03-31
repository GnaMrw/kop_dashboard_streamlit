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
