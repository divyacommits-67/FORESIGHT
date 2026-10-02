import pandas as pd

# Load forecast
forecast = pd.read_csv("processed/forecast_4_week.csv")
forecast["Week_Start"] = pd.to_datetime(forecast["Week_Start"])

# Load historical weekly features
history = pd.read_csv("processed/weekly_features.csv")
history["Week_Start"] = pd.to_datetime(history["Week_Start"])

# Exclude final partial historical week
history = history[history["Week_Start"] < "2025-12-29"].copy()

print("\nFORESIGHT — Forecast Sanity Check")
print("----------------------------------")

# Basic validation
print(f"Forecast rows: {len(forecast):,}")
print(f"Forecast SKUs: {forecast['SKU'].nunique()}")
print(f"Forecast weeks: {forecast['Week_Start'].nunique()}")

print("\nForecast date range:")
print(f"{forecast['Week_Start'].min().date()} to {forecast['Week_Start'].max().date()}")

# Historical weekly demand
historical_weekly = (
    history
    .groupby("Week_Start")["Weekly_Units_Sold"]
    .sum()
)

print("\nHistorical weekly demand:")
print(f"Average: {historical_weekly.mean():,.0f}")
print(f"Minimum: {historical_weekly.min():,.0f}")
print(f"Maximum: {historical_weekly.max():,.0f}")

# Forecast weekly demand
forecast_weekly = (
    forecast
    .groupby("Week_Start")["Forecast_Units"]
    .sum()
)

print("\nForecast weekly demand:")
print(forecast_weekly.round(0).to_string())

# Compare forecast with historical average
forecast_average = forecast["Forecast_Units"].sum() / 4

historical_average = historical_weekly.mean()

difference_pct = (
    (forecast_average - historical_average)
    / historical_average
) * 100

print("\nForecast vs historical average:")
print(f"Historical weekly average: {historical_average:,.0f}")
print(f"Forecast weekly average: {forecast_average:,.0f}")
print(f"Difference: {difference_pct:+.2f}%")

# Per-SKU forecast totals
sku_forecast = (
    forecast
    .groupby("SKU")["Forecast_Units"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTop 10 forecasted SKUs:")
print(sku_forecast.head(10).round(0).to_string())

print("\nBottom 10 forecasted SKUs:")
print(sku_forecast.tail(10).round(0).to_string())

# Check for invalid forecasts
negative_forecasts = (forecast["Forecast_Units"] < 0).sum()
zero_forecasts = (forecast["Forecast_Units"] == 0).sum()

print("\nForecast validity checks:")
print(f"Negative forecasts: {negative_forecasts}")
print(f"Zero forecasts: {zero_forecasts}")

print("\nSanity check complete.")