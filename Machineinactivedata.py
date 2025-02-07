import pandas as pd
import requests

# Base URL for the API
base_url = "https://pa8ag6d1fl.execute-api.ap-south-1.amazonaws.com/dev/smart-mattress/api"


sign_in_url = f"{base_url}/user/signIn"
sign_in_payload = {
    "email": "smartmattress2023@gmail.com",  
    "password": "Welcome@123"  
}

headers = {
    "Content-Type": "application/json"
}

# Step 1: Sign in to get the access token
try:
    response = requests.post(sign_in_url, json=sign_in_payload, headers=headers, verify=False)
    response.raise_for_status()  

    if response.status_code == 200:
        access_token = response.json().get("accessToken")
        print("Login successful. Access token obtained.")
    else:
        print(f"Login failed. Status code: {response.status_code}")
        print("Response:", response.json())
        exit()

except requests.exceptions.RequestException as e:
    print("An error occurred during login:", e)
    exit()

# Step 2: Fetch All Machine IDs
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
        print("Response:", machine_response.json())
        exit()

except requests.exceptions.RequestException as e:
    print("An error occurred while fetching machine IDs:", e)
    exit()

# Step 3: Fetch Data for Each Machine ID 
single_machine_data_url = f"{base_url}/machineInactive/singleMachineInactiveData"


all_machine_data = []


for machine_id in machine_ids:

    machine_data_payload = {
        "machineId": machine_id["machineId"],  
        "page": 1,
        "nFilter": {},  
        "sortBy": "DESC",
        "sortValue": "timeStamp",
        "download": 0,
        "fields": [],
        "limit": 20  
    }

    try:
        single_machine_response = requests.post(single_machine_data_url, json=machine_data_payload, headers=machine_headers, verify=False)
        single_machine_response.raise_for_status()  

        if single_machine_response.status_code == 200:
            machine_data = single_machine_response.json().get("data", [])  
            if machine_data:
                print(f"Data for Machine ID {machine_id['machineId']}:")
                print(machine_data)  # Print raw data for debugging
                all_machine_data.extend(machine_data)  # Add data to the list
            else:
                print(f"No data found for Machine ID {machine_id['machineId']}.")
        else:
            print(f"Failed to fetch data for Machine ID {machine_id['machineId']}. Status code: {single_machine_response.status_code}")
            print("Response:", single_machine_response.json())

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for Machine ID {machine_id['machineId']}:", e)

# Step 4: Convert the collected data into a DataFrame and export to Excel
if all_machine_data:

    df = pd.DataFrame(machine_data)
    

    raw_output_file = "all_machineinactive_data.xlsx"
    df.to_excel(raw_output_file, index=False)
    print(f"Raw data successfully saved to {raw_output_file}")
    
    # Step 5: Structure the Excel data
    structured_data = pd.DataFrame()


    for index, row in df.iterrows():
        new_row = {}
        for col, value in row.items():
            if isinstance(value, list):
                # Split function
                for idx, item in enumerate(value):
                    new_col_name = f"{col}_{idx + 1}"
                    new_row[new_col_name] = item
            elif isinstance(value, dict):
                # If the value is a dictionary, expand it into separate columns
                for sub_key, sub_value in value.items():
                    new_col_name = f"{col}_{sub_key}"
                    new_row[new_col_name] = sub_value
            elif isinstance(value, str) and ':' in value:
                # If the value contains a colon, split it into key-value
                parts = value.split(":", 1)
                new_row[parts[0].strip()] = parts[1].strip()
            else:
                new_row[col] = value

        structured_data = structured_data.append(new_row, ignore_index=True)

 
    structured_output_file = "structured_machineinactive_data.xlsx"
    structured_data.to_excel(structured_output_file, index=False)
    print(f"Structured data saved to {structured_output_file}")
else:
    print("No data found for the given machine IDs.")