import subprocess
import re
import os
import datetime
import json

def remove_top_x(input_list, x):
    """
    Removes the top X items from a list.

    Args:
        input_list: The list to modify.
        x: The number of items to remove from the beginning.

    Returns:
        A new list with the top X items removed, or the original list if x is invalid.
    """
    if not isinstance(input_list, list):
        return [] #return empty list if input is not a list

    if not isinstance(x, int) or x < 0:
        return input_list  # Return the original list if x is not a positive integer.

    if x >= len(input_list):
        return []  # Return an empty list if x is greater than or equal to the list length.

    return input_list[x:]

def parse_netstat_i():
    """
    Executes netstat -i and parses the output into an array of interface statistics,
    skipping the first line (header).
    """
    try:
        process = subprocess.Popen(['netstat', '-i'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error executing netstat -i: {stderr}")
            return None

        lines = stdout.strip().split('\n')

        if len(lines) <= 1: #check if there is anything other than the header
            return [] #return empty array if no data

        interface_stats = []
        for line in lines[2:]: #skip the first line
            values = re.split(r'\s+', line.strip())
            interface_stats.append(values)

        return interface_stats

    except FileNotFoundError:
        print("netstat command not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
interface_stats = parse_netstat_i()
now = datetime.datetime.now()

if interface_stats:
    for stats in interface_stats:
        int_file = f"/dev/shm/{stats[0]}.stat"
        json_file = f"/dev/shm/{stats[0]}.json"

        rx = int(stats[2])
        tx = int(stats[6])
        d = 60

        if os.path.exists(int_file):
            data = ""
            with open(int_file, "r") as text_file:
                data = text_file.read()

            string_values = data.split(',')
            int_values = [int(value.strip()) for value in string_values]

            rxd = (rx - int_values[0]) / d
            txd = (tx - int_values[1]) / d

            data_time = []

            if os.path.exists(json_file):
                with open(json_file, "r") as text_file:
                    data_time = json.load(text_file)

            data_time.append({"timestamp":now.strftime("%Y-%m-%d %H:%M:%S"), "rx":rxd, "tx":txd})

            if 1440 < len(data_time):
                data_time = remove_top_x(data_time, len(data_time) - 1440)

            with open(json_file, "w") as text_file:
                json.dump(data_time, text_file, indent=4)

            with open(int_file, "w") as text_file:
                text_file.write(f"{rx},{tx}\n")

        else:
            with open(int_file, "w") as text_file:
                text_file.write(f"{rx},{tx}\n")
else:
    print("Could not retrieve interface statistics.")
