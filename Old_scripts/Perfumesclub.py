def process_urls(urls):
    xpath = ""
    for url in urls:
        page = ""#get_page_content_hash(url)        
        if page["status_code"] == 200:
            page = ""#get_parsed_tree(page)
        else:
            print(f"Failed to fetch the page for URL: {url}. Status code: {page['status_code']}")