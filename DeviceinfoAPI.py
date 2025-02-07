import pandas as pd
import requests

# Base URL for the API
base_url = "https://pa8ag6d1fl.execute-api.ap-south-1.amazonaws.com/dev/smart-mattress/api"

# Sign In API Details
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

    if response.status_code == 200:
        access_token = response.json().get("accessToken")
        print("Login successful. Access token obtained.")
    else:
        print(f"Login failed. Status code: {response.status_code}")
        exit()

except requests.exceptions.RequestException as e:
    print("An error occurred during login:", e)
    exit()


all_machine_id_url = f"{base_url}/machine/allMachineId"
machine_headers = {
    "Content-Type": "application/json",
    "x-access-token": access_token  
}

try:
    machine_response = requests.get(all_machine_id_url, headers=machine_headers, verify=False)
    machine_response.raise_for_status()

    if machine_response.status_code == 200:
        machine_ids = machine_response.json().get("data")
        print("All Machine IDs Retrieved Successfully:")
        print(machine_ids)
    else:
        print(f"Failed to fetch machine IDs. Status code: {machine_response.status_code}")
        exit()

except requests.exceptions.RequestException as e:
    print("An error occurred while fetching machine IDs:", e)
    exit()


device_info_url = f"{base_url}/machine/singleMachineDetails"  
device_data_list = []

for machine_id in machine_ids:
    device_info_payload = {
        "machineId": machine_id["machineId"]
    }

    try:
        device_response = requests.post(device_info_url, json=device_info_payload, headers=machine_headers, verify=False)
        device_response.raise_for_status()

        if device_response.status_code == 200:
            device_data = device_response.json().get("data", {})
            print(f"Device Info for Machine ID {machine_id['machineId']}:")
            print(device_data)
            device_data_list.append(device_data)
        else:
            print(f"Failed to fetch device info for Machine ID {machine_id['machineId']}. Status code: {device_response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching device info for Machine ID {machine_id['machineId']}:", e)


if device_data_list:
    df = pd.DataFrame(device_data_list)
    
  
    output_file = "all_device_info.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Device info saved to {output_file}")
else:
    print("No device info found.")