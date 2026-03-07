"""
Filter raw energy data to keep only records up to end of 2014.
Saves filtered data to data/processed/ folder.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

# Define paths
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")

# Create processed directory if it doesn't exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Date range: ONLY 2016 data
START_DATE = datetime(2014, 1, 1, 0, 0, 0)
END_DATE = datetime(2014, 12, 31, 23, 59, 59)

def filter_csv_file(input_path, output_path):
    """
    Filter a single CSV file to keep only data up to end of 2014.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path to save filtered CSV file
    """
    try:
        # Read CSV with explicit column names
        df = pd.read_csv(input_path)
        
        # Get the timestamp column name (handle potential whitespace)
        timestamp_col = df.columns[0]
        
        # Parse timestamps - handle dd/mm/yyyy hh:mm:ss format
        df['parsed_date'] = pd.to_datetime(df[timestamp_col], format='%d/%m/%Y %H:%M:%S')
        
        # Filter to keep only data within 2016
        df_filtered = df[(df['parsed_date'] >= START_DATE) & (df['parsed_date'] <= END_DATE)].copy()
        
        # Drop the temporary parsed_date column
        df_filtered = df_filtered.drop('parsed_date', axis=1)
        
        # Save filtered data
        df_filtered.to_csv(output_path, index=False)
        
        original_count = len(df)
        filtered_count = len(df_filtered)
        removed_count = original_count - filtered_count
        
        print(f"✓ {input_path.name}: {original_count:,} → {filtered_count:,} rows ({removed_count:,} removed)")
        
        return True
        
    except Exception as e:
        print(f"✗ {input_path.name}: Error - {str(e)}")
        return False

def main():
    """Process all CSV files in raw data directory."""
    
    # Get all CSV files (excluding .gitkeep)
    csv_files = [f for f in RAW_DATA_DIR.glob("*.csv")]
    
    if not csv_files:
        print("No CSV files found in data/raw/")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    print(f"Filtering data to keep only records from {START_DATE.strftime('%d/%m/%Y')} to {END_DATE.strftime('%d/%m/%Y')}")
    print("-" * 80)
    
    success_count = 0
    
    for csv_file in sorted(csv_files):
        output_file = PROCESSED_DATA_DIR / csv_file.name
        if filter_csv_file(csv_file, output_file):
            success_count += 1
    
    print("-" * 80)
    print(f"Completed: {success_count}/{len(csv_files)} files processed successfully")
    print(f"Filtered data saved to: {PROCESSED_DATA_DIR}/")

if __name__ == "__main__":
    main()
