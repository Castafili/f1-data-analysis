# F1 Pit Stop Strategy Analysis

Statistical and econometric analysis of Formula 1 pit stop strategies and their impact on race outcomes across different circuit profiles.

## Research Question
How do pit stop frequency and pit-window timing affect driver position delta from grid to finish, and how does this effect vary depending on circuit characteristics and race context?

## Methodology & Pipeline
- **Data Ingestion (`src/ingest.py`):** Automated race, lap, and pit-stop data retrieval via the **FastF1** API.
- **Data Cleaning (`src/clean.py`):** Standardized handling of edge cases including DNFs, DNS, time/grid penalties, pit-lane starts, and disqualifications.
- **Feature Engineering (`src/features.py`):** Computation of grid-to-finish position delta, stint lengths, tire compounds, relative pit timing (undercut/overcut windows), and race-context indicators.
- **Statistical Modeling (`src/analysis.py`):** Non-parametric hypothesis testing (`scipy`) and regression models with control variables (`statsmodels`) to isolate strategy impact from confounding factors (starting grid, car/team pace, circuit type).

## Repository Structure
- `src/` — Core Python modules (`ingest.py`, `clean.py`, `features.py`, `analysis.py`)
- `data/raw/` — Raw race datasets retrieved via FastF1 API
- `data/processed/` — Cleaned, feature-engineered datasets ready for modeling
- `notebooks/` — Exploratory diagnostics and visual summaries
- `plots/` — Generated figures used for reporting
- `archive/` — Initial 4-race manual prototype kept for historical reference

## Setup & Usage
1. Create and activate a virtual environment:

    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

2. Install dependencies:

    pip install -r requirements.txt

3. Run the pipeline modules in order (`ingest.py` -> `clean.py` -> `features.py` -> `analysis.py`).

## Roadmap
- [x] Automated data collection via FastF1 API
- [x] Edge-case handling and data cleaning pipeline
- [ ] Feature engineering (relative pit timing, stint & context variables)
- [ ] Non-parametric hypothesis tests across circuit types
- [ ] Regression modeling with race-context controls
- [ ] Interactive web dashboard (`app/`)

## Contact
**Filippo Castagnola** — fi.castagnola@gmail.com