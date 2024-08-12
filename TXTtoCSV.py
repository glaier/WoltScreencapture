import re
import sys
import os
import pandas as pd
from datetime import datetime
import argparse

def parse_text_file(text_file):
    data = []
    current_date = None

    with open(text_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Date detection (e.g., 09/08/2024)
        date_match = re.match(r'\d{2}/\d{2}/\d{4}', line)
        if date_match:
            current_date = date_match.group()

        # Vendor and Time detection
        elif re.match(r'.+\s+\d{2}:\d{2}', line):
            vendor_time_match = re.match(r'(.+?)\s+(\d{2}:\d{2})', line)
            if vendor_time_match:
                vendor_name = vendor_time_match.group(1).strip()
                time_of_day = vendor_time_match.group(2).strip()

                # Move to the next line to get distance and amount
                i += 1
                if i < len(lines):
                    payment_line = lines[i].strip()
                    payment_match = re.match(r'Opgavebetaling \(incl\. (\d+\.\d{2}) km distance\) ([\d,]+) kr\.', payment_line)

                    if payment_match:
                        distance_km = payment_match.group(1).strip()
                        amount_kr = payment_match.group(2).replace(',', '.').strip()  # standardize amount to use '.' as decimal separator

                        data.append({
                            'Date': current_date,
                            'Vendor': vendor_name,
                            'Time': time_of_day,
                            'Distance (km)': distance_km,
                            'Amount (kr)': amount_kr
                        })

        i += 1

    return data

def save_to_csv(data, csv_file, remove_duplicates=False):
    # Convert the new data to a DataFrame
    new_df = pd.DataFrame(data)

    # Check if the output CSV file already exists
    if os.path.exists(csv_file):
        # Read the existing data
        existing_df = pd.read_csv(csv_file)

        # Append new data to the existing data
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    # Remove duplicates if requested
    if remove_duplicates:
        combined_df = combined_df.drop_duplicates()

    # Save the final DataFrame to CSV
    combined_df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"Data saved to {csv_file}")

def backup_existing_file(file_path):
    if os.path.exists(file_path):
        # Create a backup filename with the current date and time as a postfix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{os.path.splitext(file_path)[0]}_{timestamp}.csv"
        os.rename(file_path, backup_file)
        print(f"Existing file backed up as {backup_file}")

def main():
    parser = argparse.ArgumentParser(description="Process text files and generate a CSV output.")
    parser.add_argument('-P', '--path', type=str, help="Folder path to process all .txt files")
    parser.add_argument('-O', '--output', type=str, default='deliveries_output.csv', help="Output CSV file name")
    parser.add_argument('-d', '--deduplicate', action='store_true', help="Remove duplicates from the output")

    args = parser.parse_args()

    text_files = []

    # If a folder path is provided, add all .txt files from that path
    if args.path:
        if os.path.exists(args.path) and os.path.isdir(args.path):
            text_files = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.txt')]
        else:
            print(f"Error: The path {args.path} is not a valid directory.")
            sys.exit(1)
    
    if not text_files:
        print("No text files found to process.")
        sys.exit(1)

    # Backup the existing output file if it exists
    backup_existing_file(args.output)

    all_data = []

    for text_file in text_files:
        # Parse each text file
        data = parse_text_file(text_file)
        all_data.extend(data)

    if all_data:
        # Save the parsed data to the specified CSV file
        save_to_csv(all_data, args.output, remove_duplicates=args.deduplicate)
    else:
        print("No data was found to process.")

if __name__ == "__main__":
    main()
