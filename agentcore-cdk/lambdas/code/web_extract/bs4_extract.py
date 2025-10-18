
import requests
from bs4 import BeautifulSoup

                     
def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def get_text_from_url(some_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(some_url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        text = html_to_text(html)
        return text
    except requests.RequestException as e:
        print(f"Error fetching {some_url}: {e}")
        return ""



def extract(urls):
    results = []
    for url in urls:
        print (f"extracting url: {url}")
        raw_content = get_text_from_url(url)
        print (f"parsing content")
        parsed_content = raw_content #llm_parse_website(raw_content)
        results.append({"url": url, "raw_content": parsed_content, "images": []})
    return {"results": results, "failed_results": [], "response_time": 0}


    

