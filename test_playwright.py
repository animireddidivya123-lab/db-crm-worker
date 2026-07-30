from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.google.com/maps/search/Catering+Businesses+in+Andhra+Pradesh')
    page.wait_for_timeout(5000)
    elements = page.query_selector_all('a[href*="/maps/place/"]')
    for el in elements[:2]:
        name = el.get_attribute('aria-label')
        print("Clicking:", name)
        try:
            el.scroll_into_view_if_needed()
            el.click(force=True)
            page.wait_for_timeout(3000)
            
            # Google Maps phone button usually has data-item-id="phone:tel:+91..."
            phone_btn = page.query_selector('button[data-item-id^="phone:tel:"]')
            if phone_btn:
                phone = phone_btn.get_attribute('data-item-id').replace('phone:tel:', '')
                print("Phone found via data-item-id:", phone)
            else:
                print("No phone button found.")
        except Exception as e:
            print("Error:", e)
    browser.close()
