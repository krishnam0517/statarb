import os
import shutil
import pandas as pd
import queue

try:
    from src.data_handler import ParquetDataHandler
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.data_handler import ParquetDataHandler


def test_no_lookahead_bias():
    original_path = "data/cleaned_prices.parquet"
    base_test_path = "data/base_test_prices.parquet"
    mut_test_path = "data/mut_test_prices.parquet"
    
    if not os.path.exists(original_path):
        print(f"Skipping test: Cleaned price file not found at {original_path}.")
        return

    shutil.copy(original_path, base_test_path)
    shutil.copy(original_path, mut_test_path)
    
    try:
        # 1. Load baseline data handler
        q_base = queue.Queue()
        dh_base = ParquetDataHandler(q_base, parquet_path=base_test_path)
        
        split_idx = len(dh_base.all_dates) // 2
        
        # Mutate strictly AFTER split_idx (from split_idx + 1 onwards)
        df_mut = pd.read_parquet(mut_test_path)
        df_mut.iloc[split_idx + 1:] = df_mut.iloc[split_idx + 1:] * 10.0
        df_mut.to_parquet(mut_test_path)
        
        # Load mutated data handler
        q_mut = queue.Queue()
        dh_mut = ParquetDataHandler(q_mut, parquet_path=mut_test_path)
        
        # 2. Extract historical slices up to split_idx (inclusive)
        cutoff_date = dh_base.all_dates[split_idx]
        sub_orig = dh_base.symbol_data.loc[:cutoff_date]
        sub_mut = dh_mut.symbol_data.loc[:cutoff_date]
        
        # Assert past data is identical
        pd.testing.assert_frame_equal(sub_orig, sub_mut, check_exact=False)
        print(f"SUCCESS: No lookahead bias detected across {split_idx + 1} historical bars up to {cutoff_date.strftime('%Y-%m-%d')}.")

    finally:
        for p in [base_test_path, mut_test_path]:
            if os.path.exists(p):
                os.remove(p)


if __name__ == "__main__":
    test_no_lookahead_bias()