import pandas as pd
from pathlib import Path

# Location of our CSV files
DATA_DIR = Path("data")

files = [
    "sales_daily.csv",
    "sku_master.csv",
    "calendar.csv",
    "inventory_snapshots.csv"
]

for file_name in files:
    file_path = DATA_DIR / file_name

    print("\n" + "=" * 60)
    print(f"DATASET: {file_name}")
    print("=" * 60)

    df = pd.read_csv(file_path)

    # Basic structure
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    print(list(df.columns))

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print(f"\nDuplicate rows: {df.duplicated().sum():,}")

    # Date-related columns
    date_columns = [
        col for col in df.columns
        if "date" in col.lower()
    ]

    for col in date_columns:
        dates = pd.to_datetime(df[col], errors="coerce")

        print(f"\nDate information for '{col}':")
        print(f"  Valid dates: {dates.notna().sum():,}")
        print(f"  Minimum date: {dates.min()}")
        print(f"  Maximum date: {dates.max()}")

    # SKU information
    sku_columns = [
        col for col in df.columns
        if col.lower() == "sku"
    ]

    for col in sku_columns:
        print(f"\nUnique SKUs in '{col}': {df[col].nunique():,}")
# Check SKU overlap across datasets
print("\n" + "=" * 60)
print("SKU OVERLAP CHECK")
print("=" * 60)

sales_skus = set(pd.read_csv(DATA_DIR / "sales_daily.csv")["SKU"])
master_skus = set(pd.read_csv(DATA_DIR / "sku_master.csv")["SKU"])
inventory_skus = set(pd.read_csv(DATA_DIR / "inventory_snapshots.csv")["SKU"])

print(f"Sales SKUs: {len(sales_skus)}")
print(f"Master SKUs: {len(master_skus)}")
print(f"Inventory SKUs: {len(inventory_skus)}")

print("\nInventory SKUs not in master:")
print(sorted(inventory_skus - master_skus))

print("\nMaster SKUs not in inventory:")
print(sorted(master_skus - inventory_skus))

# Detailed data quality checks
print("\n" + "=" * 60)
print("DETAILED DATA QUALITY CHECKS")
print("=" * 60)

sales = pd.read_csv(DATA_DIR / "sales_daily.csv")
master = pd.read_csv(DATA_DIR / "sku_master.csv")
calendar = pd.read_csv(DATA_DIR / "calendar.csv")
inventory = pd.read_csv(DATA_DIR / "inventory_snapshots.csv")

# Sales checks
print("\n--- SALES DATA ---")

print(f"Units sold minimum: {sales['Units_Sold'].min()}")
print(f"Units sold maximum: {sales['Units_Sold'].max()}")
print(f"Revenue minimum: {sales['Revenue'].min():,.2f}")
print(f"Revenue maximum: {sales['Revenue'].max():,.2f}")
print(f"Price minimum: {sales['Price'].min():,.2f}")
print(f"Price maximum: {sales['Price'].max():,.2f}")

print(f"\nNegative Units_Sold: {(sales['Units_Sold'] < 0).sum()}")
print(f"Zero Units_Sold: {(sales['Units_Sold'] == 0).sum()}")
print(f"Negative Revenue: {(sales['Revenue'] < 0).sum()}")
print(f"Negative Price: {(sales['Price'] < 0).sum()}")

# SKU master checks
print("\n--- SKU MASTER ---")

print(f"Categories: {master['Category'].nunique()}")
print(f"Subcategories: {master['Subcategory'].nunique()}")

print("\nCategory values:")
print(master['Category'].value_counts())

print("\nNegative cost prices:", (master['Cost_Price'] < 0).sum())
print("Negative selling prices:", (master['Selling_Price'] < 0).sum())
print("Negative gross margins:", (master['Gross_Margin_Per_Unit'] < 0).sum())

# Calendar checks
print("\n--- CALENDAR ---")

print("Holiday values:")
print(calendar['holiday'].value_counts(dropna=False))

print("\nPromotion event values:")
print(calendar['promotion_event'].value_counts(dropna=False))

# Inventory checks
print("\n--- INVENTORY ---")

print(f"Current stock minimum: {inventory['Current_Stock'].min()}")
print(f"Current stock maximum: {inventory['Current_Stock'].max()}")

print(f"On-order minimum: {inventory['On_Order'].min()}")
print(f"On-order maximum: {inventory['On_Order'].max()}")

print(f"Lead-time minimum: {inventory['Lead_Time_Days'].min()}")
print(f"Lead-time maximum: {inventory['Lead_Time_Days'].max()}")

print(f"Safety-stock minimum: {inventory['Safety_Stock'].min()}")
print(f"Reorder-point minimum: {inventory['Reorder_Point'].min()}")

print(f"\nNegative current stock: {(inventory['Current_Stock'] < 0).sum()}")
print(f"Negative on-order quantity: {(inventory['On_Order'] < 0).sum()}")
print(f"Negative inventory value: {(inventory['Inventory_Value'] < 0).sum()}")

# Duplicate SKU/date combinations
print("\n--- DUPLICATE SKU-DATE CHECKS ---")

sales_duplicates = sales.duplicated(
    subset=['Date', 'SKU']
).sum()

inventory_duplicates = inventory.duplicated(
    subset=['Snapshot_Date', 'SKU']
).sum()

print(f"Duplicate Date + SKU in sales: {sales_duplicates}")
print(f"Duplicate Snapshot_Date + SKU in inventory: {inventory_duplicates}")