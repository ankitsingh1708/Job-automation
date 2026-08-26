import httpx
from bs4 import BeautifulSoup
import re

url = "https://in.linkedin.com/jobs/view/custom-software-engineer-at-accenture-in-india-4454591390"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

resp = httpx.get(url, headers=headers, follow_redirects=True)
print("Status:", resp.status_code)
print("URL:", resp.url)

soup = BeautifulSoup(resp.text, 'html.parser')
print("Title:", soup.title.string if soup.title else "No title")

# Find all links/buttons with apply
elements = soup.find_all(['a', 'button'])
print(f"Total elements: {len(elements)}")
for el in elements:
    txt = el.get_text(strip=True)
    href = el.get('href', '')
    cls = el.get('class', [])
    if 'apply' in txt.lower() or 'apply' in href.lower() or any('apply' in c.lower() for c in cls):
        print(f"Tag: <{el.name}> class={cls} text='{txt}' href='{href}'")
