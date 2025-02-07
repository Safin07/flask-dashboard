import requests
import certifi
import os 
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Base URL for the API
base_url = "https://pa8ag6d1fl.execute-api.ap-south-1.amazonaws.com/dev/smart-mattress/api"

# List of machine IDs
machine_ids = ["68:B6:B3:54:E8:B2", "68:B6:B3:46:BB:1E",
               "68:B6:B3:54:E8:32", "68:B6:B3:53:04:2E", "68:B6:B3:52:94:5A",
                "68:B6:B3:53:7E:0A", "34:85:18:B6:AB:CE", "34:85:18:66:30:16",
                "68:B6:B3:52:87:F2", "68:B6:B3:52:93:6E", "68:B6:B3:51:BA:AE",
                "34:85:18:66:30:2E", "68:B6:B3:51:B9:7A", "68:B6:B3:52:94:12",
                "34:85:18:B6:97:56", "68:B6:B3:51:A9:CA", "68:B6:B3:52:93:26",
                "68:B6:B3:51:B9:82", "34:85:18:B6:97:4E", "68:B6:B3:2C:95:DE",
                "34:85:18:66:39:E6", "68:B6:B3:52:88:92", "68:B6:B3:54:D7:32",
                "68:B6:B3:52:92:BE", "68:B6:B3:54:E7:D6", "34:85:18:B8:23:56",
                "68:B6:B3:54:E8:4A", "68:B6:B3:54:E7:E2", "68:B6:B3:52:93:A2",
                "68:B6:B3:52:93:EE", "68:B6:B3:51:AB:DE", "68:B6:B3:54:E8:6A",
                "34:85:18:B6:98:06", "34:85:18:66:30:22"]  

# Sign In and get the access token
sign_in_url = f"{base_url}/user/signIn"
sign_in_payload = {
    "email": "smartmattress2023@gmail.com",
    "password": "Welcome@123"
}
headers = {
    "Content-Type": "application/json"
}
error_names = {
    1: "ERR_HEATER1_OPEN",
    2: "ERR_HEATER1_FAILURE",
    3: "ERR_HEATER1_OUTOFRANGE",
    4: "ERR_HEATER1_MIN_CURRENT",
    5: "ERR_SYSTEM_BROWNOUT",
    6: "ERR_SYSTEM_CACHE",
    7: "ERR_SYSTEM_MEMORYPROTECTION",
    8: "ERR_SYSTEM_STACK",
    9: "ERR_SYSTEM_HEAP",
    10: "ERR_SYSTEM_UBSAN",
    11: "ERR_SYSTEM_DEFAULT",
    20: "ERR_HEATER1_FAILURE",
    21: "ERR_HEATER1_OPEN",
    22: "ERR_HEATER1_OUTOFRANGE",
    23: "ERR_HEATER2_MIN_CURRENT",
    24: "ERR_HEATER2_FAILURE",
    25: "ERR_HEATER2_OPEN",
    26: "ERR_HEATER2_OUTOFRANGE",
    27: "ERR_HEATER2_MIN_CURRENT",
    28: "ERR_HEATER3_FAILURE",
    29: "ERR_HEATER3_OPEN",
    30: "ERR_HEATER3_OUTOFRANGE",
    31: "ERR_HEATER3_MIN_CURRENT",
    32: "ERR_HEATER4_FAILURE",
    33: "ERR_HEATER4_OPEN",
    34: "ERR_HEATER4_OUTOFRANGE",
    35: "ERR_HEATER4_MIN_CURRENT",
    36: "ERR_HEATER_SENSOR_MISMATCH",
    40: "ERR_TSENSOR1_OPEN",
    41: "ERR_TSENSOR1_FAILURE",
    42: "ERR_TSENSOR1_OUTOFRANGE",
    43: "ERR_TSENSOR2_OPEN",
    44: "ERR_TSENSOR2_FAILURE",
    45: "ERR_TSENSOR2_OUTOFRANGE",
    46: "ERR_TSENSOR3_OPEN",
    47: "ERR_TSENSOR3_FAILURE",
    48: "ERR_TSENSOR3_OUTOFRANGE",
    49: "ERR_TSENSOR4_OPEN",
    50: "ERR_TSENSOR4_FAILURE",
    51: "ERR_TSENSOR4_OUTOFRANGE",
    52: "ERR_PIB_SENSOR_OPEN",
    53: "ERR_PIB_SENSOR_FAILURE",
    54: "ERR_PIB_SENSOR_OUTOFRANGE",
    60: "ERR_TSENSOR5_OPEN",
    61: "ERR_TSENSOR5_FAILURE",
    62: "ERR_TSENSOR5_OUTOFRANGE",
    70: "ERR_BLE_INIT",
    71: "ERR_BLE_SERVICESINIT",
    72: "ERR_BLE_CONNECT",
    73: "ERR_BLE_ADVT",
    74: "ERR_BLE_PROTOCOL",
    80: "ERR_SMGR_INIT",
    81: "ERR_SMGR_PIB_INDEX_RD",
    82: "ERR_SMGR_PIB_INDEX_WR",
    83: "ERR_SMGR_PIB_SET",
    84: "ERR_SMGR_PIB_GET",
    85: "ERR_SMGR_MD_INDEX_RD",
    86: "ERR_SMGR_MD_INDEX_WR",
    87: "ERR_SMGR_MD_SET",
    88: "ERR_SMGR_MD_GET",
    89: "ERR_SMGR_ERH_INDEX_RD",
    90: "ERR_SMGR_ERH_INDEX_WR",
    91: "ERR_SMGR_ERH_SET",
    92: "ERR_SMGR_ERH_GET",
    93: "ERR_SMGR_PIBCONFIGVER_RD",
    94: "ERR_SMGR_MD_RECCOUNT_RD",
    95: "ERR_SMGR_MD_RECCOUNT_WR",
    96: "ERR_SMGR_PIB_RECCOUNT_RD",
    97: "ERR_SMGR_PIB_RECCOUNT_WR",
    98: "ERR_SMGR_ERH_RECCOUNT_RD",
    99: "ERR_SMGR_ERH_RECCOUNT_WR",
    100: "ERR_CONFIG_READ",
    101: "ERR_CONFIG_WRITE",
    102: "ERR_CONFIG_CORRUPT",
    103: "ERR_CONFIG_MODIFIERSOUTOFRANGE",
    104: "ERR_CONFIG_PIBOUTOFRANGE",
    110: "ERR_TC_TASKCREATE",
    120: "ERR_BME_INIT",
    121: "ERR_BME_BSEC_INIT",
    122: "ERR_BME_RUNTIME_CONFIG",
    123: "ERR_BME_BSEC_RUNTIME_CONFIG",
    124: "ERR_BME_RESET",
    125: "ERR_BME_TEMPERATURE",
    126: "ERR_BME_HUMIDITY",
    127: "ERR_BME_PRESSURE",
    128: "ERR_BME_IAQ",
    129: "ERR_BME_VOC",
    130: "ERR_BME_TASK",
    131: "ERR_BME_FAILURE",
    140: "ERR_CMDH_DEVICESTATUS",
    141: "ERR_CMDH_AQI",
    142: "ERR_CMDH_THERMALCONFIG",
    143: "ERR_CMDH_LIVEMODIFIER",
    144: "ERR_CMDH_DATETIME",
    145: "ERR_CMDH_DEVICECONFIG",
    146: "ERR_CMDH_DEVICERESET",
    147: "ERR_CMDH_MACHINEDATA",
    150: "ERR_CMU_DEVICEINFO",
    160: "ERR_STM_TASKCREATE",
    170: "ERR_TIMER1_INIT",
    171: "ERR_TIMER1_START",
    172: "ERR_TIMER1_STOP",
    173: "ERR_TIMER1_DELETE",
    174: "ERR_TIMER2_INIT",
    175: "ERR_TIMER2_START",
    176: "ERR_TIMER2_STOP",
    177: "ERR_TIMER2_DELETE",
    178: "ERR_TIMER3_INIT",
    179: "ERR_TIMER3_START",
    180: "ERR_TIMER3_STOP",
    181: "ERR_TIMER3_DELETE",
    182: "ERR_GPIO_INIT",
    183: "ERR_GPIO_SETOUTPUTLEVEL",
    184: "ERR_WDT_INIT",
    185: "ERR_WDT_WDIRESET",
    190: "ERR_I2C0_INIT",
    191: "ERR_I2C1_INIT",
    192: "ERR_I2C_PARAMETER",
    193: "ERR_I2C_START",
    194: "ERR_I2C_STOP",
    195: "ERR_I2C_READ",
    196: "ERR_I2C_WRITE",
    197: "ERR_ADC_CALIBRATION",
    198: "ERR_ADC_CONFIGURATION",
    199: "ERR_ADC_READ",
    200: "ERR_ADC_PARAMETER",
    201: "ERR_ADC_GETRAWDATA",
    202: "ERR_ADC_CHANNEL",
    203: "ERR_ADC_BUSVOLTAGE",
    204: "ERR_HISW_INIT",
    205: "ERR_UART_DISABLE",
    210: "ERR_RTC_INIT",
    211: "ERR_RTC_CONFIG",
    212: "ERR_RTC_READ",
    213: "ERR_RTC_WRITE",
    214: "ERR_RTC_BAT_LOW",
    220: "ERR_MQTT_CONN",
    221: "ERR_MQTT_CONN_INTPED",
    222: "ERR_MQTT_PUB",
    223: "ERR_HTTP_CONN",
    224: "ERR_HTTP_DISCONN",
    225: "ERR_HTTP_Post",
    226: "ERR_OTA_INIT",
    227: "ERR_HTTP_READ_AND_OTA_WRITE",
    228: "ERR_HTTP_READ_COMPLETE",
    229: "ERR_OTA_COMPLETE",
    230: "ERR_MD5_HASH",
    231: "ERR_WIFI_FOTA_IN_PROGRESS",
    232: "ERR_BLE_FOTA_IN_PROGRESS",
    233: "ERR_HTTPS_POST_MD_DATA",
    234: "ERR_WIFI_TASKCREATE"
}
    
    
    
#     dsvdsvsdvsdvsd
    
    
 
def get_today_date():
    # Fetch today's date in UTC for comparison
    return datetime.now(tz=timezone.utc).date()

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.strato.de')  # Your SMTP server
SMTP_PORT = 587  # Standard port for SMTP over TLS
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'safin.chowdhury@variowell-development.com')

# Store recipient emails in a comma-separated string or environment variable
RECEIVER_EMAIL = os.getenv(
    'RECEIVER_EMAIL',
    'safin.chowdhury@variowell-development.com,albine.bilalli@variowell-development.com,altania.vega@variowell-development.com'
)

# Convert the comma-separated string to a list of emails
RECEIVER_EMAIL_LIST = [email.strip() for email in RECEIVER_EMAIL.split(',')]

PASSWORD = os.getenv('EMAIL_PASSWORD', 'Saf#Mail535!')  # Your email password

def send_email(subject, body):
    for recipient in RECEIVER_EMAIL_LIST:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient  # Set the recipient in the 'To' field
        msg.attach(MIMEText(body, 'plain'))

        try:
            s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            s.starttls()
            s.login(SENDER_EMAIL, PASSWORD)
            s.sendmail(SENDER_EMAIL, recipient, msg.as_string())
            print(f"Email sent successfully to {recipient}!")
        except Exception as e:
            print(f"Failed to send email to {recipient}: {e}")
        finally:
            s.quit()

try:
    response = requests.post(sign_in_url, json=sign_in_payload, headers=headers, verify=certifi.where())
    response.raise_for_status()
    access_token = response.json().get("accessToken")
    print("Login successful. Access token obtained.")
except requests.exceptions.RequestException as e:
    print(f"Error during login: {e}")
    exit()

today_date = get_today_date()
error_found = False  # Flag to check if any error matches today's date
error_messages = []

for machine_id in machine_ids:
    error_data_url = f"{base_url}/machine/singleErrorData"
    machine_error_payload = {
        "machineId": machine_id,
        "page": 1,
        "nFilter": {},
        "sortBy": "DESC",
        "sortValue": "arrivalTime",
        "download": 0,
        "fields": ["machineId", "arrivalTime", "zoneValue", "error", "logCounter", "timeStamp"]
    }
    error_headers = {
        "Content-Type": "application/json",
        "x-access-token": access_token
    }

    error_response = requests.post(error_data_url, json=machine_error_payload, headers=error_headers, verify=certifi.where())
    error_response.raise_for_status()
    error_data = error_response.json().get("data", [])
    print(f"Fetched error data for machine {machine_id}:", error_data)

    if not error_data:
        print("No error data received, check API or payload.")
        continue

    for item in error_data.get('result', []):
        error_code = item.get("error")
        error_name = error_names.get(error_code, "Unknown Error")
        arrival_time = item.get("arrivalTime")
        if arrival_time:
            error_date = datetime.fromtimestamp(arrival_time, tz=timezone.utc).date()
            if error_date == today_date:
                # Convert timeStamp to datetime format
                timestamp_value = item.get("timeStamp")
                if timestamp_value:
                    timestamp_datetime = datetime.fromtimestamp(timestamp_value, tz=timezone.utc)
                    timestamp_str = timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')
                else:
                    timestamp_str = "N/A"

                error_message = (
                    f"Error on {error_date}: Code {error_code} - {error_name}, "
                    f"Details: Machine ID: {item.get('machineId')}, "
                    f"TimeStamp: {timestamp_str}"
                )
                print(error_message)
                error_messages.append(error_message)
                error_found = True

if error_found:
    send_email("Daily Error Report", "\n".join(error_messages))
else:
    print("No errors for today.")
    
    
    
    
    
