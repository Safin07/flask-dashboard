import requests
import pandas as pd
import logging
from datetime import datetime
import pytz

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL for the API
base_url = "https://pa8ag6d1fl.execute-api.ap-south-1.amazonaws.com/dev/smart-mattress/api"

# Sign in credentials
sign_in_url = f"{base_url}/user/signIn"
sign_in_payload = {
    "email": "smartmattress2023@gmail.com",
    "password": "Welcome@123"
}

# API request headers
headers = {
    "Content-Type": "application/json"
}

# Error names and descriptions mapping
error_metadata = {
    1: ("ERR_SYSTEM_BOOT", "Device failed to initialize during power on boot"),
    2: ("ERR_SYSTEM_PANIC", "Device restarted due to Panic error by the controller"),
    3: ("ERR_SYSTEM_INTWDT", "Device restarted due to interrupt watchdog timer by the controller"),
    4: ("ERR_SYSTEM_TASKWDT", "Device restarted due to task watchdog timer by the controller"),
    5: ("ERR_SYSTEM_BROWNOUT", "Device restarted due to supply voltage below brownout threshold level"),
    6: ("ERR_SYSTEM_CACHE", "Device restarted due to system cache failure"),
    7: ("ERR_SYSTEM_MEMORYPROTECTION", "Device restarted due to memory protection failure"),
    8: ("ERR_SYSTEM_STACK", "Device restarted due to stack failure"),
    9: ("ERR_SYSTEM_HEAP", "Device restarted due to Heap memory failure"),
    10: ("ERR_SYSTEM_UBSAN", "Device restarted due to Undefined behavior sanitizer (UBSAN) checks"),
    11: ("Unknown Error", "Unknown Description"),
    12: ("Unknown Error", "Unknown Description"),
    13: ("Unknown Error", "Unknown Description"),
    14: ("Unknown Error", "Unknown Description"),
    15: ("Unknown Error", "Unknown Description"),
    16: ("Unknown Error", "Unknown Description"),
    17: ("Unknown Error", "Unknown Description"),
    18: ("Unknown Error", "Unknown Description"),
    19: ("Unknown Error", "Unknown Description"),
    20: ("ERR_HEATER1_FAILURE", "Heater1 circuit is in either short circuit or over temperature or current threshold limit"),
    21: ("ERR_HEATER1_OPEN", "Heater1 is in open state"),
    22: ("ERR_HEATER1_OUTOFRANGE", "Heater1 current is out of range"),
    23: ("ERR_HEATER1_MIN_CURRENT", "Heater1 current is below minimum Threshold"),
    24: ("ERR_HEATER2_FAILURE", "Heater2 circuit is in either short circuit or over temperature or current threshold limit"),
    25: ("ERR_HEATER2_OPEN", "Heater2 is in open state"),
    26: ("ERR_HEATER2_OUTOFRANGE", "Heater2 current is out of range"),
    27: ("ERR_HEATER2_MIN_CURRENT", "Heater2 current is below minimum Threshold"),
    28: ("ERR_HEATER3_FAILURE", "Heater3 circuit is in either short circuit or over temperature or current threshold limit"),
    29: ("ERR_HEATER3_OPEN", "Heater3 is in open state"),
    30: ("ERR_HEATER3_OUTOFRANGE", "Heater3 current is out of range"),
    31: ("ERR_HEATER3_MIN_CURRENT", "Heater3 current is below minimum Threshold"),
    32: ("ERR_HEATER4_FAILURE", "Heater4 circuit is in either short circuit or over temperature or current threshold limit"),
    33: ("ERR_HEATER4_OPEN", "Heater4 is in open state"),
    34: ("ERR_HEATER4_OUTOFRANGE", "Heater4 current is out of range"),
    35: ("ERR_HEATER4_MIN_CURRENT", "Heater4 current is below minimum Threshold"),
    36: ("ERR_HEATER_SENSOR_MISMATCH", "Heater and sensor mismatch"),
    37: ("Unknown Error", "Unknown Description"),
    38: ("Unknown Error", "Unknown Description"),
    39: ("Unknown Error", "Unknown Description"),
    40: ("ERR_TSENSOR1_OPEN", "Zone 1 sensor is short to ground or in open state"),
    41: ("ERR_TSENSOR1_FAILURE", "Zone 1 sensor is shorted to source"),
    42: ("ERR_TSENSOR1_OUTOFRANGE", "Zone 1 sensor is out of range"),
    43: ("ERR_TSENSOR2_OPEN", "Zone 2 sensor is short to ground or in open state"),
    44: ("ERR_TSENSOR2_FAILURE", "Zone 2 sensor is shorted to source"),
    45: ("ERR_TSENSOR2_OUTOFRANGE", "Zone 2 sensor is out of range"),
    46: ("ERR_TSENSOR3_OPEN", "Zone 3 sensor is short to ground or in open state"),
    47: ("ERR_TSENSOR3_FAILURE", "Zone 3 sensor is shorted to source"),
    48: ("ERR_TSENSOR3_OUTOFRANGE", "Zone 3 sensor is out of range"),
    49: ("ERR_TSENSOR4_OPEN", "Zone 4 sensor is short to ground or in open state"),
    50: ("ERR_TSENSOR4_FAILURE", "Zone 4 sensor is shorted to source"),
    51: ("ERR_TSENSOR4_OUTOFRANGE", "Zone 4 sensor is out of range"),
    52: ("ERR_PIB_SENSOR_OPEN", "Zone PIB sensor is short to ground or in open state"),
    53: ("ERR_PIB_SENSOR_FAILURE", "Zone PIB sensor is shorted to source"),
    54: ("ERR_PIB_SENSOR_OUTOFRANGE", "Zone PIB sensor is out of range"),
    60: ("ERR_TSENSOR5_OPEN", "Enclosure sensor is short to ground or in open state"),
    61: ("ERR_TSENSOR5_FAILURE", "Enclosure sensor is shorted to source"),
    62: ("ERR_TSENSOR5_OUTOFRANGE", "Enclosure sensor is out of range"),
    70: ("ERR_BLE_INIT", "BLE stack Initialization failed"),
    71: ("ERR_BLE_SERVICESINIT", "BLE service Initialization failed"),
    72: ("ERR_BLE_CONNECT", "BLE connection failed"),
    73: ("ERR_BLE_ADVT", "BLE Advertisement failed"),
    74: ("ERR_BLE_PROTOCOL", "Receive wrong/unexpected BLE frame format"),
    80: ("ERR_SMGR_INIT", "Storage manager (NVS) initialization failed"),
    81: ("ERR_SMGR_PIB_INDEX_RD", "Reading Person-In-Bed Index from NVS memory failed"),
    82: ("ERR_SMGR_PIB_INDEX_WR", "Writing Person-In-Bed Index to NVS memory failed"),
    83: ("ERR_SMGR_PIB_SET", "Person-In-Bed Set write commit failed"),
    84: ("ERR_SMGR_PIB_GET", "Person-In-Bed Get Read failed"),
    85: ("ERR_SMGR_MD_INDEX_RD", "Reading Machine data Index from NVS memory failed"),
    86: ("ERR_SMGR_MD_INDEX_WR", "Writing Machine data to NVS memory failed"),
    87: ("ERR_SMGR_MD_SET", "Machine data Set write commit failed"),
    88: ("ERR_SMGR_MD_GET", "Machine data Get Read failed"),
    89: ("ERR_SMGR_ERH_INDEX_RD", "Reading Error History Index from NVS memory failed"),
    90: ("ERR_SMGR_ERH_INDEX_WR", "Writing Error History to NVS memory failed"),
    91: ("ERR_SMGR_ERH_SET", "Error History Set write commit failed"),
    92: ("ERR_SMGR_ERH_GET", "Error History Get Read failed"),
    100: ("ERR_CONFIG_READ", "Failure in reading Pib configuration parameters from NVS and updating them to Runtime variables"),
    101: ("ERR_CONFIG_WRITE", "Failure in updating Zone modifiers and Failure in updating Pib configuration parameters to NVS"),
    120: ("ERR_BME_INIT", "BME initialization failure due to library or due to I2C communication failure"),
    121: ("ERR_BME_BSEC_INIT", "BME initialization failure due to library or I2C communication failure"),
    124: ("ERR_BME_RESET", "Device Not able to Reset the BME sensor"),
    126: ("ERR_BME_HUMIDITY", "BME Humidity sensor value is out of range"),
    130: ("ERR_BME_TASK", "Failed to start BME task"),
    140: ("ERR_CMDH_DEVICESTATUS", "Failure in appending device status data to BLE buffer"),
    147: ("ERR_CMDH_MACHINEDATA", "Failure in appending machine data to BLE buffer"),
 150: ("ERR_CMU_DEVICEINFO", "Failure in reading device information using BLE"),
    160: ("ERR_STM_TASKCREATE", "State machine task creation failed"),
    170: ("ERR_TIMER1_INIT", "Error if Zone scan timer failed to initialize"),
    171: ("ERR_TIMER1_START", "Error if Zone scan timer failed to start"),
    172: ("ERR_TIMER1_STOP", "Error if Zone scan timer failed to stop"),
    173: ("ERR_TIMER1_DELETE", "Error if Zone scan timer failed to delete"),
    174: ("ERR_TIMER2_INIT", "Error if LED timer failed to initialize"),
    175: ("ERR_TIMER2_START", "Error if LED timer failed to start"),
    176: ("ERR_TIMER2_STOP", "Error if LED timer failed to stop"),
    177: ("ERR_TIMER2_DELETE", "Error if LED timer failed to delete"),
    178: ("ERR_TIMER3_INIT", "Error if SW timer for WDT failed to initialize"),
    179: ("ERR_TIMER3_START", "Error if SW timer for WDT failed to start"),
    180: ("ERR_TIMER3_STOP", "Error if SW timer for WDT failed to stop"),
    181: ("ERR_TIMER3_DELETE", "Error if SW timer for WDT failed to delete"),
    182: ("ERR_GPIO_INIT", "Error if GPIO Initialization failed"),
    183: ("ERR_GPIO_SETOUTPUTLEVEL", "Error if Setting output level for GPIO failed"),
    184: ("ERR_WDT_INIT", "Error if WDT initialization failed"),
    185: ("ERR_WDT_WDIRESET", "Error if WDT - Input signal reset failed"),
    190: ("ERR_I2C0_INIT", "I2C0 Initialization failure"),
    191: ("ERR_I2C1_INIT", "I2C1 Initialization failure"),
    192: ("ERR_I2C_PARAMETER", "I2C Invalid parameter return"),
    193: ("ERR_I2C_START", "I2C driver start failure"),
    194: ("ERR_I2C_STOP", "I2C driver stop failure"),
    195: ("ERR_I2C_READ", "I2C driver read failure"),
    196: ("ERR_I2C_WRITE", "I2C driver write failure"),
    197: ("ERR_ADC_CALIBRATION", "ADC Calibration failure"),
    198: ("ERR_ADC_CONFIGURATION", "ADC Configuration failure"),
    199: ("ERR_ADC_READ", "ADC read failure"),
    200: ("ERR_ADC_PARAMETER", "ADC Invalid parameter return"),
    201: ("ERR_ADC_GETRAWDATA", "ADC getting raw data failure"),
    202: ("ERR_ADC_CHANNEL", "ADC Channel failure"),
    203: ("ERR_ADC_BUSVOLTAGE", "Set if Bus voltage goes low below the threshold voltage"),
    204: ("ERR_HISW_INIT", "High side switch Initialization failure"),
    205: ("ERR_UART_DISABLE", "Disabling UART ROM download mode and UART driver delete for FCT failure"),
    210: ("ERR_RTC_INIT", "External RTC initialization failure"),
    211: ("ERR_RTC_CONFIG", "RTC configuration Error"),
    212: ("ERR_RTC_READ", "RTC reading Error"),
    213: ("ERR_RTC_WRITE", "RTC writing error"),
    214: ("ERR_RTC_BAT_LOW", "Set if Battery voltage goes low below the threshold voltage"),
    220: ("ERR_MQTT_CONN", "Set if MQTT connection to client failed"),
    221: ("ERR_MQTT_CONN_INTPED", "Set if MQTT connection is interrupted"),
    222: ("ERR_MQTT_PUB", "Set if publish failed"),
    223: ("ERR_HTTP_CONN", "Set if HTTP connection failed"),
    224: ("ERR_HTTP_DISCONN", "Set if HTTP connection was interrupted"),
    225: ("ERR_HTTP_Post", "Set if HTTP set post field failed"),
    226: ("ERR_OTA_INIT", "Set if OTA initialization failed"),
    227: ("ERR_HTTP_READ_AND_OTA_WRITE", "Set if HTTP read failed"),
    228: ("ERR_HTTP_READ_COMPLETE", "Set if complete data is not received"),
    229: ("ERR_OTA_COMPLETE", "Set if OTA is not completed"),
    230: ("ERR_MD5_HASH", "Set if MD5 mismatch detected"),
    231: ("ERR_WIFI_FOTA_IN_PROGRESS", "Set if WiFi FOTA is in progress and BLE FOTA is triggered"),
    232: ("ERR_BLE_FOTA_IN_PROGRESS", "Set if BLE FOTA is in progress and WiFi FOTA is triggered"),
    233: ("ERR_HTTPS_POST_MD_DATA", "Set if Machine data transmission through WiFi failed"),
    234: ("ERR_WIFI_TASKCREATE", "WiFi Task creation failed")
}

# Function to get access token
def get_access_token():
    try:
        response = requests.post(sign_in_url, json=sign_in_payload, headers=headers, verify=False)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json().get("accessToken")
        else:
            logging.error(f"Login failed. Status code: {response.status_code}")
            logging.error("Response: %s", response.json())
            exit()
    except requests.exceptions.RequestException as e:
        logging.error("An error occurred during login: %s", e)
        exit()

# Function to fetch data with pagination
def fetch_data(url, payload, access_token):
    all_records = []
    page = 1
    while True:
        payload['page'] = page
        headers = {
            "Content-Type": "application/json",
            "x-access-token": access_token
        }
        try:
            response = requests.post(url, json=payload, headers=headers, verify=False)
            response.raise_for_status()
            data = response.json().get("data", {}).get("result", [])
            if not data:
                break
            all_records.extend(data)
            page += 1
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred: {e}")
            break
    return all_records

# Function to convert timestamps to CEST with "hh:mm" format
def convert_to_cest(timestamp):
    utc_time = datetime.utcfromtimestamp(timestamp)
    cest = pytz.timezone('Europe/Berlin')
    cest_time = pytz.utc.localize(utc_time).astimezone(cest)
    date = cest_time.strftime('%Y-%m-%d')
    time_short = cest_time.strftime('%H:%M')  # Only "hh:mm" format
    return date, time_short


# Function to fetch device info
def fetch_device_info(access_token):
    device_info_url = f"{base_url}/machine/singleMachineDetails"
    all_machine_ids_url = f"{base_url}/machine/allMachineId"
    headers = {"Content-Type": "application/json", "x-access-token": access_token}

    try:
        # Fetch all machine IDs
        response = requests.get(all_machine_ids_url, headers=headers, verify=False)
        response.raise_for_status()
        machine_ids = response.json().get("data", [])
        device_info_list = []

        # Fetch device details for each machine ID
        for machine in machine_ids:
            payload = {"machineId": machine["machineId"]}
            try:
                device_response = requests.post(device_info_url, json=payload, headers=headers, verify=False)
                device_response.raise_for_status()
                device_data = device_response.json().get("data", {})
                device_info_list.append(device_data)
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching device info for Machine ID {machine['machineId']}: {e}")
        
        return pd.DataFrame(device_info_list) if device_info_list else pd.DataFrame()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching device info: {e}")
        return pd.DataFrame()
# Function to structure data
def structure_data(data, include_error_metadata=False):
    rows = []
    for row in data:
        if isinstance(row, dict):
            structured_row = {}
            for col, value in row.items():
                if col == 'timeStamp':  # Convert timeStamp to CEST
                    device_date, device_time_short = convert_to_cest(value)
                    structured_row['Device local Date'] = device_date
                    structured_row['Device local Time'] = device_time_short
                elif col == 'arrivalTime':  # Convert arrivalTime to CEST
                    arrival_date, arrival_time_short = convert_to_cest(value)
                    structured_row['Arrival Date'] = arrival_date
                    structured_row['Arrival Time'] = arrival_time_short
                elif col == 'fwReleaseDate':  # Convert arrivalTime to CEST
                    fwReleaseDate, fwReleaseDate_time_short = convert_to_cest(value)
                    structured_row['fwReleaseDate Date'] = fwReleaseDate
                    structured_row['fwReleaseDate Time'] = fwReleaseDate_time_short          
                elif col == 'manufactureDate':  # Convert arrivalTime to CEST
                    manufactureDate_date, manufactureDate_time_short = convert_to_cest(value)
                    structured_row['manufactureDate Date'] = manufactureDate_date
                    structured_row['manufactureDate Time'] = manufactureDate_time_short
                elif include_error_metadata and col == 'error':  # Map error codes to error names and descriptions
                    error_name, error_description = error_metadata.get(value, ("Unknown Error", "No description available"))
                    structured_row['Error Code'] = value
                    structured_row['Error Name'] = error_name
                    structured_row['Description'] = error_description
                elif isinstance(value, list):  # Flatten lists
                    for idx, item in enumerate(value):
                        structured_row[f"{col}_item{idx + 1}"] = item
                elif isinstance(value, dict):  # Flatten dictionaries
                    for sub_key, sub_value in value.items():
                        structured_row[f"{col}_{sub_key}"] = sub_value
                else:
                    structured_row[col] = value
            rows.append(structured_row)
    return pd.DataFrame(rows)

def fetch_device_info_for_machine(machine_id, access_token):
    """
    Fetches the device info for a specific machine ID and returns only one record.
    Converts fwReleaseDate and manufactureDate fields to datetime format.
    """
    device_info_url = f"{base_url}/machine/singleMachineDetails"
    headers = {"Content-Type": "application/json", "x-access-token": access_token}

    try:
        # Fetch device info for the specific machine ID
        payload = {"machineId": machine_id}
        response = requests.post(device_info_url, json=payload, headers=headers, verify=False)
        response.raise_for_status()
        device_data = response.json().get("data", {}).get("result", [])
        
        if not device_data:
            logging.info(f"No device info found for Machine ID {machine_id}.")
            return pd.DataFrame()

        # Filter to keep only the latest record
        latest_record = None
        for record in device_data:
            if record.get("isLatest", False):
                latest_record = record
                break
        
        # If no record with "isLatest" is found, select the record with the highest "Id"
        if not latest_record:
            latest_record = max(device_data, key=lambda x: x.get("Id", 0))

        # Convert timestamps to datetime format
        if latest_record:
            if "fwReleaseDate" in latest_record and latest_record["fwReleaseDate"]:
                # Convert from milliseconds to seconds and overwrite
                date, time = convert_to_cest(latest_record["fwReleaseDate"] / 1000)
                latest_record["fwReleaseDate"] = f"{date} {time}"

            if "manufactureDate" in latest_record and latest_record["manufactureDate"]:
                # Convert from milliseconds to seconds and overwrite
                date, time = convert_to_cest(latest_record["manufactureDate"] / 1000)
                latest_record["manufactureDate"] = f"{date} {time}"

        # Convert the record into a DataFrame
        return pd.DataFrame([latest_record]) if latest_record else pd.DataFrame()

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching device info for Machine ID {machine_id}: {e}")
        return pd.DataFrame()
        
        
    # Function to fetch FOTA history for a specific machine ID
def fetch_fota_history_for_machine(machine_id, access_token):
    fota_history_url = f"{base_url}/fota/history"
    fota_history_payload = {
        "page": 1,
        "limit": 3000,
        "status": ["Completed", "Pending", "Cancelled"],
        "sortBy": "DESC",
        "sortValue": "releasedId",
        "machineId": machine_id
    }
    headers = {"Content-Type": "application/json", "x-access-token": access_token}

    try:
        response = requests.post(fota_history_url, json=fota_history_payload, headers=headers, verify=False)
        response.raise_for_status()
        fota_data = response.json().get("data", [])
        # Handle nested 'result' field if present
        if 'result' in fota_data:
            fota_data = fota_data['result']
        # Filter data for the specified machine ID
        filtered_fota_data = [record for record in fota_data if record.get("machineId") == machine_id]
        return pd.DataFrame(filtered_fota_data) if filtered_fota_data else pd.DataFrame()
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching FOTA history for Machine ID {machine_id}: {e}")
        return pd.DataFrame()
# Function to fetch COTA history for a specific machine ID
def fetch_cota_history_for_machine(machine_id, access_token):
    cota_history_url = f"{base_url}/device/cotaHistory"
    cota_history_payload = {
        "page": 1,
        "limit": 3000,
        "status": ["Completed", "Pending", "Cancelled"],
        "sortBy": "DESC",
        "sortValue": "releasedId",
        "machineId": machine_id
    }
    headers = {"Content-Type": "application/json", "x-access-token": access_token}

    try:
        response = requests.post(cota_history_url, json=cota_history_payload, headers=headers, verify=False)
        response.raise_for_status()
        cota_data = response.json().get("data", [])
        # Handle nested 'result' field if present
        if 'result' in cota_data:
            cota_data = cota_data['result']
        # Filter data for the specified machine ID
        filtered_cota_data = [record for record in cota_data if record.get("machineId") == machine_id]
        return pd.DataFrame(filtered_cota_data) if filtered_cota_data else pd.DataFrame()
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching COTA history for Machine ID {machine_id}: {e}")
        return pd.DataFrame()
    
    
def main():
    # Get access token
    access_token = get_access_token()

    # Get machine ID input from the user
    user_machine_id = input("Enter the Machine ID you want to fetch data for: ").strip()

    # Fetch Machine Data
    machine_url = f"{base_url}/machine/single"
    machine_payload = {
        "machineId": user_machine_id,
        "nFilter": {},
        "sortBy": "DESC",
        "sortValue": "timeStamp",
        "download": 0,
        "fields": [],
        "limit": 100
    }
    machine_data = fetch_data(machine_url, machine_payload, access_token)

    # Fetch Machine Inactive Data
    machine_inactive_url = f"{base_url}/machineInactive/singleMachineInactiveData"
    machine_inactive_payload = {
        "machineId": user_machine_id,
        "nFilter": {},
        "sortBy": "DESC",
        "sortValue": "timeStamp",
        "download": 0,
        "fields": [],
        "limit": 100
    }
    machine_inactive_data = fetch_data(machine_inactive_url, machine_inactive_payload, access_token)

    # Fetch Error Data
    error_url = f"{base_url}/machine/singleErrorData"
    error_payload = {
        "machineId": user_machine_id,
        "nFilter": {},
        "sortBy": "DESC",
        "sortValue": "arrivalTime",
        "download": 0,
        "fields": ["machineId", "arrivalTime", "zoneValue", "error", "logCounter"],
        "limit": 100
    }
    error_data = fetch_data(error_url, error_payload, access_token)

    # Fetch Device Info for the specific machine
    device_info_df = fetch_device_info_for_machine(user_machine_id, access_token)

    # Fetch FOTA History for the specific machine
    fota_history_df = fetch_fota_history_for_machine(user_machine_id, access_token)

    # Fetch COTA History for the specific machine
    cota_history_df = fetch_cota_history_for_machine(user_machine_id, access_token)

    # Structure Data
    machine_df = structure_data(machine_data)
    machine_inactive_df = structure_data(machine_inactive_data)
    error_df = structure_data(error_data, include_error_metadata=True)

    # Save to Excel
    output_file = "structured_machine_data.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        machine_df.to_excel(writer, sheet_name='Machine Data', index=False)
        machine_inactive_df.to_excel(writer, sheet_name='Machine Inactive Data', index=False)
        error_df.to_excel(writer, sheet_name='Error Data', index=False)
        if not device_info_df.empty:
            device_info_df.to_excel(writer, sheet_name='Device Info', index=False)
        if not fota_history_df.empty:
            fota_history_df.to_excel(writer, sheet_name='FOTA History', index=False)
        if not cota_history_df.empty:
            cota_history_df.to_excel(writer, sheet_name='COTA History', index=False)
    logging.info(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    main()