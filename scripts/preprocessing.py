import pandas as pd
import numpy as np
import logging

# Configure module logger
logger = logging.getLogger(__name__)

def resample_monthly(df):
    """Resamples the wide dataframe to month-end, keeping the last value."""
    try:
        logger.info("Resampling data to month-end...")
        df_resampled = df.set_index('Date').sort_index().resample('BME').last()
        return df_resampled
    except Exception as e:
        logger.error(f"Error resampling data: {e}")
        raise

def filter_price_outliers(df, min_price=0.1, max_price=10000.0):
    """Masks prices outside the valid range with NaN."""
    try:
        logger.info(f"Filtering prices outside [{min_price}, {max_price}]...")
        return df.where((df >= min_price) & (df <= max_price))
    except Exception as e:
        logger.error(f"Error filtering price outliers: {e}")
        raise

def compute_past_returns(df):
    """Computes standard historical monthly returns."""
    try:
        logger.info("Computing past returns...")
        return df.pct_change(1, fill_method=None)
    except Exception as e:
        logger.error(f"Error computing past returns: {e}")
        raise

def compute_future_returns(df):
    """Computes future returns (shift -1)."""
    try:
        logger.info("Computing future returns...")
        return df.shift(-1) / df - 1
    except Exception as e:
        logger.error(f"Error computing future returns: {e}")
        raise

def filter_return_outliers(df, min_ret=-0.5, max_ret=1.0):
    """Removes return outliers, strictly skipping the 2008-2009 financial crisis."""
    try:
        logger.info("Filtering return outliers (skipping 2008-2009)...")
        outlier_mask = (df > max_ret) | (df < min_ret)
        
        # FIX: Correctly slice the DatetimeIndex for 2008-2009 to set mask to False
        try:
            outlier_mask.loc['2008':'2009'] = False
        except KeyError:
            pass # Ignore if 2008-2009 doesn't exist in the specific slice
            
        return df.mask(outlier_mask, np.nan)
    except Exception as e:
        logger.error(f"Error filtering return outliers: {e}")
        raise

def combine_to_multiIndex(prices, past, future):
    """Stacks the 3 wide dataframes into a single MultiIndex (Date, Ticker) format."""
    try:
        logger.info("Stacking dataframes into MultiIndex format...")
        p = prices.stack(future_stack=True).rename('Price')
        pst = past.stack(future_stack=True).rename('monthly_past_return')
        fut = future.stack(future_stack=True).rename('monthly_future_return')
        
        df_combined = pd.concat([p, pst, fut], axis=1)
        df_combined.index.names = ['Date', 'Ticker']
        return df_combined
    except Exception as e:
        logger.error(f"Error stacking dataframes: {e}")
        raise

def fill_and_drop_missing(df):
    """Forward fills missing values per ticker and drops remaining NaNs."""
    try:
        logger.info("Filling missing values per company...")
        df = df.groupby(level='Ticker').ffill()
        
        logger.info("Dropping remaining un-fillable missing values...")
        df = df.dropna()
        
        # Final Assertion Check
        missing_count = df.isnull().sum().sum()
        assert missing_count == 0, f"Failed assertion: Found {missing_count} missing values!"
        logger.info("Assertion passed: 0 missing values remain.")
        
        return df
    except AssertionError as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.error(f"Error handling missing values: {e}")
        raise

def preprocess_sp500(df):
    """Preprocesses the S&P 500 benchmark data."""
    try:
        logger.info("Preprocessing SP500 benchmark data...")
        df = resample_monthly(df)
        df['monthly_past_return'] = df['Adjusted Close'].pct_change(1, fill_method=None)
        return df.dropna(subset=['monthly_past_return'])
    except Exception as e:
        logger.error(f"Error preprocessing SP500: {e}")
        raise

def preprocessing(prices_df, sp500_df):
    """Main orchestrator function for Phase 4."""
    logger.info("--- Starting Preprocessing Phase ---")
    
    try:
        # 1. Prices Preprocessing
        logger.info("[Prices] Starting transformations...")
        wide_prices = resample_monthly(prices_df)
        wide_prices = filter_price_outliers(wide_prices)
        
        past_ret = compute_past_returns(wide_prices)
        future_ret = compute_future_returns(wide_prices)
        
        past_ret = filter_return_outliers(past_ret)
        future_ret = filter_return_outliers(future_ret)
        
        final_prices = combine_to_multiIndex(wide_prices, past_ret, future_ret)
        final_prices = fill_and_drop_missing(final_prices)
        
        # 2. Benchmark Preprocessing
        logger.info("[SP500] Starting transformations...")
        final_sp500 = preprocess_sp500(sp500_df)
        
        logger.info("--- Preprocessing Complete ---")
        return final_prices, final_sp500
        
    except Exception as e:
        logger.critical(f"Preprocessing pipeline failed: {e}")
        raise