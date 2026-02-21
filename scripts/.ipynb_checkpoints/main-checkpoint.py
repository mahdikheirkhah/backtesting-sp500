import os
import logging
from memory_reducer import memory_reducer

# Configure logging for main
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("--- Starting SP500 Backtest Pipeline ---")
    
    # 1. Import Data & Reduce Memory
    logger.info("Step 1: Loading and optimizing data...")
    
    prices_path = os.path.join('data', 'stock_prices.csv')
    sp500_path = os.path.join('data', 'sp500.csv')
    
    try:
        prices = memory_reducer(prices_path)
        sp500 = memory_reducer(sp500_path)
    except Exception as e:
        logger.critical(f"Pipeline failed during data loading: {e}")
        return # Stop execution if data fails to load

    # Placeholder for the next phases:
    # prices, sp500 = preprocessing(prices, sp500)
    # prices = create_signal(prices)
    # backtest(prices, sp500)
    
    logger.info("--- Pipeline Execution Complete ---")

if __name__ == "__main__":
    main()