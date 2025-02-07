import pandas as pd
import ast
from datetime import datetime
import pytz

def convert_to_cest(timestamp):
    """Convert a UNIX timestamp to Central European Summer Time (CEST)."""
    try:
        print(f"Attempting to convert timestamp: {timestamp}")  # Debugging print
        # Ensure the timestamp is treated as an integer
        if isinstance(timestamp, (float, str)):
            timestamp = int(timestamp)
        
        # Convert the timestamp to a UTC datetime object
        utc_time = datetime.utcfromtimestamp(timestamp)
        print(f"UTC time: {utc_time}")  # Debugging print
        
        # Define the CEST timezone (Berlin)
        cest = pytz.timezone('Europe/Berlin')
        # Localize the time and convert it to CEST
        cest_time = pytz.utc.localize(utc_time).astimezone(cest)
        
        # Return the formatted date and time in CEST
        formatted_time = cest_time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Converted to CEST: {formatted_time}")  # Debugging print
        return formatted_time
    except Exception as e:
        print(f"Error during conversion: {e}")  # Debugging print
        return f"Error: {e}"  # Return an error message if conversion fails

def parse_string_to_dict(s):
    """Parse a string into a dictionary and convert timestamps where necessary."""
    print(f"Parsing string: {s}")  # Debugging print
    s = s.strip('{}')
    result_dict = {}

    pairs = []
    current_pair = []
    bracket_level = 0

    for char in s:
        if char == ',' and bracket_level == 0:
            pairs.append(''.join(current_pair).strip())
            current_pair = []
        else:
            if char == '[':
                bracket_level += 1
            elif char == ']':
                bracket_level -= 1
            current_pair.append(char)
    pairs.append(''.join(current_pair).strip())

    for pair in pairs:
        key_value = pair.split(':', 1)
        if len(key_value) == 2:
            key = key_value[0].strip().strip("'\" ")
            value = key_value[1].strip().strip("'\" ")
            print(f"Processing key: {key}, value: {value}")  # Debugging print

            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                pass

            # Convert fwReleaseDate and manufactureDate to CEST if they are UNIX timestamps
            if key in ['fwReleaseDate', 'manufactureDate'] and isinstance(value, (int, float)):
                print(f"Converting timestamp for {key}: {value}")  # Debugging print
                value = convert_to_cest(value)

            result_dict[key] = value

        else:
            print(f"Warning: Failed to parse pair '{pair}'")

    return result_dict

# Read the data from your all_device_info.xlsx file
file_path = 'all_device_info.xlsx'  # Replace with your file path
print(f"Reading data from {file_path}")  # Debugging print
raw_data_df = pd.read_excel(file_path)  # Removed nrows parameter to process all rows
print("Raw data read successfully")  # Debugging print

# Parse the 'result' column and extract the list of dictionaries
device_info_list = []

for devices in raw_data_df['result']:
    print(f"Processing row: {devices}")  # Debugging print
    if isinstance(devices, str):
        # Try to parse the string into a list of devices
        try:
            devices_parsed = ast.literal_eval(devices)  # Convert the string to a list
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing devices: {e}")  # Debugging print
            devices_parsed = []

        print(f"Parsed devices: {devices_parsed}")  # Debugging print
        if isinstance(devices_parsed, list):
            for device_entry in devices_parsed:
                if isinstance(device_entry, dict):
                    device_info_list.append(device_entry)
                elif isinstance(device_entry, str):
                    device_dict = parse_string_to_dict(device_entry)
                    device_info_list.append(device_dict)
                else:
                    print(f"Unexpected device entry type: {type(device_entry)}")  # Debugging print
        elif isinstance(devices_parsed, dict):
            device_info_list.append(devices_parsed)
    elif isinstance(devices, list):
        for device in devices:
            if isinstance(device, dict):
                device_info_list.append(device)
            else:
                print(f"Unexpected device entry: {device}")  # Debugging print

# Convert fwReleaseDate and manufactureDate to CEST format
for device in device_info_list:
    for date_field in ['fwReleaseDate', 'manufactureDate']:
        if date_field in device:
            timestamp = device[date_field]
            # Check if the timestamp is a number (int or float)
            if isinstance(timestamp, (int, float)):
                device[date_field] = convert_to_cest(timestamp)
            # Check if the timestamp is a string representation of a number
            elif isinstance(timestamp, str) and timestamp.isdigit():
                device[date_field] = convert_to_cest(int(timestamp))
            else:
                print(f"Invalid timestamp for {date_field}: {timestamp}")  # Debugging print

# Convert the list of device dictionaries into a structured DataFrame
structured_device_df = pd.DataFrame(device_info_list)
print(f"Structured DataFrame created: \n{structured_device_df}")  # Debugging print

# Save the structured data to an Excel file
output_file_path = 'structured_device_info.xlsx'  # Replace with your desired path
structured_device_df.to_excel(output_file_path, index=False)
print(f"Data saved to {output_file_path}")  # Debugging print