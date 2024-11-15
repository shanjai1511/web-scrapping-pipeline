import os
import glob
import requests
import hashlib
import json
import sys
import csv
import ast
import yaml
import importlib.util
import logging
from openpyxl import load_workbook  # type: ignore
from datetime import datetime
import time
from bs4 import BeautifulSoup
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline/logs/pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class CommonModule:
    @staticmethod
    def print_error_message(status, info):
        status_message = {
            "status": status,
            "info": info
        }
        json_message = json.dumps(status_message, indent=4)
        logging.error(json_message)

    @staticmethod
    def print_info_message(status, info=None, url=None):
        status_message = {
            "status": status,
            "info": info
        }
        if url is not None:
            status_message["url"] = url
            
        json_message = json.dumps(status_message, indent=4)
        logging.info(json_message)

    @staticmethod
    def get_page_content_hash(url, extended_header=None):
        if url:
            try:
                response = requests.get(url, headers=extended_header, verify=False) if extended_header else requests.get(url, verify=False)

                if response.status_code == 200:
                    result = {
                        "page_doc": response.text,
                        "status_code": response.status_code,
                        "url": url
                    }
                    output_dir = Path("C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline/cache/")
                    output_dir.mkdir(parents=True, exist_ok=True)

                    output_file = output_dir / f"{CommonModule.encode(url)}.html"
                    with open(output_file, 'wb') as file:
                        file.write(response.content)
                    CommonModule.print_info_message("success", str(output_file), "Page fetched successfully.")
                    return result
                else:
                    return {
                        "page_doc": response.text,
                        "status_code": response.status_code,
                        "url": url
                    }

            except requests.RequestException as e:
                logging.exception("Request failed")
                return {
                    "page_doc": "",
                    "status_code": None,
                    "url": url
                }
        else:
            return {"page_doc": "", "status_code": None, "url": url}

    @staticmethod
    def get_parsed_tree(page_doc):
        try:
            soup = BeautifulSoup(page_doc["page_doc"], 'html5lib')
            CommonModule.print_info_message("success", "Page document parsed successfully.")
            return soup
        except Exception as e:
            CommonModule.print_error_message("error", f"Unexpected error during parsing: {e}")
            logging.exception("Parsing failed")
            return None

    @staticmethod
    def get_value_from_xpath(parsed_tree, xpath_expr, count, attr="none"):
        try:
            elements = parsed_tree.select(xpath_expr)
            text_content = [element.get_text() for element in elements if element]
            if attr != "none":
                text_content = [link[attr] for link in elements if link.has_attr(attr)]
            return text_content if count == "all" else (text_content[0] if text_content else None)
        except Exception as e:
            logging.exception("XPath extraction failed")
            return f"Unexpected error: {e}"

    @staticmethod
    def get_value_from_css_selector(parsed_tree, css_selector, count, attr="none"):
        try:
            elements = parsed_tree.select(css_selector)
            text_content = [element.get_text() for element in elements if element]
            if attr != "none":
                text_content = [element.get(attr) for element in elements if element.has_attr(attr)]
            return text_content if count == "all" else (text_content[0] if text_content else None)
        except Exception as e:
            logging.exception("CSS selector extraction failed")
            return f"Unexpected error: {e}"

    @staticmethod
    def encode(array):
        combined_str = ''.join(array)
        unique_id = hashlib.md5(combined_str.encode()).hexdigest()
        return unique_id

class UrlCollector:
    def __init__(self, base_dir, project_name, site_name):
        self.base_dir = base_dir
        self.output_dir = ""
        self.collector_dir = ""
        self.project_name = project_name
        self.site_name = site_name
        self.count = 0

    def write_url_in_txt(self, result_url):
        filepath = Path(self.output_dir) / f"{self.site_name}_{self.project_name}.txt"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'a') as file:
            for item in result_url:
                file.write(f"{item}\n")
        CommonModule.print_info_message("success", "Successfully written URLs")

    def enter_count_in_sheet(self):
        if self.count <= 0:
            CommonModule.print_info_message("Failure","No urls to enter in the sheet")
            return
        excel_file = Path(self.base_dir) / "url_collector" / "url_collector_count_sheet.xlsx"
        sheet_name = "collector_count"
        book = load_workbook(excel_file)
        sheet = book[sheet_name]

        row_num = 2
        while sheet.cell(row=row_num, column=1).value is not None:
            row_num += 1

        array = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), self.site_name, self.project_name]
        unique_id = CommonModule.encode(array)
        total_url_count = self.count

        sheet.cell(row=row_num, column=1, value=unique_id)
        sheet.cell(row=row_num, column=2, value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        sheet.cell(row=row_num, column=3, value=self.project_name)
        sheet.cell(row=row_num, column=4, value=self.site_name)
        sheet.cell(row=row_num, column=5, value=total_url_count)

        book.save(excel_file)
        CommonModule.print_info_message("success", f"Data written to {excel_file}")

    def get_final_url(self, url, depth, current_depth_level, max_depth, module_instance):
        current_depth = depth[f"depth{current_depth_level}"]
        method_name = current_depth["method_name"]
        method_to_call = getattr(module_instance, method_name)
        if method_to_call is None:
            return

        for i in url:
            try:
                result_url = method_to_call(i, depth, current_depth_level)
            except Exception as e:
                logging.exception("URL fetching failed")
                continue
            if current_depth_level == max_depth:
                self.write_url_in_txt(result_url)
                self.count += len(result_url)
            else:
                self.get_final_url(result_url, depth, current_depth_level + 1, max_depth, module_instance)

    def main_execution(self):
        try:
            yaml_file_path = Path(self.collector_dir) / f"{self.site_name}_{self.project_name}.yml"
            CommonModule.print_info_message("info", f"Loading configuration file: {yaml_file_path}")
            with open(yaml_file_path, 'r') as file:
                depth = yaml.safe_load(file)

            module_path = Path(self.collector_dir) / f"{self.site_name}_{self.project_name}.py"

            class_name_in_site_script = f"{self.site_name}_{self.project_name}"
            class_name_in_site_script = ''.join([word.capitalize() for word in class_name_in_site_script.split('_')])
            try:
                spec = importlib.util.spec_from_file_location(class_name_in_site_script, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                SiteClass = getattr(module, class_name_in_site_script)
                site_instance = SiteClass()
            except Exception as e:
                CommonModule.print_error_message("error", f"Error importing module from {module_path}: {e}")
                logging.exception("Module import failed")
                return

            seed_url = depth["depth0"]["seed_url"]
            if not isinstance(seed_url, list):
                seed_url = [seed_url]

            self.get_final_url(seed_url, depth, 0, len(depth) - 1, site_instance)
            self.enter_count_in_sheet()

        except Exception as e:
            CommonModule.print_error_message("error", f"Unhandled error during execution: {e}")
            logging.exception("Unhandled error during execution")
            raise

    def main(self):
        CommonModule.print_info_message("info", f"Starting script execution of url_collector for {self.site_name}_{self.project_name}")
        self.output_dir = Path(self.base_dir) / f"scrape_output /collector_output/{self.project_name}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collector_dir = Path(self.base_dir) / f"url_collector/{self.project_name}"
        filepath = self.output_dir / f"{self.site_name}_{self.project_name}.txt"
        with open(filepath, 'w') as file:
            file.write('')
        self.main_execution()

class UrlFetcher:
    def __init__(self, base_dir, project_name, site_name):
        self.base_dir = base_dir
        self.output_dir = ""
        self.project_name = project_name
        self.site_name = site_name

    def fetch_collector_output(self):
        urls = []
        try:
            self.output_dir = Path(self.base_dir) / f"scrape_output/collector_output/{self.project_name}"
            filepath = self.output_dir / f"{self.site_name}_{self.project_name}.txt"

            with open(filepath, "r") as f:
                for url in f:
                    urls.append(url.strip())
        except FileNotFoundError as e:
            CommonModule.print_error_message("error", f"File not found: {filepath}")
            logging.exception("File not found")
        return urls

    def main(self):
        CommonModule.print_info_message("info", f"Starting script execution of url_fetcher for {self.site_name}_{self.project_name}")
        yaml_file_path = Path(self.base_dir) / f"url_collector/{self.project_name}/{self.site_name}_{self.project_name}.yml"
        CommonModule.print_info_message("info", f"Loading configuration file: {yaml_file_path}")
        with open(yaml_file_path, 'r') as file:
            yaml_content = yaml.safe_load(file)

        extended_header = yaml_content.get("request_params", {}).get("extended_header",{})
        urls = self.fetch_collector_output()

        output_dir = Path(self.base_dir) / f"scrape_output/fetcher_output/{self.project_name}"
        output_dir.mkdir(parents=True, exist_ok=True)
        for url in urls:
            if extended_header:
                result = CommonModule.get_page_content_hash(url, extended_header)
            else:
                result = CommonModule.get_page_content_hash(url)
            output_file = output_dir / f"{CommonModule.encode(url)}.html"
            if result["status_code"] == 200:
                with open(output_file, "wb") as f:
                    f.write(result["page_doc"].encode("utf-8"))
                CommonModule.print_info_message("success", f"Successfully fetched page content for URL: {url}")
            else:
                CommonModule.print_error_message("error", f"Failed to fetch page content for URL: {url}")

class UrlExtractor:
    def __init__(self, base_dir, project_name, site_name):
        self.base_dir = base_dir
        self.output_dir = ""
        self.extractor_dir = Path(base_dir) / "url_data_extractor"
        self.project_name = project_name
        self.site_name = site_name
        self.count = 0

    def main(self):
        try:
            yaml_file_path = self.extractor_dir / f"{self.project_name}/{self.site_name}_{self.project_name}.yml"
            CommonModule.print_info_message("info", f"Loading configuration file: {yaml_file_path}")
            with open(yaml_file_path, 'r') as file:
                depth = yaml.safe_load(file)

            module_path = self.extractor_dir / f"{self.project_name}/{self.site_name}_{self.project_name}.py"

            class_name_in_site_script = f"{self.site_name}_{self.project_name}"
            class_name_in_site_script = ''.join([word.capitalize() for word in class_name_in_site_script.split('_')])
            try:
                spec = importlib.util.spec_from_file_location(class_name_in_site_script, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                SiteClass = getattr(module, class_name_in_site_script)
                site_instance = SiteClass()
            except Exception as e:
                CommonModule.print_error_message("error", f"Error importing module from {module_path}: {e}")
                return

            fetcher_output = self.extractor_dir / f"{self.project_name}/{self.site_name}_{self.project_name}"
            file_paths = glob.glob(str(fetcher_output / "*"))
            data = []
            fields_name = []
            for output in file_paths:
                page_content = ""
                with open(output, 'r') as file:
                    page_content = file.read()
                page_content = ast.literal_eval(page_content)
                parsed_content = CommonModule.get_parsed_tree(page_content)
                fields = depth['fields'] 
                record = {}
                fields_name = []
                for field in fields:
                    field_name = field
                    fields_name.append(field_name)
                    hash = fields[field]
                    hash['url'] = page_content['url']
                    method_name = f"get_{field_name}"
                    method_to_call = getattr(site_instance, method_name)
                    result = method_to_call(parsed_content,hash)
                    record[field_name] = result
                data.append(record)
            output_file = self.extractor_dir / f"{self.project_name}/{self.site_name}_{self.project_name}_{datetime.now().strftime('%d%m%Y')}.csv"
            with open(output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fields_name)
                writer.writeheader()
                writer.writerows(data)

        except Exception as e:
            CommonModule.print_error_message("error", f"Unhandled error during execution: {e}")
            logging.exception("Unhandled error during execution")
            raise

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python url_fetcher.py <project_name> <site_name>")
        sys.exit(1)
    method_to_execute = sys.argv[1]
    project_name = sys.argv[2]
    site_name = sys.argv[3]
    base_dir = "C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline"
    if method_to_execute == "url_collector":
        url_collector = UrlCollector(base_dir,project_name,site_name)
        url_collector.main()
    elif method_to_execute == "url_fetcher":
        url_fetcher = UrlFetcher(base_dir,project_name,site_name)
        url_fetcher.main()
    elif method_to_execute == "url_extractor":
        url_extractor = UrlExtractor(base_dir,project_name,site_name)
        url_extractor.main()
# import os
# import glob
# import requests
# import hashlib
# import json
# import sys
# import csv
# import ast
# import yaml
# import importlib.util
# import logging
# from openpyxl import load_workbook # type: ignore
# from datetime import datetime
# import time
# from bs4 import BeautifulSoup

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler("C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline/logs/pipeline.log"),
#         logging.StreamHandler(sys.stdout)
#     ]
# )

# class CommonModule:
#     @staticmethod
#     def print_error_message(status, info):
#         status_message = {
#             "status": status,
#             "info": info
#         }
#         json_message = json.dumps(status_message, indent=4)
#         logging.error(json_message)

#     @staticmethod
#     def print_info_message(status, info=None, url=None):
#         status_message = {
#             "status": status,
#             "info": info
#         }
#         if url is not None:
#             status_message["url"] = url
            
#         json_message = json.dumps(status_message, indent=4)
#         logging.info(json_message)

#     @staticmethod
#     def get_page_content_hash(url, extended_header=None):
#         if url:
#             try:
#                 if extended_header:
#                     response = requests.get(url, headers=extended_header, verify=False)
#                 else:
#                     response = requests.get(url, verify=False)

#                 if response.status_code == 200:
#                     result = {
#                         "page_doc": response.text,
#                         "status_code": response.status_code,
#                         "url": url
#                     }
#                     output_dir = "C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline/cache/"
#                     os.makedirs(output_dir, exist_ok=True)

#                     output_file = os.path.join(output_dir, CommonModule.encode(url) + '.html')
#                     with open(output_file, 'wb') as file:
#                         file.write(response.content)
#                     CommonModule.print_info_message("success", output_file, "Page fetched successfully.")
#                     return result
#                 else:
#                     return {
#                         "page_doc": response.text,
#                         "status_code": response.status_code,
#                         "url": url
#                     }

#             except requests.RequestException as e:
#                 logging.exception("Request failed")
#                 return {
#                     "page_doc": "",
#                     "status_code": e.response,
#                     "url": url
#                 }
#         else:
#             return {"page_doc": "", "status_code": None, "url": url}

#     @staticmethod
#     def get_parsed_tree(page_doc):
#         try:
#             soup = BeautifulSoup(page_doc["page_doc"], 'html5lib')
#             CommonModule.print_info_message("success", "Page document parsed successfully.")
#             return soup
#         except Exception as e:
#             CommonModule.print_error_message("error", f"Unexpected error during parsing: {e}")
#             logging.exception("Parsing failed")
#             return None

#     @staticmethod
#     def get_value_from_xpath(parsed_tree, xpath_expr, count, attr = "none"):
#         try:
#             elements = parsed_tree.select(xpath_expr)
#             text_content = [element.get_text() for element in elements if element]
#             if attr != "none":
#                 links = parsed_tree.select(xpath_expr)
#                 text_content = [link[attr] for link in links if link.has_attr(attr)]
#             if count == "all":
#                 return text_content
#             elif count == "first":
#                 return text_content[0] if text_content else None
#         except Exception as e:
#             logging.exception("XPath extraction failed")
#             return f"Unexpected error: {e}"

#     @staticmethod
#     def get_value_from_css_selector(parsed_tree, css_selector, count, attr="none"):
#         try:
#             elements = parsed_tree.select(css_selector)
#             text_content = [element.get_text() for element in elements if element]
#             if attr != "none":
#                 text_content = [element.get(attr) for element in elements if element.has_attr(attr)]
#             if count == "all":
#                 return text_content
#             elif count == "first":
#                 return text_content[0] if text_content else None
#         except Exception as e:
#             logging.exception("CSS selector extraction failed")
#             return f"Unexpected error: {e}"

#     @staticmethod
#     def encode(array):
#         combined_str = ''.join(array)
#         unique_id = hashlib.md5(combined_str.encode()).hexdigest()
#         return unique_id

# class UrlCollector(CommonModule):
#     def __init__(self, base_dir, project_name, site_name):
#         self.base_dir = base_dir
#         self.output_dir = ""
#         self.collector_dir = ""
#         self.project_name = project_name
#         self.site_name = site_name
#         self.count = 0

#     @staticmethod
#     def write_url_in_txt(self, result_url):
#         filepath = os.path.join(self.output_dir, f"{self.site_name}_{self.project_name}.txt")
#         os.makedirs(os.path.dirname(filepath), exist_ok=True)
#         with open(filepath, 'a') as file:
#             for item in result_url:
#                 file.write(f"{item}\n")
#         CommonModule.print_info_message("success", "Successfully written URLs")

#     @staticmethod
#     def encode(array):
#         combined_str = ''.join(array)
#         unique_id = hashlib.md5(combined_str.encode()).hexdigest()
#         return unique_id

#     @staticmethod
#     def enter_count_in_sheet(self):
#         if self.count <= 0:
#             CommonModule.print_info_message("Failure","No urls to enter in the sheet")
#             return
#         excel_file = os.path.join(self.base_dir, "url_collector", "url_collector_count_sheet.xlsx")
#         sheet_name = "collector_count"
#         book = load_workbook(excel_file)
#         sheet = book[sheet_name]

#         row_num = 2
#         while sheet.cell(row=row_num, column=1).value is not None:
#             row_num += 1

#         array = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), self.site_name, self.project_name]
#         unique_id = self.encode(array)
#         total_url_count = self.count

#         sheet.cell(row=row_num, column=1, value=unique_id)
#         sheet.cell(row=row_num, column=2, value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#         sheet.cell(row=row_num, column=3, value=self.project_name)
#         sheet.cell(row=row_num, column=4, value=self.site_name)
#         sheet.cell(row=row_num, column=5, value=total_url_count)

#         book.save(excel_file)
#         CommonModule.print_info_message("success", f"Data written to {excel_file}")

#     @staticmethod
#     def get_final_url(self, url, depth, current_depth_level, max_depth, module_instance):
#         current_depth = depth[f"depth{current_depth_level}"]
#         method_name = current_depth["method_name"]
#         method_to_call = getattr(module_instance, method_name)
#         if method_to_call is None:
#             return

#         for i in url:
#             try:
#                 result_url = method_to_call(i, depth, current_depth_level)
#             except Exception as e:
#                 logging.exception("URL fetching failed")
#                 continue
#             if current_depth_level == max_depth:
#                 self.write_url_in_txt(self, result_url)
#                 self.count += len(result_url)
#             else:
#                 self.get_final_url(self, result_url, depth, current_depth_level + 1, max_depth, module_instance)

#     @staticmethod
#     def main_execution(self):
#         try:
#             yaml_file_path = os.path.join(self.collector_dir, f"{self.site_name}_{self.project_name}.yml")
#             CommonModule.print_info_message("info", f"Loading configuration file: {yaml_file_path}")
#             with open(yaml_file_path, 'r') as file:
#                 depth = yaml.safe_load(file)

#             module_path = os.path.join(self.collector_dir, f"{self.site_name}_{self.project_name}.py")

#             class_name_in_site_script = f"{self.site_name}_{self.project_name}"
#             class_name_in_site_script = ''.join([word.capitalize() for word in class_name_in_site_script.split('_')])
#             try:
#                 spec = importlib.util.spec_from_file_location(class_name_in_site_script, module_path)
#                 module = importlib.util.module_from_spec(spec)
#                 spec.loader.exec_module(module)
#                 SiteClass = getattr(module, class_name_in_site_script)
#                 site_instance = SiteClass()
#             except Exception as e:
#                 CommonModule.print_error_message("error", f"Error importing module from {module_path}: {e}")
#                 logging.exception("Module import failed")
#                 return

#             seed_url = depth["depth0"]["seed_url"]
#             if not isinstance(seed_url, list):
#                 seed_url = [seed_url]

#             self.get_final_url(self, seed_url, depth, 0, len(depth) - 1, site_instance)
#             self.enter_count_in_sheet(self)

#         except Exception as e:
#             CommonModule.print_error_message("error", f"Unhandled error during execution: {e}")
#             logging.exception("Unhandled error during execution")
#             raise

#     @staticmethod
#     def main(self):
#         CommonModule.print_info_message("info", f"Starting script execution of url_collector for {site_name}_{project_name}")
#         self.output_dir = os.path.join(self.base_dir, f"scrape_output/collector_output/{self.project_name}")
#         self.collector_dir = os.path.join(self.base_dir, f"url_collector/{self.project_name}")
#         filepath = os.path.join(self.output_dir, f"{self.site_name}_{self.project_name}.txt")
#         with open(filepath, 'w') as file:
#             file.write('')
#         self.main_execution(self)

# class UrlFetcher(CommonModule):
#     def __init__(self, base_dir, project_name, site_name):
#         self.base_dir = base_dir
#         self.output_dir = ""
#         self.project_name = project_name
#         self.site_name = site_name

#     def encode(self, code):
#         unique_id = hashlib.md5(code.encode()).hexdigest()
#         return unique_id
    
#     def fetch_collector_output(self, project_name, site_name):
#         urls = []
#         try:
#             self.output_dir = os.path.join(self.base_dir, f"scrape_output/collector_output/{project_name}")
#             filepath = os.path.join(self.output_dir, f"{site_name}_{project_name}.txt")

#             with open(filepath, "r") as f:
#                 for url in f:
#                     urls.append(url.strip())
#         except FileNotFoundError as e:
#             CommonModule.print_error_message("error", f"File not found: {filepath}")
#             logging.exception("File not found")
#         return urls

#     def main(self):
#         CommonModule.print_info_message("info", f"Starting script execution of url_fetcher for {site_name}_{project_name}")
#         yaml_file_path = os.path.join(self.base_dir, f"url_collector/{self.project_name}/{self.site_name}_{self.project_name}.yml")
#         CommonModule.print_info_message("info", f"Loading configuration file: {yaml_file_path}")
#         with open(yaml_file_path, 'r') as file:
#             yaml_content = yaml.safe_load(file)

#         extended_header = yaml_content.get("request_params", {}).get("extended_header",{})
#         urls = self.fetch_collector_output(self.project_name, self.site_name)

#         output_dir = os.path.join(self.base_dir, f"scrape_output/fetcher_output/{self.project_name}")
#         os.makedirs(output_dir, exist_ok=True)
#         for url in urls:
#             if extended_header:
#                 result = self.get_page_content_hash(url, extended_header)
#             else:
#                 result = self.get_page_content_hash(url)
#             output_file = os.path.join(output_dir, f"{self.encode(url)}.html")
#             if result["status_code"] == 200:
#                 with open(output_file, "wb") as f:
#                     f.write(result["page_doc"].encode("utf-8"))
#                 CommonModule.print_info_message("success", f"Successfully fetched page content for URL: {url}")
#             else:
#                 CommonModule.print_error_message("error", f"Failed to fetch page content for URL: {url}")

# class UrlExtractor(CommonModule):
#     def __init__(self, base_dir, project_name, site_name):
#         self.base_dir = base_dir
#         self.output_dir = ""
#         self.extractor_dir = f"{base_dir}/url_data_extractor"
#         self.project_name = project_name
#         self.site_name = site_name
#         self.count = 0

#     @staticmethod
#     def main(self):
#         try:
#             yaml_file_path = os.path.join(self.extractor_dir, f"{self.project_name}/{self.site_name}_{self.project_name}.yml")
#             #CommonModule.print_info_message("info", f"Loading configuration file: {yaml_file_path}")
#             with open(yaml_file_path, 'r') as file:
#                 depth = yaml.safe_load(file)

#             module_path = os.path.join(self.extractor_dir, f"{self.project_name}/{self.site_name}_{self.project_name}.py")

#             class_name_in_site_script = f"{self.site_name}_{self.project_name}"
#             class_name_in_site_script = ''.join([word.capitalize() for word in class_name_in_site_script.split('_')])
#             try:
#                 spec = importlib.util.spec_from_file_location(class_name_in_site_script, module_path)
#                 module = importlib.util.module_from_spec(spec)
#                 spec.loader.exec_module(module)
#                 SiteClass = getattr(module, class_name_in_site_script)
#                 site_instance = SiteClass()
#                 fetcher_output = f"C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline/scrape_output/fetcher_output/{project_name}/{site_name}_{project_name}"
#                 file_paths = glob.glob(os.path.join(fetcher_output, "*"))
#                 data = []
#                 fields_name = []
#                 for output in file_paths:
#                     page_content = ""
#                     with open(output, 'r') as file:
#                         page_content = file.read()
#                     page_content = ast.literal_eval(page_content)
#                     parsed_content = CommonModule.get_parsed_tree(page_content)
#                     fields = depth['fields'] 
#                     record = {}
#                     fields_name = []
#                     for field in fields:
#                         field_name = field
#                         fields_name.append(field_name)
#                         hash = fields[field]
#                         hash['url'] = page_content['url']
#                         method_name = f"get_{field_name}"
#                         method_to_call = getattr(site_instance, method_name)
#                         result = method_to_call(parsed_content,hash)
#                         record[field_name] = result
#                     data.append(record)
#                 output_file = f"C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline/scrape_output/extractor_output/{project_name}/{site_name}_{project_name}_{datetime.now().strftime("%d%m%Y")}.csv"
#                 with open(output_file, mode='w', newline='', encoding='utf-8') as file:
#                     writer = csv.DictWriter(file, fields_name)
#                     writer.writeheader()
#                     writer.writerows(data)
#             except Exception as e:
#                 CommonModule.print_error_message("error", f"Error importing module from {module_path}: {e}")
#                 return

#         except Exception as e:
#             CommonModule.print_error_message("error", f"Unhandled error during execution: {e}")
#             raise

# if __name__ == "__main__":
#     if len(sys.argv) != 4:
#         print("Usage: python url_fetcher.py <project_name> <site_name>")
#         sys.exit(1)
#     method_to_execute = sys.argv[1]
#     project_name = sys.argv[2]
#     site_name = sys.argv[3]
#     base_dir = "C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline"
#     if method_to_execute == "url_collector":
#         url_collector = UrlCollector(base_dir,project_name,site_name)
#         url_collector.main(url_collector)
#     elif method_to_execute == "url_fetcher":
#         url_fetcher = UrlFetcher(base_dir,project_name,site_name)
#         url_fetcher.main()
#     elif method_to_execute == "url_extractor":
#         url_extractor = UrlExtractor(base_dir,project_name,site_name)
#         url_extractor.main(url_extractor)