from sdf_module import *
class PradaComInternalFeasibility:
    def get_page_content(self, url, args_hash):
        page_content = CommonModule.get_page_content_hash(url, args_hash)
        return page_content
