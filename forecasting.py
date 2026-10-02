import pandas as pd
from sklearn.ensemble import RandomForestRegressor


# Load data

df = pd.read_csv("processed/weekly_features.csv")
df["Week_Start"] = pd.to_datetime(df["Week_Start"])

# Remove final incomplete week
df = df[df["Week_Start"] < "2025-12-29"].copy()

df = df.sort_values(["SKU", "Week_Start"])


# Features used by the ML model

feature_columns = [
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



# Prepare categorical variables
# Convert SKU and Category into numeric one-hot features
df = pd.get_dummies(
    df,
    columns=["SKU", "Category", "Subcategory"],
    dtype=int
)

# Rebuild feature list after one-hot encoding
encoded_features = [
    column
    for column in df.columns
    if column.startswith("SKU_")
    or column.startswith("Category_")
    or column.startswith("Subcategory_")
]

feature_columns = feature_columns + encoded_features



# Rolling-origin folds

folds = [
      ("2025-06-23", "2025-06-30", "2025-07-21"),
    ("2025-07-21", "2025-07-28", "2025-08-18"),
    ("2025-08-18", "2025-08-25", "2025-09-15"),
    ("2025-09-15", "2025-09-22", "2025-10-13"),
    ("2025-10-13", "2025-10-20", "2025-11-10"),
    ("2025-11-10", "2025-11-17", "2025-12-08"),
]


results = []
all_predictions = []
feature_importances = []



# Run rolling-origin validation

for fold_number, (train_end, validation_start, validation_end) in enumerate(
    folds, start=1
):

    train_end = pd.Timestamp(train_end)
    validation_start = pd.Timestamp(validation_start)
    validation_end = pd.Timestamp(validation_end)

    train = df[df["Week_Start"] <= train_end].copy()

    validation = df[
        (df["Week_Start"] >= validation_start)
        & (df["Week_Start"] <= validation_end)
    ].copy()

    # Remove rows with missing lag/rolling features
    train = train.dropna(subset=feature_columns)
    validation = validation.dropna(subset=feature_columns)

    X_train = train[feature_columns]
    y_train = train["Weekly_Units_Sold"]

    X_validation = validation[feature_columns]
    y_validation = validation["Weekly_Units_Sold"]

    
    # Random Forest

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    # Store feature importance for this fold
    fold_importance = pd.DataFrame({
        "Feature": feature_columns,
        "Importance": model.feature_importances_
})

    feature_importances.append(fold_importance)

    predictions = model.predict(X_validation)

    validation["ML_Forecast"] = predictions

    # Absolute error
    validation["Absolute_Error"] = (
        validation["Weekly_Units_Sold"]
        - validation["ML_Forecast"]
    ).abs()

# Recover original SKU from one-hot encoded columns
    sku_columns = [c for c in validation.columns if c.startswith("SKU_")]
    validation["SKU"] = validation[sku_columns].idxmax(axis=1).str.replace(
       "SKU_", "", regex=False
)

    # WAPE
    fold_wape = (
        validation["Absolute_Error"].sum()
        / validation["Weekly_Units_Sold"].abs().sum()
    ) * 100

    results.append({
        "Fold": fold_number,
        "Train_End": train_end.date(),
        "Validation_Start": validation_start.date(),
        "Validation_End": validation_end.date(),
        "Validation_Weeks": validation["Week_Start"].nunique(),
        "WAPE": fold_wape
    })

    validation["Fold"] = fold_number
    all_predictions.append(validation)



# Results

results_df = pd.DataFrame(results)

print("\nRandom Forest Rolling-Origin Backtest")
print("-------------------------------------")
print(results_df.to_string(index=False))


# Overall pooled WAPE
all_predictions_df = pd.concat(
    all_predictions,
    ignore_index=True
)

overall_wape = (
    all_predictions_df["Absolute_Error"].sum()
    / all_predictions_df["Weekly_Units_Sold"].abs().sum()
) * 100

print(f"\nOverall Random Forest WAPE: {overall_wape:.2f}%")


# Aggregated Feature Importance

importance_df = pd.concat(
    feature_importances,
    ignore_index=True
)

average_importance = (
    importance_df
    .groupby("Feature")["Importance"]
    .mean()
    .sort_values(ascending=False)
)

print("\nTop 15 Feature Importances")
print("--------------------------")
print(average_importance.head(15).to_string())


# Per-SKU Forecast Performance

sku_wape = (
    all_predictions_df
    .groupby("SKU")
    .apply(
        lambda x: (
            x["Absolute_Error"].sum()
            / x["Weekly_Units_Sold"].abs().sum()
        ) * 100
    )
    .sort_values()
)

print("\nBest 10 SKUs by WAPE")
print("--------------------")
print(sku_wape.head(10).to_string())

print("\nWorst 10 SKUs by WAPE")
print("---------------------")
print(sku_wape.tail(10).sort_values(ascending=False).to_string())


# Per-SKU Forecast Diagnostics

sku_diagnostics = (
    all_predictions_df
    .groupby("SKU")
    .agg(
        Actual_Units=("Weekly_Units_Sold", "sum"),
        Forecast_Units=("ML_Forecast", "sum"),
        Absolute_Error=("Absolute_Error", "sum")
    )
)

sku_diagnostics["Forecast_Bias"] = (
    sku_diagnostics["Forecast_Units"]
    - sku_diagnostics["Actual_Units"]
)

sku_diagnostics["WAPE"] = (
    sku_diagnostics["Absolute_Error"]
    / sku_diagnostics["Actual_Units"].abs()
) * 100

sku_diagnostics["Absolute_Error_Per_Week"] = (
    sku_diagnostics["Absolute_Error"] / 24
)

print("\nPer-SKU Forecast Diagnostics")
print("----------------------------")
print(
    sku_diagnostics
    .sort_values("WAPE")
    .to_string()
)