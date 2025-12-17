import pandas as pd
from pathlib import Path

CSV_PATH = Path("ARKOSE-donnees_2025_graph.csv")


class DataLoadError(Exception):
    """Erreur personnalisée pour le chargement des données."""


def load_data():
    if not CSV_PATH.exists():
        raise DataLoadError(f"Fichier introuvable : {CSV_PATH.resolve()}")

    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        raise DataLoadError(f"Erreur de lecture du CSV : {e}") from e

    if "Date" not in df.columns:
        raise DataLoadError("La colonne 'Date' est manquante dans le CSV.")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    num_cols = [
        "Passage", "Plat", "Entrée", "Total_jour",
        "% Passage", "% Plat", "% Entrée",
        "Cumul Passage", "Cumul Plat", "Cumul Entrée",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    
    df["Semaine"] = df["Date"].dt.isocalendar().week
    df["Jour_semaine_num"] = df["Date"].dt.weekday  
    return df


def filter_data(df, mois=None, jours=None, start_date=None, end_date=None):
    out = df.copy()
    if mois:
        out = out[out["Mois"].isin(mois)]
    if jours:
        out = out[out["Jour"].isin(jours)]
    if start_date is not None and end_date is not None:
        out = out[(out["Date"] >= start_date) & (out["Date"] <= end_date)]
    return out


def apply_segment(df, segment: str):
    out = df.copy()
    if segment == "Week-end uniquement":
        out = out[out["Jour"].isin(["Samedi", "Dimanche"])]
    elif segment == "Semaine uniquement":
        out = out[~out["Jour"].isin(["Samedi", "Dimanche"])]
    elif segment == "Jours forts (top 20%)" and not out.empty:
        seuil = out["Passage"].quantile(0.80)
        out = out[out["Passage"] >= seuil]
    return out


def kpis(df):
    if df.empty:
        return {"total_passage": 0, "total_plat": 0, "total_entree": 0, "nb_jours": 0}
    return {
        "total_passage": int(df["Passage"].sum()),
        "total_plat": int(df["Plat"].sum()),
        "total_entree": int(df["Entrée"].sum()),
        "nb_jours": int(df["Date"].nunique()),
    }


def aggregates_by_month(df):
    if df.empty:
        return df.head(0)
    return (
        df.groupby("Mois")[["Passage", "Plat", "Entrée"]]
        .mean()
        .reset_index()
        .sort_values("Passage", ascending=False)
    )


def aggregates_by_day(df):
    if df.empty:
        return df.head(0)
    return (
        df.groupby("Jour")[["Passage", "Plat", "Entrée"]]
        .mean()
        .reset_index()
        .sort_values("Passage", ascending=False)
    )


def top_days(df, n=10):
    if df.empty:
        return df.head(0)
    cols = ["Date", "Jour", "Mois", "Passage", "Plat", "Entrée", "Total_jour"]
    return df.sort_values("Passage", ascending=False).head(n)[cols]


def weekly_kpis(df):
    if df.empty:
        return df.head(0)
    weekly = (
        df.groupby("Semaine")[["Passage", "Plat", "Entrée"]]
        .sum()
        .reset_index()
        .rename(
            columns={
                "Passage": "Passage_total",
                "Plat": "Plat_total",
                "Entrée": "Entree_total",
            }
        )
    )
    return weekly


def high_climb_low_food(df, q_passage=0.75, q_food=0.25):
    if df.empty:
        return df.head(0)

    total_food = df["Plat"] + df["Entrée"]
    q_pass = df["Passage"].quantile(q_passage)
    q_food_val = total_food.quantile(q_food)

    mask = (df["Passage"] >= q_pass) & (total_food <= q_food_val)
    cols = ["Date", "Jour", "Mois", "Passage", "Plat", "Entrée", "Total_jour"]
    return df.loc[mask, cols].sort_values("Passage", ascending=False)
