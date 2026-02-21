import pandas as pd
import logging

# Configure module logger
logger = logging.getLogger(__name__)

def compute_rolling_average(df, window=12):
    """
    Computes the 12-month rolling average of past returns per ticker.
    Uses transform to perfectly align the new column with the MultiIndex.
    """
    try:
        logger.info(f"Computing {window}-month rolling average of past returns...")
        
        # Group by Ticker (level=1) and calculate rolling mean
        # min_periods=window ensures we don't start trading until we have a full year of history
        rolling_avg = (
            df.groupby(level='Ticker')['monthly_past_return']
            .transform(lambda x: x.rolling(window=window, min_periods=window).mean())
        )
        return rolling_avg
        
    except Exception as e:
        logger.error(f"Error computing rolling average: {e}")
        raise

def generate_top_n_signal(df, n=20):
    """
    Ranks tickers cross-sectionally per month by their 1-year average return.
    Flags the top N tickers with signal = True.
    """
    try:
        logger.info(f"Ranking companies cross-sectionally to find Top {n} signals per month...")
        
        # Group by Date (level=0) and rank descending (highest returns get rank 1, 2, 3...)
        # na_option='bottom' ensures companies with missing data (NaN) aren't accidentally ranked #1
        ranks = df.groupby(level='Date')['average_return_1y'].rank(
            ascending=False, 
            method='first', 
            na_option='bottom'
        )
        
        # Create a boolean mask: True if rank is <= 20 AND the average return actually exists
        signal = (ranks <= n) & df['average_return_1y'].notna()
        
        return signal
        
    except Exception as e:
        logger.error(f"Error generating ranking signal: {e}")
        raise

def create_signal(df):
    """
    Main orchestrator function for Phase 5.
    Takes the preprocessed prices dataframe and adds the signal columns.
    """
    logger.info("--- Starting Signal Generation Phase ---")
    
    try:
        # 1. Calculate the moving average of past returns
        df['average_return_1y'] = compute_rolling_average(df, window=12)
        
        # 2. Rank and generate the True/False trading signal
        df['signal'] = generate_top_n_signal(df, n=20)
        
        # Quality Check: Count how many months have exactly 20 signals
        signal_counts = df[df['signal']].groupby(level='Date').size()
        valid_months = (signal_counts == 20).sum()
        logger.info(f"Signal generated successfully. Found {valid_months} months with exactly 20 tradable stocks.")
        
        logger.info("--- Signal Generation Complete ---")
        return df
        
    except Exception as e:
        logger.critical(f"Signal generation pipeline failed: {e}")
        raise