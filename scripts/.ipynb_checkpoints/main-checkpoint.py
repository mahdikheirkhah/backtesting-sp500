import os
import logging
from memory_reducer import memory_reducer
from preprocessing import preprocessing
from create_signal import create_signal

# Configure logging for main
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("--- Starting SP500 Backtest Pipeline ---")
    
    # 1. Import Data & Reduce Memory
    logger.info("Step 1: Loading and optimizing data...")
    paths = [os.path.join('data', 'stock_prices.csv'), os.path.join('data', 'sp500.csv')]
    
    try:
        prices, sp500 = memory_reducer(paths)
    except Exception as e:
        logger.critical(f"Pipeline failed during data loading: {e}")
        return

    # 2. Data Preprocessing
    logger.info("Step 2: Preprocessing datasets...")
    try:
        prices, sp500 = preprocessing(prices, sp500)
    except Exception as e:
        logger.critical(f"Pipeline failed during preprocessing: {e}")
        return

    # 3. Create Signal
    logger.info("Step 3: Generating trading signals...")
    try:
        prices = create_signal(prices)
    except Exception as e:
        logger.critical(f"Pipeline failed during signal generation: {e}")
        return

    # Placeholder for final phase:
    # backtest(prices, sp500)
    
    logger.info("--- Pipeline Execution Complete ---")

if __name__ == "__main__":
    main()