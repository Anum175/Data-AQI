import requests
import time
import datetime

# Replace with your OpenWeather API key
API_KEY = "bc06f35431e57d2f4ed229c70296df62"

# Coordinates for Lahore
lat = 31.5497
lon = 74.3436

# Function to fetch historical data
def fetch_historical_data(start_timestamp, end_timestamp):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_timestamp}&end={end_timestamp}&appid={API_KEY}"
    response = requests.get(url)
    return response.json()

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

        # Log the result to see the response for debugging
        print("API Response:", result)

        if "list" in result:
            data.extend(result["list"])  # Append pollutant data
        else:
            print(f"No data found for range {start} - {end}")

    except Exception as e:
        print(f"Error fetching data for {timestamp}: {e}")

# Save the data to a text file
with open("lahore_air_pollution_daily_hour.txt", "w") as f:
    for entry in data:
        timestamp = entry.get("dt", "N/A")
        components = entry.get("components", {})  # Pollutant concentrations

        # Get PM2.5 and PM10 levels
        pm2_5 = components.get("pm2_5", 0)  # Default to 0 if not available
        pm10 = components.get("pm10", 0)  # Default to 0 if not available

        # Use the maximum of PM2.5 or PM10 as the estimated AQI
        aqi = max(pm2_5, pm10)

        # Format pollutants data
        pollutants = "\n".join([f"{k}: {v}" for k, v in components.items()])

        entry_text = f"""
Timestamp: {datetime.datetime.utcfromtimestamp(timestamp)}
Estimated AQI (based on max(PM2.5, PM10)): {aqi}
Pollutants:
{pollutants}
---------------------------------------------
"""
        f.write(entry_text)

print(f"Saved {len(data)} daily data points to lahore_air_pollution_daily_hour.txt")
