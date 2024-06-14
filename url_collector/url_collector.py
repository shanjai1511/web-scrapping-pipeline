import os
import sys
import yaml
import importlib.util

base_dir = "C:/Users/shanj/OneDrive/Desktop/scraping_pipeline"
output_dir = ""
fetcher_dir = ""
project_name = ""
site_name = ""
#make changes ti op dir
def write_url_in_txt(result_url):
    filepath = os.path.join(output_dir, f"{site_name}_{project_name}.txt")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'a') as file:
        for item in result_url:
            file.write(f"{item}\n")
    print_status("success", filepath, "Successfully written URLs")

def print_status(status, file_name, info):
    status_message = {
        "status": status,
        "file_name": file_name,
        "project": project_name,
        "site_name": site_name,
        "info": info
    }
    print(status_message)

def get_final_url(url, depth, current_depth_level, max_depth, module):
    current_depth = depth[f"depth{current_depth_level}"]
    method_name = current_depth["method_name"]
    method_to_call = getattr(module, method_name, None)

    if method_to_call is None:
        print_status("error", "", f"Method {method_name} not found in module {module.__name__}.")
        return

    for i in url:
        try:
            print_status("processing", "", f"Processing {i} with method {method_name}")
            result_url = method_to_call(i, depth, current_depth_level)
        except Exception as e:
            print_status("error", "", f"Error calling method {method_name} with argument {i}: {e}")
            continue

        if current_depth_level == max_depth:
            write_url_in_txt(result_url)
        else:
            get_final_url(result_url, depth, current_depth_level + 1, max_depth, module)

def main():
    print_status("info", "", "Starting script execution.")
    yaml_file_path = os.path.join(fetcher_dir, f"{site_name}_{project_name}.yml")
    try:
        print_status("info", "", f"Loading configuration file: {yaml_file_path}")
        with open(yaml_file_path, 'r') as file:
            depth = yaml.safe_load(file)
    except FileNotFoundError:
        print_status("error", "", f"Configuration file {yaml_file_path} not found.")
        return
    except yaml.YAMLError as e:
        print_status("error", "", f"Error loading YAML configuration file: {e}")
        return

    module_name = f"{site_name}_{project_name}"
    module_path = os.path.join(fetcher_dir, "jbhifi_nz_com_apple_aus.py")
    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        print_status("error", "", f"Could not locate module file at {module_path}.")
        return

    try:
        print_status("info", "", f"Importing module from {module_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception as e:
        print_status("error", "", f"Error importing module from {module_path}: {e}")
        return

    url = depth["depth0"]["seed_url"]
    if not isinstance(url, list):
        url = [url]

    get_final_url(url, depth, 0, len(depth) - 1, module)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_status("error", "", "Usage: python url_collector.py <project_name> <site_name>")
        sys.exit(1)

    project_name = sys.argv[1]
    site_name = sys.argv[2]
    output_dir = os.path.join(base_dir, f"scrape_output/collector_output/{project_name}")
    fetcher_dir = os.path.join(base_dir, f"url_collector/{project_name}")
    filepath = os.path.join(output_dir, f"{site_name}_{project_name}.txt")
    with open(filepath, 'w') as file:
        file.write('')
    print_status("success", filepath, "Cleared existing output file")

    main()
