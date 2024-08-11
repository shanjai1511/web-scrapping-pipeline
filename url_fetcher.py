import os
import sys
from common_module import CommonModule
import json
import yaml
import pdb
import hashlib
# Define the root directories and file locations
base_dir = "C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline"

class UrlFetcher(CommonModule):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.output_dir = ""

    def print_status(self, status, file_name, info):
        status_message = {
            "status": status,
            "file_name": file_name,
            "project": self.project_name,
            "site_name": self.site_name,
            "info": info
        }
        json_message = json.dumps(status_message, indent=4)
        print(json_message)

    def encode(self, code):
        pdb.set_trace()
        unique_id = hashlib.md5(code.encode()).hexdigest()
        return unique_id
    
    def fetch_collector_output(self, project_name, site_name):
        """Fetch the URLs from the specified file and store them in an array."""
        urls = []
        try:
            # Construct the file path
            self.output_dir = os.path.join(self.base_dir, f"scrape_output/collector_output/{project_name}")
            filepath = os.path.normpath(os.path.join(self.output_dir, f"{site_name}_{project_name}.txt"))

            filepath = filepath.replace("//", "/")
            # Debugging: Print constructed file path
            print(f"Constructed file path: {filepath}")
            # Check if the file exists
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            # Read the contents of the file and store them in an array
            with open(filepath, 'r') as file:
                urls = [line.strip() for line in file.readlines()]
            # Print status message
            status_message = {
                "status": "Success",
                "file_name": f"{site_name}_{project_name}.txt",
                "project": project_name,
                "site_name": site_name,
                "info": "File contents fetched and printed successfully."
            }
            #UrlFetcher.print_status(status_message)
            args_hash = {}
            yaml_file = os.path.normpath(os.path.join(self.base_dir, f"url_fetcher/apple_aus/{site_name}_{project_name}.yml"))
            with open(yaml_file, 'r') as file:
                args_hash = yaml.safe_load(file)

            for url in urls:
                pdb.set_trace()
                #page_content = CommonModule.get_page_content_hash(url)
                output_file_path = os.path.normpath(f"C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline/scrape_output/fetcher_output/apple_aus/jbhifi_nz_com_apple_aus/{UrlFetcher.encode(url)}.txt")
                pdb.set_trace()
                with open(output_file_path, 'w') as file:
                    file.write("page_content")
            return urls

        except FileNotFoundError as e:
            status_message = {
                "status": "Error",
                "file_name": f"{site_name}_{project_name}.txt",
                "project": project_name,
                "site_name": site_name,
                "info": str(e)
            }
            #UrlFetcher.print_status(status_message)
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
    url_fetcher = UrlFetcher(base_dir)
    urls = url_fetcher.fetch_collector_output(project_name, site_name)
    # Optionally, you can do something with the urls array here