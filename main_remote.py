import os
import json
import time
from datetime import datetime
import apprise
from playwright.sync_api import sync_playwright
import pytz

cwd = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(cwd, 'config.json')

def toronto_time():
    toronto_tz = pytz.timezone('America/Toronto')
    utc_now = datetime.now(pytz.utc)
    return utc_now.astimezone(toronto_tz)


def main():
    with open(config_path, 'r') as f:
        config = json.load(f)

    discord, interval, url = config['discord'], config['interval'] * 60, config['url_base'] + str(config['round'])

    now = toronto_time()

    # Wait until 12 PM if current time is before 12 PM
    if now.hour < 12:
        target_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
        time_to_wait = (target_time - now).total_seconds()
        time.sleep(time_to_wait)

    apobj = apprise.Apprise()
    apobj.add('discord://' + discord)
    title = ''
    with sync_playwright() as p:
        browser = p.firefox.launch(executable_path=os.path.join(cwd,'ms-playwright/firefox-1458/firefox/firefox'))
        page = browser.new_page()

        while True:
            page.goto(url)
            time.sleep(1)
            element = page.query_selector("//*[@id='wb-auto-5']")
            if element and element.inner_text() == '':
                now = toronto_time()
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
                page.evaluate("(element) => element.remove()", pop)

            draw.screenshot(path='result.png')
            title = url
            body = '@everyone'
            config['round'] += 1
            break

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        apobj.notify(
            title=title,
            body=body,
            attach='result.png'
        )

        if os.path.exists("result.png"):
            os.remove("result.png")

        browser.close()

if __name__ == "__main__":
    main()
