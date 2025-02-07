import requests
import logging

# Disable warnings for insecure HTTPS requests (if needed)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Base URL and machine ID (hardcoded for testing)
base_url = "https://api-prod.variowell-iot.com/smart-mattress/api"
machine_id = "68:B6:B3:52:94:5A"  # Example machine

# Replace with a valid access token
access_token = "eyJraWQiOiJLU1wvZnNPQnNVdFwvK3E1NEtvM2trOVVISEhpdlwvYjhiRU15ckZTSkIxSVdvPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzM2VlMTFkYS1jZTc4LTRjNTgtOTEwOC01ZDU2MzI2MjEzY2YiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGgtMS5hbWF6b25hd3MuY29tXC9hcC1zb3V0aC0xX0prcmdXYUxobCIsImNsaWVudF9pZCI6IjdlY3V2N282ZnVvaHZsc3RrdGtkMHF2amYyIiwib3JpZ2luX2p0aSI6IjVhNDBiYzUxLTliYjktNDc4Yy1hODA1LWYzMWNjYzMzZWU0YyIsImV2ZW50X2lkIjoiZWRiNTEyYmUtNDg4ZC00MjBhLWIyMTItMTU4ZDU4ODQ5NTNhIiwidG9rZW5fdXNlIjoiYWNjZXNzIiwic2NvcGUiOiJhd3MuY29nbml0by5zaWduaW4udXNlci5hZG1pbiIsImF1dGhfdGltZSI6MTczODc4MjU0OCwiZXhwIjoxNzM4Nzg2MTQ4LCJpYXQiOjE3Mzg3ODI1NDgsImp0aSI6IjY1YWEwNjM2LTRkMDgtNDI2MS1iZTE3LTk5M2ZlMWYyMmQ0NCIsInVzZXJuYW1lIjoiMzNlZTExZGEtY2U3OC00YzU4LTkxMDgtNWQ1NjMyNjIxM2NmIn0.E9MWuK_n98PNpG3_Th09slEPWbwFq7igm_ExUpeZxgQahPsP1sCH8k3XdR_dnAEp0sH6Mrmq7aTrj9gl4Z5-N_BFTM8d5mtEirqgnHVnxPtvx7SuwHErtajKNadYUAvT07cMQb96QnJK6pAaPS8IMDmS8cp8NbNSERlmimSDMGy6MYsf2q_dAhSM9C7QbB850MooizDUZAynXRK8S50af4TJ2YuY_LweTdM5FGRMmLQ3AZ6w0mSa6G-0sSPmTtn-rX1b-syO3ZcjYI5WJcHXBRGasUsYa4XElmI0z3JdYuahKmH0nqxZDwUxBCtZZQLJhur8g7jPMCuOFl0dwTeeTA"
def get_zone_name(machine_id, access_token):
    # Request headers
    headers = {
        "Content-Type": "application/json",
        "x-access-token": access_token
    }
    
    # 1) POST to /group to fetch the list of groups/regions
    group_url = f"{base_url}/group"
    payload_groups = {
        "page": 1,
        "limit": 10
    }
    try:
        resp = requests.post(group_url, json=payload_groups, headers=headers, verify=False)
        resp.raise_for_status()
        # The groups are under data->result
        groups = resp.json().get("data", {}).get("result", [])
        print("Fetched groups:", groups)
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching groups: %s", e)
        return ""
    
    # 2) For each group/region, POST to /group/viewGrouping with {"regionId": ...}
    view_grouping_url = f"{base_url}/group/viewGrouping"
    
    for group_item in groups:
        region_id = group_item.get("regionId")
        zone_name = group_item.get("zoneName", "")
        print(f"Checking region: {region_id}, zoneName: {zone_name}")
        
        if region_id is None:
            continue  # Skip invalid region
        
        # Build payload with the dynamic regionId
        payload_view = {
            "regionId": region_id
        }
        
        try:
            resp_view = requests.post(view_grouping_url, json=payload_view, headers=headers, verify=False)
            resp_view.raise_for_status()
            grouping_list = resp_view.json().get("data", [])
            print(f"Grouping data for regionId {region_id}:", grouping_list)
        except requests.exceptions.RequestException as e:
            logging.error("Error fetching grouping data for region %s: %s", region_id, e)
            continue
        
        # 3) Check if the machine is in any of the returned grouping entries
        for entry in grouping_list:
            if entry.get("machineId") == machine_id:
                print(f"Found machine {machine_id} in region {region_id} with zoneName = {zone_name}")
                return zone_name
    
    # If no region contained the machine ID
    print(f"Machine {machine_id} was not found in any region.")
    return ""

if __name__ == '__main__':
    zone_name = get_zone_name(machine_id, access_token)
    print(f"Zone Name for machine {machine_id}: {zone_name}")