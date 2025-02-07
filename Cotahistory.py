import pandas as pd
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://pa8ag6d1fl.execute-api.ap-south-1.amazonaws.com/dev/smart-mattress/api"

sign_in_url = f"{base_url}/user/signIn"
sign_in_payload = {
    "email": "smartmattress2023@gmail.com",
    "password": "Welcome@123"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(sign_in_url, json=sign_in_payload, headers=headers, verify=False)
    response.raise_for_status()
    access_token = response.json().get("accessToken")
    print("Login successful. Access token obtained.")
except requests.exceptions.RequestException as e:
    print("An error occurred during login:", e)
    exit()

fota_history_url = f"{base_url}/device/cotaHistory"
fota_history_payload = {
    "page": 1,
    "limit": 3000,
    "status": ["Completed", "Pending", "Cancelled"],
    "sortBy": "DESC",
    "sortValue": "releasedId",
    "machineId": "68:B6:B3:54:E8:B2"
}
machine_headers = {"Content-Type": "application/json", "x-access-token": access_token}

try:
    fota_response = requests.post(fota_history_url, json=fota_history_payload, headers=machine_headers, verify=False)
    fota_response.raise_for_status()
    fota_data = fota_response.json().get("data", [])
    print(f"FOTA History for Machine ID {fota_history_payload['machineId']} retrieved successfully.")
    # print(fota_data)
    if 'result' in fota_data:
        fota_data = fota_data['result']
except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching FOTA history for Machine ID {fota_history_payload['machineId']}:", e)
    exit()

if fota_data and isinstance(fota_data, list):
    try:
        # Load the data into a DataFrame
        df = pd.DataFrame(fota_data)

        # Debug print to check the contents of df before filtering
        print("Initial DataFrame:")
        print(df)

        # Ensure the DataFrame is not None and contains the 'machineId' column
        if df is not None and not df.empty and 'machineId' in df.columns:
            # Filter the DataFrame for the specific machine ID
            df_filtered = df[df['machineId'] == fota_history_payload['machineId']]

            # Debug print to check the filtered DataFrame
            print("Filtered DataFrame:")
            print(df_filtered)

            # If df_filtered is not empty, save it to an Excel file
            if  df is not None:
                output_file = "Cota_history_single_machine.xlsx"
                df.to_excel(output_file, index=False)
                print(f"COTA history saved to {output_file}")
            else:
                print(f"No FOTA history data found for Machine ID {fota_history_payload['machineId']}.")
        else:
            print(f"DataFrame is empty or 'machineId' column is missing.")
    except Exception as e:
        print(f"An error occurred while saving data to Excel: {e}")
else:
    print(f"No FOTA history data found for Machine ID {fota_history_payload['machineId']}.")