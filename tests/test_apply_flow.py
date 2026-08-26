from playwright.sync_api import sync_playwright
import time

def test_external_apply():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()
        
        # Test Accenture or Access Group job
        url = "https://in.linkedin.com/jobs/view/custom-software-engineer-at-accenture-in-india-4454591390"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(2)
        print("Title:", page.title())
        
        # Find all buttons / links with apply in text or href
        links = page.locator("a, button").all()
        for idx, el in enumerate(links):
            try:
                txt = el.inner_text().strip()
                href = el.get_attribute("href") or ""
                if "apply" in txt.lower() or "apply" in href.lower():
                    tag = el.evaluate("e => e.tagName")
                    cls = el.get_attribute("class") or ""
                    print(f"Match {idx}: <{tag} class='{cls[:30]}'> text='{txt}' href='{href[:70]}'")
            except Exception:
                pass
                
        # Try clicking the main apply button
        apply_btn = page.locator("a.apply-button, button.jobs-apply-button, a[data-tracking-control-name*='apply']").first
        if apply_btn.count() > 0:
            print("Found apply button. Clicking...")
            href = apply_btn.get_attribute("href")
            print("Apply button target href:", href)
            
        browser.close()

if __name__ == "__main__":
    test_external_apply()
