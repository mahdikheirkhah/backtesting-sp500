import pandas as pd
import numpy as np
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def memory_reducer(file_path):
    """
    Reads a CSV file and downcasts numeric columns to the smallest 
    safe data type to optimize memory usage.
    """
    logger.info(f"Starting memory optimization for: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        start_mem = df.memory_usage(deep=True).sum() / 1024**2
        logger.info(f"Original memory usage of {os.path.basename(file_path)}: {start_mem:.4f} MB")
        
    except FileNotFoundError:
        logger.error(f"File not found at path: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

    for col in df.columns:
        try:
            # Optimize Date column separately 
            if col.lower() == 'date':
                df[col] = pd.to_datetime(df[col])
                continue
                
            col_type = df[col].dtype
            
            # Determine if the column is numeric
            if pd.api.types.is_numeric_dtype(col_type):
                
                c_min = df[col].min()
                c_max = df[col].max()
                
                has_nan = df[col].isnull().any()
                
                # Determine if the column can be represented by an integer
                if not has_nan and 'float' in str(col_type):
                    
                    if (df[col] == df[col].astype(np.int64)).all():
                        col_type = np.dtype(np.int64)
                
                # Determine and apply the smallest datatype that can fit the range
                if 'int' in str(col_type) and not has_nan:
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    else:
                        df[col] = df[col].astype(np.int64)
                else:
                    # If it's a true float, or contains NaNs, cast to float32 (as per requirements)
                    df[col] = df[col].astype(np.float32)
                    
        except Exception as e:
            logger.warning(f"Could not optimize column '{col}' due to error: {e}")

    try:
        end_mem = df.memory_usage(deep=True).sum() / 1024**2
        reduction = 100 * (start_mem - end_mem) / start_mem
        logger.info(f"Optimized memory usage of {os.path.basename(file_path)}: {end_mem:.4f} MB")
        logger.info(f"Memory decreased by {reduction:.2f}%\n")
    except Exception as e:
        logger.error(f"Error calculating final memory stats: {e}")

    return df