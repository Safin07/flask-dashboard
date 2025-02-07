import pandas as pd
import requests
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
def fetch_data(url, machine_id, access_token):
    all_records = []
    page = 1  # Start from the first page

    while True:
        data_payload = {
            "machineId": machine_id,
            "page": page,
            "nFilter": {},
            "sortBy": "DESC",
            "sortValue": "timeStamp",
            "download": 0,
            "fields": [],
            "limit": 100  # Fetch 100 records per page
        }
        headers = {
            "Content-Type": "application/json",
            "x-access-token": access_token
        }

        try:
            response = requests.post(url, json=data_payload, headers=headers, verify=False)
            response.raise_for_status()
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {}).get("result", [])
                if not data:
                    break  # Exit the loop if no more data is returned
                all_records.extend(data)
                page += 1  # Move to the next page
            else:
                logging.error(f"Failed to fetch data from {url} for Machine ID {machine_id}. Status code: {response.status_code}")
                logging.error("Response: %s", response.json())
                break
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching data from {url} for Machine ID {machine_id}: %s", e)
            break

    return all_records

# Function to convert timestamps to CEST
def convert_to_cest(timestamp):
    utc_time = datetime.utcfromtimestamp(timestamp)
    cest = pytz.timezone('Europe/Berlin')
    cest_time = pytz.utc.localize(utc_time).astimezone(cest)
    
    date = cest_time.strftime('%Y-%m-%d')
    time_short = cest_time.strftime('%H:%M')  # Only "hh:mm" format
    
    return date, time_short

# Function to structure the data
def structure_data(data):
    rows = []
    for row in data:
        if isinstance(row, dict):  # Ensure the row is a dictionary
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

# Main function
def main():
    # Get access token
    access_token = get_access_token()

    # Get machine ID input from the user
    user_machine_id = input("Enter the Machine ID you want to fetch data for: ").strip()

    # URLs for both APIs
    machine_data_url = f"{base_url}/machine/single"
    machine_inactive_data_url = f"{base_url}/machineInactive/singleMachineInactiveData"

    # Fetch machine data
    logging.info("Fetching Machine Data...")
    machine_data = fetch_data(machine_data_url, user_machine_id, access_token)
    structured_machine_data = structure_data(machine_data)

    # Fetch machine inactive data
    logging.info("Fetching Machine Inactive Data...")
    machine_inactive_data = fetch_data(machine_inactive_data_url, user_machine_id, access_token)
    structured_machine_inactive_data = structure_data(machine_inactive_data)

    # Create a single Excel file with multiple sheets
    output_file = "structured_machine_data.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        if not structured_machine_data.empty:
            structured_machine_data.to_excel(writer, sheet_name="Machine Data", index=False)
        if not structured_machine_inactive_data.empty:
            structured_machine_inactive_data.to_excel(writer, sheet_name="Machine Inactive Data", index=False)

    logging.info(f"Structured data successfully saved to {output_file}")

if __name__ == "__main__":
    main()