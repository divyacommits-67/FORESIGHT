import pandas as pd
from pathlib import Path

# Location of processed datasets
PROCESSED_DIR = Path("processed")

# Load cleaned datasets
sales = pd.read_csv(PROCESSED_DIR / "sales_clean.csv")
master = pd.read_csv(PROCESSED_DIR / "sku_master_clean.csv")
calendar = pd.read_csv(PROCESSED_DIR / "calendar_clean.csv")
inventory = pd.read_csv(PROCESSED_DIR / "inventory_clean.csv")

# Convert date columns
sales["Date"] = pd.to_datetime(sales["Date"])
master["Launch_Date"] = pd.to_datetime(master["Launch_Date"])
calendar["date"] = pd.to_datetime(calendar["date"])
inventory["Snapshot_Date"] = pd.to_datetime(inventory["Snapshot_Date"])

print("Processed datasets loaded successfully.")

print("\nSales:", sales.shape)
print("Master:", master.shape)
print("Calendar:", calendar.shape)
print("Inventory:", inventory.shape)


# 1. Overall daily demand

daily_demand = (
    sales.groupby("Date")["Units_Sold"]
    .sum()
    .reset_index()
)

print("\n" + "=" * 60)
print("OVERALL DAILY DEMAND")
print("=" * 60)

print(f"Total units sold: {sales['Units_Sold'].sum():,}")
print(f"Average daily demand: {daily_demand['Units_Sold'].mean():,.2f}")
print(f"Minimum daily demand: {daily_demand['Units_Sold'].min():,}")
print(f"Maximum daily demand: {daily_demand['Units_Sold'].max():,}")

print("\nFirst 5 days:")
print(daily_demand.head())

print("\nLast 5 days:")
print(daily_demand.tail())



# 2. Daily demand trend

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))

plt.plot(
    daily_demand["Date"],
    daily_demand["Units_Sold"]
)

plt.title("Daily Units Sold - Overall Demand Trend")
plt.xlabel("Date")
plt.ylabel("Units Sold")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Promotion and holiday analysis

promotion_dates = calendar[
    calendar["promotion_event"].notna() &
    (calendar["promotion_event"] != "None")
]

print("\nPromotion periods:")
print(promotion_dates[["date", "promotion_event"]].head(20))

print("\nNumber of promotion days:", len(promotion_dates))

holiday_dates = calendar[
    calendar["holiday"].notna() &
    (calendar["holiday"] != "None")
]

print("\nHoliday dates:")
print(holiday_dates[["date", "holiday"]])

# Compare demand on promotion vs non-promotion days

sales_calendar = sales.merge(
    calendar[["date", "promotion_event"]],
    left_on="Date",
    right_on="date",
    how="left"
)

sales_calendar["Is_Promotion"] = (
    sales_calendar["promotion_event"].notna() &
    (sales_calendar["promotion_event"] != "None")
)

promotion_demand = (
    sales_calendar.groupby("Is_Promotion")["Units_Sold"]
    .mean()
)

print("\nAverage daily units sold:")
print("Non-promotion days:", round(promotion_demand[False], 2))
print("Promotion days:", round(promotion_demand[True], 2))

# Monthly demand analysis

sales["Date"] = pd.to_datetime(sales["Date"])

monthly_demand = (
    sales.groupby(sales["Date"].dt.to_period("M"))["Units_Sold"]
    .sum()
    .reset_index()
)

monthly_demand["Date"] = monthly_demand["Date"].dt.to_timestamp()

print("\nMonthly demand:")
print(monthly_demand.to_string(index=False))

# SKU-level demand analysis

sku_demand = (
    sales.groupby("SKU")["Units_Sold"]
    .agg(["sum", "mean", "std"])
    .reset_index()
)

sku_demand = sku_demand.sort_values("sum", ascending=False)

print("\nTop 10 SKUs by total units sold:")
print(sku_demand.head(10).to_string(index=False))

print("\nBottom 10 SKUs by total units sold:")
print(sku_demand.tail(10).sort_values("sum").to_string(index=False))

# Monthly demand trend

plt.figure(figsize=(12, 5))
plt.plot(
    monthly_demand["Date"],
    monthly_demand["Units_Sold"],
    marker="o"
)

plt.title("Monthly Demand Trend")
plt.xlabel("Month")
plt.ylabel("Total Units Sold")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Category-level demand analysis

category_demand = (
    sales.merge(
        master[["SKU", "Category"]],
        on="SKU",
        how="left"
    )
    .groupby("Category")["Units_Sold"]
    .agg(["sum", "mean"])
    .reset_index()
    .sort_values("sum", ascending=False)
)

print("\nCategory-level demand:")
print(category_demand.to_string(index=False))

# Category-level monthly demand

category_monthly = (
    sales.merge(
        master[["SKU", "Category"]],
        on="SKU",
        how="left"
    )
    .groupby([
        sales["Date"].dt.to_period("M"),
        "Category"
    ])["Units_Sold"]
    .sum()
    .reset_index()
)

category_monthly["Date"] = category_monthly["Date"].dt.to_timestamp()

print("\nCategory monthly demand:")
print(category_monthly.to_string(index=False))

# Inventory health analysis

inventory_summary = inventory[
    [
        "Current_Stock",
        "On_Order",
        "Lead_Time_Days",
        "Safety_Stock",
        "Reorder_Point",
        "Inventory_Value"
    ]
].describe()

print("\nInventory summary:")
print(inventory_summary)

# Stock position relative to reorder point

inventory["Below_Reorder_Point"] = (
    inventory["Current_Stock"] < inventory["Reorder_Point"]
)

print("\nInventory below reorder point:")
print(
    inventory["Below_Reorder_Point"]
    .value_counts()
)

print("\nPercentage of inventory snapshots below reorder point:")
print(
    round(
        inventory["Below_Reorder_Point"].mean() * 100,
        2
    ),
    "%"
)

# Inventory value by SKU

sku_inventory = (
    inventory.groupby("SKU")
    .agg(
        Avg_Current_Stock=("Current_Stock", "mean"),
        Avg_On_Order=("On_Order", "mean"),
        Avg_Inventory_Value=("Inventory_Value", "mean"),
        Avg_Lead_Time=("Lead_Time_Days", "mean"),
        Below_Reorder_Count=("Below_Reorder_Point", "sum"),
        Snapshot_Count=("Below_Reorder_Point", "count")
    )
    .reset_index()
)

sku_inventory["Below_Reorder_Pct"] = (
    sku_inventory["Below_Reorder_Count"]
    / sku_inventory["Snapshot_Count"]
    * 100
)

sku_inventory = sku_inventory.sort_values(
    "Avg_Inventory_Value",
    ascending=False
)

print("\nTop 10 SKUs by average inventory value:")
print(
    sku_inventory.head(10).to_string(index=False)
)

print("\nTop 10 SKUs by percentage of snapshots below reorder point:")
print(
    sku_inventory
    .sort_values("Below_Reorder_Pct", ascending=False)
    .head(10)
    .to_string(index=False)
)

# Inventory analysis by category

inventory_category = (
    inventory.merge(
        master[["SKU", "Category"]],
        on="SKU",
        how="left"
    )
    .groupby("Category")
    .agg(
        Avg_Current_Stock=("Current_Stock", "mean"),
        Avg_On_Order=("On_Order", "mean"),
        Avg_Inventory_Value=("Inventory_Value", "mean"),
        Avg_Lead_Time=("Lead_Time_Days", "mean"),
        Below_Reorder_Count=("Below_Reorder_Point", "sum"),
        Snapshot_Count=("Below_Reorder_Point", "count")
    )
    .reset_index()
)

inventory_category["Below_Reorder_Pct"] = (
    inventory_category["Below_Reorder_Count"]
    / inventory_category["Snapshot_Count"]
    * 100
)

print("\nInventory analysis by category:")
print(
    inventory_category
    .sort_values("Avg_Inventory_Value", ascending=False)
    .to_string(index=False)
)



# Demand vs inventory analysis

sku_demand_inventory = (
    sku_demand[["SKU", "mean"]]
    .rename(columns={"mean": "Avg_Daily_Demand"})
    .merge(
        sku_inventory[
            [
                "SKU",
                "Avg_Current_Stock",
                "Avg_On_Order",
                "Avg_Inventory_Value",
                "Avg_Lead_Time",
                "Below_Reorder_Pct"
            ]
        ],
        on="SKU",
        how="inner"
    )
)

sku_demand_inventory["Stock_Coverage_Days"] = (
    sku_demand_inventory["Avg_Current_Stock"]
    / sku_demand_inventory["Avg_Daily_Demand"]
)

sku_demand_inventory["Total_Available_Coverage_Days"] = (
    (
        sku_demand_inventory["Avg_Current_Stock"]
        + sku_demand_inventory["Avg_On_Order"]
    )
    / sku_demand_inventory["Avg_Daily_Demand"]
)

print("\nSKUs with lowest stock coverage:")

print(
    sku_demand_inventory[
        [
            "SKU",
            "Avg_Daily_Demand",
            "Avg_Current_Stock",
            "Avg_On_Order",
            "Avg_Lead_Time",
            "Stock_Coverage_Days",
            "Total_Available_Coverage_Days",
            "Below_Reorder_Pct"
        ]
    ]
    .sort_values("Stock_Coverage_Days")
    .head(10)
    .to_string(index=False)
)