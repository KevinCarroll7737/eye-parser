import argparse
import os
from bs4 import BeautifulSoup
import re
import json
import csv

"""
This script regroups targets from an eyewitness report based on their technology.

It uses the following information contained in HTTP responses:
- Page Title (same technology)
- Content-length header (i.e.: same page)
- Server header
"""

identified_technology = {
        "page_title":{},
        "content_length":{},
        "server": {}
        }


def write_csv(csv_file):
    # Convert dictionary to CSV
    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Category", "Subcategory", "URL"])
        for category, subcategories in identified_technology.items():
            for subcategory, urls in subcategories.items():
                for url in urls:
                    writer.writerow([category, subcategory, url])

    print(f"CSV file '{csv_file}' has been created.")


def check_and_add_url(dictionary, key, value, url):
    if value in dictionary[key]:
        dictionary[key][value].append(url)
        print(f"Appended {url} to {value} in {key}.")
    else:
        dictionary[key][value] = [url]
        print(f"Added {value} with value {url} to {key}.")


def my_parser(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <a> tags containing href attribute with "http://"
    http_links = soup.find_all('a', href=re.compile(r'^http://'))                                           

    # Iterate through each <a> tag                                                                          
    for link in http_links:                                                                                 
        url = link.get('href')  # Extract the URL                                                           
        div_tag = link.find_parent('div')  # Find the parent <div> tag                                      

        if div_tag:  # If the parent <div> tag exists                                                       
            # Extract Page Title, Server, and Content-Length                                                
            page_title = div_tag.find('b', text=re.compile(r'Page Title:'))                                 
            server = div_tag.find('b', text=re.compile(r'Server:'))                                         
            content_length = div_tag.find('b', text=re.compile(r'Content-Length:'))                         

            # Extract the values if found                                                                   
            if page_title:                                                                                  
                page_title = page_title.next_sibling.strip()                                                
                check_and_add_url(identified_technology, "page_title", page_title, url)
            if server:                                                                                      
                server = server.next_sibling.strip()                                                        
                check_and_add_url(identified_technology, "server", server, url)
            if content_length:                                                                              
                content_length = content_length.next_sibling.strip()                                        
                check_and_add_url(identified_technology, "content_length", content_length, url)

    print("DONE")
    # Print the dictionary in JSON format
    print(json.dumps(identified_technology, indent=4))


def parse_html_files(directory):
    # Check if the directory exists
    if not os.path.isdir(directory):
        print("Error: Directory does not exist.")
        return

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            # Open one HTML file
            with open(filepath, "r") as file:
                html_content = file.read()
                # Parse the HTML content
                my_parser(html_content)


def read_file(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
            print("File contents:")
            print(content)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List files in a directory.")
    parser.add_argument("-d", "--directory", required=True, help="Path to the directory to list files from")
    parser.add_argument("-c", "--csv", required=True, help="Filename of the csv output")

    args = parser.parse_args()
    directory_path = args.directory
    csv_file = args.csv
    parse_html_files(directory_path)
    if csv_file:
        write_csv(csv_file)
