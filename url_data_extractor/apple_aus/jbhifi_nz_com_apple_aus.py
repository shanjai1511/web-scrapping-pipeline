from sdf_module import *
from datetime import datetime
class JbhifiNzComAppleAus():

    @staticmethod
    def get_crawl_timestamp(page_doc, inhash):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_uniq_id(page_doc, inhash):
        return CommonModule.encode(inhash['url'])

    @staticmethod
    def get_page_url(page_doc, inhash):
        return inhash['url']

    @staticmethod
    def get_product_name(page_doc, inhash):
        return CommonModule.get_value_from_xpath(page_doc, inhash['desc_of_xpath'],"first").rstrip().strip()
        
    @staticmethod
    def get_price(page_doc, inhash):
        value = CommonModule.get_value_from_xpath(page_doc, inhash['desc_of_xpath'],"first")
        if value:
            return value.rstrip().strip()