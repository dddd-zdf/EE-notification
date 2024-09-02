from playwright.sync_api import sync_playwright
from utils import toronto_time
import time

def scrape_page(url, interval):
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        
        # try refresh the page to get draw result
        while True:
            # try repetitively to visit the page
            while True:
                try:
                    page.goto(url)
                except:
                    continue
                else:
                    break
            
            
            time.sleep(10)
            cut_off = page.locator("#wb-auto-10")
            if cut_off and cut_off.inner_text() == '':
                now = toronto_time()
                if now.hour < 16:
                    time.sleep(interval)
                    continue
                else:
                    browser.close()
                    return {}
            
            draw = {
                'class': page.locator("#wb-auto-6").inner_text(),
                'cut_off': int(cut_off.inner_text()),
                'tie_breaking': page.locator("#wb-auto-11").inner_text()
            }
            
            browser.close()
            return draw