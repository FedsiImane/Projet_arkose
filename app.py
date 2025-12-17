# app.py
import streamlit as st
import plotly.express as px
import pandas as pd

import data_service as ds

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="Dashboard Arkose Montreuil",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏔️ Dashboard Growth - Arkose Montreuil")
st.caption("Suivi 2025 de la fréquentation et de la restauration pour guider la communication & le marketing.")

# ------------------ DATA ------------------
@st.cache_data
def get_data():
    return ds.load_data()

try:
    df = get_data()
except ds.DataLoadError as e:
    st.error(f"Erreur de chargement des données : {e}")
    st.stop()

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.header("🎯 Segmentation & objectifs")

    segment = st.radio(
        "Segment rapide",
        options=[
            "Tous les jours",
            "Week-end uniquement",
            "Semaine uniquement",
            "Jours forts (top 20%)",
        ],
        index=0,
        help="Applique un filtre automatique sur les types de jours.",
    )

    objectif = st.selectbox(
        "Objectif du moment",
        ["Remplir les jours creux", "Maximiser le panier moyen", "Lancer un nouvel event"],
        help="Adapte les recommandations marketing à ton objectif.",
    )

    st.markdown("---")
    st.subheader("Filtres avancés")

    mois_unique = df["Mois"].unique()
    mois_selection = st.multiselect(
        "Mois",
        options=mois_unique,
        default=list(mois_unique),
        help="Filtre l'analyse sur certains mois.",
    )

    jours_unique = df["Jour"].unique()
    jours_selection = st.multiselect(
        "Jour de la semaine",
        options=jours_unique,
        default=list(jours_unique),
        help="Filtre l'analyse sur certains jours.",
    )

    date_min, date_max = df["Date"].min(), df["Date"].max()
    start_date, end_date = st.date_input(
        "Plage de dates",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
        help="Limite l'analyse à une plage de dates précise.",
    )

# ------------------ FILTRES & SEGMENT ------------------
df_filtered = ds.filter_data(
    df,
    mois=mois_selection,
    jours=jours_selection,
    start_date=pd.to_datetime(start_date),
    end_date=pd.to_datetime(end_date),
)

df_filtered = ds.apply_segment(df_filtered, segment)

if df_filtered.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# ------------------ KPI & RÉSUMÉ AUTOMATIQUE ------------------
st.subheader("Vue d'ensemble")

kpi = ds.kpis(df_filtered)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total grimpeurs", f"{kpi['total_passage']:,}".replace(",", " "))
c2.metric("Total plats", f"{kpi['total_plat']:,}".replace(",", " "))
c3.metric("Total entrées", f"{kpi['total_entree']:,}".replace(",", " "))
c4.metric("Jours observés", kpi["nb_jours"])

# résumé auto
mean_passage = int(df_filtered["Passage"].mean())
peak_day = df_filtered.sort_values("Passage", ascending=False).iloc[0]
peak_date = peak_day["Date"].strftime("%d/%m")
peak_value = int(peak_day["Passage"])

st.info(
    f"Sur la période et le segment sélectionnés, Arkose accueille en moyenne **{mean_passage} grimpeurs par jour**, "
    f"avec un pic de **{peak_value} passages** le **{peak_date} ({peak_day['Jour']})**."
)

with st.expander("💡 Comment lire ces indicateurs ?"):
    st.write(
        "- **Total grimpeurs** : volume de fréquentation sur la période et le segment sélectionnés.\n"
        "- **Restauration** : activité du restaurant associée à la grimpe (plats, entrées, etc.).\n"
        "- **Jours observés** : taille de l'échantillon sur lequel porte ton analyse."
    )

# ------------------ ONGLET D’ANALYSE ------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tendances temporelles",
    "📊 Profils de jours & mois",
    "🍽️ Grimpe vs Restauration",
    "🚀 Opportunités marketing",
])

# ----- TAB 1 : TENDANCES -----
with tab1:
    metric_choice = st.segmented_control(
        "Métrique affichée",
        options=["Passage", "Plat", "Entrée"],
        default="Passage",
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Évolution journalière")
        fig_metric = px.line(
            df_filtered,
            x="Date",
            y=metric_choice,
            color="Jour",
            labels={metric_choice: metric_choice, "Date": "Date", "Jour": "Jour"},
        )
        st.plotly_chart(fig_metric, width="stretch")

    with col_b:
        st.markdown("### Restauration par jour")
        fig_food = px.line(
            df_filtered,
            x="Date",
            y=["Plat", "Entrée"],
            labels={"value": "Volume", "Date": "Date", "variable": "Type"},
        )
        st.plotly_chart(fig_food, width="stretch")

    st.markdown("### Top jours les plus fréquentés")
    st.dataframe(ds.top_days(df_filtered))

# ----- TAB 2 : PROFILS -----
with tab2:
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("### Passages moyens par mois")
        mean_by_month = ds.aggregates_by_month(df_filtered)
        fig_month = px.bar(
            mean_by_month,
            x="Mois",
            y="Passage",
            color="Passage",
            color_continuous_scale="Blues",
            labels={"Passage": "Passages moyens", "Mois": "Mois"},
        )
        st.plotly_chart(fig_month, width="stretch")

    with col_d:
        st.markdown("### Passages moyens par jour de la semaine")
        mean_by_day = ds.aggregates_by_day(df_filtered)
        fig_day = px.bar(
            mean_by_day,
            x="Jour",
            y="Passage",
            color="Passage",
            color_continuous_scale="Greens",
            labels={"Passage": "Passages moyens", "Jour": "Jour"},
        )
        st.plotly_chart(fig_day, width="stretch")

    with st.expander("💡 Idées de ciblage par jours / mois"):
        best_month = mean_by_month.iloc[0]["Mois"] if not mean_by_month.empty else "N/A"
        best_day = mean_by_day.iloc[0]["Jour"] if not mean_by_day.empty else "N/A"
        st.write(
            f"- **Mois le plus fort** : `{best_month}` → idéal pour campagnes d'événements & contenus réseaux sociaux.\n"
            f"- **Jour le plus fort** : `{best_day}` → parfait pour soirées spéciales, contests, happy hours.\n"
            "- Les jours plus faibles peuvent être travaillés avec des offres 'off-peak' (prix doux, events ciblés)."
        )

# ----- TAB 3 : GRIMPE VS RESTO -----
with tab3:
    st.markdown("### Relation passages ↔ restauration")

    col_e, col_f = st.columns(2)

    with col_e:
        fig_plat = px.scatter(
            df_filtered,
            x="Passage",
            y="Plat",
            labels={"Passage": "Passages", "Plat": "Plats vendus"},
            title="Passages vs Plats vendus",
        )
        st.plotly_chart(fig_plat, width="stretch")

    with col_f:
        fig_entree = px.scatter(
            df_filtered,
            x="Passage",
            y="Entrée",
            labels={"Passage": "Passages", "Entrée": "Entrées vendues"},
            title="Passages vs Entrées vendues",
        )
        st.plotly_chart(fig_entree, width="stretch")

    with st.expander("💡 Comment exploiter cette relation en marketing ?"):
        st.write(
            "- Si les nuages montent avec les passages, les offres **bundle grimpe + plat** ont du potentiel.\n"
            "- Tester ces bundles les jours de forte fréquentation puis observer si les points se déplacent vers le haut."
        )

# ----- TAB 4 : OPPORTUNITÉS MARKETING -----
with tab4:
    st.markdown("### Jours à fort potentiel restauration")
    opp = ds.high_climb_low_food(df_filtered)
    st.dataframe(opp)

    with st.expander("🧠 Recommandations selon l'objectif"):
        if objectif == "Remplir les jours creux":
            st.write(
                "- Identifie les jours à faible `Passage` dans les autres onglets.\n"
                "- Propose des tarifs off-peak, offres locales ou partenariats entreprises pour lisser la fréquentation."
            )
        elif objectif == "Maximiser le panier moyen":
            st.write(
                "- Concentre-toi sur les jours déjà forts en grimpe.\n"
                "- Pousse les bundles grimpe + resto, montées en gamme (desserts, boissons), et offres limitées dans le temps."
            )
        else:  
            st.write(
                "- Choisis des jours dynamiques mais pas saturés (souvent milieu de semaine).\n"
                "- Organise des contests, soirées à thème, ou collaborations avec des marques/outdoor."
            )

    st.markdown("### Vue hebdomadaire (croissance)")
    weekly = ds.weekly_kpis(df_filtered)
    if not weekly.empty:
        fig_week = px.line(
            weekly,
            x="Semaine",
            y=["Passage_total", "Plat_total", "Entree_total"],
            labels={"value": "Volume hebdomadaire", "variable": "Indicateur"},
        )
        st.plotly_chart(fig_week, width="stretch")
    else:
        st.info("Pas de données hebdomadaires pour les filtres actuels.")
