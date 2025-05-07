import pandas as pd
import re
import os

def consolidate_transaction_reports(folder_path):
    all_data = []

    # List all CSV files in the given folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)

            # Extract date from filename
            match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
            if match:
                date = match.group(0)
            else:
                print(f"Warning: No date found in {filename}. Skipping this file.")
                continue

            # Read CSV
            df = pd.read_csv(file_path)

            # Add Date column
            df['Date'] = date

            # Append
            all_data.append(df)

    # Concatenate all dataframes
    if all_data:
        consolidated_df = pd.concat(all_data, ignore_index=True)
        return consolidated_df
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    # Folder containing all CSVs
    folder_path = os.path.join(os.path.dirname(__file__), 'all-csv')

    result_df = consolidate_transaction_reports(folder_path)

    # Save the output
    output_path = os.path.join(os.path.dirname(__file__), 'consolidated_transaction_report.csv')
    result_df.to_csv(output_path, index=False)

    print(f"Consolidated report saved at '{output_path}' with {len(result_df)} rows.")
