import requests
import pandas as pd

# Base URL for the API
base_url = "https://pa8ag6d1fl.execute-api.ap-south-1.amazonaws.com/dev/smart-mattress/api"

# Step 1: Sign In and get the access token
sign_in_url = f"{base_url}/user/signIn"
sign_in_payload = {
    "email": "smartmattress2023@gmail.com",  
    "password": "Welcome@123"  
}
headers = {
    "Content-Type": "application/json"
}

try:
    # Sign in to get access token
    response = requests.post(sign_in_url, json=sign_in_payload, headers=headers, verify=False)
    response.raise_for_status()
    access_token = response.json().get("accessToken")
    print("Login successful. Access token obtained.")
except requests.exceptions.RequestException as e:
    print(f"Error during login: {e}")
    exit()

# Step 2: Fetch error data for machine ID 68:B6:B3:54:E8:B2
error_data_url = f"{base_url}/machine/singleErrorData"
machine_error_payload = {
    "machineId": "68:B6:B3:54:E8:B2",
    "page": 1,
    "nFilter": {},
    "sortBy": "DESC",
    "sortValue": "arrivalTime",
    "download": 0,
    "fields": ["machineId", "arrivalTime", "zoneValue", "error", "logCounter"]
}

error_headers = {
    "Content-Type": "application/json",
    "x-access-token": access_token  # Include the access token in headers
}

try:
    # Fetch error data for the machine
    error_response = requests.post(error_data_url, json=machine_error_payload, headers=error_headers, verify=False)
    error_response.raise_for_status()
    error_data = error_response.json().get("data", [])

    if error_data:
        print("Error data retrieved successfully for machine ID 68:B6:B3:54:E8:B2")
    else:
        print("No error data found for machine ID 68:B6:B3:54:E8:B2")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching error data: {e}")
    exit()

# Step 3: Save the error data to an Excel file
if error_data:
    df = pd.DataFrame(error_data)
    output_file = "machine_68B6B354E8B2_error_data.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Error data saved to {output_file}")
else:
    print("No error data to save.")