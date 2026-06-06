# Football Player Statistical Twin Finder ⚽🔍

A terminal-based scouting engine that identifies the most statistically similar professional football players ("statistical twins") across Europe's Top 5 Leagues using the 2024-25 dataset. The project processes 33 per-90 metrics to provide objective, data-driven player comparisons and features interactive radar charts for visual analysis.

## 🚀 Features

* **Simpson's Paradox Mitigation:** Players who transfer mid-season (e.g., playing for two different clubs) are merged into a single profile. Their statistics are aggregated using a **90s-weighted average**, ensuring that varying sample sizes do not distort the final metrics.
* **Feature Normalization:** All statistics are scaled to a `[0.0, 1.0]` range using **Min-Max Scaling** to prevent high-volume metrics (like total passes) from overshadowing high-impact, low-volume metrics (like expected goals).
* **Position-Weighted Engine:** The core logic applies domain knowledge by assigning different multipliers (weights) to metrics based on the player's position (GK, DF, MF, FW). For instance, forwards are heavily evaluated on finishing (`npxG` weight: 1.4), while their defensive actions are de-emphasized.
* **Visual Radar Comparisons:** After identifying the top statistical twins, the engine dynamically generates a polar plot (Radar Chart) using `matplotlib` to visually compare the normalized positional metrics of the target player and their closest twin.
* **Robust Name Search:** A custom string simplification algorithm handles special characters, accents, and hyphens (e.g., `á -> a`, `ş -> s`). It supports exact matches, substring matches, and provides disambiguation prompts when multiple players share similar names.

## 🧮 Mathematical Model

The engine calculates the similarity between two players using a **Weighted Euclidean Distance** formula:

d = √ Σ wᵢ · (p1ᵢ − p2ᵢ)²

Where `wᵢ` represents the position-specific weight for a given statistic, and `p1`, `p2` represent the normalized stat values of the two players.

To convert this mathematical distance into an intuitive 0-100% scouting score, an empirical maximum distance threshold of `1.5` is applied:

Similarity% = max(0.0, (1 − d / 1.5) × 100)

## 🛠️ Usage

### Prerequisites
* Python 3.x
* Required libraries: `matplotlib`, `numpy`

You can install the required dependencies using pip:
`pip install matplotlib numpy`

### Running the Engine
1. Clone the repository.
2. Ensure your FBref dataset (`player_stats.csv`) is located in the `files.data` directory relative to the script.
3. Run the main script via terminal:

`python main.py`

### Example Interaction

Total players loaded & normalized: 2701

Type a player name to find twins (or type 'exit' to close):
Player Name: kvaratskhelia

Top 5 Statistical-Twins for;
**Khvicha Kvaratskhelia** (Napoli/PSG | FW,MF | 23):

- Nicolas Pépé      (Villarreal | FW,MF | 29) | Similarity: 87.5%
- Paulo Dybala      (Roma       | FW,MF | 30) | Similarity: 87.2%
- Jon Rowe          (Marseille  | FW,MF | 21) | Similarity: 87.1%
- Zito Luvumbo      (Cagliari   | FW,MF | 22) | Similarity: 85.7%
- Jonas Wind        (Wolfsburg  | FW,MF | 25) | Similarity: 85.5%

---------------------------------------------------
Would you like to see the Radar Chart comparing Khvicha Kvaratskhelia and Nicolas Pépé? (y/n): y
Generating chart... Please check your new window.


## 📊 Data Source
* **FBref (via Sports Reference LLC):** 2024-25 Season Data for Europe's Top 5 Leagues. Includes advanced metrics like Expected Goals (`xG`), Expected Assisted Goals (`xAG`), Progressive Carries (`PrgC`), and Shot-Creating Actions (`SCA`).
