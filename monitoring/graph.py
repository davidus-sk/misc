import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def plot_two_time_series_from_json(json_file, title="Time Series Plot", time_format="%Y-%m-%d %H:%M:%S", value1_key="rx", value2_key="tx"):
    """
    Creates a PNG graph of two time series from a JSON file.

    Args:
        json_file (str): The path to the JSON file.
        title (str, optional): The title of the plot. Defaults to "Time Series Plot".
        time_format (str, optional): The format of the timestamps in the JSON.
                                     Defaults to "%Y-%m-%d %H:%M:%S".
        value1_key (str, optional): The key for the first value. Defaults to "value1".
        value2_key (str, optional): The key for the second value. Defaults to "value2".
    """
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        timestamps = []
        values1 = []
        values2 = []

        for item in data:
            try:
                timestamp = datetime.strptime(item['timestamp'], time_format)
                value1 = item[value1_key]
                value2 = item[value2_key]
                timestamps.append(timestamp)
                values1.append(value1)
                values2.append(value2)
            except (ValueError, KeyError) as e:
                print(f"Error parsing data: {e}. Skipping item.")
                continue

        if not timestamps:
            print("No valid data found in JSON file.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, values1, marker='o', label=value1_key)
        plt.plot(timestamps, values2, marker='x', label=value2_key)
        plt.title(title)
        plt.xlabel("Timestamp")
        plt.ylabel("Value")
        plt.grid(True)
        plt.legend() #add legend
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.gcf().autofmt_xdate()

        output_filename = json_file.replace('.json', '.png')
        plt.savefig(output_filename)
        plt.show()
        print(f"Graph saved to {output_filename}")

    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example Usage (assuming you have a data.json file):

ifaces = ["eth0", "wlan0", "tun0"]

for i in ifaces:
    plot_two_time_series_from_json(f"/dev/shm/{i}.json", title=f"Packets per second for {i}")
