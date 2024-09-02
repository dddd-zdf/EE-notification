import time
from utils import get_cwd, load_config, toronto_time, is_ee_day, setup_notification
from scraper import scrape_page
from datetime import datetime
import json
import os

def main():
    cwd = get_cwd()
    config_path = os.path.join(cwd, 'config.json')
    config = load_config(config_path)
    
    discord = config['discord']
    interval = config['interval'] * 60
    url = config['url_base'] + str(config['round'])
    crs = config['CRS']
    category = config['category']
    submitted = datetime.strptime(config['submitted'], "%Y-%m-%d %H:%M %Z")
    anchor_draw_date = datetime.strptime(config['anchor_draw_date'], "%Y-%m-%d")
    
    now = toronto_time()

    # wait til 12pm
    if now.hour < 12:
        target_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
        time_to_wait = (target_time - now).total_seconds()
        time.sleep(time_to_wait)
    
    # get the result
    draw = scrape_page(url, interval)
    draw_text = ''
    # if no draw
    if not draw:
        # if on an EE day, notify
        if is_ee_day(anchor_draw_date):
            title = 'no draw today'
            url = ''
        # if there is no draw and its not an EE day, dont send anything
        else:
            return
        
    # if there is a draw today
    else:
        config['round'] += 1
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        draw_text = f"""
{draw['class']}
{draw['cut_off']}
{draw['tie_breaking']}
"""
        # if im in the class
        if any(match in draw['class'] for match in category):
            # if im getting an ITA
            if draw['cut_off'] < crs or (draw['cut_off'] == crs and submitted <= datetime.strptime(draw['tie_breaking'], "%B %d, %Y at %H:%M:%S %Z")):
                title =  'YYYYYYYYYYYYYYYYYYYYES@everyone\n'
            # i missed it
            else:
                title = 'NOOOOOOOOOOOOOOOOOOOOO\n'
        # if im not in the class
        else:
            title =  'NOT YOUR DRAW!\n'
    
    # if text being set in body, send notification
    body = f"""
{title}{draw_text}\n{url}"""
    apobj = setup_notification(discord)
    apobj.notify(body=body)

if __name__ == "__main__":
    main()
