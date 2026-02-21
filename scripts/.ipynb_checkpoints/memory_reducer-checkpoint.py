import pandas as pd
import numpy as np
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def memory_reducer(paths):
    """
    Reads CSV file(s) and downcasts numeric columns.
    Accepts a single file path string or a list of file paths.
    Returns a single DataFrame or a tuple of DataFrames.
    """
    # Convert single string to list so we can loop it consistently
    if isinstance(paths, str):
        paths = [paths]
        
    dataframes = []
    
    for file_path in paths:
        logger.info(f"Starting memory optimization for: {file_path}")
        try:
            df = pd.read_csv(file_path)
            start_mem = df.memory_usage(deep=True).sum() / 1024**2
            
            for col in df.columns:
                try:
                    if col.lower() == 'date':
                        df[col] = pd.to_datetime(df[col])
                        continue
                        
                    col_type = df[col].dtype
                    
                    if pd.api.types.is_numeric_dtype(col_type):
                        c_min, c_max = df[col].min(), df[col].max()
                        has_nan = df[col].isnull().any()
                        
                        if not has_nan and 'float' in str(col_type):
                            if (df[col] == df[col].astype(np.int64)).all():
                                col_type = np.dtype(np.int64)
                        
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
                            df[col] = df[col].astype(np.float32)
                except Exception as e:
                    logger.warning(f"Could not optimize column '{col}': {e}")

            end_mem = df.memory_usage(deep=True).sum() / 1024**2
            logger.info(f"Optimized {os.path.basename(file_path)}: {end_mem:.4f} MB")
            
            dataframes.append(df)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise

    # Return a tuple if multiple paths were provided (matching main.py layout)
    if len(dataframes) == 1:
        return dataframes[0]
    return tuple(dataframes)