import pandas as pd

# FORESIGHT — Inventory Risk Engine
# 1. Load processed datasets

sales = pd.read_csv("processed/sales_clean.csv")
inventory = pd.read_csv("processed/inventory_clean.csv")
sku_master = pd.read_csv("processed/sku_master_clean.csv")

sales["Date"] = pd.to_datetime(sales["Date"])
inventory["Snapshot_Date"] = pd.to_datetime(inventory["Snapshot_Date"])


# 2. Use the latest inventory snapshot

latest_inventory_date = inventory["Snapshot_Date"].max()

latest_inventory = inventory[
    inventory["Snapshot_Date"] == latest_inventory_date
].copy()

print(f"Inventory snapshot date: {latest_inventory_date.date()}")
print(f"SKUs evaluated: {latest_inventory['SKU'].nunique()}")



# 3. Calculate recent demand
# Used the most recent 28 days ending
# on the inventory snapshot date.

demand_end_date = latest_inventory_date
demand_start_date = demand_end_date - pd.Timedelta(days=27)

recent_sales = sales[
    (sales["Date"] >= demand_start_date)
    & (sales["Date"] <= demand_end_date)
].copy()

recent_demand = (
    recent_sales
    .groupby("SKU")
    .agg(
        Units_28_Days=("Units_Sold", "sum")
    )
    .reset_index()
)

recent_demand["Avg_Daily_Demand"] = (
    recent_demand["Units_28_Days"] / 28
)



# 4. Combine inventory + demand

risk = latest_inventory.merge(
    recent_demand,
    on="SKU",
    how="left"
)

risk = risk.merge(
    sku_master[
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

risk["Avg_Daily_Demand"] = risk["Avg_Daily_Demand"].fillna(0)



# 5. Calculate demand during lead time

risk["Lead_Time_Demand"] = (
    risk["Avg_Daily_Demand"]
    * risk["Lead_Time_Days"]
)



# 6. Calculate inventory coverage

risk["Current_Stock_Coverage_Days"] = (
    risk["Current_Stock"]
    / risk["Avg_Daily_Demand"].replace(0, pd.NA)
)

risk["Total_Stock_Coverage_Days"] = (
    (risk["Current_Stock"] + risk["On_Order"])
    / risk["Avg_Daily_Demand"].replace(0, pd.NA)
)



# 7. Calculate inventory position

risk["Inventory_Position"] = (
    risk["Current_Stock"]
    + risk["On_Order"]
)



# 8. Determine stock risk

def determine_risk(row):

    demand = row["Avg_Daily_Demand"]
    current_stock = row["Current_Stock"]
    lead_time_demand = row["Lead_Time_Demand"]
    safety_stock = row["Safety_Stock"]

    if demand <= 0:
        return "No Demand"

    if current_stock < lead_time_demand:
        return "Critical"

    if current_stock < (lead_time_demand + safety_stock):
        return "High"

    if current_stock < row["Reorder_Point"]:
        return "Medium"

    return "Low"


risk["Risk_Level"] = risk.apply(
    determine_risk,
    axis=1
)



# 9. Calculate reorder requirement
# Target inventory =
# lead-time demand + safety stock

risk["Target_Inventory"] = (
    risk["Lead_Time_Demand"]
    + risk["Safety_Stock"]
)

risk["Recommended_Order_Qty"] = (
    risk["Target_Inventory"]
    - risk["Current_Stock"]
    - risk["On_Order"]
).clip(lower=0)



# 10. Determine operational action

def determine_action(row):

    if row["Risk_Level"] == "Critical":
        if row["Recommended_Order_Qty"] > 0:
            return "Urgent Reorder"
        return "Expedite Existing Order"

    if row["Risk_Level"] == "High":
        if row["Recommended_Order_Qty"] > 0:
            return "Reorder"
        return "Monitor Incoming Stock"

    if row["Risk_Level"] == "Medium":
        if row["Recommended_Order_Qty"] > 0:
            return "Plan Reorder"
        return "Monitor"

    if row["Risk_Level"] == "No Demand":
        return "Review Demand"

    return "No Action"


risk["Recommended_Action"] = risk.apply(
    determine_action,
    axis=1
)



# 11. Calculate inventory value

risk["Current_Inventory_Value"] = (
    risk["Current_Stock"]
    * risk["Cost_Price"]
)

risk["Recommended_Order_Value"] = (
    risk["Recommended_Order_Qty"]
    * risk["Cost_Price"]
)



# 12. Risk priority score
# Higher score = greater operational urgency.

risk["Risk_Score"] = 0

risk.loc[
    risk["Risk_Level"] == "Critical",
    "Risk_Score"
] = 4

risk.loc[
    risk["Risk_Level"] == "High",
    "Risk_Score"
] = 3

risk.loc[
    risk["Risk_Level"] == "Medium",
    "Risk_Score"
] = 2

risk.loc[
    risk["Risk_Level"] == "Low",
    "Risk_Score"
] = 1

risk["Risk_Score"] = (
    risk["Risk_Score"]
    + (
        risk["Recommended_Order_Qty"]
        / risk["Avg_Daily_Demand"].replace(0, pd.NA)
    ).fillna(0).clip(upper=10) * 0.1
)


# 13. Select final columns

final_columns = [
    "SKU",
    "Product_Name",
    "Category",
    "Subcategory",

    "Snapshot_Date",

    "Current_Stock",
    "On_Order",
    "Inventory_Position",

    "Avg_Daily_Demand",
    "Units_28_Days",

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

risk = risk[final_columns]



# 14. Clean numeric values

numeric_columns = [
    "Avg_Daily_Demand",
    "Lead_Time_Demand",
    "Current_Stock_Coverage_Days",
    "Total_Stock_Coverage_Days",
    "Target_Inventory",
    "Recommended_Order_Qty",
    "Risk_Score",
    "Current_Inventory_Value",
    "Recommended_Order_Value"
]

risk[numeric_columns] = risk[numeric_columns].round(2)



# 15. Sort by operational risk

risk = risk.sort_values(
    ["Risk_Score", "Recommended_Order_Qty"],
    ascending=[False, False]
)



# 16. Save output

output_path = "processed/inventory_risk.csv"

risk.to_csv(
    output_path,
    index=False
)



# 17. Print summary

print("\nFORESIGHT Inventory Risk Summary")
print("---------------------------------")

print("\nRisk Distribution:")
print(
    risk["Risk_Level"]
    .value_counts()
    .to_string()
)

print("\nRecommended Actions:")
print(
    risk["Recommended_Action"]
    .value_counts()
    .to_string()
)

print("\nTotal Recommended Order Units:")
print(
    f"{risk['Recommended_Order_Qty'].sum():,.0f}"
)

print("\nTotal Recommended Order Value:")
print(
    f"{risk['Recommended_Order_Value'].sum():,.2f}"
)

print("\nTop 10 Inventory Risks:")
print(
    risk[
        [
            "SKU",
            "Product_Name",
            "Current_Stock",
            "On_Order",
            "Avg_Daily_Demand",
            "Lead_Time_Days",
            "Risk_Level",
            "Recommended_Order_Qty",
            "Recommended_Action"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print(f"\nSaved inventory risk output to: {output_path}")