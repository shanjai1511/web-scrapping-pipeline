import requests
from lxml import etree

def get_page_content_hash(url, extended_header=None):
    if url:
        try:
            if extended_header:
                response = requests.get(url, headers=extended_header)
            else:
                response = requests.get(url)

            result = {
                "page_doc": response.text,
                "status_code": response.status_code,
                "url": url
            }
            
            if response.status_code != 200:
                print("***Page fetch failed***")
                
            return result
        except requests.RequestException as e:
            print(f"***Page fetch failed: {e}***")
            return {
                "page_doc": "",
                "status_code": None,
                "url": url
            }
    else:
        print("***No url found***")
        return "No url found"

def get_parsed_tree(page_doc):
    try:
        parser = etree.HTMLParser()
        tree = etree.fromstring(page_doc["page_doc"], parser)
        page_doc["page_doc"] = tree
    except etree.XMLSyntaxError as e:
        print(f"XML Syntax Error: {e}")
        page_doc["page_doc"] = f"XML Syntax Error: {e}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        page_doc["page_doc"] = f"Unexpected error: {e}"
    return page_doc