from common_module import *
import yaml

def get_final_url(url, depth, current_depth_level):
    page_url = []
    try:
        dom = get_page_content_hash(url)
        if dom["status_code"] != 200:
            raise Exception("No preper dom found")
        dom = get_parsed_tree(dom)

        name = get_value_from_xpath(dom, "", "all")
    except Exception as e:
        print(f"Exception occurend: {e}")
    return page_url