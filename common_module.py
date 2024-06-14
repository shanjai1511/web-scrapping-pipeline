import requests
from lxml import etree

def print_status(status, url, info=""):
    status_message = {
        "status": status,
        "url": url,
        "info": info
    }
    print(status_message)

def get_page_content_hash(url, extended_header=None):
    if url:
        try:
            if extended_header:
                response = requests.get(url, headers=extended_header)
            else:
                response = requests.get(url)

            if response.status_code == 200:
                result = {
                    "page_doc": response.text,
                    "status_code": response.status_code,
                    "url": url
                }
                print_status("success", url, "Page fetched successfully.")
                return result
            else:
                print_status("error", url, f"Page fetch failed with status code {response.status_code}.")
                return {
                    "page_doc": "",
                    "status_code": response.status_code,
                    "url": url
                }

        except requests.RequestException as e:
            print_status("error", url, f"Page fetch failed: {e}")
            return {
                "page_doc": "",
                "status_code": None,
                "url": url
            }
    else:
        print_status("error", url, "No URL found")
        return {"page_doc": "", "status_code": None, "url": url}

def get_parsed_tree(page_doc):
    try:
        parser = etree.HTMLParser()
        tree = etree.fromstring(page_doc["page_doc"], parser)
        page_doc["page_doc"] = tree
        print_status("success", page_doc["url"], "Page document parsed successfully.")
    except etree.XMLSyntaxError as e:
        print_status("error", page_doc["url"], f"XML Syntax Error: {e}")
        page_doc["page_doc"] = f"XML Syntax Error: {e}"
    except Exception as e:
        print_status("error", page_doc["url"], f"Unexpected error: {e}")
        page_doc["page_doc"] = f"Unexpected error: {e}"
    return page_doc

def get_value_from_xpath(parsed_tree, xpath_expr, count):
    try:
        elements = parsed_tree.xpath(xpath_expr)
        text_content = [element.text for element in elements if element.text]
        print_status("success", parsed_tree.base, f"Text extracted successfully using XPath: {xpath_expr}")
        if count == "all":
            return text_content
        elif count == "first":
            return text_content[0]
    except etree.XPathError as e:
        print_status("error", parsed_tree.base, f"XPath Error: {e}")
        return f"XPath Error: {e}"
    except Exception as e:
        print_status("error", parsed_tree.base, f"Unexpected error: {e}")
        return f"Unexpected error: {e}"