from sdf_module import *
class JbhifiNzComAppleAus():

    @staticmethod
    def get_uniq_id(page_doc, inhash):
        return CommonModule.encode(inhash['url'])

    @staticmethod
    def get_page_url(page_doc, inhash):
        return inhash['url']

    @staticmethod
    def get_product_name(page_doc, inhash):
        return CommonModule.get_value_from_xpath(page_doc, inhash['desc_of_xpath'],"first")
        
    @staticmethod
    def get_price(page_doc, inhash):
        return CommonModule.get_value_from_xpath(page_doc, inhash['desc_of_xpath'],"first")