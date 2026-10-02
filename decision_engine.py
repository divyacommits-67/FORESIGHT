import pandas as pd


# Load datasets
forecast = pd.read_csv("processed/forecast_4_week.csv")
inventory = pd.read_csv("processed/inventory_risk.csv")
master = pd.read_csv("processed/sku_master_clean.csv")


# Load historical weekly demand for volatility analysis
history = pd.read_csv("processed/weekly_features.csv")

history["Week_Start"] = pd.to_datetime(history["Week_Start"])

history = history[history["Week_Start"] < "2025-12-29"].copy()

volatility = (
    history
    .groupby("SKU")["Weekly_Units_Sold"]
    .agg(
        Historical_Mean_Weekly_Demand="mean",
        Historical_Std_Weekly_Demand="std"
    )
    .reset_index()
)

volatility["Demand_CV"] = (
    volatility["Historical_Std_Weekly_Demand"]
    / volatility["Historical_Mean_Weekly_Demand"]
)



# Convert dates
forecast["Week_Start"] = pd.to_datetime(forecast["Week_Start"])
inventory["Snapshot_Date"] = pd.to_datetime(inventory["Snapshot_Date"])


# 1. Aggregate 4-week forecast by SKU

forecast_summary = (
    forecast
    .groupby("SKU", as_index=False)
    .agg(
        Forecast_4_Week_Units=("Forecast_Units", "sum"),
        Avg_Weekly_Forecast=("Forecast_Units", "mean")
    )
)


# 2. Select relevant inventory information

inventory_summary = inventory[
    [
        "SKU",
        "Product_Name",
        "Category",
        "Subcategory",
        "Snapshot_Date",
        "Current_Stock",
        "On_Order",
        "Inventory_Position",
        "Avg_Daily_Demand",
        "Lead_Time_Days",
        "Lead_Time_Demand",
        "Safety_Stock",
        "Reorder_Point",
        "Current_Stock_Coverage_Days",
        "Total_Stock_Coverage_Days",
        "Target_Inventory",
        "Recommended_Order_Qty",
        "Risk_Level",
        "Risk_Score",
        "Recommended_Action",
        "Cost_Price",
        "Current_Inventory_Value",
        "Recommended_Order_Value"
    ]
].copy()



# 3. Merge forecast + inventory

decision_df = inventory_summary.merge(
    forecast_summary,
    on="SKU",
    how="left",
    validate="one_to_one"
)



# 4. Add product master information if needed

master_columns = [
    "SKU",
    "Selling_Price",
    "Gross_Margin_Per_Unit"
]

master_subset = master[master_columns].copy()

decision_df = decision_df.merge(
    master_subset,
    on="SKU",
    how="left",
    validate="one_to_one"
)

# Add historical demand volatility
decision_df = decision_df.merge(
    volatility,
    on="SKU",
    how="left",
    validate="one_to_one"
)


# 5. Basic calculations

decision_df["Forecast_Avg_Daily_Demand"] = (
    decision_df["Forecast_4_Week_Units"] / 28
)

decision_df["Available_Inventory"] = (
    decision_df["Current_Stock"] +
    decision_df["On_Order"]
)

decision_df["Forecast_4_Week_Gap"] = (
    decision_df["Available_Inventory"] -
    decision_df["Forecast_4_Week_Units"]
)

decision_df["Forecast_Stock_Coverage_Days"] = (
    decision_df["Available_Inventory"] /
    decision_df["Forecast_Avg_Daily_Demand"]
)



# 6. Financial impact calculations

# Units that may be uncovered by the 4-week forecast
decision_df["Forecast_Shortfall_Units"] = (
    decision_df["Forecast_4_Week_Units"]
    - decision_df["Available_Inventory"]
).clip(lower=0)

# Potential revenue exposure from uncovered demand
decision_df["Potential_Revenue_Exposure"] = (
    decision_df["Forecast_Shortfall_Units"]
    * decision_df["Selling_Price"]
)

# Potential gross-margin exposure from uncovered demand
decision_df["Potential_Gross_Margin_Exposure"] = (
    decision_df["Forecast_Shortfall_Units"]
    * decision_df["Gross_Margin_Per_Unit"]
)

# Inventory above forecast + safety-stock requirement
decision_df["Excess_Inventory_Units"] = (
    decision_df["Available_Inventory"]
    - (
        decision_df["Forecast_4_Week_Units"]
        + decision_df["Safety_Stock"]
    )
).clip(lower=0)

# Cost value of excess inventory
decision_df["Excess_Inventory_Value"] = (
    decision_df["Excess_Inventory_Units"]
    * decision_df["Cost_Price"]
)



print(
    f"Total excess inventory value: "
    f"₹{decision_df['Excess_Inventory_Value'].sum():,.2f}"
)

print(
    f"Potential revenue exposure: "
    f"₹{decision_df['Potential_Revenue_Exposure'].sum():,.2f}"
)

print(
    f"Potential gross-margin exposure: "
    f"₹{decision_df['Potential_Gross_Margin_Exposure'].sum():,.2f}"
)

# Additional units required to cover forecast + safety stock
decision_df["Reorder_Units"] = (
    decision_df["Forecast_4_Week_Units"]
    + decision_df["Safety_Stock"]
    - decision_df["Available_Inventory"]
).clip(lower=0)

# Estimated cash investment required for replenishment
decision_df["Reorder_Investment"] = (
    decision_df["Reorder_Units"]
    * decision_df["Cost_Price"]
)


# 7. Business decision logic

def determine_action(row):

    available_inventory = row["Available_Inventory"]
    forecast_demand = row["Forecast_4_Week_Units"]
    lead_time_demand = row["Lead_Time_Demand"]
    safety_stock = row["Safety_Stock"]
    reorder_point = row["Reorder_Point"]
    current_stock = row["Current_Stock"]
    demand_cv = row["Demand_CV"]
    risk_level = str(row["Risk_Level"]).strip().lower()

    # Inventory needed to cover forecast period
    forecast_requirement = forecast_demand + safety_stock

    # Inventory needed during supplier lead time
    lead_time_requirement = lead_time_demand + safety_stock

    # 1. Reorder Now
    if (
        (available_inventory < forecast_requirement)
        or
        (
            row["Inventory_Position"] < reorder_point
            and current_stock < lead_time_requirement
        )
    ):
        return "Reorder Now"

    # 2. Markdown / Clear
    if (
        current_stock > (forecast_demand * 1.5 + safety_stock)
        and risk_level in ["low", "medium"]
    ):
        return "Markdown / Clear"

    # 3. Watch / Volatile
    if (
        demand_cv >= 0.35
        or
        risk_level in ["high", "critical"]
    ):
        return "Watch / Volatile"

    # 4. Healthy
    return "Healthy"


decision_df["Business_Action"] = decision_df.apply(
    determine_action,
    axis=1
)


# 8. Validation

print("\nFORESIGHT — Decision Engine")
print("---------------------------")

print(f"SKUs: {decision_df['SKU'].nunique()}")
print(f"Rows: {len(decision_df)}")
print("\nBusiness Action Distribution:")
print(
    decision_df["Business_Action"]
    .value_counts()
    .to_string()
)
print("\nForecast summary:")
print(
    f"Total 4-week forecast: "
    f"{decision_df['Forecast_4_Week_Units'].sum():,.0f} units"
)

print(
    f"Total available inventory: "
    f"{decision_df['Available_Inventory'].sum():,.0f} units"
)

print(
    f"SKUs with negative forecast gap: "
    f"{(decision_df['Forecast_4_Week_Gap'] < 0).sum()}"
)

print(
    f"SKUs with positive forecast gap: "
    f"{(decision_df['Forecast_4_Week_Gap'] >= 0).sum()}"
)

print("\nSample decision table:")
print(
    decision_df[
        [
            "SKU",
            "Product_Name",
            "Current_Stock",
            "On_Order",
            "Forecast_4_Week_Units",
            "Available_Inventory",
            "Forecast_4_Week_Gap",
            "Risk_Level"
        ]
    ].head(10).to_string(index=False)
)


# Save intermediate decision table
output_path = "processed/decision_table.csv"
decision_df.to_csv(output_path, index=False)

print(f"\nSaved to: {output_path}")

print("\nLow-risk SKUs marked Reorder Now:")
print(
    decision_df[
        (decision_df["Business_Action"] == "Reorder Now") &
        (decision_df["Risk_Level"] == "Low")
    ][
        [
            "SKU",
            "Product_Name",
            "Current_Stock",
            "On_Order",
            "Available_Inventory",
            "Forecast_4_Week_Units",
            "Forecast_4_Week_Gap",
            "Lead_Time_Days",
            "Lead_Time_Demand",
            "Safety_Stock",
            "Reorder_Point",
            "Current_Stock_Coverage_Days",
            "Total_Stock_Coverage_Days",
            "Risk_Level"
        ]
    ].to_string(index=False)
)

print("\nMarkdown / Clear SKUs:")
print(
    decision_df[
        decision_df["Business_Action"] == "Markdown / Clear"
    ][
        [
            "SKU",
            "Product_Name",
            "Current_Stock",
            "On_Order",
            "Available_Inventory",
            "Forecast_4_Week_Units",
            "Forecast_4_Week_Gap",
            "Lead_Time_Days",
            "Safety_Stock",
            "Current_Stock_Coverage_Days",
            "Total_Stock_Coverage_Days",
            "Risk_Level",
            "Current_Inventory_Value"
        ]
    ].sort_values(
        "Forecast_4_Week_Gap",
        ascending=False
    ).to_string(index=False)
)

print("\nWatch / Volatile SKUs:")
print(
    decision_df[
        decision_df["Business_Action"] == "Watch / Volatile"
    ][
        [
            "SKU",
            "Product_Name",
            "Current_Stock",
            "On_Order",
            "Available_Inventory",
            "Forecast_4_Week_Units",
            "Forecast_4_Week_Gap",
            "Demand_CV",
            "Lead_Time_Days",
            "Safety_Stock",
            "Current_Stock_Coverage_Days",
            "Total_Stock_Coverage_Days",
            "Risk_Level"
        ]
    ].to_string(index=False)
)


# 0. Decision validation

print("\nBusiness Action vs Risk Level:")
print(
    pd.crosstab(
        decision_df["Business_Action"],
        decision_df["Risk_Level"]
    )
)

print("\nBusiness Action vs Forecast Gap:")
print(
    decision_df.groupby("Business_Action")["Forecast_4_Week_Gap"]
    .agg(["count", "min", "max", "mean"])
)