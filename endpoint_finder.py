```python
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; endpoint_finder/1.0)"
}

JS_PATTERN = re.compile(r'<script.*?src=[\'"]([^\'"]+\.js)[\'"]', re.IGNORECASE)
ENDPOINT_PATTERN = re.compile(r'["\'](/[^"\'\s]{2,})["\']')
FULL_URL_PATTERN = re.compile(r'["\'](https?://[^\s"\'<>]+)["\']')

def get_js_links(target_url):
    try:
        r = requests.get(target_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        matches = JS_PATTERN.findall(r.text)
        full_links = [urljoin(target_url, link) for link in matches]
        return list(set(full_links))
    except Exception as e:
        print(f"[!] Failed to fetch JS links: {e}")
        return []

def extract_endpoints(js_url):
    try:
        r = requests.get(js_url, headers=HEADERS, timeout=10)
        content = r.text
        endpoints = ENDPOINT_PATTERN.findall(content)
        full_urls = FULL_URL_PATTERN.findall(content)
        return list(set(endpoints + full_urls))
    except Exception as e:
        print(f"[!] Error reading {js_url}: {e}")
        return []

def main(url, output_file):
    js_files = get_js_links(url)
    print(f"[+] Found {len(js_files)} JS files.")
    all_endpoints = []

    for js in js_files:
        print(f"[~] Analyzing {js}")
        eps = extract_endpoints(js)
        if eps:
            print(f" └─ Found {len(eps)} endpoints")
            all_endpoints.extend(eps)

    all_endpoints = sorted(set(all_endpoints))

    with open(output_file, 'w') as f:
        for e in all_endpoints:
            f.write(e + '\n')

    print(f"[✓] Extracted {len(all_endpoints)} unique endpoints.")
    print(f"[✓] Results saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find API endpoints in JS files.")
    parser.add_argument("url", help="Target full URL (e.g. https://example.com)")
    parser.add_argument("-o", "--output", help="Output file to save results", default="endpoints.txt")
    args = parser.parse_args()

    main(args.url, args.output)
```
