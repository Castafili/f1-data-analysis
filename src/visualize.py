from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

FEATURES_FILE = Path("data/processed/f1_2025_races_features.csv")
COEF_FILE = Path("outputs/tables/regression_coefficients.csv")
PLOTS_DIR = Path("plots")


def setup_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams["figure.dpi"] = 150
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["axes.titleweight"] = "bold"


def plot_strategy_distribution(std_df: pd.DataFrame, out_dir: Path) -> None:
    order = ["1-stop", "2-stop", "3+-stop"]
    fig, ax = plt.subplots(figsize=(8.5, 5.2))

    sns.boxplot(
        data=std_df,
        x="strategy_group",
        y="position_delta",
        order=order,
        width=0.45,
        palette=["#4C72B0", "#DD8452", "#55A868"],
        fliersize=0,
        ax=ax,
    )
    sns.stripplot(
        data=std_df,
        x="strategy_group",
        y="position_delta",
        order=order,
        color="#222222",
        alpha=0.35,
        jitter=0.18,
        size=4.5,
        ax=ax,
    )

    ax.axhline(0, color="#888888", linestyle="--", linewidth=1)
    ax.set_title("Position Delta by Pit Stop Strategy (2025 Season, 22 Standard GPs)")
    ax.set_xlabel("Pit Stop Strategy")
    ax.set_ylabel("Position Delta (Grid - Finish)")

    # Annotazioni con numerosità e mediana
    for idx, grp in enumerate(order):
        sub = std_df[std_df["strategy_group"] == grp]["position_delta"]
        ax.text(
            idx,
            ax.get_ylim()[1] - 0.8,
            f"n={len(sub)}\nmed={sub.median():.1f}",
            ha="center",
            va="top",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#CCCCCC", alpha=0.9),
        )

    fig.tight_layout()
    fig.savefig(out_dir / "01_position_delta_by_strategy.png")
    plt.close(fig)


def plot_pit_timing_window(std_df: pd.DataFrame, out_dir: Path) -> None:
    order = ["Early (<= -3 laps)", "Standard (-2 to +2 laps)", "Late (>= +3 laps)"]
    fig, ax = plt.subplots(figsize=(8.8, 5.2))

    sns.boxplot(
        data=std_df,
        x="pit_timing_window",
        y="position_delta",
        order=order,
        width=0.45,
        palette=["#C44E52", "#8172B3", "#64B5CD"],
        fliersize=0,
        ax=ax,
    )
    sns.stripplot(
        data=std_df,
        x="pit_timing_window",
        y="position_delta",
        order=order,
        color="#222222",
        alpha=0.35,
        jitter=0.18,
        size=4.5,
        ax=ax,
    )

    ax.axhline(0, color="#888888", linestyle="--", linewidth=1)
    ax.set_title("Position Delta by Relative First Pit Stop Window (2025 Season)")
    ax.set_xlabel("First Pit Stop Timing vs. Race Median")
    ax.set_ylabel("Position Delta (Grid - Finish)")

    for idx, grp in enumerate(order):
        sub = std_df[std_df["pit_timing_window"] == grp]["position_delta"]
        ax.text(
            idx,
            ax.get_ylim()[1] - 0.8,
            f"n={len(sub)}\nmean={sub.mean():.2f}",
            ha="center",
            va="top",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#CCCCCC", alpha=0.9),
        )

    fig.tight_layout()
    fig.savefig(out_dir / "02_position_delta_by_pit_timing.png")
    plt.close(fig)


def plot_regression_forest(coef_df: pd.DataFrame, out_dir: Path) -> None:
    label_map = {
        "stops_vs_race_median": "Extra Stops vs. Race Median",
        "grid_position": "Starting Grid Position",
        "first_pit_vs_race_median": "First Pit Lap vs. Race Median",
        "race_had_sc[T.True]": "Safety Car in Race",
        "is_high_degradation[T.True]": "High-Degradation Circuit",
        "is_street_circuit[T.True]": "Street Circuit",
    }

    sub = coef_df[coef_df["term"].isin(label_map.keys())].copy()
    sub["label"] = sub["term"].map(label_map)
    sub = sub.sort_values("coef", ascending=True)

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.axvline(0, color="#888888", linestyle="--", linewidth=1.1)

    colors = ["#C44E52" if p < 0.05 else "#4C72B0" for p in sub["p_value"]]

    for idx, (_, row) in enumerate(sub.iterrows()):
        ax.errorbar(
            x=row["coef"],
            y=idx,
            xerr=[[row["coef"] - row["ci_lower_95"]], [row["ci_upper_95"] - row["coef"]]],
            fmt="o",
            color=colors[idx],
            ecolor=colors[idx],
            elinewidth=2,
            capsize=4,
            markersize=7,
        )

    ax.set_yticks(range(len(sub)))
    ax.set_yticklabels(sub["label"])
    ax.set_xlabel("OLS Coefficient (Effect on Position Delta, 95% HC3 CI)")
    ax.set_title("Key Drivers of Position Delta (Controlling for Constructor Pace)")

    fig.tight_layout()
    fig.savefig(out_dir / "03_regression_forest_plot.png")
    plt.close(fig)


def generate_all_plots() -> None:
    setup_style()
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(FEATURES_FILE)
    std_df = df[~df["is_chaotic_race"]].copy()
    coef_df = pd.read_csv(COEF_FILE)

    plot_strategy_distribution(std_df, PLOTS_DIR)
    plot_pit_timing_window(std_df, PLOTS_DIR)
    plot_regression_forest(coef_df, PLOTS_DIR)

    print(f"Grafici salvati con successo in {PLOTS_DIR}/:")
    for img in sorted(PLOTS_DIR.glob("0*_*.png")):
        print(f" - {img.name}")


if __name__ == "__main__":
    generate_all_plots()