from pathlib import Path
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

FEATURES_FILE = Path("data/processed/f1_2025_races_features.csv")
TABLES_DIR = Path("outputs/tables")


def run_analysis(input_path: Path = FEATURES_FILE, output_dir: Path = TABLES_DIR) -> dict:
    df = pd.read_csv(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Campione principale: 22 GP standard (escludiamo le 2 gare caotiche con mediana >= 4 stop)
    std = df[~df["is_chaotic_race"]].copy()

    # 1. Tabelle descrittive
    strategy_summary = (
        std.groupby("strategy_group", as_index=False)["position_delta"]
        .agg(count="count", mean="mean", median="median", std="std")
        .round(3)
    )
    timing_summary = (
        std.groupby("pit_timing_window", as_index=False)["position_delta"]
        .agg(count="count", mean="mean", median="median", std="std")
        .round(3)
    )

    strategy_summary.to_csv(output_dir / "strategy_summary.csv", index=False)
    timing_summary.to_csv(output_dir / "pit_timing_summary.csv", index=False)

    # 2. Test statistici non parametrici (SciPy)
    strat_groups = [g["position_delta"].values for _, g in std.groupby("strategy_group")]
    kw_strat_h, kw_strat_p = stats.kruskal(*strat_groups)

    timing_groups = [g["position_delta"].values for _, g in std.groupby("pit_timing_window")]
    kw_time_h, kw_time_p = stats.kruskal(*timing_groups)

    spearman_rho, spearman_p = stats.spearmanr(
        std["first_pit_vs_race_median"], std["position_delta"], nan_policy="omit"
    )

    tests_df = pd.DataFrame(
        [
            {
                "test": "Kruskal-Wallis: Position Delta across Strategy Groups",
                "statistic": round(float(kw_strat_h), 4),
                "p_value": round(float(kw_strat_p), 4),
                "n_obs": len(std),
            },
            {
                "test": "Kruskal-Wallis: Position Delta across Pit Timing Windows",
                "statistic": round(float(kw_time_h), 4),
                "p_value": round(float(kw_time_p), 4),
                "n_obs": len(std),
            },
            {
                "test": "Spearman Correlation: Relative First Pit Lap vs Position Delta",
                "statistic": round(float(spearman_rho), 4),
                "p_value": round(float(spearman_p), 4),
                "n_obs": len(std),
            },
        ]
    )
    tests_df.to_csv(output_dir / "hypothesis_tests.csv", index=False)

    # 3. Modello di regressione OLS con errori standard robusti (HC3) e controlli
    formula = (
        "position_delta ~ grid_position + stops_vs_race_median + first_pit_vs_race_median "
        "+ C(team) + is_high_degradation + is_street_circuit + race_had_sc"
    )
    model = smf.ols(formula, data=std).fit(cov_type="HC3")

    coef_table = pd.DataFrame(
        {
            "term": model.params.index,
            "coef": model.params.values,
            "std_err_hc3": model.bse.values,
            "z_stat": model.tvalues.values,
            "p_value": model.pvalues.values,
            "ci_lower_95": model.conf_int()[0].values,
            "ci_upper_95": model.conf_int()[1].values,
        }
    ).round(4)
    coef_table.to_csv(output_dir / "regression_coefficients.csv", index=False)

    print("=== SUMMARY STRATEGIE (22 GP STANDARD, N=388) ===")
    print(strategy_summary.to_string(index=False))
    print("\n=== SUMMARY FINESTRE PRIMO PIT STOP ===")
    print(timing_summary.to_string(index=False))
    print("\n=== TEST NON PARAMETRICI ===")
    print(tests_df.to_string(index=False))
    print(f"\n=== REGRESSIONE OLS (HC3) | R2 = {model.rsquared:.3f} | Adj. R2 = {model.rsquared_adj:.3f} ===")
    key_terms = [
        "Intercept",
        "grid_position",
        "stops_vs_race_median",
        "first_pit_vs_race_median",
        "is_high_degradation[T.True]",
        "is_street_circuit[T.True]",
        "race_had_sc[T.True]",
    ]
    print(coef_table[coef_table["term"].isin(key_terms)].to_string(index=False))
    print(f"\nTabelle salvate in: {output_dir}")

    return {
        "strategy_summary": strategy_summary,
        "timing_summary": timing_summary,
        "tests": tests_df,
        "regression": coef_table,
        "r_squared": model.rsquared,
    }


if __name__ == "__main__":
    run_analysis()