import pandas as pd
import ast
from datetime import datetime
import pytz

def convert_to_cest(timestamp):
    utc_time = datetime.utcfromtimestamp(timestamp)
    cest = pytz.timezone('Europe/Berlin')
    cest_time = pytz.utc.localize(utc_time).astimezone(cest)
    
    date = cest_time.strftime('%Y-%m-%d')
    time_full = cest_time.strftime('%H:%M:%S')
    time_short = cest_time.strftime('%H:%M')
    
    return date, time_full, time_short

def parse_string_to_dict(s):
    result_dict = {}
    
    s = s.strip('{}')
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
            
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                pass
            
            if key == 'ZoneTemperature4' and isinstance(value, list) and len(value) == 4:
                result_dict['Zone1'] = value[0]
                result_dict['Zone2'] = value[1]
                result_dict['Zone3'] = value[2]
                result_dict['Zone4'] = value[3]
            elif key == 'requiredTemperature' and isinstance(value, list) and len(value) == 4:
                result_dict['Required Zone1'] = value[0]
                result_dict['Required Zone2'] = value[1]
                result_dict['Required Zone3'] = value[2]
                result_dict['Required Zone4'] = value[3]
            elif key == 'heaterCurrent' and isinstance(value, list) and len(value) == 4:
                result_dict['Heater Zone1'] = value[0] / 1000 if value[0] > 100 else value[0]
                result_dict['Heater Zone2'] = value[1] / 1000 if value[1] > 100 else value[1]
                result_dict['Heater Zone3'] = value[2] / 1000 if value[2] > 100 else value[2]
                result_dict['Heater Zone4'] = value[3] / 1000 if value[3] > 100 else value[3]
            elif key == 'busVoltage' and isinstance(value, int) and value > 100:
                result_dict['busVoltage'] = value / 1000
            elif key == 'timeStamp':
                device_date, _, device_time = convert_to_cest(value)
                result_dict['Device local Date'] = device_date
                result_dict['Device local Time'] = device_time
            elif key == 'arrivalTime':
                arrival_date, _, arrival_time = convert_to_cest(value)
                result_dict['Arrival  Date'] = arrival_date
                result_dict['Arrival  Time'] = arrival_time
            else:
                result_dict[key] = value
        else:
            print(f"Warning: Failed to parse pair '{pair}'")

    return result_dict

example_data = '''{'Id': 306265, 'machineId': '68:B6:B3:52:88:92', 'timeStamp': 1727760248, 'arrivalTime': 1727766066, 'counter': 69, 'aqi': 74, 'humidity': 60.7, 'timeInBedStatus': True, 'timeInBedSensor': 24.6, 'ZoneTemperature4': [24, 24, 32.2, 32.3], 'enclosureTemperature': 41.7, 'roomTemperature': 21.3, 'requiredTemperature': [23.8, 23.8, 32.1, 32.1], 'heaterCurrent': [908, 0, 1200, 0], 'ZoneHeaterStatus4': '0000', 'errorStatus': 0, 'errorCode': 0, 'busVoltage': 20339, 'isLatest': True, 'isDeleted': False, 'zoneValue': 120}'''

parsed_dict = parse_string_to_dict(example_data)

print(parsed_dict)

file_path = '/Users/safinchowdhury/CODEBASE/Pipedrive/all_machineinactive_data.xlsx'
raw_data_df = pd.read_excel(file_path, header=None)
parsed_data = [parse_string_to_dict(row[0]) for index, row in raw_data_df.iterrows() if pd.notna(row[0])]
structured_df = pd.DataFrame(parsed_data)

print(structured_df)

structured_df.to_excel('/Users/safinchowdhury/CODEBASE/Pipedrive/structured_machineinactive_data.xlsx', index=False)