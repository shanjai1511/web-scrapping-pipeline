import os
import sys
from common_module import *
import pdb

# Define the root directories and file locations
base_dir = "C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline"
output_dir = ""

def fetch_collector_output(project_name, site_name):
    """Fetch the URLs from the specified file and store them in an array."""
    urls = []
    try:
        # Construct the file path
        filepath = os.path.normpath(os.path.join(output_dir, f"{site_name}_{project_name}.txt"))

        filepath = filepath.replace("\\","/")
        # Debugging: Print constructed file path
        print(f"Constructed file path: {filepath}")
        pdb.set_trace()
        # Check if the file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        # Read the contents of the file and store them in an array
        with open(filepath, 'r') as file:
            urls = [line.strip() for line in file.readlines()]

        # Print the contents
        for url in urls:
            data = get_page_content_hash(url)
            print(data)

        # Print status message
        status_message = {
            "status": "Success",
            "file_name": f"{site_name}_{project_name}.txt",
            "project": project_name,
            "site_name": site_name,
            "info": "File contents fetched and printed successfully."
        }
        print(status_message)

        return urls

    except FileNotFoundError as e:
        status_message = {
            "status": "Error",
            "file_name": f"{site_name}_{project_name}.txt",
            "project": project_name,
            "site_name": site_name,
            "info": str(e)
        }
        print(status_message)
        return []

    except Exception as e:
        status_message = {
            "status": "Error",
            "file_name": f"{site_name}_{project_name}.txt",
            "project": project_name,
            "site_name": site_name,
            "info": f"An unexpected error occurred: {e}"
        }
        print(status_message)
        return []

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python url_fetcher.py <project_name> <site_name>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    site_name = sys.argv[2]
    output_dir = os.path.join(base_dir, f"scrape_output/collector_output/{project_name}")
    urls = fetch_collector_output(project_name, site_name)
    # Optionally, you can do something with the urls array here