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
    return datetime.now()


def main():
    with open(config_path, 'r') as f:
        config = json.load(f)

    discord, interval, url = config['discord'], config['interval'], config['url_base'] + str(config['round'])

    now = toronto_time()

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
            tie = page.query_selector("//*[@id='wb-auto-11']")
            if tie and tie.inner_text() == '':
                now = toronto_time()
                if now.hour < 16:
                    time.sleep(interval)
                    continue
                else:
                    body = 'no draw today'
                    break

            draw = {
                'class': page.query_selector("//*[@id='wb-auto-6']").inner_text(),
                'cut-off': page.query_selector("//*[@id='wb-auto-10']").inner_text(),
                'tie-breaking': tie.inner_text()
            }


            body = f"""
@everyone
{draw['class']}
{draw['cut-off']}
{draw['tie-breaking']}
{url}
            """

            config['round'] += 1
            break

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        apobj.notify(
            body=body
        )

        browser.close()

if __name__ == "__main__":
    main()
