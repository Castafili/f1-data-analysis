from pathlib import Path
import numpy as np
import pandas as pd

CLEAN_FILE = Path("data/processed/f1_2025_races_clean.csv")
FEATURES_FILE = Path("data/processed/f1_2025_races_features.csv")

# Classificazione dei circuiti in base alle caratteristiche tecniche e di sorpasso
CIRCUIT_TYPE_MAP = {
    "Monaco": "Street / Low-Overtaking",
    "Marina Bay": "Street / Low-Overtaking",
    "Baku": "Street / High-Speed",
    "Jeddah": "Street / High-Speed",
    "Melbourne": "Street / Hybrid",
    "Montréal": "Stop-and-Go / Hybrid",
    "Miami Gardens": "Street / Hybrid",
    "Las Vegas": "Street / High-Speed",
    "Monza": "Low-Downforce / High-Speed",
    "Spa-Francorchamps": "Low-Downforce / High-Speed",
    "Sakhir": "High-Degradation",
    "Barcelona": "High-Degradation",
    "Suzuka": "High-Degradation",
    "Silverstone": "High-Degradation",
    "Lusail": "High-Degradation",
    "Shanghai": "High-Degradation",
    "Austin": "Balanced / Technical",
    "Budapest": "High-Downforce / Technical",
    "Zandvoort": "High-Downforce / Technical",
    "Imola": "High-Downforce / Technical",
    "Spielberg": "Short / High-Efficiency",
    "Mexico City": "High-Altitude / Low-Grip",
    "São Paulo": "Balanced / Overtaking-Friendly",
    "Yas Island": "Balanced / Technical",
}


def build_features(input_path: Path = CLEAN_FILE, output_path: Path = FEATURES_FILE) -> pd.DataFrame:
    df = pd.read_csv(input_path)

    # Teniamo solo i piloti che hanno completato la gara (Finished o Lapped)
    df = df[df["valid_for_strategy_analysis"]].copy()

    # 1. Variabile dipendente: Position Delta (positivo = posizioni guadagnate dalla griglia)
    df["position_delta"] = df["grid_position"] - df["finish_position"]

    # 2. Tipologia e caratteristiche del circuito
    df["circuit_type"] = df["circuit"].map(CIRCUIT_TYPE_MAP).fillna("Other")
    df["is_high_degradation"] = df["circuit_type"] == "High-Degradation"
    df["is_street_circuit"] = df["circuit_type"].str.startswith("Street")

    # 3. Categorie di strategia pit stop (1-stop, 2-stop, 3+-stop)
    df["strategy_group"] = np.select(
        [df["pit_stops"] == 1, df["pit_stops"] == 2, df["pit_stops"] >= 3],
        ["1-stop", "2-stop", "3+-stop"],
        default="Other",
    )

    # 4. Indicatori relativi alla singola gara (contesto ed effetti gara)
    race_stats = (
        df.groupby("round", as_index=False)
        .agg(
            race_median_stops=("pit_stops", "median"),
            race_median_first_pit=("first_pit_lap", "median"),
            race_finishers=("driver", "count"),
        )
    )
    df = df.merge(race_stats, on="round", how="left")

    # Gare anomale/caotiche (es. pioggia o neutralizzazioni multiple con mediana >= 4 soste)
    df["is_chaotic_race"] = df["race_median_stops"] >= 4

    # Differenza numero soste rispetto alla strategia standard di quella gara
    df["stops_vs_race_median"] = df["pit_stops"] - df["race_median_stops"]

    # Tempismo primo pit stop normalizzato sulla lunghezza gara (%) e relativo al gruppo
    df["first_pit_pct"] = (df["first_pit_lap"] / df["total_race_laps"]) * 100.0
    df["first_pit_vs_race_median"] = df["first_pit_lap"] - df["race_median_first_pit"]

    # Classificazione finestra primo pit stop (Early = undercut/reattivo, Standard, Late = overcut)
    df["pit_timing_window"] = np.select(
        [
            df["first_pit_vs_race_median"] <= -3,
            df["first_pit_vs_race_median"] >= 3,
        ],
        ["Early (<= -3 laps)", "Late (>= +3 laps)"],
        default="Standard (-2 to +2 laps)",
    )

    # 5. Variabile di contesto gomme (partenza con mescola morbida vs media/dura/bagnato)
    df["starting_compound"] = df["compounds_used"].astype(str).str.split("->").str[0]
    df["started_on_soft"] = df["starting_compound"] == "SOFT"
    df["wet_race_flag"] = df["compounds_used"].astype(str).str.contains("INTERMEDIATE|WET", regex=True)

    df = df.sort_values(["round", "finish_position"]).reset_index(drop=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Feature engineering completato: {len(df)} righe, {df.shape[1]} colonne.")
    print(f"Gare standard: {(~df['is_chaotic_race']).sum()} righe | Gare caotiche (mediana >= 4 stop): {df['is_chaotic_race'].sum()} righe.")
    print(f"File salvato in: {output_path}")
    return df


if __name__ == "__main__":
    build_features()