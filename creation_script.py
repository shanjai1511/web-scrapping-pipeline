import os
import pandas as pd
import sys
import json
def print_status(status, file_name, project, site_name, info):
    status_message = {
        "status": status,
        "file_name": file_name,
        "project": project,
        "site_name": site_name,
        "info": info
    }
    status_message = json.dumps(status_message, indent=4)
    print(status_message)

def create_project_structure(base_path, project_name, site_name, py_content, yml_content):
    project_path = os.path.join(base_path, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print_status("created", project_path, project_name, site_name, "Directory created")

    py_file_path = os.path.join(project_path, f"{site_name}_{project_name}.py")
    yml_file_path = os.path.join(project_path, f"{site_name}_{project_name}.yml")

    with open(py_file_path, 'w') as py_file:
        py_file.write(py_content)
        print_status("created", py_file_path, project_name, site_name, "Python file created")

    with open(yml_file_path, 'w') as yml_file:
        yml_file.write(yml_content)
        print_status("created", yml_file_path, project_name, site_name, "YAML file created")

def create_text_file(base_path, project_name, site_name):
    project_path = os.path.join(base_path, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print_status("created", project_path, project_name, site_name, "Directory created")
        
    txt_file_path = os.path.join(project_path, f"{site_name}_{project_name}.txt")
    with open(txt_file_path, 'w') as txt_file:
        txt_file.write("")
        print_status("created", txt_file_path, project_name, site_name, "Text file created")

def create_folder(base_path, project_name, site_name):
    project_path = os.path.join(base_path, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print_status("created", project_path, project_name, site_name, "Directory created")

    site_folder_path = os.path.join(project_path, f"{site_name}_{project_name}")
    if not os.path.exists(site_folder_path):
        os.makedirs(site_folder_path)
        print_status("created", site_folder_path, project_name, site_name, "Site folder created")

def create_excel_file(base_path, project_name, site_name):
    project_path = os.path.join(base_path, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print_status("created", project_path, project_name, site_name, "Directory created")

    excel_file_path = os.path.join(project_path, f"{site_name}_{project_name}.xlsx")
    df = pd.DataFrame()  # Empty DataFrame to create an empty Excel file
    df.to_excel(excel_file_path, index=False)
    print_status("created", excel_file_path, project_name, site_name, "Excel file created")

def main():
    if len(sys.argv) != 3:
        print("Usage: python automated_script.py <project_name> <site_name>")
        sys.exit(1)

    project_name = sys.argv[1]
    site_name = sys.argv[2]

    base_dir = os.getcwd()

    url_collector_path = os.path.join(base_dir, 'url_collector')
    url_fetcher_path = os.path.join(base_dir, 'url_fetcher')
    url_extractor_path = os.path.join(base_dir, 'url_data_extractor')
    scrape_output_path = os.path.join(base_dir, 'scrape_output')
    
    # Content for each file type
    collector_py_content = """def process_urls(urls):
    xpath = ""
    for url in urls:
        page = "" # get_page_content_hash(url)        
        if page["status_code"] == 200:
            page = "" # get_parsed_tree(page)
        else:
            print(f"Failed to fetch the page for URL: {url}. Status code: {page['status_code']}")
    """
    collector_yml_content = """depth0:
  depth1:"""
    
    fetcher_py_content = """def fetch_data():
    print("Fetching data...")
"""
    fetcher_yml_content = """depth0:
  depth1:"""
    
    extractor_py_content = """def extract_data():
    print("Extracting data...")
"""
    extractor_yml_content = """depth0:
  depth1:"""
    
    create_project_structure(url_collector_path, project_name, site_name, collector_py_content, collector_yml_content)
    create_project_structure(url_fetcher_path, project_name, site_name, fetcher_py_content, fetcher_yml_content)
    create_project_structure(url_extractor_path, project_name, site_name, extractor_py_content, extractor_yml_content)

    scrape_collector_output = os.path.join(scrape_output_path, 'collector_output')
    scrape_fetcher_output = os.path.join(scrape_output_path, 'fetcher_output')
    scrape_extractor_output = os.path.join(scrape_output_path, 'extractor_output')

    create_text_file(scrape_collector_output, project_name, site_name)
    create_folder(scrape_fetcher_output, project_name, site_name)
    create_excel_file(scrape_extractor_output, project_name, site_name)

if __name__ == "__main__":
    main()