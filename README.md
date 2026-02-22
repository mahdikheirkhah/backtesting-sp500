# Backtesting S&P 500 Momentum Strategy

## Overview

This project implements a full backtesting pipeline for a stock-picking strategy on historical S&P 500 constituents. The goal is to clean and preprocess messy financial data, build a momentum-style signal based on past returns, and compare strategy performance against the S&P 500 benchmark.

The repository simulates a realistic quantitative hedge-fund workflow — starting from raw CSV files and ending with validated strategy performance metrics and plots.

---

## Project Structure

```
project/
│   README.md
│   requirements.txt
│
└───data/
│   │   sp500.csv
│   │   stock_prices.csv
│
└───notebook/
│   │   analysis.ipynb
│
└───scripts/
│   │   memory_reducer.py
│   │   preprocessing.py
│   │   create_signal.py
│   │   backtester.py
│   │   main.py
│
└───results/
    │   plots/
    │   results.txt
    │   outliers.txt
```

---

## How to Run the Project (From Empty Environment)

### Option 1 — Using venv script

Run:

```bash
bash setup_venv.sh
```

This script:

* creates a virtual environment
* installs dependencies
* launches Jupyter

The script automatically installs packages from `requirements.txt` if present, otherwise installs defaults. 

---

### Option 2 — Manual Setup

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python scripts/main.py
```

Running `main.py` executes the entire pipeline:

1. Load and optimize data
2. Clean + preprocess
3. Generate signals
4. Backtest strategy
5. Save results + plots

---

## Python Files Summary

### `memory_reducer.py`

Optimizes dataset memory usage by:

* inspecting each column
* detecting numeric ranges
* downcasting to smallest safe dtype
* preserving financial precision (minimum `float32`)

Targets:

* prices dataset < 8MB
* SP500 dataset < 0.15MB

This ensures efficient processing of large datasets without precision loss.

---

### `preprocessing.py`

Cleans and prepares financial time-series data:

* Resamples to monthly frequency using last observation
* Sorts all data chronologically (critical for correctness)
* Removes extreme price outliers (<0.1 or >10,000)
* Computes:

  * historical returns (past-only)
  * future returns (future-only)
* Flags return outliers (>1 or <-0.5) and sets them to NaN
  *(except during 2008–2009 crisis years)*
* Forward fills missing values within each company only
* Drops unfillable rows
* Ensures final dataset contains **zero missing values**

Design rationale:
Financial data is noisy. Cleaning focuses on impactful anomalies rather than perfect reconstruction.

---

### `create_signal.py`

Builds the stock-selection signal.

Steps:

1. Compute `average_return_1y`

   * rolling mean of past 12 monthly returns per company
2. Rank companies cross-sectionally per month
3. Select top 20
4. Assign boolean `signal` column

This implements a classic momentum strategy.

---

### `backtester.py`

Simulates portfolio performance using fully vectorized operations:

* PnL = signal × future returns
* Strategy return = total PnL / total positions
* Benchmark = constant investment of $20/month in SP500
* Cumulative PnL computed using `cumsum`
* Generates performance plot with title, labels, legend
* Saves results to:

  * `results/results.txt`
  * `results/plots/`

Sanity check:

> If total PnL exceeds $75 → data cleaning likely failed.

---

### `main.py`

Orchestrates entire pipeline sequentially:

```python
prices, sp500 = memory_reducer(paths)
prices, sp500 = preprocessing(prices, sp500)
prices = create_signal(prices)
backtest(prices, sp500)
```

Running this file alone reproduces the entire experiment.

---

## Exploratory Data Analysis Notebook

`notebook/analysis.ipynb` includes:

* missing values analysis
* outlier detection
* average price visualization
* cross-checked historical outliers
* saved plots with titles + axis labels

This ensures transparency in data quality and preprocessing decisions.

---

## Data Cleaning Methodology (Stakeholder Explanation)

**Approach:**
Financial datasets often contain:

* missing prices
* reporting errors
* corporate action distortions
* extreme spikes

To ensure realistic backtesting:

| Issue          | Solution                     |
| -------------- | ---------------------------- |
| Missing prices | per-ticker forward fill      |
| Extreme prices | removed outside bounds       |
| Return spikes  | filtered except crisis years |
| Chronology     | enforced date sorting        |

Key principle:

> Clean enough to avoid false signals, not so much that real market behavior is removed.

---

## Strategy Logic Explanation

Signal is based on **past performance persistence**:

* Stocks with strongest past 12-month returns are assumed to continue outperforming.
* Portfolio invests equally in top 20 ranked stocks monthly.

This is a simplified implementation of a momentum factor model widely studied in academic finance.

---

## Handling the 2008–2009 Financial Crisis

Return filters are **disabled** for these years because:

* extreme moves were real market events
* filtering them would distort reality
* crisis regimes must be preserved in backtests

---

## Results & Strategy Performance

The pipeline successfully processed historical data, corrected major anomalies, and ran a bias-free backtest.

Key outcome:

* Final cumulative PnL remained under the strict $75 validation threshold.
* Indicates outlier handling worked correctly.
* Strategy produced realistic performance vs benchmark.

See:

```
results/results.txt
results/plots/
```

for exact metrics and performance chart.

---

## Limitations

* Dataset is intentionally noisy
* Not all errors can be corrected automatically
* Strategy is simplified
* No transaction costs
* No slippage modeling
* No risk management layer

---

## Educational Disclaimer

This project is for educational purposes only and does **not** constitute investment advice.
