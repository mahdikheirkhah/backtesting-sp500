import pandas as pd
import matplotlib.pyplot as plt
import os
import logging

# Configure module logger
logger = logging.getLogger(__name__)

def compute_strategy_performance(df):
    """Computes vectorized PnL and returns for the top 20 stock-picking strategy."""
    try:
        logger.info("Computing Strategy PnL and Returns...")
        
        # Calculate individual stock PnL (Signal is True/1 or False/0)
        df['PnL'] = df['signal'] * df['monthly_future_return']
        
        # Aggregate to monthly portfolio level
        monthly_pnl = df.groupby(level='Date')['PnL'].sum()
        monthly_signal_sum = df.groupby(level='Date')['signal'].sum()
        
        # Calculate strategy returns and cumulative PnL
        monthly_return = monthly_pnl / monthly_signal_sum
        cumulative_pnl = monthly_pnl.cumsum()
        
        return monthly_pnl, monthly_return, cumulative_pnl
        
    except Exception as e:
        logger.error(f"Error computing strategy performance: {e}")
        raise

def compute_benchmark_performance(sp500):
    """Computes PnL and returns for the S&P 500 benchmark."""
    try:
        logger.info("Computing Benchmark PnL and Returns...")
        
        # Calculate future returns for the SP500 to align perfectly with the strategy
        sp500['monthly_future_return'] = sp500['Adjusted Close'].pct_change(fill_method=None).shift(-1)
        
        # The benchmark signal is a constant 20-unit exposure every month
        sp500_signal = pd.Series(20, index=sp500.index)
        
        # Calculate PnL and cumulative PnL
        monthly_pnl = sp500_signal * sp500['monthly_future_return']
        cumulative_pnl = monthly_pnl.cumsum()
        
        return monthly_pnl, cumulative_pnl
        
    except Exception as e:
        logger.error(f"Error computing benchmark performance: {e}")
        raise

def save_results(strategy_pnl, strategy_ret, sp500_pnl):
    """Saves the summary metrics to results/results.txt."""
    try:
        logger.info("Saving performance metrics to results.txt...")
        os.makedirs('results', exist_ok=True)
        
        # Drop NaNs that occur at the very end of the dataset due to future returns (shift -1)
        total_strategy_pnl = strategy_pnl.dropna().sum()
        total_benchmark_pnl = sp500_pnl.dropna().sum()
        
        # Sanity Check Assertion from Project Description
        logger.info(f"Checking Sanity: Total PnL is ${total_strategy_pnl:.2f}")
        assert total_strategy_pnl < 75, f"Sanity check failed: Total PnL {total_strategy_pnl} is not less than 75!"
        
        with open('results/results.txt', 'w') as f:
            f.write("--- Backtest Performance Summary ---\n")
            f.write(f"Strategy Total PnL: ${total_strategy_pnl:.2f}\n")
            f.write(f"Benchmark (SP500) Total PnL: ${total_benchmark_pnl:.2f}\n")
            f.write(f"Strategy Average Monthly Return: {(strategy_ret.mean() * 100):.2f}%\n")
            
    except AssertionError as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise

def plot_performance(strategy_cum_pnl, sp500_cum_pnl):
    """Generates and saves the cumulative performance plot."""
    try:
        logger.info("Generating cumulative performance plot...")
        os.makedirs(os.path.join('results', 'plots'), exist_ok=True)
        
        plt.figure(figsize=(12, 6))
        
        # Plot both cumulative PnLs
        plt.plot(strategy_cum_pnl.index, strategy_cum_pnl.values, label='Stock Picking Top 20', color='blue')
        plt.plot(sp500_cum_pnl.index, sp500_cum_pnl.values, label='S&P 500 Benchmark', color='orange')
        
        plt.title("Cumulative PnL: Strategy vs S&P 500 Benchmark")
        plt.xlabel("Date")
        plt.ylabel("Cumulative PnL ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save the plot
        plt.savefig(os.path.join('results', 'plots', 'cumulative_performance.png'), bbox_inches='tight')
        plt.close()
        logger.info("Plot saved successfully to results/plots/cumulative_performance.png")
        
    except Exception as e:
        logger.error(f"Error plotting performance: {e}")
        raise

def backtest(prices_df, sp500_df):
    """Main orchestrator function for the backtester."""
    logger.info("--- Starting Backtest Phase ---")
    
    try:
        strat_pnl, strat_ret, strat_cum_pnl = compute_strategy_performance(prices_df)
        bench_pnl, bench_cum_pnl = compute_benchmark_performance(sp500_df)
        
        save_results(strat_pnl, strat_ret, bench_pnl)
        plot_performance(strat_cum_pnl, bench_cum_pnl)
        
        logger.info("--- Backtest Complete ---")
        
    except Exception as e:
        logger.critical(f"Backtesting pipeline failed: {e}")
        raise