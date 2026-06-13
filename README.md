# ⚽ StatsTwin — Football Scouting Engine

> Find the **statistical twins** of any footballer in Europe's Top 5 leagues using data-driven algorithms.

StatsTwin uses **weighted Euclidean distance** (a KNN-inspired approach) to identify the players who are statistically closest to any given target — built with position-specific feature weights and Min-Max normalization to ensure fair, meaningful comparisons.

The project ships in two flavours that share the same core engine:

| Version | File | Interface |
|---|---|---|
| 🖥️ Terminal | `main.py` | Interactive CLI with aligned table output |
| 🌐 Web App | `app.py` | Streamlit UI with player photos & radar charts |

---

## How It Works

### 1. Data Loading & Transfer Merging
Player data is read from a CSV file (`player_stats.csv`). Players who transferred mid-season appear in the dataset twice — once per club. StatsTwin detects these duplicates by normalizing names (removing accents, diacritics, hyphens) and merges their stats using a **weighted average based on 90s played**, avoiding Simpson's Paradox.

### 2. Min-Max Normalization
All statistics are scaled to a `[0.0, 1.0]` range across the entire player pool so that metrics with large raw values (e.g. total carries) don't dominate over small-scale metrics (e.g. xAG per 90).

### 3. Position-Specific Feature Weights
Rather than treating all stats equally, each position group uses a tailored weight profile:

| Position | Key Weighted Stats |
|---|---|
| **GK** | PSxG+/-, Save%, AvgDist, Stp% |
| **DF** | TklW, Int, Won%, PrgP, Clr |
| **MF** | PrgP, xAG, SCA, PrgC, 1/3, Tkl+Int |
| **FW** | npxG, npxG/Sh, xAG, Att Pen, GCA, PrgR |

### 4. Weighted Euclidean Distance
For each pair of same-position players, the engine computes:

$$d = \sqrt{\sum_{i} w_i \cdot (v_{1i} - v_{2i})^2}$$

This distance is then converted to a **similarity percentage** (0–100%) capped at a max distance of 1.5.

### 5. Fuzzy Name Search
A smart multi-priority name lookup handles partial names and foreign characters:
- **Exact match** → used immediately
- **High priority** → name or surname matches (e.g. "arda" → Arda Güler)
- **Low priority** → partial string match (e.g. "arda" → Mamardashvili)
- Returns disambiguation suggestions when 2–5 candidates are found

---

## Project Structure

```
statsTwin/
├── files.data/
│   └── player_stats.csv    # Player statistics dataset
├── src/
│   └── app.py              # Streamlit web application
│   └── terminal.py         # Terminal (CLI) application
└──.gitignore
└── LICENSE
└── README.md
└── requirements.txt
```

> **Note:** Both scripts resolve the dataset path relative to their own location (`../files.data/player_stats.csv`), so the folder structure above must be maintained.

---

---
 
## Getting Started
 
### Step 1 — Download the project
 
Click the green **Code** button at the top of this page, then select **Download ZIP**. Once downloaded, extract the ZIP file anywhere on your computer.
 
If you have Git installed, you can alternatively run:
```bash
git clone https://github.com/y4kupov/StatTwin-ScoutingEngine.git
cd statsTwin
```
 
---
 
### Step 2 — Install Python
 
If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/) and run the installer.
 
> **Important (Windows):** During installation, check the box that says **"Add Python to PATH"** before clicking Install. Without this, the commands below won't work.
 
To verify Python is installed correctly, open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:
```bash
python --version
```
You should see something like `Python 3.11.2`. Any version 3.8 or above is fine.
 
---
 
### Step 3 — Open a terminal in the project folder
 
**Windows:** Open the extracted folder, click on the address bar at the top, type `cmd`, and press Enter.
 
**Mac:** Right-click the folder and select **New Terminal at Folder**.
 
**Linux:** Right-click inside the folder and select **Open Terminal**.
 
---
 
### Step 4 — Install the required libraries
 
Paste this command into the terminal and press Enter:
 
```bash
pip install streamlit matplotlib numpy requests
```
 
Wait for it to finish. You only need to do this once.
 
---
 
### Step 5 — Run the app
 
Pick whichever version you prefer:
 
#### 🖥️ Terminal Version
 
```bash
python main.py
```
 
The program will load the dataset and ask you for a player name:
 
```
Total players loaded & normalized: 2850
 
Type a player name to find twins (or type 'exit' to close):
Player Name: Kvaratskhelia
 
Top 5 Statistical-Twins for;
**Khvicha Kvaratskhelia** (Paris S-G     | FW | 23):
 
- Bukayo Saka             (Arsenal       | FW | 23) | Similarity: 91.4%
- Mohamed Salah           (Liverpool     | FW | 32) | Similarity: 88.7%
...
 
Would you like to see the Radar Chart comparing Kvaratskhelia and Bukayo Saka? (y/n):
```
 
You can search as many players as you like. Type `exit` and press Enter to quit.
 
#### 🌐 Web Version
 
```bash
streamlit run app.py
```
 
Your browser will open automatically at `http://localhost:8501`. If it doesn't, open your browser and go to that address manually.
 
- Type any player name in the search box and click **Start Scouting 🔍**
- The app displays the **Top 5 statistical twins** with Wikipedia photos and Transfermarkt links
- A **radar chart** compares the target player against their closest twin across all position-relevant metrics
To stop the web app, go back to the terminal and press `Ctrl + C`.
 
---

## Dataset Format

The engine expects a CSV file with the following columns (FBref-compatible export):

```
Player, Squad, Age, Pos, 90s,
xG, npxG, npxG/Sh, G-xG, xAG, SCA, GCA, Att Pen, PrgC, PrgR, Succ, CPA,
PrgP, 1/3, Cmp% Long, TB, Mid 3rd, Carries, Tkl+Int, Recov,
TklW, TklDri%, Int, Clr, Blocks, Won%, Def 3rd,
PSxG+/-, Save%, Stp%, AvgDist, Launch%, Att (GK)
```

The dataset should cover all outfield players and goalkeepers from the leagues you want to analyse. Missing values are treated as `0.0`.

---

## Notes

- The similarity engine only compares players **within the same broad position group** (GK / DF / MF / FW), so a striker will never appear as a twin for a centre-back.
- The web app fetches player photos live from the **Wikipedia API** and links to **Transfermarkt** — an internet connection is required for those features.
- The terminal version saves no state between sessions; all data is re-loaded and re-normalized each run.
