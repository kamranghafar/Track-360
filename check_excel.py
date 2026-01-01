import pandas as pd

# Path to the Excel file
excel_file = "QA Automation Sprint Alignment.xlsx"

# Read the Excel file
try:
    # Try to read the file with pandas
    df = pd.read_excel(excel_file)
    
    # Print basic information about the dataframe
    print("Excel file successfully read.")
    print(f"Shape: {df.shape}")
    print("\nColumns:")
    for col in df.columns:
        print(f"- {col}")
    
    # Print a sample of the data
    print("\nSample data (first 5 rows):")
    print(df.head())
    
except Exception as e:
    print(f"Error reading Excel file: {e}")