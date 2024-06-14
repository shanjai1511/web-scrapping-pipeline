import os

# Function to create the Python script
def create_python_script(name):
    script_content = f"""
from Page_fetcher import *

def process_urls(urls):
    
    for url in urls:
        page = get_page_content_hash(url)
        
        if page["status_code"] == 200:
            pass  # Add your processing code here
        else:
            print(f"Failed to fetch the page for URL: {{url}}. Status code: {{page['status_code']}}")

if __name__ == "__main__":
    urls = read_urls_from_file('{name}_urls.txt')
    process_urls(urls)
"""

    # Write the script content to {Name}.py
    with open(f"{name}.py", "w") as py_file:
        py_file.write(script_content.strip())

# Function to create the URLs file
def create_urls_file(name):
    # Create an empty {Name}_urls.txt file
    with open(f"{name}_urls.txt", "w") as urls_file:
        urls_file.write("")

if __name__ == "__main__":
    # Replace 'Name' with the desired name
    name = "Mouthshut"  # Change 'Example' to your desired file name without the extension
    create_python_script(name)
    create_urls_file(name)
    print(f"Files {name}.py and {name}_urls.txt have been created.")
