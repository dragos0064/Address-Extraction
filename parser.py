import random
import string
import re
import requests
from bs4 import BeautifulSoup as bs
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import urllib3
from colorama import Fore, Style
import logging

# Format: country, region, city, postcode, road, and road numbers.

# Set up logging
logging.basicConfig(
    filename="output/app.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class AddressParser:
    def __init__(self, timeout=2):
        self.timeout = timeout
        self.geolocator = Nominatim(user_agent=self.geolocatorRandomUserAgent())
        self.zip_code_regex = re.compile(r"\b\d{5}(?:[-\s]\d{4})?\b")
        self.street_regex = re.compile(
            r"(?i)(^|\s)\d{2,7}\b\s+.{5,30}\b\s+(?:road|rd|way|street|st|str|avenue|ave|boulevard|blvd|lane|ln|drive|dr|terrace|ter|place|pl|court|ct)(?:\.|\s|$)"
        )
        self.po_box_regex = re.compile(r"(?i)(?:po|p.o.)\s+(?:box)")
        self.geocode = RateLimiter(
            self.geolocator.geocode,
            max_retries=3,
            swallow_exceptions=True,
        )

    def geolocatorRandomUserAgent(self):

        arr = [
            *f"veridionAssignment{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))}"
        ]
        random.shuffle(arr)
        str = "".join(arr)

        return str

    def create_final_address(self, location_from_street, location_from_zip):

        if not location_from_street and not location_from_zip:
            return None

        # Get the raw address from the locations
        address_from_street = (
            location_from_street.raw.get("address") if location_from_street else None
        )
        address_from_zip = (
            location_from_zip.raw.get("address") if location_from_zip else None
        )

        if not address_from_street and not address_from_zip:
            return None

        country = self.get_field_value(address_from_street, address_from_zip, "country")
        region = self.get_field_value(address_from_street, address_from_zip, "state")
        city = self.get_field_value(address_from_street, address_from_zip, "city")
        postcode = self.get_field_value(
            address_from_street, address_from_zip, "postcode"
        )
        road = self.get_field_value(address_from_street, address_from_zip, "road")
        house_number = self.get_field_value(
            address_from_street, address_from_zip, "house_number"
        )

        # Return the final address as a dictionary
        return {
            "country": country,
            "region": region,
            "city": city,
            "postcode": postcode,
            "road": road,
            "house_number": house_number,
        }

    def get_field_value(self, first, second, field):


        field1 = first.get(field) if first else None
        field2 = second.get(field) if second else None

        if field == "road" and field1:  # prioritize the road from the street address
            return field1

        return field2 or field1

    def get_location(self, soup, regex, url):
        try:
            for val in soup.find_all(string=regex):
                if (
                    len(val) <= 100
                ):  # if the string is too long, it's probably not an address
                    location = re.search(regex, val).group(0)
                    location = re.sub(self.po_box_regex, "", location)
                    return location
        except AttributeError:
            print(
                f"AttributeError: Unable to find or process the location from {url}"
            )
            logging.error(
                f"AttributeError: Unable to find or process the location from {url}"
            )
        except Exception as e:
            print(
                f"Unexpected error {e} occurred while getting location from {url}"
            )
            logging.error(
                f"Unexpected error {e} occurred while getting location from {url}"
            )
        return None

    def parse_address(self, responses, user_agent, output_arr):

        list_of_street_addresses = []
        list_of_zip_codes = []
        if not responses:
            return

        urllib3.disable_warnings()
        for response in responses:
            url = response.get("domain")

            try:
                soup = bs(response.get("response"), "lxml")
            except Exception as e:
                print(
                    f"{Fore.RED}Error occurred while {Fore.YELLOW}parsing{Fore.RED} page {url}. Error: {e}{Style.RESET_ALL}"
                )
                logging.error(f"Error occurred while parsing page {url}. Error: {e}")
                return

            street_address = self.get_location(soup, self.street_regex, url)
            zip_code = self.get_location(soup, self.zip_code_regex, url)

            location_from_street = None
            location_from_zip = None

            if street_address and street_address not in list_of_street_addresses:
                list_of_street_addresses.append(street_address)
                try:
                    location_from_street = self.geolocator.geocode(
                        street_address, addressdetails=True, timeout=self.timeout
                    )
                except Exception as e:
                    print(
                        f"{Fore.RED}Error validating location from the street_address {street_address} from page {url}. Error: {e}{Style.RESET_ALL}"
                    )
                    logging.error(
                        f"Error validating location from the street_address {street_address} from page {url}. Error: {e}"
                    )

            if zip_code and zip_code not in list_of_zip_codes:
                list_of_zip_codes.append(zip_code)
                try:
                    location_from_zip = self.geolocator.geocode(zip_code)
                except Exception as e:
                    print(
                        f"{Fore.RED}Error validating location from the zip_code {zip_code} from page {url}. Error: {e}{Style.RESET_ALL}"
                    )
                    logging.error(
                        f"Error validating location from the zip_code {zip_code} from page {url}. Error: {e}"
                    )

            final_address = None
            try:
                final_address = self.create_final_address(
                    location_from_street, location_from_zip
                )
            except Exception as e:
                print(
                    f"{Fore.RED}Error getting final address from page {url}. Error {e}{Style.RESET_ALL}"
                )
                logging.error(f"Error getting final address from page {url}. Error {e}")

            if final_address:
                output_arr.append({"domain": url, "address": final_address})
                break  # we only need one address per website

            return