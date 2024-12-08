# PokeSetTracker

# Garrett Maury
# 8-7-2024 3:13 AM - Python 3.9
# 12-8-2024 12:49 AM - Python 3.12
# A script to check a website to scrap data to find out what value each Pokémon card set is

import concurrent.futures
import networking
import format

url_sets = "xxxxx"
formatted_data_folder = "formatted_data"
data_folder = "data"


if __name__ == "__main__":

    html = networking.query(url_sets)
    links = networking.parse(html)
    current_date = networking.get_current_date()

    all_set_names = [None] * len(links)
    all_set_prices = [None] * len(links)

    # Use ThreadPoolExecutor with a maximum of 10 threads

    max_threads = 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submit tasks to the executor, associating each with its index
        future_to_index = {executor.submit(networking.process_link, idx, link): idx for idx, link in enumerate(links)}

        for future in concurrent.futures.as_completed(future_to_index):
            try:
                # Retrieve results
                index, set_name, set_price = future.result()
                # Validate and store results in correct order
                if 0 <= index < len(all_set_names):  # Prevent out-of-range errors
                    all_set_names[index] = set_name
                    all_set_prices[index] = set_price
                else:
                    print(f"Warning: Index {index} out of range.")
            except Exception as e:
                print(f"Error in thread: {e}")

    # Time to record all the data in a text file
    format.record_data(all_set_names, all_set_prices, current_date)

    # Delete any duplicate lines if there are any
    format.delete_duplicate_lines(data_folder)

    # Format the data if we so choose
    format.format_data(current_date, data_folder, formatted_data_folder)

