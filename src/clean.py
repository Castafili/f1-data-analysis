from pathlib import Path
import pandas as pd

RAW_FILE = Path("data/raw/f1_2025_races_raw.csv")
PROCESSED_DIR = Path("data/processed")
CLEAN_FILE = PROCESSED_DIR / "f1_2025_races_clean.csv"


def clean_race_data(input_path: Path = RAW_FILE, output_path: Path = CLEAN_FILE) -> pd.DataFrame:
    df = pd.read_csv(input_path)

    # 1. Normalizzazione tipi numerici
    int_cols = ["season", "round", "total_race_laps", "grid_position", "finish_position", "laps_completed"]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df["pit_stops"] = pd.to_numeric(df["pit_stops"], errors="coerce").astype("Int64")
    df["first_pit_lap"] = pd.to_numeric(df["first_pit_lap"], errors="coerce").astype("Int64")
    df["num_stints"] = pd.to_numeric(df["num_stints"], errors="coerce").astype("Int64")
    df["points"] = pd.to_numeric(df["points"], errors="coerce")

    # 2. Normalizzazione stringhe
    df["status"] = df["status"].astype(str).str.strip()
    df["classified_position"] = df["classified_position"].astype(str).str.strip()
    df["circuit"] = df["circuit"].astype(str).str.strip()

    # 3. Flag espliciti per gli edge case
    df["is_dns"] = df["status"] == "Did not start"
    df["is_dsq"] = df["status"] == "Disqualified"
    df["is_dnf"] = df["status"] == "Retired"
    df["is_lapped"] = df["status"] == "Lapped"
    df["is_finished_on_lead_lap"] = df["status"] == "Finished"

    # Classificato ufficialmente FIA (include chi si ritira dopo il 90% della gara)
    df["is_classified"] = ~df["classified_position"].isin(["R", "D", "W"])

    # Campione valido per valutare l'impatto della strategia sul risultato finale:
    # escludiamo DNS, DSQ e DNF (chi non ha tagliato il traguardo per ritiro/squalifica)
    df["valid_for_strategy_analysis"] = df["status"].isin(["Finished", "Lapped"])

    # 4. Rimozione eventuali duplicati su (season, round, driver)
    df = df.drop_duplicates(subset=["season", "round", "driver"]).sort_values(["round", "finish_position"])

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    total = len(df)
    valid = int(df["valid_for_strategy_analysis"].sum())
    print(f"Pulizia completata: {total} righe totali -> {valid} valide per analisi strategia ({total - valid} edge case flaggati).")
    print(f"File salvato in: {output_path}")
    return df


if __name__ == "__main__":
    clean_race_data()