# sales/csv.py
import pandas as pd

REQUIRED_COLUMNS = {
    'date',
    'product',
    'region',
    'units_sold',
    'unit_price'
}

def process_sales_csv(file_path):
    """
    Reads CSV, validates data, computes revenue, returns DataFrame
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"CSV file could not be read: {e}")

    # Validate columns
    if not REQUIRED_COLUMNS.issubset(df.columns):
        missing = REQUIRED_COLUMNS - set(df.columns)
        raise ValueError(f"Missing columns: {missing}")

    df = df.dropna()
    if df.empty:
        raise ValueError("CSV contains no valid rows")

    # Date parsing
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if df['date'].isna().any():
        raise ValueError("Invalid date format found in CSV")

    # Numeric validation
    try:
        df['units_sold'] = df['units_sold'].astype(int)
        df['unit_price'] = df['unit_price'].astype(float)
    except ValueError:
        raise ValueError("units_sold or unit_price contains invalid numbers")

    # Business sanity rules
    if (df['units_sold'] <= 0).any():
        raise ValueError("units_sold must be greater than zero")
    if (df['unit_price'] <= 0).any():
        raise ValueError("unit_price must be greater than zero")

    # Revenue calculation
    df['revenue'] = df['units_sold'] * df['unit_price']

    # Remove duplicates
    df = df.drop_duplicates(subset=['date', 'product', 'region'], keep='first')
    if df.empty:
        raise ValueError("All rows were duplicates")

    return df
