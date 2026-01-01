import pandas as pd
import numpy as np

# Path to the Excel file
excel_file = "QA Automation Sprint Alignment.xlsx"

# Read the Excel file
try:
    # Try to read the file with pandas
    df = pd.read_excel(excel_file)
    
    # Print basic information about the dataframe
    print("Excel file successfully read.")
    print(f"Shape: {df.shape}")
    
    # Print detailed column information
    print("\nDetailed Column Information:")
    for col in df.columns:
        non_null_count = df[col].count()
        data_type = df[col].dtype
        print(f"- {col}: {non_null_count} non-null values, type: {data_type}")
        
        # Print unique values for categorical columns with few unique values
        if df[col].dtype == 'object' and df[col].nunique() < 10:
            unique_values = df[col].dropna().unique()
            print(f"  Unique values: {unique_values}")
    
    # Check if "Metrics" column exists and examine its structure
    if "Metrics" in df.columns:
        print("\nMetrics Column Details:")
        metrics_sample = df["Metrics"].head(10)
        print(metrics_sample)
        
        # Check if Metrics column has nested structure
        if df["Metrics"].dtype == 'object':
            try:
                # Try to parse as JSON if it's a string representation of a dictionary
                first_non_null = df["Metrics"].dropna().iloc[0] if not df["Metrics"].dropna().empty else None
                print(f"\nFirst non-null Metrics value: {first_non_null}")
                if first_non_null and isinstance(first_non_null, str) and ('{' in first_non_null or '[' in first_non_null):
                    print("Metrics column might contain JSON data")
            except:
                pass
    
    # Print a more detailed sample of the data
    print("\nDetailed Sample Data (first 5 rows):")
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.width', 1000)  # Wider display
    print(df.head())
    
    # Check for any potential issues with data types
    print("\nChecking for data type issues:")
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    for col in date_columns:
        if col in df.columns:
            print(f"Date column '{col}' has type: {df[col].dtype}")
            if df[col].dtype != 'datetime64[ns]':
                print(f"  Warning: '{col}' might not be properly formatted as a date")
    
except Exception as e:
    print(f"Error reading Excel file: {e}")