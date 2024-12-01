from timeit import default_timer as timer
from threading import Thread, Semaphore
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from colorama import init as colorama_init
import numpy as np

from io_operations import IOHandler
from crawler import WebsiteCrawler
from user_agent_provider import UserAgentProvider
from parser import AddressParser


TIMEOUT = 2
NUM_THREADS = 40
CHUNK_SIZE = 100
semaphore = Semaphore(NUM_THREADS)

def crawl_website_with_semaphore(df_element, user_agent, responses):
    semaphore.acquire()

    try:
        WebsiteCrawler(TIMEOUT).crawl_website(df_element, user_agent, responses)
    finally:
        semaphore.release()


def crawl_websites(df, no_of_websites, user_agent_provider):

    threads = []
    responses = []

    # Iterate over the existing elements in the DataFrame
    for i in range(min(len(df), no_of_websites)):
        element = df[i]
        t = Thread(
            target=crawl_website_with_semaphore,
            args=(
                element,
                user_agent_provider.get_random_user_agent(),
                responses,
            ),
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return responses


def main():
    start = timer()

    colorama_init()

    def print_error_and_exit(error_message):
        print(f"ERROR: {error_message}")
        sys.exit(1)

    # Create the Tkinter root
    Tk().withdraw()

    # Ask the user to select a file
    print(
        f"Input Parquet: Please select the file containing the list of company websites\n"
    )

    path = askopenfilename(
        title="Choose the file containing the list of company websites",
    )

    if path:
        print(f"File loaded successfully: {path}")
    else:
        print_error_and_exit("No file selected")

    try:
        print("Loading user agents")
        user_agents = open("input/user-agents.txt", "r").read().split("\n")
        print("User agents loaded successfully")
    except:
        print_error_and_exit("Could not load user agents")

    io_handler = IOHandler()
    user_agent_provider = UserAgentProvider(user_agents)
    address_parser = AddressParser(timeout=TIMEOUT)

    df = io_handler.parse_parquet(path, "domain")
    list_of_addresses = []

    df = df.reset_index(drop=True)

    groups = df.groupby(
        np.arange(len(df)) // CHUNK_SIZE
    )

    for _, group in groups:
        print(
            f"[{group.index[0] + 1}-{group.index[-1] + 1}]Crawling websites {group.index[0] + 1}-{group.index[-1] + 1} out of {len(df)}"
        )

        current_index = group.index[0]
        # Reset the index of group
        group = group.reset_index(drop=True)

        # Crawl the websites and get the links
        responses = crawl_websites(group, CHUNK_SIZE, user_agent_provider)

        # Parse the addresses from the links
        for element in responses:
            print(
                f"Extracting address from {element[0].get('domain')}"
            )

            address_parser.parse_address(
                element,
                user_agent_provider.get_random_user_agent(),
                list_of_addresses,
            )

    # Write the addresses to a parquet file and then to a csv file

    io_handler.write_to_parquet(list_of_addresses)
    io_handler.write_to_csv(list_of_addresses)
    io_handler.show_pie_chart_for_countries(list_of_addresses)

    # Calculate and print the elapsed time
    end = timer()
    seconds = end - start
    m, s = divmod(seconds, 60)

    print("\n-------------------------------------------------------")
    print(f"Time passed: {m} minutes and {s} seconds")
    print(
        f"Extracted {len(list_of_addresses)} addresses from {df.size} domains"
    )
    print("-------------------------------------------------------")


if __name__ == "__main__":
    main()