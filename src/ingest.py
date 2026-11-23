from pathlib import Path
import logging
import fastf1
import pandas as pd

# Riduciamo i log verbosi di FastF1 mantenendo solo warning ed errori
logging.getLogger("fastf1").setLevel(logging.WARNING)

RAW_DIR = Path("data/raw")
CACHE_DIR = RAW_DIR / ".fastf1_cache"
OUTPUT_FILE = RAW_DIR / "f1_2025_races_raw.csv"


def setup_directories() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))


def extract_driver_pit_info(driver_laps: pd.DataFrame) -> dict:
    """Estrae numero di soste, giro del primo pit stop e sequenza mescole per un pilota."""
    if driver_laps.empty:
        return {
            "pit_stops": pd.NA,
            "first_pit_lap": pd.NA,
            "compounds_used": pd.NA,
            "num_stints": pd.NA,
        }

    # In FastF1 ogni rientro ai box ha PitInTime non nullo
    pit_in_laps = driver_laps[driver_laps["PitInTime"].notna()].sort_values("LapNumber")
    pit_stops = int(len(pit_in_laps))
    first_pit_lap = int(pit_in_laps["LapNumber"].iloc[0]) if pit_stops > 0 else pd.NA

    # Ricostruiamo la sequenza degli stint e delle mescole
    stints = (
        driver_laps.sort_values("LapNumber")
        .groupby("Stint", dropna=True)["Compound"]
        .first()
        .dropna()
        .tolist()
    )
    compounds_used = "->".join(str(c) for c in stints) if stints else pd.NA
    num_stints = len(stints) if stints else pd.NA

    return {
        "pit_stops": pit_stops,
        "first_pit_lap": first_pit_lap,
        "compounds_used": compounds_used,
        "num_stints": num_stints,
    }


def ingest_season(year: int = 2025) -> pd.DataFrame:
    setup_directories()

    schedule = fastf1.get_event_schedule(year, include_testing=False)
    # Escludiamo eventuali eventi non convenzionali e prendiamo solo i round ufficiali
    races = schedule[schedule["RoundNumber"] > 0].sort_values("RoundNumber")

    all_rows = []

    for _, event in races.iterrows():
        round_num = int(event["RoundNumber"])
        event_name = event["EventName"]
        country = event["Country"]
        location = event["Location"]

        print(f"[{round_num:02d}/{len(races)}] Scaricamento {event_name} ({location})...")

        try:
            # 'R' carica esclusivamente la gara principale (esclude Qualifying e Sprint)
            session = fastf1.get_session(year, round_num, "R")
            session.load(laps=True, telemetry=False, weather=False, messages=False)
        except Exception as exc:
            print(f"  -> Errore nel caricamento di {event_name}: {exc}")
            continue

        results = session.results
        laps = session.laps

        if results is None or results.empty:
            print(f"  -> Nessun risultato disponibile per {event_name}, salto.")
            continue

        # Flag di gara: presenza di Safety Car ("4") o Virtual Safety Car ("6", "7") nei TrackStatus
        track_statuses = set(laps["TrackStatus"].dropna().astype(str)) if not laps.empty else set()
        race_had_sc = any("4" in s for s in track_statuses)
        race_had_vsc = any(("6" in s or "7" in s) for s in track_statuses)
        total_race_laps = int(laps["LapNumber"].max()) if not laps.empty else pd.NA

        for _, row in results.iterrows():
            driver_abbr = row.get("Abbreviation", pd.NA)
            driver_num = str(row.get("DriverNumber", ""))

            driver_laps = (
                laps[laps["DriverNumber"].astype(str) == driver_num]
                if not laps.empty
                else pd.DataFrame()
            )
            pit_info = extract_driver_pit_info(driver_laps)

            all_rows.append(
                {
                    "season": year,
                    "round": round_num,
                    "event_name": event_name,
                    "country": country,
                    "circuit": location,
                    "total_race_laps": total_race_laps,
                    "driver": driver_abbr,
                    "driver_number": driver_num,
                    "team": row.get("TeamName", pd.NA),
                    "grid_position": row.get("GridPosition", pd.NA),
                    "finish_position": row.get("Position", pd.NA),
                    "classified_position": row.get("ClassifiedPosition", pd.NA),
                    "status": row.get("Status", pd.NA),
                    "points": row.get("Points", pd.NA),
                    "laps_completed": row.get("Laps", pd.NA),
                    "pit_stops": pit_info["pit_stops"],
                    "first_pit_lap": pit_info["first_pit_lap"],
                    "num_stints": pit_info["num_stints"],
                    "compounds_used": pit_info["compounds_used"],
                    "race_had_sc": race_had_sc,
                    "race_had_vsc": race_had_vsc,
                }
            )

    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nCompletato! Salvate {len(df)} righe in {OUTPUT_FILE}")
    return df


if __name__ == "__main__":
    ingest_season(2025)