import requests
import time
import datetime
import csv

# Replace with your OpenWeather API key
API_KEY = "bc06f35431e57d2f4ed229c70296df62"
# Coordinates for Karachi
lat = 24.8607
lon = 67.0011

# Function to fetch historical data for each hour
def fetch_hourly_data(start_timestamp, end_timestamp):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_timestamp}&end={end_timestamp}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Received status code {response.status_code} for range {start_timestamp} - {end_timestamp}")
        return {}

# Get the current time and 3 years before (for the last 3 years)
end_time = int(time.time())  # Current time
start_time = end_time - (60 * 60 * 24 * 365 * 3)  # 3 years ago (approximately)

# Break the range into hourly intervals (hourly data)
hourly_interval = 60 * 60  # One hour in seconds
data = []

# Loop over the hourly intervals and fetch data for the last 3 years
for timestamp in range(start_time, end_time, hourly_interval):
    try:
        # Fetch data for each hour
        start = timestamp
        end = timestamp + hourly_interval
        print(f"Fetching data for range {start} - {end}")
        result = fetch_hourly_data(start, end)

        if "list" in result:
            data.extend(result["list"])  # Append hourly data points
        else:
            print(f"No data found for range {start} - {end}")

    except Exception as e:
        print(f"Error fetching data for {timestamp}: {e}")

# Save the data to a CSV file
with open("karachi_air_pollution_hourly_3years.csv", "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow(["Timestamp", "AQI", "PM2.5", "PM10", "CO", "NO", "NO2", "O3", "SO2", "NH3"])

    for entry in data:
        timestamp = entry.get("dt", "N/A")
        components = entry.get("components", {})  # Pollutant concentrations

        # Get pollutant levels (default to 0 if not available)
        pm2_5 = components.get("pm2_5", 0)
        pm10 = components.get("pm10", 0)
        co = components.get("co", 0)
        no = components.get("no", 0)
        no2 = components.get("no2", 0)
        o3 = components.get("o3", 0)
        so2 = components.get("so2", 0)
        nh3 = components.get("nh3", 0)

        # Use the maximum of PM2.5 or PM10 as the estimated AQI
        aqi = max(pm2_5, pm10)

        # Write the row to the CSV file
        csvwriter.writerow([
            datetime.datetime.utcfromtimestamp(timestamp),
            aqi,
            pm2_5,
            pm10,
            co,
            no,
            no2,
            o3,
            so2,
            nh3
        ])

print(f"Saved {len(data)} hourly data points to karachi_air_pollution_hourly_3years.csv")
