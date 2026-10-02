import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
PROCESSED_DIR = Path("processed")

PROCESSED_DIR.mkdir(exist_ok=True)

sales = pd.read_csv(DATA_DIR / "sales_daily.csv")
master = pd.read_csv(DATA_DIR / "sku_master.csv")
calendar = pd.read_csv(DATA_DIR / "calendar.csv")
inventory = pd.read_csv(DATA_DIR / "inventory_snapshots.csv")

print("Raw datasets loaded successfully.")

sales["Date"] = pd.to_datetime(sales["Date"])
master["Launch_Date"] = pd.to_datetime(master["Launch_Date"])
calendar["date"] = pd.to_datetime(calendar["date"])
inventory["Snapshot_Date"] = pd.to_datetime(inventory["Snapshot_Date"])

calendar["holiday"] = calendar["holiday"].fillna("None")
calendar["promotion_event"] = calendar["promotion_event"].fillna("None")

sales_skus = set(sales["SKU"])
master_skus = set(master["SKU"])

inventory = inventory[
    inventory["SKU"].isin(master_skus)
].copy()

sales.to_csv(PROCESSED_DIR / "sales_clean.csv", index=False)
master.to_csv(PROCESSED_DIR / "sku_master_clean.csv", index=False)
calendar.to_csv(PROCESSED_DIR / "calendar_clean.csv", index=False)
inventory.to_csv(PROCESSED_DIR / "inventory_clean.csv", index=False)


print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(f"Sales rows: {len(sales):,}")
print(f"Master rows: {len(master):,}")
print(f"Calendar rows: {len(calendar):,}")
print(f"Inventory rows after SKU filtering: {len(inventory):,}")

print("\nProcessed files created:")
print("- sales_clean.csv")
print("- sku_master_clean.csv")
print("- calendar_clean.csv")
print("- inventory_clean.csv")