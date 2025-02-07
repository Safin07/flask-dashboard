import pandas as pd
import ast
from datetime import datetime
import pytz

# Function to convert epoch timestamp to CEST 
def convert_to_cest(timestamp):
    try:
        utc_time = datetime.utcfromtimestamp(timestamp)
        cest = pytz.timezone('Europe/Berlin')
        cest_time = pytz.utc.localize(utc_time).astimezone(cest)
        date = cest_time.strftime('%Y-%m-%d')
        time_full = cest_time.strftime('%H:%M:%S')
        return date, time_full
    except Exception as e:
        return f"Error: {e}", "N/A"

input_file_path = 'all_machine_error_data.xlsx'
raw_data_df = pd.read_excel(input_file_path)

structured_data = []


for index, row in raw_data_df.iterrows():

    if isinstance(row[0], str):
        try:
            data_dict = ast.literal_eval(row[0])  
        except Exception as e:
            print(f"Error parsing row {index}: {e}")
            continue
    else:
        data_dict = row[0]

    structured_row = {}

 
    structured_row['Machine ID'] = data_dict.get('machineId', 'N/A')
    
    # Convert arrivalTime and timeStamp from epoch to CEST date and time
    arrival_date, arrival_time = convert_to_cest(data_dict.get('arrivalTime', 0))
    structured_row['Arrival Date'] = arrival_date
    structured_row['Arrival Time'] = arrival_time

    timestamp_date, timestamp_time = convert_to_cest(data_dict.get('timeStamp', 0))
    structured_row['Timestamp Date'] = timestamp_date
    structured_row['Timestamp Time'] = timestamp_time


    structured_row['Error Code'] = data_dict.get('error', 'N/A')
    structured_row['Log Counter'] = data_dict.get('logCounter', 'N/A')
    structured_row['Zone Value'] = data_dict.get('zoneValue', 'N/A')
    
 
    structured_data.append(structured_row)

# Convert the list of structured rows into a DataFrame
structured_df = pd.DataFrame(structured_data)

# Save the structured DataFrame to a new Excel file
output_file_path = 'structured_machine_68B6B354E8B2_error_data.xlsx'
structured_df.to_excel(output_file_path, index=False)

print(f"Structured data saved to {output_file_path}")