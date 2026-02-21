## Backtesting SP500

### Overview

The goal of this project is to perform a backtest on the SP500 constituents, which represent the 500 largest companies by market capitalization in the United States. You will preprocess messy financial data, develop a stock-picking signal, implement a backtesting framework, and compare your strategy against the SP500 benchmark.

### Role Play

You are quantitative analysts at a prestigious hedge fund. Your manager has tasked you with developing and backtesting a stock-picking strategy using historical data from the S&P 500 index. The goal is to create a strategy that outperforms the market benchmark. You will need to clean and preprocess messy financial data, develop a signal for stock selection, implement a backtesting framework, and present your findings to the investment committee.

### Learning Objectives

Through this project, you will learn to:

- **Implement** memory optimization techniques for large financial datasets
- **Design** data preprocessing pipelines for messy financial time series
- **Build** a stock-picking signal based on historical performance metrics
- **Analyze** strategy performance through backtesting and benchmark comparison
- **Implement** modular Python scripts that execute end-to-end from data import to results

### Instructions

#### Data

The input files are:

- [`sp500.csv`](./data/sp500.csv) - Contains SP500 index data. The SP500 is a stock market index that measures the stock performance of 500 large companies listed on stock exchanges in the United States.
- [`stock_prices.csv`](./data/stock_prices.csv) - Contains close prices for all companies that have been in the SP500. It contains a lot of missing data.

The adjusted close price may be unavailable because the company does not exist at date `d`, is not publicly traded, or its close price has not been reported.

_Note: The quality of this data set is not good: some prices are wrong, there are price spikes, and there are price adjustments (share split, dividend distribution). The idea is not to correct the full data set manually, but to correct the main problems._

_Note: The corrections will not fix the data perfectly, so results may be abnormal compared to cleaned financial data. That is expected for this project._

It is important to understand that the SP500 components change over time. Facebook entered the SP500 in 2013, meaning another company had to be removed.

There are five parts:

#### 1. Preliminary - memory_reducer.py

- Create a function that takes as input one CSV data file, optimizes the types to reduce its size, and returns a memory-optimized DataFrame.
- For `float` data, the smallest data type used must be `np.float32` (not smaller, to preserve precision).
- The optimized **prices** data set must weigh less than **8MB**.
- The optimized **sp500** data set must weigh less than **0.15MB**.

Steps to implement the memory reducer:

1. Iterate over every column
2. Determine if the column is numeric
3. Determine if the column can be represented by an integer
4. Find the min and max values
5. Determine and apply the smallest datatype that can fit the range of values

#### 2. Data Wrangling and Preprocessing - preprocessing.py

- Create a Jupyter Notebook (`analysis.ipynb`) to analyze the data sets and perform EDA. This notebook must contain at least:
  - Missing values analysis (e.g., number of missing values per variable or per year)
  - Outliers analysis
  - A graph showing the average price for companies over time or comparing price consistency across companies. Save the plot as an image.
  - Identify and describe at least 5 outliers (`ticker`, `date`, `price`) by cross-referencing historical stock prices from an external source. Save them in `outliers.txt` in the `results` folder.

_Note: Create functions that generate plots and save them in `results/plots/`. Add a parameter `plot` with default value `False` which does not display the plot. All plots must contain titles and axis labels._

- Preprocess the **prices** data:
  - Resample data on month and keep the last value. **All data must be sorted by date.**
  - Filter price outliers: remove prices outside the range $0.1 to $10,000.
  - Compute monthly returns:
    - Historical returns: `returns(current month) = (price(current month) - price(previous month)) / price(previous month)`
    - Future returns: `returns(current month) = (price(next month) - price(current month)) / price(current month)`
  - Replace returns outliers by setting them to NaN for returns greater than 1 or smaller than -0.5. **Do not apply this filter to the years 2008 and 2009** (the financial crisis impacted the market brutally). A value is considered an outlier relative to the other returns of the same company.
  - Fill missing values using the last available value **for the same company**. Ensure filling is done within each company's data independently.
  - Drop missing values that cannot be filled.
  - Verify that the number of missing values is 0.

At this stage the DataFrame should look like this:

|                                                      |   Price | monthly_past_return | monthly_future_return |
| :--------------------------------------------------- | ------: | ------------------: | --------------------: |
| (Timestamp('2000-12-31 00:00:00', freq='M'), 'A')    | 36.7304 |                 nan |           -0.00365297 |
| (Timestamp('2000-12-31 00:00:00', freq='M'), 'AA')   | 25.9505 |                 nan |              0.101194 |
| (Timestamp('2000-12-31 00:00:00', freq='M'), 'AAPL') | 1.00646 |                 nan |              0.452957 |
| (Timestamp('2000-12-31 00:00:00', freq='M'), 'ABC')  | 11.4383 |                 nan |            -0.0528713 |
| (Timestamp('2000-12-31 00:00:00', freq='M'), 'ABT')  | 38.7945 |                 nan |              -0.07205 |

- Preprocess the **sp500.csv** data:
  - Resample data on month and keep the last value.
  - Compute historical monthly returns on the adjusted close.

#### 3. Create Signal - create_signal.py

- Create a column `average_return_1y` that contains the average of monthly past returns over the previous year (12 consecutive rows), grouped by company.
- Create a column named `signal` that contains `True` if `average_return_1y` is among the 20 highest within the same month. The highest metric gets rank 1.

#### 4. Backtester - backtester.py

- Compute the PnL by multiplying the signal Series by the future returns. **Do not use a for loop.**
- Compute the return of the strategy by dividing the PnL by the sum of the signal Series.
- For the SP500 benchmark, the signal is `pd.Series([20, 20, ..., 20])` (investing $20 each month on the SP500).
- Compute the cumulative PnL using `cumsum` for both strategies.
- The PnL on the full historical data must be **smaller than $75**. If not, it means outliers were not corrected correctly.
- Save the PnL and total return results for both strategies in `results/results.txt`.
- Create a plot showing cumulative performance over time for both the SP500 benchmark and the Stock Picking 20 strategy. The plot must contain a title, a legend, and x-axis and y-axis labels. Save the plot in the results folder.

#### 5. Main - main.py

The command `python main.py` must execute the entire pipeline from data imports to the backtest and save all results. It must not return any errors.

```python
# main.py

# import data
prices, sp500 = memory_reducer(paths)

# preprocessing
prices, sp500 = preprocessing(prices, sp500)

# create signal
prices = create_signal(prices)

# backtest
backtest(prices, sp500)
```

### Submission Structure

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

### Tips

- When working with large datasets, optimize memory usage by selecting appropriate data types for each column.
- Spend time understanding the data through visualization and statistical analysis before developing the strategy.
- When resampling time series data, keep the last value for month-end prices.
- Calculate both historical and future returns separately to avoid look-ahead bias.
- Handle outliers within each company's data independently, not across the full dataset.
- Be cautious about removing outliers during periods of high market volatility (2008-2009).
- Implement backtesting logic without loops for better performance using vectorized operations.
- Organize your code into modular functions for readability and reusability.

### Resources

- [pandas Documentation](https://pandas.pydata.org/docs/): Handling time series, resampling, and returns.
- [NumPy Documentation](https://numpy.org/doc/): Vectorized operations and memory optimization.
- [Matplotlib Documentation](https://matplotlib.org/stable/index.html): Plotting cumulative returns and EDA visuals.
- [Investopedia – Backtesting](https://www.investopedia.com/terms/b/backtesting.asp): Introduction to strategy testing.
- [S&P 500 Index (Wikipedia)](https://en.wikipedia.org/wiki/S%26P_500): Background on the index and its historical changes.
- [Momentum Investing (Investopedia)](https://www.investopedia.com/terms/m/momentum_investing.asp): Theory behind using past returns as a signal.
- [Handling Missing Data in Pandas](https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html): Guide for filling and dropping missing values.

### AI Prompts For Learning

- "Explain how to optimize memory usage in a pandas DataFrame by downcasting numeric columns, and describe the tradeoffs between float32 and float64 precision in financial data."
- "Describe how to implement a simple momentum-based stock-picking strategy using historical returns, including how to create a monthly signal and backtest it against a benchmark index."
