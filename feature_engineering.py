import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("processed")

# Load processed datasets
sales = pd.read_csv(PROCESSED_DIR / "sales_clean.csv")
master = pd.read_csv(PROCESSED_DIR / "sku_master_clean.csv")
calendar = pd.read_csv(PROCESSED_DIR / "calendar_clean.csv")

# Convert dates
sales["Date"] = pd.to_datetime(sales["Date"])
master["Launch_Date"] = pd.to_datetime(master["Launch_Date"])
calendar["date"] = pd.to_datetime(calendar["date"])

print("Processed datasets loaded successfully.")


# 1. Create weekly SKU-level demand

sales["Week_Start"] = (
    sales["Date"]
    .dt.to_period("W-SUN")
    .dt.start_time
)

weekly_sales = (
    sales.groupby(["Week_Start", "SKU"])
    .agg(
        Weekly_Units_Sold=("Units_Sold", "sum"),
        Weekly_Revenue=("Revenue", "sum"),
        Avg_Price=("Price", "mean"),
        Total_Promotion_Days=("Promotion", "sum")
    )
    .reset_index()
)

print("\nWeekly sales created:")
print("Rows:", len(weekly_sales))
print("SKUs:", weekly_sales["SKU"].nunique())
print(
    "Weeks:",
    weekly_sales["Week_Start"].nunique()
)


# 2. Create weekly calendar features

calendar["Week_Start"] = (
    calendar["date"]
    .dt.to_period("W-SUN")
    .dt.start_time
)

weekly_calendar = (
    calendar.groupby("Week_Start")
    .agg(
        Year=("year", "first"),
        Month=("month", "first"),
        Quarter=("quarter", "first"),
        Week_Of_Year=("week", "first"),
        Weekend_Days=("is_weekend", "sum"),
        Holiday_Days=("is_holiday", "sum"),
        Promotion_Days=("promotion_event", lambda x: (
            (x.notna()) & (x != "None")
        ).sum())
    )
    .reset_index()
)



# 3. Merge weekly demand with calendar

weekly_features = weekly_sales.merge(
    weekly_calendar,
    on="Week_Start",
    how="left"
)


# 4. Add SKU master information

weekly_features = weekly_features.merge(
    master[
        [
            "SKU",
            "Product_Name",
            "Category",
            "Subcategory",
            "Cost_Price",
            "Selling_Price",
            "Gross_Margin_Per_Unit"
        ]
    ],
    on="SKU",
    how="left"
)


# 5. Sort before creating lag features

weekly_features = weekly_features.sort_values(
    ["SKU", "Week_Start"]
).reset_index(drop=True)



# 6. Lag features

for lag in [1, 2, 4, 8, 52]:
    weekly_features[f"Lag_{lag}_Week"] = (
        weekly_features
        .groupby("SKU")["Weekly_Units_Sold"]
        .shift(lag)
    )


# 7. Rolling demand features

sku_demand_series = (
    weekly_features
    .groupby("SKU")["Weekly_Units_Sold"]
)

weekly_features["Rolling_4_Week_Mean"] = (
    sku_demand_series
    .transform(
        lambda x: x.shift(1).rolling(4).mean()
    )
)

weekly_features["Rolling_8_Week_Mean"] = (
    sku_demand_series
    .transform(
        lambda x: x.shift(1).rolling(8).mean()
    )
)

weekly_features["Rolling_12_Week_Mean"] = (
    sku_demand_series
    .transform(
        lambda x: x.shift(1).rolling(12).mean()
    )
)


# 8. Save feature dataset

output_path = PROCESSED_DIR / "weekly_features.csv"

weekly_features.to_csv(
    output_path,
    index=False
)

print("\nFeature engineering complete.")
print("Feature rows:", len(weekly_features))
print("Feature columns:", len(weekly_features.columns))
print("Saved to:", output_path)

print("\nFeature columns:")
print(weekly_features.columns.tolist())


# 9. Validate feature dataset

print("\nMissing values by column:")
print(
    weekly_features.isna()
    .sum()
    .sort_values(ascending=False)
)

print("\nDuplicate Week + SKU rows:")
print(
    weekly_features.duplicated(
        subset=["Week_Start", "SKU"]
    ).sum()
)

print("\nDate range:")
print(
    weekly_features["Week_Start"].min(),
    "to",
    weekly_features["Week_Start"].max()
)

print("\nRows per SKU:")
print(
    weekly_features.groupby("SKU").size().describe()
)