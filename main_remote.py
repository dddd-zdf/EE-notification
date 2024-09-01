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

    discord, interval, url, crs = config['discord'], config['interval'] * 60, config['url_base'] + str(config['round']), config['CRS']

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

            # retry go to page
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
                    body = 'no draw today'
                    break
            draw = {
                'class': page.locator("#wb-auto-6").inner_text(),
                'cut_off': int(cut_off.inner_text()),
                'tie_breaking': page.locator("#wb-auto-11").inner_text()
            }

            result = ''

            if (any(match in draw['class'] for match in config['category'])):
                if draw['cut_off'] < crs or (draw['cut_off'] == crs and datetime.strptime(config['submitted'], "%Y-%m-%d %H:%M %Z") <= datetime.strptime(draw['tie_breaking'], "%B %d, %Y at %H:%M:%S %Z")):
                    result = 'YYYYYYYYYYYYYYYYYYYYES@everyone'
                else:
                    result = 'NOOOOOOOOOOOOOOOOOOOOO'
            else:
                result = 'NOT YOUR DRAW!'

            body = f"""
{result}
{draw['class']}
{draw['cut_off']}
{draw['tie_breaking']}
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
