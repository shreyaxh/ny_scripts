import os
import hashlib
import re

def process_log_file(log_file_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Dictionary to store unique file hashes
    unique_files = {}
    file_counter = 1

    # Check if the log file exists
    if not os.path.exists(log_file_path):
        print(f"Error: Log file not found at {log_file_path}")
        return

    with open(log_file_path, 'r') as log_file:
        for line_number, line in enumerate(log_file, start=1):
            # Check for the specific marker
            if "Request body for signing:" in line:
                print(f"Line {line_number}: Found target line.")

                # Extract the content to the right of the marker
                json_content = line.split("Request body for signing:", 1)[1].strip()

                # Remove all occurrences of '\\'
                json_content = json_content.replace("\\", "")

                # Remove " from the beginning and "}" from the end
                if json_content.startswith('"') and json_content.endswith('""}"}'):
                    json_content = json_content[1:-5]

                # Compute a hash of the content to check for duplicates
                content_hash = hashlib.md5(json_content.encode('utf-8')).hexdigest()

                if content_hash not in unique_files:
                    # Write the unique content to a new file
                    output_file_path = os.path.join(output_folder, f"{file_counter}.json")
                    with open(output_file_path, 'w') as output_file:
                        output_file.write(json_content)

                    unique_files[content_hash] = output_file_path
                    file_counter += 1

    # Regex patterns for extracting context fields
    context_action_pattern = re.compile(r'"action"\s*:\s*"([^"]+)"')
    transaction_id_pattern = re.compile(r'"transaction_id"\s*:\s*"([^"]+)"')
    existing_filenames = {}
    
    for file_path in unique_files.values():
        try:
            with open(file_path, 'r') as file:
                content = file.read()

            action_match = context_action_pattern.search(content)
            transaction_match = transaction_id_pattern.search(content)
            
            context_action = action_match.group(1) if action_match else "unknown_action"
            transaction_id = transaction_match.group(1) if transaction_match else "unknown_transaction"
            
            # Create a folder for the transaction_id if it doesn't exist
            transaction_folder = os.path.join(output_folder, transaction_id)
            os.makedirs(transaction_folder, exist_ok=True)
            
            base_name = context_action
            count = existing_filenames.get(base_name, 0) + 1
            existing_filenames[base_name] = count
            new_file_name = f"{base_name}{count}.json"
            new_file_path = os.path.join(transaction_folder, new_file_name)

            # Rename the file and move it to the transaction_id folder
            os.rename(file_path, new_file_path)

        except (FileNotFoundError, OSError) as e:
            print(f"Warning: Could not rename file {file_path} due to error: {e}")

    if file_counter == 1:
        print(f"No valid content found in the log file: {log_file_path}")
    else:
        print(f"Processing complete. Unique files saved in: {output_folder}")

if __name__ == "__main__":
    # Input log file path (update with your actual log file path)
    log_file_path = "/Users/shreyash/scripts/bap.log"

    # Output folder for unique files
    output_folder = "unique_files"

    process_log_file(log_file_path, output_folder)