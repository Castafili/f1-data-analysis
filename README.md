# F1 Pit Stop Strategy Analysis 🏎️

![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-in%20progress-yellow.svg)

> *From Big Data to Race Strategy: Using AI in Formula 1*

Statistical analysis of pit stop strategy impact on race results, based on circuit characteristics — 2025 F1 season.

---

## 🎯 Research Question

**Does the impact of pit stop strategy on position delta vary depending on circuit characteristics?**

---

## 🏁 Circuits Analyzed

| Circuit | Key Characteristic |
|---|---|
| Bahrain | High tire degradation, strategy-critical |
| Monza | High speed, low downforce, fewer stops expected |
| Silverstone | Balanced, benchmark circuit |
| Monaco | Extreme case: overtaking nearly impossible |

---

## 📊 Methodology

- **Dependent Variable**: Position Delta (positions gained/lost from grid to finish)
- **Independent Variables**: Number of pit stops, timing of first pit stop, circuit type
- **Sample**: 20 drivers × 4 races (2025 season)
- **Edge Cases Handled**: DNF, penalties, DNS, pit lane starts, disqualifications

---

## 🔍 Hypotheses

1. Pit strategy has **greater impact** on high-degradation circuits (e.g. Bahrain)
2. At Monaco, strategy has **minimal impact** due to low overtaking opportunities
3. Optimal first pit stop timing varies significantly by circuit type

---

## 📈 Preliminary Findings

> ⚠️ Results are based on a limited dataset and may evolve.

### Pit Stop Strategy Distribution
![Pit Stop Distribution](plots/pitstop_distribution_by_gp.png)

- **2-stop strategies** dominate and show a median position gain of ~+1
- **1-stop strategies** are largely neutral
- **3-stop strategies** show high variability (sample too small for conclusions)

### First Pit Stop Timing vs Race Outcome
![Timing vs Delta](plots/first_pit_vs_delta.png)

- No strong linear relationship between first pit lap and final position delta
- Early stops show high variability (often reactive decisions)
- Mid-race stops tend to produce neutral outcomes

### Circuit Dependency
- The same strategy produces very different results depending on the track
- **Provisional conclusion**: pit stop strategy alone does not fully explain race performance — race context plays a key role

---

## 🛠️ Tech Stack

`Python` · `pandas` · `matplotlib` · `statsmodels` · `scipy`

---

## 🗺️ Roadmap

- [x] Data collection (4 circuits)
- [x] Edge case handling
- [x] Descriptive analysis and initial visualizations
- [ ] Correlation analysis (pit stop timing ↔ position delta)
- [ ] Regression model to quantify strategy impact by circuit
- [ ] Advanced comparative visualizations
- [ ] Final conclusions

---

## 📬 Contact

**Filippo Castagnola** — fi.castagnola@gmail.com

Suggestions, data corrections, or ideas for additional analysis are always welcome — feel free to open an issue!

---

<!-- *This project is the core of my BSc thesis in Computer Science — University of Perugia.* --> 
