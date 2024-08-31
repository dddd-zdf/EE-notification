import json
import time
from datetime import datetime
import apprise
from playwright.sync_api import sync_playwright

def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    discord, interval, url = config['discord'], config['interval'] * 60, config['url_base'] + str(config['round'])
    now = datetime.now()

    # Wait until 12 PM if current time is before 12 PM
    if now.hour < 12:
        target_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
        time_to_wait = (target_time - now).total_seconds()
        time.sleep(time_to_wait)

    apobj = apprise.Apprise()
    apobj.add('discord://' + discord)

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()

        while True:
            page.goto(url)
            time.sleep(1)
            element = page.query_selector("//*[@id='wb-auto-5']")
            if element and element.inner_text() == '':
                print('empty')
                now = datetime.now()
                if now.hour < 16:
                    time.sleep(interval)
                    continue
                else:
                    body = 'no draw today'
                    break

            draw = page.query_selector('.well')

            # Hide the popup if it exists
            pop = page.query_selector('#gc-im-popup')
            if pop:
                page.evaluate("arguments[0].style.display = 'none';", pop)

            draw.screenshot(path='result.png')
            title = url
            body = '@everyone'
            config['round'] += 1
            break

        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        apobj.notify(
            title=title,
            body=body,
            attach='result.png'
        )

        import os
        if os.path.exists("result.png"):
            os.remove("result.png")

        browser.close()

if __name__ == "__main__":
    main()
