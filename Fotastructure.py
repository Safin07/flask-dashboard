import pandas as pd
import ast
from datetime import datetime
import pytz

def convert_iso_to_cest(iso_timestamp):
    """Convert an ISO 8601 timestamp to Central European Summer Time (CEST)."""
    try:
        utc_time = datetime.strptime(iso_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        cest = pytz.timezone('Europe/Berlin')
        utc_time = pytz.utc.localize(utc_time)
        cest_time = utc_time.astimezone(cest)
        return cest_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return f"Error: {e}"

# Read the data from your Excel file
file_path = 'fota_history.xlsx'
raw_data_df = pd.read_excel(file_path)

# Initialize an empty list to collect all structured data
all_structured_data = []

# Iterate over each row in the DataFrame
for index, row in raw_data_df.iterrows():
    data_str = row.iloc[0]  # Assuming the data is in the first column of each row
    if isinstance(data_str, str):
        try:
            data_parsed = ast.literal_eval(data_str)
            fota_data_list = data_parsed if isinstance(data_parsed, list) else [data_parsed]
            structured_fota_df = pd.DataFrame(fota_data_list)
            timestamp_fields = ['releasedAt', 'modifiedAt']
            for field in timestamp_fields:
                if field in structured_fota_df.columns:
                    structured_fota_df[field] = structured_fota_df[field].apply(
                        lambda x: convert_iso_to_cest(x) if pd.notnull(x) and isinstance(x, str) else x
                    )
            all_structured_data.append(structured_fota_df)
        except Exception as e:
            print(f"Error parsing data on row {index}: {e}")
    else:
        print(f"Data in row {index} is not a string and was skipped.")

# Concatenate all DataFrame parts into one DataFrame
final_structured_df = pd.concat(all_structured_data, ignore_index=True)

# Save the structured data to an Excel file
output_file_path = 'fota_history_structured1.xlsx'
final_structured_df.to_excel(output_file_path, index=False)
print(f"Data saved to {output_file_path}")