from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

FEATURES_FILE = Path("data/processed/f1_2025_races_features.csv")
COEF_FILE = Path("outputs/tables/regression_coefficients.csv")
TESTS_FILE = Path("outputs/tables/hypothesis_tests.csv")

st.set_page_config(
    page_title="F1 Pit Stop Strategy Analysis | 2025 Telemetry",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(FEATURES_FILE)
    coefs = pd.read_csv(COEF_FILE)
    tests = pd.read_csv(TESTS_FILE)
    return df, coefs, tests


# Inizializza lo stato del tema (Dark Mode di default, coerente con l'anima muretto box)
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True


def toggle_theme():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]


def inject_theme_css(dark_mode: bool) -> dict:
    if dark_mode:
        palette = {
            "bg": "#111317",
            "surface": "#181B20",
            "border": "#2A2F38",
            "text": "#F2F4F8",
            "muted": "#8E96A4",
            "accent": "#F5C542",
            "plotly_template": "plotly_dark",
        }
    else:
        palette = {
            "bg": "#F5F4EE",
            "surface": "#FDFDFD",
            "border": "#DCDAD0",
            "text": "#1A1A1A",
            "muted": "#5C6169",
            "accent": "#B8860B",
            "plotly_template": "plotly_white",
        }

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Space+Grotesk:wght@600;700&display=swap');

        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: {palette['bg']} !important;
            color: {palette['text']} !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}
        .block-container {{
            padding-top: 3.2rem !important;
            padding-bottom: 3rem;
            max-width: 1380px;
        }}
        .telemetry-kicker {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            letter-spacing: 0.14em;
            color: {palette['accent']} !important;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }}
        .telemetry-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.65rem;
            font-weight: 700;
            line-height: 1.1;
            margin: 0.35rem 0 0.5rem 0;
            color: {palette['text']} !important;
        }}
        .telemetry-title span {{
            color: {palette['accent']} !important;
        }}
        .telemetry-subtitle {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.88rem;
            color: {palette['muted']} !important;
            max-width: 850px;
            line-height: 1.5;
            margin-bottom: 1.3rem;
        }}
        .stButton > button {{
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.1em !important;
            background-color: {palette['surface']} !important;
            color: {palette['text']} !important;
            border: 1px solid {palette['border']} !important;
            border-radius: 4px !important;
            padding: 0.35rem 0.85rem !important;
            text-transform: uppercase;
        }}
        .stButton > button:hover {{
            border-color: {palette['accent']} !important;
            color: {palette['accent']} !important;
        }}
        .section-header {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            letter-spacing: 0.12em;
            color: {palette['muted']} !important;
            text-transform: uppercase;
            border-top: 1px solid {palette['border']};
            padding-top: 0.85rem;
            margin-top: 1.2rem;
            margin-bottom: 0.6rem;
        }}
        .filter-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            color: {palette['muted']} !important;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }}
        .kpi-card {{
            background-color: {palette['surface']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 1rem 1.2rem;
            margin-top: 0.4rem;
            margin-bottom: 1.2rem;
        }}
        .kpi-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            color: {palette['muted']} !important;
            text-transform: uppercase;
        }}
        .kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.15rem;
            font-weight: 700;
            color: {palette['text']} !important;
            margin: 0.25rem 0 0.15rem 0;
        }}
        .kpi-sub {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: {palette['muted']} !important;
        }}
        .stApp label, .stApp p, .stApp span, .stApp div {{
            color: {palette['text']};
            font-family: 'JetBrains Mono', monospace !important;
        }}
        div[data-baseweb="select"] > div {{
            background-color: {palette['surface']} !important;
            border-color: {palette['border']} !important;
            color: {palette['text']} !important;
            border-radius: 4px;
        }}
        div[data-baseweb="popover"], ul[role="listbox"], li[role="option"] {{
            background-color: {palette['surface']} !important;
            color: {palette['text']} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return palette


def main() -> None:
    if not FEATURES_FILE.exists():
        st.error("Processed dataset not found. Run `python src/features.py` first.")
        st.stop()

    df, coefs, tests = load_data()

    # Apply theme CSS based on active session state
    palette = inject_theme_css(st.session_state["dark_mode"])

    # 1. Top Bar: Kicker + Theme Toggle button directly underneath
    st.markdown(
        '<div class="telemetry-kicker">PIT WALL &nbsp;/&nbsp; STRATEGY TELEMETRY &nbsp;/&nbsp; 2025 SEASON</div>',
        unsafe_allow_html=True,
    )
    btn_label = "☾ DARK" if st.session_state["dark_mode"] else "☼ LIGHT"
    st.button(btn_label, on_click=toggle_theme)

    # App Title & Subtitle
    st.markdown(
        '<h1 class="telemetry-title">F1 Pit Stop <span>Strategy</span> Analysis</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="telemetry-subtitle">'
        'Empirical impact of tire strategy and pit-window timing on grid-to-finish position delta '
        'across all 24 Grands Prix of the 2025 FIA Formula One World Championship.'
        '</div>',
        unsafe_allow_html=True,
    )

    # 2. Filter Bar (Circuit + Team + Stops + Race Regime)
    f1, f2, f3, f4 = st.columns([1.5, 1.5, 1.3, 1.2])

    with f1:
        st.markdown('<div class="filter-label">CIRCUIT / GRAND PRIX</div>', unsafe_allow_html=True)
        circuits = ["All GPs (2025 Season)"] + sorted(df["circuit"].unique().tolist())
        selected_circuit = st.selectbox("Circuit", circuits, label_visibility="collapsed")

    with f2:
        st.markdown('<div class="filter-label">CONSTRUCTOR (TEAM)</div>', unsafe_allow_html=True)
        teams = ["All Teams"] + sorted(df["team"].unique().tolist())
        selected_team = st.selectbox("Team", teams, label_visibility="collapsed")

    with f3:
        st.markdown('<div class="filter-label">PIT STOP STRATEGY</div>', unsafe_allow_html=True)
        selected_strat = st.radio(
            "Stops",
            ["All", "1-stop", "2-stop", "3+-stop"],
            horizontal=True,
            label_visibility="collapsed",
        )

    with f4:
        st.markdown('<div class="filter-label">RACE REGIME</div>', unsafe_allow_html=True)
        exclude_chaotic = st.checkbox("Exclude chaotic GPs (AUS, CAN)", value=True)

    # Apply filters
    filtered = df.copy()
    if exclude_chaotic:
        filtered = filtered[~filtered["is_chaotic_race"]]
    if selected_circuit != "All GPs (2025 Season)":
        filtered = filtered[filtered["circuit"] == selected_circuit]
    if selected_team != "All Teams":
        filtered = filtered[filtered["team"] == selected_team]
    if selected_strat != "All":
        filtered = filtered[filtered["strategy_group"] == selected_strat]

    # 3. KPI Card Row (4 horizontal cards)
    n_obs = len(filtered)
    mean_delta = filtered["position_delta"].mean() if n_obs > 0 else 0.0
    med_delta = filtered["position_delta"].median() if n_obs > 0 else 0.0
    dom_strat = (
        filtered["strategy_group"].mode().iloc[0]
        if n_obs > 0 and not filtered["strategy_group"].mode().empty
        else "N/A"
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">SAMPLE SIZE</div>
                <div class="kpi-value">{n_obs}</div>
                <div class="kpi-sub">classified driver-races</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">MEAN &Delta;</div>
                <div class="kpi-value">{mean_delta:+.2f}</div>
                <div class="kpi-sub">positions (grid &minus; finish)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">MEDIAN &Delta;</div>
                <div class="kpi-value">{med_delta:+.1f}</div>
                <div class="kpi-sub">positions (robust center)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">DOMINANT STRATEGY</div>
                <div class="kpi-value">{dom_strat}</div>
                <div class="kpi-sub">most frequent stop count</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if n_obs == 0:
        st.warning("No entries match the current filter combination. Try relaxing one of the filters.")
        st.stop()

    # Pastel telemetry colors adapted to Dark / Light theme
    strat_colors = {
        "1-stop": "#6EE787" if st.session_state["dark_mode"] else "#38B764",
        "2-stop": "#6C9EFF" if st.session_state["dark_mode"] else "#3B76F6",
        "3+-stop": "#F06A6A" if st.session_state["dark_mode"] else "#D94343",
    }

    # Chart 1: Strategy Distribution by Grand Prix
    st.markdown('<div class="section-header">STRATEGY DISTRIBUTION BY GRAND PRIX</div>', unsafe_allow_html=True)
    dist_df = (
        filtered.groupby(["round", "circuit", "strategy_group"], as_index=False)
        .size()
        .rename(columns={"size": "drivers"})
        .sort_values("round")
    )
    fig_dist = px.bar(
        dist_df,
        x="circuit",
        y="drivers",
        color="strategy_group",
        barmode="group",
        color_discrete_map=strat_colors,
        category_orders={"strategy_group": ["1-stop", "2-stop", "3+-stop"]},
        template=palette["plotly_template"],
        labels={"circuit": "", "drivers": "Classified Finishers", "strategy_group": "Strategy"},
    )
    fig_dist.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=15, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", size=11, color=palette["text"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    # 4. Double Row: Mean Position Delta by Strategy & Pit Timing Window
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown('<div class="section-header">MEAN &Delta; BY PIT STOP STRATEGY</div>', unsafe_allow_html=True)
        delta_strat = (
            filtered.groupby("strategy_group", as_index=False)
            .agg(mean_delta=("position_delta", "mean"), count=("position_delta", "count"))
        )
        fig_s = px.bar(
            delta_strat,
            x="mean_delta",
            y="strategy_group",
            orientation="h",
            color="strategy_group",
            color_discrete_map=strat_colors,
            category_orders={"strategy_group": ["1-stop", "2-stop", "3+-stop"]},
            text=delta_strat.apply(lambda r: f"{r['mean_delta']:+.2f} (n={int(r['count'])})", axis=1),
            template=palette["plotly_template"],
            labels={"mean_delta": "Mean Position Delta", "strategy_group": ""},
        )
        fig_s.add_vline(x=0, line_dash="dash", line_color=palette["muted"])
        fig_s.update_traces(textposition="outside")
        fig_s.update_layout(
            height=280,
            showlegend=False,
            margin=dict(l=10, r=45, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono, monospace", size=11, color=palette["text"]),
        )
        st.plotly_chart(fig_s, use_container_width=True)

    with c_right:
        st.markdown('<div class="section-header">POSITION &Delta; BY RELATIVE FIRST PIT WINDOW</div>', unsafe_allow_html=True)
        window_order = ["Early (<= -3 laps)", "Standard (-2 to +2 laps)", "Late (>= +3 laps)"]
        fig_w = px.box(
            filtered,
            x="pit_timing_window",
            y="position_delta",
            color="pit_timing_window",
            category_orders={"pit_timing_window": window_order},
            color_discrete_sequence=(
                ["#F06A6A", "#9E8CFC", "#56CCF2"]
                if st.session_state["dark_mode"]
                else ["#D94343", "#795BE3", "#2292BF"]
            ),
            points="all",
            template=palette["plotly_template"],
            labels={"pit_timing_window": "", "position_delta": "Position Delta"},
        )
        fig_w.add_hline(y=0, line_dash="dash", line_color=palette["muted"])
        fig_w.update_layout(
            height=280,
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono, monospace", size=11, color=palette["text"]),
        )
        st.plotly_chart(fig_w, use_container_width=True)

    # 5. Row 3: Econometric Model & SciPy Hypothesis Tests
    st.markdown(
        '<div class="section-header">MULTIVARIABLE OLS REGRESSION (HC3 ROBUST SEs, N = 388 STANDARD GPs, R&sup2; = 0.426)</div>',
        unsafe_allow_html=True,
    )
    reg_col1, reg_col2 = st.columns([1.35, 1])

    with reg_col1:
        label_map = {
            "stops_vs_race_median": "Extra Stops vs. Race Median",
            "grid_position": "Starting Grid Position",
            "first_pit_vs_race_median": "First Pit Lap vs. Race Median",
            "race_had_sc[T.True]": "Safety Car in Race",
            "is_high_degradation[T.True]": "High-Degradation Circuit",
            "is_street_circuit[T.True]": "Street Circuit",
        }
        sub_coef = coefs[coefs["term"].isin(label_map.keys())].copy()
        sub_coef["label"] = sub_coef["term"].map(label_map)
        sub_coef = sub_coef.sort_values("coef", ascending=True)
        sub_coef["sig_color"] = sub_coef["p_value"].apply(
            lambda p: palette["accent"] if p < 0.05 else ("#6C9EFF" if st.session_state["dark_mode"] else "#3B76F6")
        )

        fig_reg = go.Figure()
        fig_reg.add_vline(x=0, line_dash="dash", line_color=palette["muted"])
        for _, row in sub_coef.iterrows():
            fig_reg.add_trace(
                go.Scatter(
                    x=[row["coef"]],
                    y=[row["label"]],
                    mode="markers",
                    marker=dict(size=10, color=row["sig_color"]),
                    error_x=dict(
                        type="data",
                        symmetric=False,
                        array=[row["ci_upper_95"] - row["coef"]],
                        arrayminus=[row["coef"] - row["ci_lower_95"]],
                        color=row["sig_color"],
                        thickness=2,
                        width=5,
                    ),
                    name=row["label"],
                    hovertemplate=(
                        f"<b>{row['label']}</b><br>"
                        f"Coef: {row['coef']:+.3f}<br>"
                        f"95% CI: [{row['ci_lower_95']:+.3f}, {row['ci_upper_95']:+.3f}]<br>"
                        f"p-value: {row['p_value']:.4f}<extra></extra>"
                    ),
                )
            )
        fig_reg.update_layout(
            height=300,
            showlegend=False,
            template=palette["plotly_template"],
            xaxis_title="OLS Coefficient (Effect on Position Delta, 95% CI)",
            margin=dict(l=10, r=20, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono, monospace", size=11, color=palette["text"]),
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    with reg_col2:
        st.markdown("**Non-Parametric Hypothesis Tests (SciPy)**")
        st.dataframe(
            tests.rename(
                columns={
                    "test": "Hypothesis Test",
                    "statistic": "Stat",
                    "p_value": "p-value",
                    "n_obs": "N",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Controlling for starting grid and constructor fixed effects, each additional pit stop "
            "beyond the race median reduces finishing position by 1.92 places (p < 0.001)."
        )
        
if __name__ == "__main__":
    main()