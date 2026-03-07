"""
Aggregate energy consumption data across households.
Calculates:
1. Average usage in each 30-minute block
2. Average daily usage
3. Average monthly usage
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Define paths
PROCESSED_DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs")

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_all_households():
    """Load and combine data from all household CSV files."""
    csv_files = sorted(list(PROCESSED_DATA_DIR.glob("*.csv")))
    
    if not csv_files:
        print("No CSV files found in data/processed/")
        return None
    
    print(f"Loading {len(csv_files)} household datasets...")
    
    all_data = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            
            # Skip empty files
            if len(df) == 0:
                print(f"  ⚠️  Skipping {csv_file.name} (empty)")
                continue
            
            # Get column names
            timestamp_col = df.columns[0]
            energy_col = df.columns[1]
            
            # Parse timestamps
            df['timestamp'] = pd.to_datetime(df[timestamp_col], format='%d/%m/%Y %H:%M:%S')
            df['energy_wh'] = df[energy_col]
            
            # Add household identifier
            df['household'] = csv_file.stem  # Filename without extension
            
            # Keep only relevant columns
            df = df[['household', 'timestamp', 'energy_wh']]
            
            all_data.append(df)
            print(f"  ✓ Loaded {csv_file.name}: {len(df):,} records")
            
        except Exception as e:
            print(f"  ✗ Error loading {csv_file.name}: {str(e)}")
    
    if not all_data:
        print("No valid data loaded!")
        return None
    
    # Combine all household data
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n✓ Combined data: {len(combined_df):,} total records from {len(all_data)} households")
    
    return combined_df

def aggregate_30min_blocks(df):
    """Calculate average usage for each 30-minute time block across all households."""
    print("\n" + "="*80)
    print("1. AGGREGATING BY 30-MINUTE BLOCKS")
    print("="*80)
    
    # Extract time components
    df['date'] = df['timestamp'].dt.date
    df['time'] = df['timestamp'].dt.time
    
    # Group by date and time (30-min blocks) and calculate average across households
    agg_30min = df.groupby(['date', 'time']).agg({
        'energy_wh': ['mean', 'std', 'min', 'max', 'count'],
        'household': 'nunique'
    }).reset_index()
    
    # Flatten column names
    agg_30min.columns = ['date', 'time', 'avg_energy_wh', 'std_energy_wh', 
                         'min_energy_wh', 'max_energy_wh', 'num_readings', 'num_households']
    
    # Combine date and time back to full timestamp
    agg_30min['timestamp'] = pd.to_datetime(agg_30min['date'].astype(str) + ' ' + agg_30min['time'].astype(str))
    
    # Reorder columns
    agg_30min = agg_30min[['timestamp', 'avg_energy_wh', 'std_energy_wh', 
                           'min_energy_wh', 'max_energy_wh', 'num_households', 'num_readings']]
    
    # Save to CSV
    output_file = OUTPUT_DIR / "aggregated_30min_blocks.csv"
    agg_30min.to_csv(output_file, index=False)
    
    print(f"✓ Created {len(agg_30min):,} 30-minute time blocks")
    print(f"  Average energy per 30-min block: {agg_30min['avg_energy_wh'].mean():.2f} Wh")
    print(f"  Saved to: {output_file}")
    
    return agg_30min

def aggregate_daily(df):
    """Calculate average daily usage across all households."""
    print("\n" + "="*80)
    print("2. AGGREGATING BY DAY")
    print("="*80)
    
    # Extract date
    df['date'] = df['timestamp'].dt.date
    
    # First, calculate total daily consumption per household
    daily_per_household = df.groupby(['household', 'date']).agg({
        'energy_wh': 'sum'
    }).reset_index()
    daily_per_household.columns = ['household', 'date', 'daily_total_wh']
    
    # Then calculate average across households for each day
    agg_daily = daily_per_household.groupby('date').agg({
        'daily_total_wh': ['mean', 'std', 'min', 'max'],
        'household': 'count'
    }).reset_index()
    
    # Flatten column names
    agg_daily.columns = ['date', 'avg_daily_wh', 'std_daily_wh', 
                         'min_daily_wh', 'max_daily_wh', 'num_households']
    
    # Convert date to datetime for consistency
    agg_daily['date'] = pd.to_datetime(agg_daily['date'])
    
    # Convert Wh to kWh for readability
    agg_daily['avg_daily_kwh'] = agg_daily['avg_daily_wh'] / 1000
    
    # Save to CSV
    output_file = OUTPUT_DIR / "aggregated_daily.csv"
    agg_daily.to_csv(output_file, index=False)
    
    print(f"✓ Created {len(agg_daily):,} daily aggregations")
    print(f"  Average daily consumption: {agg_daily['avg_daily_kwh'].mean():.2f} kWh/day")
    print(f"  Saved to: {output_file}")
    
    return agg_daily

def aggregate_monthly(df):
    """Calculate average monthly usage across all households."""
    print("\n" + "="*80)
    print("3. AGGREGATING BY MONTH")
    print("="*80)
    
    # Extract year-month
    df['year_month'] = df['timestamp'].dt.to_period('M')
    
    # First, calculate total monthly consumption per household
    monthly_per_household = df.groupby(['household', 'year_month']).agg({
        'energy_wh': 'sum'
    }).reset_index()
    monthly_per_household.columns = ['household', 'year_month', 'monthly_total_wh']
    
    # Then calculate average across households for each month
    agg_monthly = monthly_per_household.groupby('year_month').agg({
        'monthly_total_wh': ['mean', 'std', 'min', 'max'],
        'household': 'count'
    }).reset_index()
    
    # Flatten column names
    agg_monthly.columns = ['year_month', 'avg_monthly_wh', 'std_monthly_wh', 
                           'min_monthly_wh', 'max_monthly_wh', 'num_households']
    
    # Convert year_month to string for CSV compatibility
    agg_monthly['year_month'] = agg_monthly['year_month'].astype(str)
    
    # Convert Wh to kWh for readability
    agg_monthly['avg_monthly_kwh'] = agg_monthly['avg_monthly_wh'] / 1000
    
    # Save to CSV
    output_file = OUTPUT_DIR / "aggregated_monthly.csv"
    agg_monthly.to_csv(output_file, index=False)
    
    print(f"✓ Created {len(agg_monthly):,} monthly aggregations")
    print(f"  Average monthly consumption: {agg_monthly['avg_monthly_kwh'].mean():.2f} kWh/month")
    print(f"  Saved to: {output_file}")
    
    return agg_monthly

def print_summary_statistics(agg_30min, agg_daily, agg_monthly):
    """Print summary statistics for all aggregations."""
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    print("\n📊 30-Minute Blocks:")
    print(f"   Total time blocks: {len(agg_30min):,}")
    print(f"   Average consumption per block: {agg_30min['avg_energy_wh'].mean():.2f} ± {agg_30min['avg_energy_wh'].std():.2f} Wh")
    print(f"   Peak average block: {agg_30min['avg_energy_wh'].max():.2f} Wh")
    print(f"   Lowest average block: {agg_30min['avg_energy_wh'].min():.2f} Wh")
    
    print("\n📊 Daily Aggregations:")
    print(f"   Total days: {len(agg_daily):,}")
    print(f"   Average daily consumption: {agg_daily['avg_daily_kwh'].mean():.2f} ± {agg_daily['avg_daily_kwh'].std():.2f} kWh")
    print(f"   Peak day: {agg_daily['avg_daily_kwh'].max():.2f} kWh")
    print(f"   Lowest day: {agg_daily['avg_daily_kwh'].min():.2f} kWh")
    
    print("\n📊 Monthly Aggregations:")
    print(f"   Total months: {len(agg_monthly):,}")
    print(f"   Average monthly consumption: {agg_monthly['avg_monthly_kwh'].mean():.2f} ± {agg_monthly['avg_monthly_kwh'].std():.2f} kWh")
    print(f"   Peak month: {agg_monthly['avg_monthly_kwh'].max():.2f} kWh")
    print(f"   Lowest month: {agg_monthly['avg_monthly_kwh'].min():.2f} kWh")
    
    print("\n" + "="*80)

def main():
    """Main function to run all aggregations."""
    print("="*80)
    print("HOUSEHOLD ENERGY DATA AGGREGATION")
    print("="*80)
    
    # Load all household data
    df = load_all_households()
    
    if df is None:
        return
    
    # Perform aggregations
    agg_30min = aggregate_30min_blocks(df.copy())
    agg_daily = aggregate_daily(df.copy())
    agg_monthly = aggregate_monthly(df.copy())
    
    # Print summary
    print_summary_statistics(agg_30min, agg_daily, agg_monthly)
    
    print("\n✅ All aggregations completed successfully!")
    print(f"📁 Results saved to: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
