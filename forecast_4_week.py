import pandas as pd
from sklearn.ensemble import RandomForestRegressor


# FORESIGHT — 4-Week Forward Demand Forecast
# 1. Load weekly features


df = pd.read_csv("processed/weekly_features.csv")

df["Week_Start"] = pd.to_datetime(df["Week_Start"])

df = df.sort_values(
    ["SKU", "Week_Start"]
).copy()


# Remove final incomplete week if present
df = df[df["Week_Start"] < "2025-12-29"].copy()



# 2. Feature columns

base_features = [
    "Lag_1_Week",
    "Lag_2_Week",
    "Lag_4_Week",
    "Lag_8_Week",
    "Lag_52_Week",
    "Rolling_4_Week_Mean",
    "Rolling_8_Week_Mean",
    "Rolling_12_Week_Mean",
    "Year",
    "Month",
    "Week_Of_Year",
    "Weekend_Days",
    "Holiday_Days",
    "Promotion_Days",
    "Total_Promotion_Days",
    "Avg_Price",
]



# 3. Encode categorical variables

df = pd.get_dummies(
    df,
    columns=["SKU", "Category", "Subcategory"],
    dtype=int
)


encoded_features = [
    column
    for column in df.columns
    if column.startswith("SKU_")
    or column.startswith("Category_")
    or column.startswith("Subcategory_")
]
feature_columns = base_features + encoded_features


# 4. Train final Random Forest

train = df.dropna(
    subset=feature_columns + ["Weekly_Units_Sold"]
).copy()

X_train = train[feature_columns]
y_train = train["Weekly_Units_Sold"]


print("Training final Random Forest model...")

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=1
)

model.fit(
    X_train,
    y_train
)

print(f"Training rows: {len(train):,}")
print(f"Features: {len(feature_columns)}")



# 5. Recover original dataset before encoding

original = pd.read_csv(
    "processed/weekly_features.csv"
)

original["Week_Start"] = pd.to_datetime(
    original["Week_Start"]
)

original = original[
    original["Week_Start"] < "2025-12-29"
].copy()

original = original.sort_values(
    ["SKU", "Week_Start"]
)



# 6. Establish forecasting horizon

last_known_week = original["Week_Start"].max()

# The last complete historical week is 2025-12-22.
# 2025-12-29 is an incomplete historical week, so we
# generate it internally as a recursive bridge and then
# report the next four complete future weeks.

recursive_weeks = [
    last_known_week + pd.Timedelta(days=7 * i, unit="D")
    for i in range(1, 6)
]

forecast_weeks = recursive_weeks[1:]

print("\nForecast Horizon")
print("----------------")
for week in forecast_weeks:
    print(week.date())



# 7. Prepare recursive forecasting

forecast_records = []


skus = original["SKU"].unique()

# Create one history table for each SKU
sku_histories = {}

for sku in skus:
    sku_histories[sku] = (
        original[original["SKU"] == sku]
        .sort_values("Week_Start")
        .copy()
        .reset_index(drop=True)
    )

for forecast_week in recursive_weeks:

    prediction_rows = []
    prediction_skus = []

    week_number = forecast_week.isocalendar().week
    year = forecast_week.year
    month = forecast_week.month

    week_end = forecast_week + pd.Timedelta(days=6, unit="D")
    date_range = pd.date_range(forecast_week, week_end, freq="D")
    weekend_days = sum(date.dayofweek >= 5 for date in date_range)

    # Build all 50 SKU prediction rows first
    for sku in skus:

        sku_history = sku_histories[sku]

        demand_series = sku_history["Weekly_Units_Sold"].tolist()

        if len(demand_series) < 52:
            raise ValueError(
                f"{sku} does not have enough history for Lag_52."
            )

        lag_1 = demand_series[-1]
        lag_2 = demand_series[-2]
        lag_4 = demand_series[-4]
        lag_8 = demand_series[-8]
        lag_52 = demand_series[-52]

        rolling_4 = sum(demand_series[-4:]) / 4
        rolling_8 = sum(demand_series[-8:]) / 8
        rolling_12 = sum(demand_series[-12:]) / 12

        holiday_days = 0
        promotion_days = 0
        total_promotion_days = 0

        latest_price = sku_history["Avg_Price"].iloc[-1]

        latest_row = sku_history.iloc[-1]

        category = latest_row["Category"]
        subcategory = latest_row["Subcategory"]

        row = {
            "Lag_1_Week": lag_1,
            "Lag_2_Week": lag_2,
            "Lag_4_Week": lag_4,
            "Lag_8_Week": lag_8,
            "Lag_52_Week": lag_52,
            "Rolling_4_Week_Mean": rolling_4,
            "Rolling_8_Week_Mean": rolling_8,
            "Rolling_12_Week_Mean": rolling_12,
            "Year": year,
            "Month": month,
            "Week_Of_Year": week_number,
            "Weekend_Days": weekend_days,
            "Holiday_Days": holiday_days,
            "Promotion_Days": promotion_days,
            "Total_Promotion_Days": total_promotion_days,
            "Avg_Price": latest_price,
        }

        # Add encoded categorical features
        for column in encoded_features:
            row[column] = 0

        sku_column = f"SKU_{sku}"
        category_column = f"Category_{category}"
        subcategory_column = f"Subcategory_{subcategory}"

        row[sku_column] = 1
        row[category_column] = 1
        row[subcategory_column] = 1


        prediction_rows.append(row)
        prediction_skus.append(sku)

    # ONE prediction call for all 50 SKUs
    prediction_frame = pd.DataFrame(prediction_rows)
    prediction_frame = prediction_frame[feature_columns]

    predictions = model.predict(prediction_frame)

    predictions = [max(0, value) for value in predictions]

    # Store predictions and update each SKU history
    for sku, forecast_value in zip(prediction_skus, predictions):

        if forecast_week in forecast_weeks:

            forecast_records.append({
                "Week_Start": forecast_week,
                "SKU": sku,
                "Forecast_Units": round(forecast_value, 2),
                "Forecast_Horizon_Week": (
                    forecast_weeks.index(forecast_week) + 1
                )
            })

        # Add predicted demand to history for recursive forecasting
        new_row = pd.DataFrame([{
            "Week_Start": forecast_week,
            "SKU": sku,
            "Weekly_Units_Sold": forecast_value
        }])

        sku_histories[sku] = pd.concat(
            [sku_histories[sku], new_row],
            ignore_index=True
        )

    print(
        f"Completed recursive week: {forecast_week.date()}"
    )



# 8. Create forecast dataframe

forecast_df = pd.DataFrame(
    forecast_records
)

forecast_df = forecast_df.sort_values(
    ["SKU", "Week_Start"]
).reset_index(drop=True)



# 9. Save output

output_path = (
    "processed/forecast_4_week.csv"
)

forecast_df.to_csv(
    output_path,
    index=False
)



# 10. Summary

print("\nFORESIGHT 4-Week Forecast")
print("------------------------")

print(
    f"SKUs forecasted: "
    f"{forecast_df['SKU'].nunique()}"
)

print(
    f"Forecast weeks: "
    f"{forecast_df['Week_Start'].nunique()}"
)

print(
    f"Forecast rows: "
    f"{len(forecast_df)}"
)

print(
    f"\nTotal forecast demand: "
    f"{forecast_df['Forecast_Units'].sum():,.0f}"
)


print("\nForecast by Week:")
print(
    forecast_df
    .groupby("Week_Start")["Forecast_Units"]
    .sum()
    .round(0)
    .to_string()
)


print("\nTop 10 Forecasted SKUs:")
print(
    forecast_df
    .groupby("SKU")["Forecast_Units"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .round(0)
    .to_string()
)


print(
    f"\nSaved forecast to: "
    f"{output_path}"
)