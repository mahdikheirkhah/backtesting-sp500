# Backtesting S&P 500 Stock-Picking Strategy

## Overview

This project implements a full backtesting pipeline for a stock‑picking strategy on historical S&P 500 constituents. The goal is to clean and preprocess messy financial data, build a simple momentum‑style signal based on past returns, and compare the strategy’s performance against the S&P 500 benchmark. The project is designed as a realistic hedge‑fund style workflow, from raw CSVs to strategy PnL and plots.

## Motivation and Learning Objectives

The repository is structured as a small quantitative research project where you act as a quant analyst at a hedge fund. The “investment committee” expects a reproducible pipeline and clear evidence of how the strategy behaves versus the benchmark.

Through this project you will:

- Implement memory optimization techniques for large financial datasets.
- Design preprocessing pipelines for messy financial time series.
- Build a momentum‑like stock‑picking signal using historical returns.
- Backtest the strategy and compare it to the S&P 500 index.
- Organize modular Python scripts that run end‑to‑end via a single entry point.

## Project Structure

```text
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

- `data/`: Raw input CSVs (S&P 500 index levels and constituent stock prices).
- `notebook/`: Exploratory data analysis (EDA) and investigation of data issues.
- `scripts/`: Modular Python scripts that implement each stage of the pipeline.
- `results/`: Final outputs: plots, PnL results, and identified outliers.

## Data Description

- `data/sp500.csv`: Daily S&P 500 index data (e.g. open, high, low, close, adjusted close).  
- `data/stock_prices.csv`: Close prices for all companies that have been in the S&P 500. The dataset is intentionally messy, with missing values, price spikes, and corporate actions (splits, dividends, etc.).

Important notes:

- S&P 500 constituents change over time: companies enter and leave the index.
- The data contains incorrect or extreme prices; the goal is to handle the most problematic cases, not to build a perfect institutional‑grade dataset.
- Even after cleaning, results may look abnormal compared to fully cleaned professional data.

## Pipeline Overview

The project is split into five main parts, each implemented in a dedicated script.

### 1. Memory Reduction (`scripts/memory_reducer.py`)

- Reads CSV files and optimizes column dtypes to reduce memory usage.
- Downcasts numeric columns (integers and floats) to the smallest safe type, with a minimum of `np.float32` for floating‑point data.
- Ensures:
  - Optimized `stock_prices` DataFrame is under 8 MB.
  - Optimized `sp500` DataFrame is under 0.15 MB.

This step is a prerequisite for working efficiently with the full dataset in memory.

### 2. Data Wrangling & Preprocessing (`scripts/preprocessing.py`)

Responsibilities for `stock_prices`:

- Resample prices to monthly frequency (month‑end) and keep the last value; ensure the entire DataFrame is sorted by date.
- Filter price outliers by keeping prices in the range 0.1–10,000.
- Compute monthly past returns:  
  \(\text{past\_return}(t) = \frac{P_t - P_{t-1}}{P_{t-1}}\)
- Compute monthly future returns:  
  \(\text{future\_return}(t) = \frac{P_{t+1} - P_t}{P_t}\)
- Flag and set to `NaN` return outliers greater than 1 or less than −0.5, *per ticker*, except during 2008–2009 (no filtering in those crisis years).
- Forward‑fill missing values within each company (per‑ticker) and drop any remaining unfillable rows.
- Validate that the final preprocessed DataFrame has no missing values.

The target structure is a multi‑index or equivalent layout with:

|                      | Price | monthly_past_return | monthly_future_return |
|----------------------|------:|--------------------:|----------------------:|
| (date, ticker)       |  ...  |         ...         |          ...          |

Responsibilities for `sp500`:

- Resample to monthly frequency (month‑end) and keep the last value.
- Compute monthly historical returns on the adjusted close.

### 3. Exploratory Analysis (`notebook/analysis.ipynb`)

The notebook is used to understand data quality and behaviour before finalizing the pipeline:

- Missing values analysis (e.g. missing counts by variable and/or by year).
- Outlier analysis with appropriate visualizations.
- Plot(s) showing average prices over time or comparing price consistency between companies.
- Use reusable plotting functions from `scripts/preprocessing.py` or a utilities section, with:
  - A `plot=False` parameter to avoid displaying in non‑interactive runs.
  - All plots saved to `results/plots/` with titles and axis labels.
- Identify at least 5 clear outliers (`ticker`, `date`, `price`) by cross‑checking with an external data source and store them in `results/outliers.txt`.

### 4. Signal Construction (`scripts/create_signal.py`)

- Compute a 1‑year average past return:
  - `average_return_1y`: rolling mean of the last 12 monthly past returns per company.
- Create a boolean `signal` column:
  - For each month, select the 20 tickers with the highest `average_return_1y`.
  - Mark those rows with `signal = True` (others `False`).
  - The best performer in a given month gets rank 1, up to rank 20.

This implements a simple momentum‑style “top 20” stock‑picking rule.

### 5. Backtesting (`scripts/backtester.py`)

- Compute monthly PnL for the strategy by multiplying the `signal` (position indicator) by the `monthly_future_return` and aggregating appropriately.
- Avoid Python `for` loops; rely on vectorized pandas / NumPy operations.
- Compute the strategy return by dividing aggregated PnL by the effective exposure (sum of signals).
- Define the S&P 500 benchmark as investing a fixed 20 units into the index each month (signal is a constant series of 20s).
- Compute cumulative PnL over time (`cumsum`) for both:
  - “Stock Picking 20” strategy.
  - S&P 500 benchmark.
- Enforce a sanity check: the total PnL over the full history must be less than 75 in absolute terms; if it is larger, outlier cleaning is likely incorrect.
- Save summary metrics (PnL and total return for both strategies) in `results/results.txt`.
- Generate and save a plot of cumulative performance over time for both strategies (with title, axis labels, legend) in `results/plots/`.

### 6. Main Entry Point (`scripts/main.py`)

`main.py` ties everything together so that a single command runs the full pipeline:

```python
# main.py (high-level structure)

# import data + optimize memory
prices, sp500 = memory_reducer(paths)

# preprocessing
prices, sp500 = preprocessing(prices, sp500)

# create signal
prices = create_signal(prices)

# backtest
backtest(prices, sp500)
```

When you run:

```bash
python scripts/main.py
```

the project should:

- Load and memory‑optimize the raw CSVs.
- Preprocess prices and the S&P 500 index.
- Build the 1‑year momentum signal.
- Run the backtest and persist results (text + plots) under `results/`.

## Installation and Environment Setup

### Prerequisites

- Python (recommended via Anaconda or Miniconda).
- Git.
- A working `bash` shell if you want to use helper scripts on Unix‑like systems.

### Setup Steps

1. Clone the repository:

   ```bash
   git clone <YOUR_REPO_URL>.git
   cd project
   ```

2. Create and activate a conda environment:

   ```bash
   conda create -n sp500-backtest python=3.11 -y
   conda activate sp500-backtest
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the pipeline:

   ```bash
   python scripts/main.py
   ```

If you add a helper bash script (for example, `run_project.sh`) you can encapsulate activation and execution there for convenience.

## Development Workflow

To keep the main branch stable:

- Treat `main` as protected: no direct pushes, only pull‑requests (PRs) from feature branches.
- Create topic branches for each unit of work, for example:
  - `feature/memory-reducer`
  - `feature/preprocessing`
  - `feature/create-signal`
  - `feature/backtester`
- Open a PR into `main`, ensure the pipeline runs (at least `python scripts/main.py`) before merging.

This mirrors a real‑world quantitative research workflow where reproducibility and a clean main branch are essential.

## Limitations and Notes

- The data is noisy and partially incorrect by design; the objective is to handle the most impactful issues, not to fully reconstruct clean historical series.
- Returns in 2008–2009 may be extreme; outlier filters are intentionally not applied in those years.
- Results from this project are for educational purposes only and do not constitute investment advice.
