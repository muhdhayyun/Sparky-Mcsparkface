"""
Anomaly detection script for energy consumption datasets.
Checks for: missing values, duplicates, negative values, outliers, time gaps, and suspicious patterns.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Define paths
PROCESSED_DATA_DIR = Path("data/processed")

class AnomalyDetector:
    """Detects various types of anomalies in energy consumption data."""
    
    def __init__(self):
        self.issues = defaultdict(list)
        
    def check_file(self, file_path):
        """Run all anomaly checks on a single CSV file."""
        try:
            df = pd.read_csv(file_path)
            
            if len(df) == 0:
                self.issues[file_path.name].append("⚠️  EMPTY FILE - No data records")
                return
            
            # Get column names
            timestamp_col = df.columns[0]
            energy_col = df.columns[1]
            
            # Parse timestamps
            df['parsed_date'] = pd.to_datetime(df[timestamp_col], format='%d/%m/%Y %H:%M:%S')
            
            # Run all checks
            self._check_missing_values(df, energy_col, file_path.name)
            self._check_duplicates(df, timestamp_col, file_path.name)
            self._check_negative_values(df, energy_col, file_path.name)
            self._check_zero_values(df, energy_col, file_path.name)
            self._check_outliers(df, energy_col, file_path.name)
            self._check_time_gaps(df, file_path.name)
            self._check_constant_values(df, energy_col, file_path.name)
            
        except Exception as e:
            self.issues[file_path.name].append(f"❌ ERROR reading file: {str(e)}")
    
    def _check_missing_values(self, df, energy_col, filename):
        """Check for missing or null values."""
        null_count = df[energy_col].isnull().sum()
        if null_count > 0:
            pct = (null_count / len(df)) * 100
            self.issues[filename].append(f"⚠️  Missing values: {null_count} ({pct:.1f}%)")
    
    def _check_duplicates(self, df, timestamp_col, filename):
        """Check for duplicate timestamps."""
        duplicates = df[timestamp_col].duplicated().sum()
        if duplicates > 0:
            self.issues[filename].append(f"⚠️  Duplicate timestamps: {duplicates}")
    
    def _check_negative_values(self, df, energy_col, filename):
        """Check for negative energy values."""
        negative = (df[energy_col] < 0).sum()
        if negative > 0:
            min_val = df[energy_col].min()
            self.issues[filename].append(f"⚠️  Negative values: {negative} (min: {min_val})")
    
    def _check_zero_values(self, df, energy_col, filename):
        """Check for excessive zero values."""
        zeros = (df[energy_col] == 0).sum()
        if zeros > 0:
            pct = (zeros / len(df)) * 100
            if pct > 10:  # Flag if more than 10% are zeros
                self.issues[filename].append(f"⚠️  Excessive zeros: {zeros} ({pct:.1f}%)")
    
    def _check_outliers(self, df, energy_col, filename):
        """Check for statistical outliers using IQR method."""
        Q1 = df[energy_col].quantile(0.25)
        Q3 = df[energy_col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        
        outliers = ((df[energy_col] < lower_bound) | (df[energy_col] > upper_bound)).sum()
        if outliers > 0:
            pct = (outliers / len(df)) * 100
            max_val = df[energy_col].max()
            if pct > 1:  # Flag if more than 1% are outliers
                self.issues[filename].append(f"⚠️  Extreme outliers: {outliers} ({pct:.1f}%) - max: {max_val:,.0f} Wh")
    
    def _check_time_gaps(self, df, filename):
        """Check for unexpected gaps in timestamps."""
        df_sorted = df.sort_values('parsed_date')
        time_diffs = df_sorted['parsed_date'].diff()
        
        # Expected interval is 30 minutes
        expected_interval = timedelta(minutes=30)
        large_gaps = time_diffs[time_diffs > expected_interval * 2]  # More than 1 hour gap
        
        if len(large_gaps) > 0:
            max_gap = time_diffs.max()
            gap_count = len(large_gaps)
            self.issues[filename].append(f"⚠️  Time gaps detected: {gap_count} gaps > 1 hour (max gap: {max_gap})")
    
    def _check_constant_values(self, df, energy_col, filename):
        """Check for suspiciously constant values."""
        # Check if same value appears too frequently
        value_counts = df[energy_col].value_counts()
        if len(value_counts) > 0:
            most_common_val = value_counts.iloc[0]
            most_common_pct = (most_common_val / len(df)) * 100
            
            if most_common_pct > 20 and value_counts.index[0] != 0:  # Ignore if it's zeros
                self.issues[filename].append(
                    f"⚠️  Constant value pattern: '{value_counts.index[0]}' appears {most_common_val} times ({most_common_pct:.1f}%)"
                )
    
    def get_statistics(self, file_path):
        """Get basic statistics for a file."""
        try:
            df = pd.read_csv(file_path)
            if len(df) == 0:
                return None
            
            energy_col = df.columns[1]
            stats = {
                'records': len(df),
                'mean': df[energy_col].mean(),
                'median': df[energy_col].median(),
                'std': df[energy_col].std(),
                'min': df[energy_col].min(),
                'max': df[energy_col].max(),
            }
            return stats
        except:
            return None

def main():
    """Run anomaly detection on all processed files."""
    
    csv_files = sorted(list(PROCESSED_DATA_DIR.glob("*.csv")))
    
    if not csv_files:
        print("No CSV files found in data/processed/")
        return
    
    print("=" * 80)
    print(f"ANOMALY DETECTION REPORT - {len(csv_files)} files")
    print("=" * 80)
    print()
    
    detector = AnomalyDetector()
    
    # Run checks on all files
    for csv_file in csv_files:
        detector.check_file(csv_file)
    
    # Print results
    clean_files = []
    problem_files = []
    
    for filename in sorted(detector.issues.keys()):
        issues = detector.issues[filename]
        if issues:
            problem_files.append(filename)
            print(f"📁 {filename}")
            for issue in issues:
                print(f"   {issue}")
            print()
    
    # Files with no issues
    for csv_file in csv_files:
        if csv_file.name not in detector.issues:
            clean_files.append(csv_file.name)
    
    if clean_files:
        print("=" * 80)
        print(f"✅ CLEAN FILES ({len(clean_files)}):")
        print("=" * 80)
        for filename in clean_files:
            file_path = PROCESSED_DATA_DIR / filename
            stats = detector.get_statistics(file_path)
            if stats:
                print(f"   {filename}")
                print(f"      Records: {stats['records']:,} | Mean: {stats['mean']:.0f} Wh | "
                      f"Range: {stats['min']:.0f}-{stats['max']:,.0f} Wh")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"   Total files analyzed: {len(csv_files)}")
    print(f"   ✅ Clean files: {len(clean_files)}")
    print(f"   ⚠️  Files with issues: {len(problem_files)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
