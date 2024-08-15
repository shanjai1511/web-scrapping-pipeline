from sdf_module import CommonModule

class JbhifiNzComAppleAus(CommonModule):
    def get_final_url(self, url, depth, current_depth_level):
        page_url = []
        try:
            dom = self.get_page_content_hash(url)
            if dom["status_code"] != 200:
                raise Exception("No proper DOM found")
            parsed_tree = self.get_parsed_tree(dom)
            if parsed_tree is None:
                raise Exception("Parsing failed")
            page_url = self.get_value_from_xpath(parsed_tree, "//div[@class='listing-prod-title']/a[@class='text-truncate']/@href", "all")
        except Exception as e:
            print(f"Exception occurred: {e}")
        return page_url