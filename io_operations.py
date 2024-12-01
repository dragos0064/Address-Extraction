import sys
import pandas as pd
from fastparquet import ParquetFile
from colorama import Fore, Style
import matplotlib.pyplot as plt
from matplotlib import rcParams



class IOHandler:
    def parse_parquet(self, file_path, selected_column):
        try:
            parquet_file = ParquetFile(file_path)
            return parquet_file.to_pandas()[selected_column]
        except:
            print("Error: Could not parse parquet file")
            sys.exit(1)

    def write_to_parquet(self, address_array):
        try:
            # Create a list of dictionaries, each representing a row of data
            data = []
            for element in address_array:
                row = {
                    "domain": element.get("domain"),
                    "country": element.get("address", {}).get("country", ""),
                    "region": element.get("address", {}).get("region", ""),
                    "city": element.get("address", {}).get("city", ""),
                    "postcode": element.get("address", {}).get("postcode", ""),
                    "road": element.get("address", {}).get("road", ""),
                    "house_number": element.get("address", {}).get("house_number", ""),
                }
                data.append(row)

            # Create a DataFrame from the list of dictionaries
            df = pd.DataFrame(data)

            # Write the DataFrame to a parquet file
            df.to_parquet("output/addresses.snappy.parquet", compression="snappy")
            print(
                "\nAddresses written to addresses.snappy.parquet in the output folder."
            )
        except Exception as e:
            print(f"{Fore.RED}Error: Could not write to parquet file{Style.RESET_ALL}")
            print(str(e))
            sys.exit(1)

    def write_to_csv(self, address_array):

        try:
            data = []
            for element in address_array:
                row = {
                    "domain": element.get("domain"),
                    "country": element.get("address", {}).get("country", ""),
                    "region": element.get("address", {}).get("region", ""),
                    "city": element.get("address", {}).get("city", ""),
                    "postcode": element.get("address", {}).get("postcode", ""),
                    "road": element.get("address", {}).get("road", ""),
                    "house_number": element.get("address", {}).get("house_number", ""),
                }
                data.append(row)

            df = pd.DataFrame(data)

            df.to_csv("output/addresses.csv", index=False)
            print("\nAddresses written to addresses.csv in the output folder.")
        except Exception as e:
            print(f"{Fore.RED}Error: Could not write to csv file{Style.RESET_ALL}")
            print(str(e))
            sys.exit(1)

    def show_pie_chart_for_countries(self, address_array):
        rcParams['font.family'] = 'Arial'  # Or 'Sans-serif'
        rcParams['axes.unicode_minus'] = False

        try:
            # Prepare the data for countries
            data = []
            for element in address_array:
                country = element.get("address", {}).get("country", "").strip()
                if country:  # Only add if the country field is not empty
                    row = {
                        "domain": element.get("domain", ""),
                        "country": country
                    }
                    data.append(row)

            # Create a DataFrame with the country data
            df = pd.DataFrame(data)

            # Count occurrences by country
            country_counts = df['country'].value_counts()

            # Plot the pie chart
            plt.figure(figsize=(14, 10))
            plt.pie(
                country_counts,
                labels=country_counts.index,
                autopct='%1.1f%%',
                startangle=140
            )
            plt.title("Distribution of Extracted Addresses by Country")
            plt.show()
            print(df.head())


        except Exception as e:
            print(f"Error creating pie chart: {e}")




