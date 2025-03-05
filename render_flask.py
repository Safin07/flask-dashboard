from flask import Flask, request, render_template_string, jsonify
import requests
import pandas as pd
import logging
from datetime import datetime
import pytz
import base64
from flask_cors import CORS
import urllib3
import os

# Disable insecure HTTPS warnings (for development only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# Update LOGO_PATH as needed
LOGO_PATH = "logo3.png"

app.secret_key = "some_secret_key_for_session"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL for the API
base_url = "https://api-prod.variowell-iot.com/smart-mattress/api"

# Sign in credentials
sign_in_url = f"{base_url}/user/signIn"
sign_in_payload = {
    "email": "smartmattress2023@gmail.com",
    "password": "Welcome@123"
}
headers = {"Content-Type": "application/json"}

# (Truncated) error metadata dictionary
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

def get_access_token():
    try:
        response = requests.post(sign_in_url, json=sign_in_payload, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json().get("accessToken")
        else:
            logging.error(f"Login failed. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error("An error occurred during login: %s", e)
        return None

def convert_to_cest(timestamp):
    """
    Converts a given timestamp to CEST. If timestamp is None or invalid, returns empty strings.
    Also converts milliseconds (if needed) to seconds.
    """
    try:
        if timestamp is None:
            return "", ""
        ts = float(timestamp)
        if ts > 1e10:  # assume milliseconds
            ts = ts / 1000.0
        utc_time = datetime.utcfromtimestamp(ts)
        cest = pytz.timezone('Europe/Berlin')
        cest_time = pytz.utc.localize(utc_time).astimezone(cest)
        return cest_time.strftime('%Y-%m-%d'), cest_time.strftime('%H:%M')
    except Exception as e:
        logging.error("Error converting timestamp %s: %s", timestamp, e)
        return "", ""

def structure_data(data, include_error_metadata=False):
    rows = []
    for row in data:
        if isinstance(row, dict):
            structured_row = {}
            for col, value in row.items():
                if value is None:
                    structured_row[col] = None
                    continue
                if col == 'timeStamp':
                    date_str, time_str = convert_to_cest(value)
                    structured_row['Device local Date'] = date_str
                    structured_row['Device local Time'] = time_str
                elif col == 'arrivalTime':
                    arr_date, arr_time = convert_to_cest(value)
                    structured_row['Arrival Date'] = arr_date
                    structured_row['Arrival Time'] = arr_time
                elif col == 'fwReleaseDate':
                    fw_date, fw_time = convert_to_cest(value)
                    structured_row['fwReleaseDate Date'] = fw_date
                    structured_row['fwReleaseDate Time'] = fw_time
                elif col == 'manufactureDate':
                    manu_date, manu_time = convert_to_cest(value)
                    structured_row['manufactureDate Date'] = manu_date
                    structured_row['manufactureDate Time'] = manu_time
                elif include_error_metadata and col == 'error':
                    err_name, err_desc = error_metadata.get(value, ("Unknown Error", "No description available"))
                    structured_row['Error Code'] = value
                    structured_row['Error Name'] = err_name
                    structured_row['Description'] = err_desc
                elif isinstance(value, list):
                    for idx, item in enumerate(value):
                        structured_row[f"{col}_item{idx+1}"] = item
                elif isinstance(value, dict):
                    for sub_key, sub_val in value.items():
                        structured_row[f"{col}_{sub_key}"] = sub_val
                else:
                    structured_row[col] = value
            rows.append(structured_row)
    logging.info("Structured data: %s", rows)
    return pd.DataFrame(rows)

def df_to_records(df):
    df = df.where(pd.notnull(df), None)
    return df.applymap(lambda x: x.item() if hasattr(x, 'item') else x).to_dict(orient='records')

def fetch_data(url, payload, access_token, max_pages=None):
    """Fetches data from the API by iterating through pages.
       If max_pages is set, stops after that many pages.
    """
    all_records = []
    page = 1
    while True:
        if max_pages is not None and page > max_pages:
            logging.info("Reached max_pages limit: %s", max_pages)
            break
        payload['page'] = page
        local_headers = {"Content-Type": "application/json", "x-access-token": access_token}
        try:
            response = requests.post(url, json=payload, headers=local_headers, verify=False, timeout=30)
            response.raise_for_status()
            data = response.json().get("data", {}).get("result", [])
            logging.info("Fetched data from API (page %s): %s", page, data)
            if not data:
                break
            all_records.extend(data)
            page += 1
        except requests.exceptions.RequestException as e:
            logging.error("Error fetching data: %s", e)
            break
    return all_records

def fetch_device_info_for_machine(machine_id, access_token):
    url = f"{base_url}/machine/singleMachineDetails"
    local_headers = {"Content-Type": "application/json", "x-access-token": access_token}
    try:
        payload = {"machineId": machine_id}
        resp = requests.post(url, json=payload, headers=local_headers, verify=False)
        resp.raise_for_status()
        data = resp.json().get("data", {}).get("result", [])
        if not data:
            return pd.DataFrame()
        latest = None
        for rec in data:
            if rec.get("isLatest", False):
                latest = rec
                break
        if not latest:
            latest = max(data, key=lambda x: x.get("Id", 0))
        if latest:
            if "fwReleaseDate" in latest and latest["fwReleaseDate"]:
                d, t = convert_to_cest(latest["fwReleaseDate"])
                latest["fwReleaseDate"] = f"{d} {t}"
            if "manufactureDate" in latest and latest["manufactureDate"]:
                d, t = convert_to_cest(latest["manufactureDate"])
                latest["manufactureDate"] = f"{d} {t}"
        return pd.DataFrame([latest]) if latest else pd.DataFrame()
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching device info: %s", e)
        return pd.DataFrame()

def fetch_fota_history_for_machine(machine_id, access_token):
    url = f"{base_url}/fota/history"
    payload = {
        "page": 1,
        "limit": 3000,
        "status": ["Completed", "Pending", "Cancelled"],
        "sortBy": "DESC",
        "sortValue": "releasedId",
        "machineId": machine_id
    }
    local_headers = {"Content-Type": "application/json", "x-access-token": access_token}
    try:
        resp = requests.post(url, json=payload, headers=local_headers, verify=False)
        resp.raise_for_status()
        fota_data = resp.json().get("data", [])
        if 'result' in fota_data:
            fota_data = fota_data['result']
        filtered = [r for r in fota_data if r.get("machineId") == machine_id]
        return pd.DataFrame(filtered) if filtered else pd.DataFrame()
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching FOTA history: %s", e)
        return pd.DataFrame()

def fetch_cota_history_for_machine(machine_id, access_token):
    url = f"{base_url}/device/cotaHistory"
    payload = {
        "page": 1,
        "limit": 3000,
        "status": ["Completed", "Pending", "Cancelled"],
        "sortBy": "DESC",
        "sortValue": "releasedId",
        "machineId": machine_id
    }
    local_headers = {"Content-Type": "application/json", "x-access-token": access_token}
    try:
        resp = requests.post(url, json=payload, headers=local_headers, verify=False)
        resp.raise_for_status()
        cota_data = resp.json().get("data", [])
        if 'result' in cota_data:
            cota_data = cota_data['result']
        filtered = [r for r in cota_data if r.get("machineId") == machine_id]
        return pd.DataFrame(filtered) if filtered else pd.DataFrame()
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching COTA history: %s", e)
        return pd.DataFrame()

# ----- Routes -----

@app.route('/', methods=['GET'])
def home():
    with open(LOGO_PATH, "rb") as f:
        logo_data = f.read()
    logo_base64 = base64.b64encode(logo_data).decode('utf-8')
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Machine Data Dashboard</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        body { background-color: #f8f9fa; }
        .logo-container { text-align: center; margin-top: 30px; }
        .form-container { max-width: 500px; margin: 100px auto; padding: 30px;
                          border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); background: white; }
      </style>
    </head>
    <body>
      <div class="container logo-container">
        <img src="data:image/png;base64,{{ logo_base64 }}" alt="Logo" height="80">
      </div>
      <div class="container">
        <h1 class="mt-5">Machine Data Dashboard</h1>
        <form method="get" action="/data">
            <div class="mb-3">
                <label for="machine_id" class="form-label">Enter Machine ID</label>
                <input type="text" class="form-control" name="machine_id" placeholder="Machine ID" required>
            </div>
            <div class="d-flex justify-content-between">
                <button type="submit" class="btn btn-primary">Fetch Data</button>
                <a href="/dashboard" class="btn btn-secondary">Dashboard</a>
            </div>
        </form>
      </div>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', logo_base64=logo_base64)

@app.route('/data', methods=['GET'])
def data_view():
    machine_id = request.args.get('machine_id')
    access_token = get_access_token()
    if not access_token:
        return "Error obtaining access token.", 503

    inactive_payload = {
        "machineId": machine_id,
        "nFilter": {},
        "sortBy": "DESC",
        "sortValue": "timeStamp",
        "download": 0,
        "fields": [],
        "limit": 100
    }
    inactive_df = structure_data(fetch_data(f"{base_url}/machineInactive/singleMachineInactiveData", inactive_payload, access_token))
    error_payload = {
        "machineId": machine_id,
        "nFilter": {},
        "sortBy": "DESC",
        "sortValue": "arrivalTime",
        "download": 0,
        "fields": ["machineId", "arrivalTime", "zoneValue", "error", "logCounter"],
        "limit": 100
    }
    error_df = structure_data(fetch_data(f"{base_url}/machine/singleErrorData", error_payload, access_token), include_error_metadata=True)
    device_df = fetch_device_info_for_machine(machine_id, access_token)
    fota_df = fetch_fota_history_for_machine(machine_id, access_token)
    cota_df = fetch_cota_history_for_machine(machine_id, access_token)

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Machine Data View</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
      <link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css"/>
    </head>
    <body>
      <nav class="navbar navbar-dark bg-primary">
        <div class="container">
          <a class="navbar-brand" href="/">Machine Data Dashboard</a>
        </div>
      </nav>
      <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h2>Machine Data Report: {{ machine_id }}</h2>
          <div>
            <button type="button" class="btn btn-secondary me-2" data-bs-toggle="modal" data-bs-target="#filterModal">Filter</button>
            <button type="button" class="btn btn-secondary me-2" data-bs-toggle="modal" data-bs-target="#arrivalFilterModal">Filter by Arrival</button>
            <a href="/dashboard?machine_id={{ machine_id }}" class="btn btn-info">Dashboard</a>
          </div>
        </div>
        <div class="table-responsive">
          <h4>Machine Data (Lazy Loaded with Range Filters)</h4>
          <input type="hidden" id="machine_id" value="{{ machine_id }}">
          <table id="machineTable" class="display" style="width: 100%;">
            <thead>
              <tr>
                <th>Id</th>
                <th>machineId</th>
                <th>Device local Date</th>
                <th>Device local Time</th>
                <th>Arrival Date</th>
                <th>Arrival Time</th>
                <th>aqi</th>
                <th>iaqAccuracy</th>
                <th>co2</th>
                <th>voc</th>
                <th>humidity</th>
                <th>timeInBedStatus</th>
                <th>timeInBedSensor</th>
                <th>ZoneTemperature4_item1</th>
                <th>ZoneTemperature4_item2</th>
                <th>ZoneTemperature4_item3</th>
                <th>ZoneTemperature4_item4</th>
                <th>enclosureTemperature</th>
                <th>roomTemperature</th>
                <th>requiredTemperature_item1</th>
                <th>requiredTemperature_item2</th>
                <th>requiredTemperature_item3</th>
                <th>requiredTemperature_item4</th>
                <th>heaterCurrent_item1</th>
                <th>heaterCurrent_item2</th>
                <th>heaterCurrent_item3</th>
                <th>heaterCurrent_item4</th>
                <th>ZoneHeaterStatus4</th>
                <th>errorStatus</th>
                <th>errorCode</th>
                <th>busVoltage</th>
                <th>isLatest</th>
                <th>isDeleted</th>
                <th>zoneValue</th>
              </tr>
            </thead>
          </table>
        </div>
        <div class="table-responsive">
          <h4>Inactive Data</h4>
          {{ inactive_df.to_html(classes='table table-striped table-bordered', index=False) | safe }}
        </div>
        <div class="table-responsive">
          <h4>Error Logs</h4>
          {{ error_df.to_html(classes='table table-striped table-bordered', index=False) | safe }}
        </div>
        <div class="table-responsive">
          <h4>Device Information</h4>
          {{ device_df.to_html(classes='table table-striped table-bordered', index=False) | safe }}
        </div>
        <div class="table-responsive">
          <h4>FOTA History</h4>
          {{ fota_df.to_html(classes='table table-striped table-bordered', index=False) | safe }}
        </div>
        <div class="table-responsive">
          <h4>COTA History</h4>
          {{ cota_df.to_html(classes='table table-striped table-bordered', index=False) | safe }}
        </div>
      </div>
      <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
      <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
      <script>
        var machineColumns = [
          { data: "Id" },
          { data: "machineId" },
          { data: "Device local Date" },
          { data: "Device local Time" },
          { data: "Arrival Date" },
          { data: "Arrival Time" },
          { data: "aqi" },
          { data: "iaqAccuracy" },
          { data: "co2" },
          { data: "voc" },
          { data: "humidity" },
          { data: "timeInBedStatus" },
          { data: "timeInBedSensor" },
          { data: "ZoneTemperature4_item1" },
          { data: "ZoneTemperature4_item2" },
          { data: "ZoneTemperature4_item3" },
          { data: "ZoneTemperature4_item4" },
          { data: "enclosureTemperature" },
          { data: "roomTemperature" },
          { data: "requiredTemperature_item1" },
          { data: "requiredTemperature_item2" },
          { data: "requiredTemperature_item3" },
          { data: "requiredTemperature_item4" },
          { data: "heaterCurrent_item1" },
          { data: "heaterCurrent_item2" },
          { data: "heaterCurrent_item3" },
          { data: "heaterCurrent_item4" },
          { data: "ZoneHeaterStatus4" },
          { data: "errorStatus" },
          { data: "errorCode" },
          { data: "busVoltage" },
          { data: "isLatest" },
          { data: "isDeleted" },
          { data: "zoneValue" }
        ];
        var filterCriteria = {};
        $(document).ready(function(){
          let machineId = $('#machine_id').val();
          var table = $('#machineTable').DataTable({
            processing: true,
            serverSide: true,
            searching: false,
            autoWidth: true,
            lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
            ajax: {
              url: "/api/machine_data",
              type: "POST",
              contentType: "application/json",
              data: function(d) {
                d.machine_id = machineId;
                $.each(filterCriteria, function(key, value) {
                  d[key] = value;
                });
                return JSON.stringify(d);
              }
            },
            columns: machineColumns
          });
        });
      </script>
    </body>
    </html>
    ''', machine_id=machine_id, inactive_df=inactive_df, error_df=error_df,
         device_df=device_df, fota_df=fota_df, cota_df=cota_df)

@app.route('/api/machine_data', methods=['GET', 'POST'])
def machine_data_lazy():
    data = request.get_json() or request.args.to_dict()
    draw = data.get('draw', 1)
    start = int(data.get('start', 0))
    length = int(data.get('length', 10))
    machine_id = data.get('machine_id', None)
    if not machine_id:
        return jsonify({"draw": draw, "recordsTotal": 0, "recordsFiltered": 0, "data": []})
    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "Failed to obtain access token from remote API."}), 503

    # Determine if filtering criteria are applied.
    filter_keys = ["aqi_min", "aqi_max", "humidity_min", "humidity_max",
                   "roomTemperature_min", "roomTemperature_max", "busVoltage_min", "busVoltage_max",
                   "arrivalDate_min", "arrivalDate_max", "arrivalTime_min", "arrivalTime_max",
                   "zone1_diff_min", "zone1_diff_max", "zone2_diff_min", "zone2_diff_max",
                   "zone3_diff_min", "zone3_diff_max", "zone4_diff_min", "zone4_diff_max"]
    filtering_applied = any(data.get(k) is not None for k in filter_keys)

    if not filtering_applied:
        # No filtering: use remote API pagination to fetch only the needed page.
        remote_limit = 100
        remote_page = start // remote_limit + 1
        payload_remote = {
            "machineId": machine_id,
            "nFilter": {},
            "sortBy": "DESC",
            "sortValue": "timeStamp",
            "download": 0,
            "fields": [],
            "limit": remote_limit,
            "page": remote_page
        }
        local_headers = {"Content-Type": "application/json", "x-access-token": access_token}
        try:
            response = requests.post(f"{base_url}/machine/single", json=payload_remote, headers=local_headers, verify=False, timeout=30)
            response.raise_for_status()
            result = response.json().get("data", {})
            records = result.get("result", [])
            total = result.get("totalMachines", len(records))
        except requests.exceptions.RequestException as e:
            logging.error("Error fetching data: %s", e)
            return jsonify({"error": "Error fetching data from remote API"}), 503
        # Slice the records based on the offset within the current remote page
        offset_in_page = start % remote_limit
        sliced_records = records[offset_in_page: offset_in_page + length]
        df_all = structure_data(sliced_records)
        total_records = total
    else:
        # Filtering applied: fetch data from all pages (up to a maximum)
        payload_remote = {
            "machineId": machine_id,
            "nFilter": {},
            "sortBy": "DESC",
            "sortValue": "timeStamp",
            "download": 0,
            "fields": [],
            "limit": 100
        }
        all_data = fetch_data(f"{base_url}/machine/single", payload_remote, access_token, max_pages=50)
        df_all = structure_data(all_data)
        if data.get("arrivalDate_min"):
            df_all = df_all[df_all["Arrival Date"] >= data["arrivalDate_min"]]
        if data.get("arrivalDate_max"):
            df_all = df_all[df_all["Arrival Date"] <= data["arrivalDate_max"]]
        if data.get("arrivalTime_min"):
            df_all = df_all[df_all["Arrival Time"] >= data["arrivalTime_min"]]
        if data.get("arrivalTime_max"):
            df_all = df_all[df_all["Arrival Time"] <= data["arrivalTime_max"]]
        for col in ["aqi", "humidity", "roomTemperature", "busVoltage"]:
            if col in df_all.columns:
                df_all[col] = pd.to_numeric(df_all[col], errors='coerce')
                if data.get(col + "_min"):
                    try:
                        df_all = df_all[df_all[col] >= float(data[col + "_min"])]
                    except Exception:
                        pass
                if data.get(col + "_max"):
                    try:
                        df_all = df_all[df_all[col] <= float(data[col + "_max"])]
                    except Exception:
                        pass
        for zone in [1, 2, 3, 4]:
            temp_col = f"ZoneTemperature4_item{zone}"
            req_col = f"requiredTemperature_item{zone}"
            diff_col = f"zone{zone}_diff"
            if temp_col in df_all.columns and req_col in df_all.columns:
                df_all[diff_col] = pd.to_numeric(df_all[temp_col], errors='coerce') - pd.to_numeric(df_all[req_col], errors='coerce')
        for zone in [1, 2, 3, 4]:
            diff_col = f"zone{zone}_diff"
            if data.get(f"zone{zone}_diff_min"):
                try:
                    df_all = df_all[df_all[diff_col] >= float(data[f"zone{zone}_diff_min"])]
                except Exception:
                    pass
            if data.get(f"zone{zone}_diff_max"):
                try:
                    df_all = df_all[df_all[diff_col] <= float(data[f"zone{zone}_diff_max"])]
                except Exception:
                    pass
        total_records = len(df_all)
        df_all = df_all.iloc[start:start+length]
    data_records = df_to_records(df_all)
    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": data_records
    })

@app.route('/dashboard', methods=['GET'])
def dashboard_graphs():
    machine_id = request.args.get('machine_id')
    if not machine_id:
        return "Machine ID not provided", 400
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    access_token = get_access_token()
    if not access_token:
        return "Failed to obtain access token", 503
    all_data = fetch_data(f"{base_url}/machine/single", {
        "machineId": machine_id,
        "nFilter": {},
        "sortBy": "DESC",
        "sortValue": "timeStamp",
        "download": 0,
        "fields": [],
        "limit": 100
    }, access_token)
    df = structure_data(all_data)
    # If no date/time filters are provided, limit data to the latest active day
    if not (start_date or end_date or start_time or end_time):
        if not df.empty:
            latest_date = df["Device local Date"].max()
            df = df[df["Device local Date"] == latest_date]
    else:
        if start_date:
            df = df[df["Device local Date"] >= start_date]
        if end_date:
            df = df[df["Device local Date"] <= end_date]
        if start_time:
            df = df[df["Device local Time"] >= start_time]
        if end_time:
            df = df[df["Device local Time"] <= end_time]
    x_values = df["Device local Time"].tolist()[::-1]

    def get_zone_data(zone):
        temp = df.get(f"ZoneTemperature4_item{zone}", pd.Series([])).tolist()[::-1]
        req = df.get(f"requiredTemperature_item{zone}", pd.Series([])).tolist()[::-1]
        heater = df.get(f"heaterCurrent_item{zone}", pd.Series([])).tolist()[::-1]
        try:
            req_series = pd.to_numeric(df.get(f"requiredTemperature_item{zone}", pd.Series([])), errors='coerce').dropna()
            temp_series = pd.to_numeric(df.get(f"ZoneTemperature4_item{zone}", pd.Series([])), errors='coerce').dropna()
            if not req_series.empty and not temp_series.empty:
                ymin = float(min(req_series.min(), temp_series.min()))
                ymax = float(max(req_series.max(), temp_series.max()))
            else:
                ymin, ymax = 0, 100
        except Exception:
            ymin, ymax = 0, 100
        return temp, req, heater, ymin, ymax

    zone1_temp, zone1_req, zone1_heater, zone1_ymin, zone1_ymax = get_zone_data(1)
    zone2_temp, zone2_req, zone2_heater, zone2_ymin, zone2_ymax = get_zone_data(2)
    zone3_temp, zone3_req, zone3_heater, zone3_ymin, zone3_ymax = get_zone_data(3)
    zone4_temp, zone4_req, zone4_heater, zone4_ymin, zone4_ymax = get_zone_data(4)
    person_in_bed = df.get("timeInBedSensor", pd.Series([])).tolist()
    bus_voltage    = df.get("busVoltage", pd.Series([])).tolist()
    aqi_data       = df.get("aqi", pd.Series([])).tolist()
    humidity_data  = df.get("humidity", pd.Series([])).tolist()
    room_temp      = df.get("roomTemperature", pd.Series([])).tolist()
    enclosure_temp = df.get("enclosureTemperature", pd.Series([])).tolist()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Dashboard - Machine {{ machine_id }}</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <style> canvas { margin-bottom: 40px; } </style>
    </head>
    <body>
      <div class="container mt-4">
         <h1>Dashboard for Machine {{ machine_id }}</h1>
         <form method="get" action="/dashboard" class="row g-3 mb-4">
           <input type="hidden" name="machine_id" value="{{ machine_id }}">
           <div class="col-auto"><label for="start_date" class="col-form-label">Start Date</label></div>
           <div class="col-auto"><input type="date" id="start_date" name="start_date" class="form-control" value="{{ request.args.get('start_date', '') }}"></div>
           <div class="col-auto"><label for="end_date" class="col-form-label">End Date</label></div>
           <div class="col-auto"><input type="date" id="end_date" name="end_date" class="form-control" value="{{ request.args.get('end_date', '') }}"></div>
           <div class="col-auto"><label for="start_time" class="col-form-label">Start Time</label></div>
           <div class="col-auto"><input type="time" id="start_time" name="start_time" class="form-control" value="{{ request.args.get('start_time', '') }}"></div>
           <div class="col-auto"><label for="end_time" class="col-form-label">End Time</label></div>
           <div class="col-auto"><input type="time" id="end_time" name="end_time" class="form-control" value="{{ request.args.get('end_time', '') }}"></div>
           <div class="col-auto"><button type="submit" class="btn btn-primary">Apply Date Filter</button></div>
         </form>
         <div class="mb-4"><a href="/data?machine_id={{ machine_id }}" class="btn btn-secondary">Back to Data View</a></div>
         <h3>Zone 1</h3><canvas id="chartZone1"></canvas>
         <h3>Zone 2</h3><canvas id="chartZone2"></canvas>
         <h3>Zone 3</h3><canvas id="chartZone3"></canvas>
         <h3>Zone 4</h3><canvas id="chartZone4"></canvas>
         <h3>Person in Bed</h3><canvas id="chartPersonInBed"></canvas>
         <h3>Bus Voltage</h3><canvas id="chartBusVoltage"></canvas>
         <h3>AQI</h3><canvas id="chartAQI"></canvas>
         <h3>Humidity</h3><canvas id="chartHumidity"></canvas>
         <h3>Room Temperature</h3><canvas id="chartRoomTemp"></canvas>
         <h3>Enclosure Temperature</h3><canvas id="chartEnclosureTemp"></canvas>
      </div>
      <script>
        function createZoneChart(canvasId, xValues, tempData, reqData, heaterData, primaryMin, primaryMax) {
          new Chart(document.getElementById(canvasId).getContext('2d'), {
            type: 'line',
            data: {
              labels: xValues,
              datasets: [
                { label: 'Temperature', data: tempData, borderColor: 'rgb(255, 99, 132)', fill: false, borderWidth: 1 },
                { label: 'Required Temperature', data: reqData, borderColor: 'rgb(54, 162, 235)', fill: false, borderWidth: 1 },
                { label: 'Heater Current', data: heaterData, borderColor: 'rgb(75, 192, 192)', fill: false, borderWidth: 1, yAxisID: 'y1' }
              ]
            },
            options: {
              scales: {
                x: { title: { display: true, text: 'Device Local Time' } },
                y: { title: { display: true, text: 'Temperature / Required Temp' }, min: primaryMin, max: primaryMax },
                y1: { title: { display: true, text: 'Heater Current' }, position: 'right', min: 500, max: 3000, grid: { drawOnChartArea: false } }
              },
              plugins: { legend: { position: 'bottom' }, title: { display: true, text: canvasId.replace('chart', 'Zone ') } }
            }
          });
        }
        function createSingleSeriesChart(canvasId, xValues, dataValues, yAxisTitle, chartTitle, yMin, yMax) {
          new Chart(document.getElementById(canvasId).getContext('2d'), {
            type: 'line',
            data: { labels: xValues, datasets: [{ label: yAxisTitle, data: dataValues, borderColor: 'rgb(75, 192, 192)', fill: false, borderWidth: 1 }] },
            options: {
              scales: { x: { title: { display: true, text: 'Device Local Time' } }, y: { title: { display: true, text: yAxisTitle }, min: yMin, max: yMax } },
              plugins: { legend: { position: 'bottom' }, title: { display: true, text: chartTitle } }
            }
          });
        }
        createZoneChart("chartZone1", {{ x_values|tojson }}, {{ zone1_temp|tojson }}, {{ zone1_req|tojson }}, {{ zone1_heater|tojson }}, {{ zone1_ymin if zone1_ymin is not none else 'undefined' }}, {{ zone1_ymax if zone1_ymax is not none else 'undefined' }});
        createZoneChart("chartZone2", {{ x_values|tojson }}, {{ zone2_temp|tojson }}, {{ zone2_req|tojson }}, {{ zone2_heater|tojson }}, {{ zone2_ymin if zone2_ymin is not none else 'undefined' }}, {{ zone2_ymax if zone2_ymax is not none else 'undefined' }});
        createZoneChart("chartZone3", {{ x_values|tojson }}, {{ zone3_temp|tojson }}, {{ zone3_req|tojson }}, {{ zone3_heater|tojson }}, {{ zone3_ymin if zone3_ymin is not none else 'undefined' }}, {{ zone3_ymax if zone3_ymax is not none else 'undefined' }});
        createZoneChart("chartZone4", {{ x_values|tojson }}, {{ zone4_temp|tojson }}, {{ zone4_req|tojson }}, {{ zone4_heater|tojson }}, {{ zone4_ymin if zone4_ymin is not none else 'undefined' }}, {{ zone4_ymax if zone4_ymax is not none else 'undefined' }});
        createSingleSeriesChart("chartPersonInBed", {{ x_values|tojson }}, {{ person_in_bed|tojson }}, "Person in Bed", "Person in Bed", 0, 100);
        createSingleSeriesChart("chartBusVoltage", {{ x_values|tojson }}, {{ bus_voltage|tojson }}, "Bus Voltage", "Bus Voltage", 0, 25000);
        createSingleSeriesChart("chartAQI", {{ x_values|tojson }}, {{ aqi_data|tojson }}, "AQI", "AQI", 0, 300);
        createSingleSeriesChart("chartHumidity", {{ x_values|tojson }}, {{ humidity_data|tojson }}, "Humidity", "Humidity", 0, 100);
        createSingleSeriesChart("chartRoomTemp", {{ x_values|tojson }}, {{ room_temp|tojson }}, "Room Temperature", "Room Temperature", 0, 50);
        createSingleSeriesChart("chartEnclosureTemp", {{ x_values|tojson }}, {{ enclosure_temp|tojson }}, "Enclosure Temperature", "Enclosure Temperature", 0, 60);
      </script>
    </body>
    </html>
    ''', machine_id=machine_id,
         x_values=x_values,
         zone1_temp=zone1_temp, zone1_req=zone1_req, zone1_heater=zone1_heater, zone1_ymin=zone1_ymin, zone1_ymax=zone1_ymax,
         zone2_temp=zone2_temp, zone2_req=zone2_req, zone2_heater=zone2_heater, zone2_ymin=zone2_ymin, zone2_ymax=zone2_ymax,
         zone3_temp=zone3_temp, zone3_req=zone3_req, zone3_heater=zone3_heater, zone3_ymin=zone3_ymin, zone3_ymax=zone3_ymax,
         zone4_temp=zone4_temp, zone4_req=zone4_req, zone4_heater=zone4_heater, zone4_ymin=zone4_ymin, zone4_ymax=zone4_ymax,
         person_in_bed=person_in_bed, bus_voltage=bus_voltage, aqi_data=aqi_data, humidity_data=humidity_data,
         room_temp=room_temp, enclosure_temp=enclosure_temp)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
