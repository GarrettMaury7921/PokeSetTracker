import os
import re


# Record everything in a text file
def record_data(set_names, set_prices, date):
    directory = "data"

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Make all the files if they don't exist
    for x, set_name in enumerate(set_names):
        # Skip if set_name or set_price is None
        if set_name is None or set_prices[x] is None:
            print(f"Skipping entry {x}: set_name={set_name}, set_price={set_prices[x]}")
            continue

        # Make .txt file name for the set_name
        set_name_file = set_name + ".txt"

        # Combine the directory and set_name to get the full path
        file_path = os.path.join(directory, set_name_file)

        # Write to the file
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            # Open the file in append mode, which creates the file if it doesn't exist
            with open(file_path, 'a') as file:
                # Format: Unbroken Bonds,$500,8/9/2024
                file.write("\n" + set_name + "," + set_prices[x] + "," + date[0])
        else:
            with open(file_path, 'a') as file:
                # Format: Unbroken Bonds,$500,8/9/2024
                file.write(set_name + "," + set_prices[x] + "," + date[0])


# Delete any duplicate lines that are in each text file
def delete_duplicate_lines(folder):
    # Loop through each file in the folder
    for filename in os.listdir(folder):
        # Check if the file is a text file
        if filename.endswith('.txt'):
            file_path = os.path.join(folder, filename)

            # Read the content of the file
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Use a set to track seen lines and keep only unique ones in order
            seen = set()
            unique_lines = []
            for line in lines:
                # Strip whitespace and newline characters
                stripped_line = line.rstrip()
                # Skip blank lines
                if stripped_line and stripped_line not in seen:
                    unique_lines.append(line)  # Add original line to preserve formatting
                    seen.add(stripped_line)

            # Write the unique lines back to the file
            with open(file_path, 'w') as file:
                file.writelines(unique_lines)


# Put the data in another text file to format the data
def format_data(date_today, data_folder, formatted_data_folder):

    # Create the formatted_data folder if it doesn't exist
    if not os.path.exists(formatted_data_folder):
        os.makedirs(formatted_data_folder)

    # Example filename: set_price_sorter_8/12/2024
    output_filename = f'set_price_sorter_{date_today[1]}.txt'
    output_filepath = os.path.join(formatted_data_folder, output_filename)

    # Initialize a list to store the furthest lines
    last_lines = []

    # Process each file in the data folder
    for filename in os.listdir(data_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(data_folder, filename)

            # Read the content of the file
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Ensure there's at least one line in the file
            if lines:
                # Add the last line from the file
                last_line = lines[-1].strip()
                last_lines.append(last_line)

    def extract_price(line):
        # Improved regex to capture prices with commas and optional dollar sign
        match = re.search(r'\$([0-9,]+(?:\.[0-9]+)?)', line)
        if match:
            price_str = match.group(0)  # Get the full match including the dollar sign
            # Remove the dollar sign and commas, then convert to float
            price_str = price_str.replace('$', '').replace(',', '')
            return float(price_str)
        return 0.0

    # Sort the lines by price in descending order
    last_lines.sort(key=extract_price, reverse=True)

    # Format and write the lines to the output file
    with open(output_filepath, 'w') as output_file:
        for line in last_lines:

            # Split line into components using the first comma only
            parts = line.split(',', 2)

            if len(parts) == 3:
                item_name = parts[0].ljust(35)  # Adjust width as needed
                price = parts[1].rjust(12)  # Adjust width to fit larger prices
                date = parts[2].rjust(10)
                formatted_line = f"{item_name} {price} {date}\n"
                output_file.write(formatted_line)
            else:
                # Debugging: Print lines that do not match expected format
                print(f"Skipping line due to incorrect format: {line}")
