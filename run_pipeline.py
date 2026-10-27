import subprocess
import sys

def run_command(command):
    print(f"\n>>> Running: {' '.join(command)}")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Error executing {' '.join(command)}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    print("==========================================")
    print("   STATISTICAL ARBITRAGE PIPELINE BUILD   ")
    print("==========================================")
    
    # 1. Fetch Ticker List & Download Raw Prices
    run_command([sys.executable, "src/download_data.py"])
    
    # 2. Fetch Sector & Industry Mappings
    run_command([sys.executable, "src/get_sectors.py"])
    
    # 3. Clean Data & Save Parquet
    run_command([sys.executable, "src/cleaning.py"])
    
    # 4. Generate Data Quality Report
    run_command([sys.executable, "src/data_report.py"])
    
    print("\n==========================================")
    print(" Pipeline build complete successfully!    ")
    print("==========================================")