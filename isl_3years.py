import requests
import time
import datetime
import csv

# Replace with your OpenWeather API key
API_KEY = "bc06f35431e57d2f4ed229c70296df62"

# Coordinates for Islamabad
lat = 33.6844
lon = 73.0479

# Function to fetch historical data
def fetch_historical_data(start_timestamp, end_timestamp):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_timestamp}&end={end_timestamp}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Received status code {response.status_code} for range {start_timestamp} - {end_timestamp}")
        return {}

# Get timestamps for the past 3 years
end_time = int(time.time())  # Current time
start_time = end_time - (60 * 60 * 24 * 365 * 3)  # 3 years ago (approximately)

# Break the range into daily intervals
daily_interval = 60 * 60 * 24  # One day in seconds
data = []

for timestamp in range(start_time, end_time, daily_interval):
    try:
        # Fetch data for each day
        start = timestamp
        end = timestamp + daily_interval
        print(f"Fetching data for range {start} - {end}")
        result = fetch_historical_data(start, end)

        if "list" in result:
            data.append(result["list"])  # Append hourly data for the day
        else:
            print(f"No data found for range {start} - {end}")

    except Exception as e:
        print(f"Error fetching data for {timestamp}: {e}")

# Aggregate daily data
aggregated_data = []
for daily_entries in data:
    if not daily_entries:
        continue

    # Initialize daily totals
    daily_totals = {
        "pm2_5": 0, "pm10": 0, "co": 0, "no": 0, "no2": 0,
        "o3": 0, "so2": 0, "nh3": 0, "count": 0
    }

    for entry in daily_entries:
        components = entry.get("components", {})
        for key in daily_totals.keys():
            if key != "count":
                daily_totals[key] += components.get(key, 0)
        daily_totals["count"] += 1

    # Calculate averages
    count = daily_totals["count"]
    if count:
        pm2_5_avg = daily_totals["pm2_5"] / count
        pm10_avg = daily_totals["pm10"] / count
    else:
        pm2_5_avg, pm10_avg = 0, 0

    aqi = max(pm2_5_avg, pm10_avg)  # Estimated AQI based on max(PM2.5, PM10)

    aggregated_data.append({
        "date": datetime.datetime.utcfromtimestamp(daily_entries[0]["dt"]).strftime("%Y-%m-%d"),
        "aqi": round(aqi, 2),
        "pm2_5": round(pm2_5_avg, 2),
        "pm10": round(pm10_avg, 2),
        "co": round(daily_totals["co"] / count, 2) if count else 0,
        "no": round(daily_totals["no"] / count, 2) if count else 0,
        "no2": round(daily_totals["no2"] / count, 2) if count else 0,
        "o3": round(daily_totals["o3"] / count, 2) if count else 0,
        "so2": round(daily_totals["so2"] / count, 2) if count else 0,
        "nh3": round(daily_totals["nh3"] / count, 2) if count else 0,
    })

# Save the aggregated data to a CSV file
with open("islamabad_air_pollution_daily.csv", "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow(["Date", "AQI", "PM2.5", "PM10", "CO", "NO", "NO2", "O3", "SO2", "NH3"])

    for entry in aggregated_data:
        csvwriter.writerow([
            entry["date"],
            entry["aqi"],
            entry["pm2_5"],
            entry["pm10"],
            entry["co"],
            entry["no"],
            entry["no2"],
            entry["o3"],
            entry["so2"],
            entry["nh3"]
        ])

print(f"Saved {len(aggregated_data)} daily data points to islamabad_air_pollution_daily.csv")
