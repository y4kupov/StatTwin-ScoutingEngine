# StatTwin-ScoutingEngine ⚽

### Project Overview
The **StatTwin-ScoutingEngine** is a data-driven tool designed to solve the "Talent Identification Gap" in professional football. Using a custom **K-Nearest Neighbors (KNN)** algorithm implemented from scratch, the engine identifies undervalued "statistical twins" for elite players based on their 2024-25 performance metrics.

This project is developed as part of the **DSA 102: Computer Programming** course.

### Key Features
- **From-Scratch KNN:** Implementation of the K-Nearest Neighbors logic using only core Python lists and loops (no Scikit-Learn).
- **Custom Distance Logic:** Uses Euclidean Distance to find the closest matches in n-dimensional performance space.
- **Min-Max Normalization:** Custom preprocessing to ensure all metrics (goals, pass completion, etc.) contribute equally to the search.
- **OOP Design:** Developed using Object-Oriented Programming principles for clean and modular code.

### Project Structure
The repository is organized as follows:
- `src/`: Contains the Python source code (`main.py`, `engine.py`, etc.).
- `files.data/`: Contains the football performance datasets in CSV format.
- `README.md`: Project documentation and instructions.
- `REPORT.pdf`: The final academic paper.

### Dependencies
This project uses **Python 3** and only relies on the following standard libraries:
- `csv` (for data loading and handling)

### How to Run
To run the Scouting Engine, follow these steps:
1. Copy the repository to your local machine.
2. Make sure your dataset is placed in the `files.data/` directory.
3. Open the `src/` folder.
4. Run the main script:
   ```bash
   python main.py
