import os
import requests
import hashlib
from lxml import etree
import json
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the single InsecureRequestWarning from urllib3 needed if suppressing warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

class CommonModule:
    @staticmethod
    def print_status(status, url, info=""):
        status_message = {
            "status": status,
            "url": url,
            "info": info
        }
        json_message = json.dumps(status_message, indent=4)
        print(json_message)

    @staticmethod
    def get_page_content_hash(url, extended_header=None):
        if url:
            try:
                if extended_header:
                    response = requests.get(url, headers=extended_header, verify=False)
                else:
                    response = requests.get(url, verify=False)

                if response.status_code == 200:
                    result = {
                        "page_doc": response.text,
                        "status_code": response.status_code,
                        "url": url
                    }
                    output_dir = "C:/Users/shanj/OneDrive/Desktop/web-scrapping-pipeline/cache/"
                    os.makedirs(output_dir, exist_ok=True)  # Ensure the cache directory exists

                    output_file = os.path.join(output_dir, hashlib.md5(url.encode()).hexdigest() + '.html')
                    with open(output_file, 'wb') as file:
                        file.write(response.content)
                    CommonModule.print_status("success", url, "Page fetched successfully.")
                    return result
                else:
                    CommonModule.print_status("error", url, f"Page fetch failed with status code {response.status_code}.")
                    return {
                        "page_doc": "",
                        "status_code": response.status_code,
                        "url": url
                    }

            except requests.RequestException as e:
                CommonModule.print_status("error", url, f"Page fetch failed: {e}")
                return {
                    "page_doc": "",
                    "status_code": None,
                    "url": url
                }
        else:
            CommonModule.print_status("error", url, "No URL found")
            return {"page_doc": "", "status_code": None, "url": url}

    @staticmethod
    def get_parsed_tree(page_doc):
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(page_doc["page_doc"], parser)
            CommonModule.print_status("success", page_doc["url"], "Page document parsed successfully.")
            return tree
        except etree.XMLSyntaxError as e:
            CommonModule.print_status("error", page_doc["url"], f"XML Syntax Error: {e}")
            return None
        except Exception as e:
            CommonModule.print_status("error", page_doc["url"], f"Unexpected error: {e}")
            return None

    @staticmethod
    def get_value_from_xpath(parsed_tree, xpath_expr, count):
        try:
            elements = parsed_tree.xpath(xpath_expr)
            text_content = [element for element in elements if element]
            CommonModule.print_status("success", "XPath evaluation", f"Text extracted successfully using XPath: {xpath_expr}")
            if count == "all":
                return text_content
            elif count == "first":
                return text_content[0] if text_content else None
        except etree.XPathError as e:
            CommonModule.print_status("error", "XPath evaluation", f"XPath Error: {e}")
            return f"XPath Error: {e}"
        except Exception as e:
            CommonModule.print_status("error", "XPath evaluation", f"Unexpected error: {e}")
            return f"Unexpected error: {e}"