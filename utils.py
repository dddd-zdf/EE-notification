import os
import json
from datetime import datetime
import pytz
import apprise


def get_cwd():
    return os.path.dirname(os.path.abspath(__file__))

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def is_ee_day(example_date):
    today = datetime.today().date()
    if today.weekday() in [0, 3, 4]:
        return False
    day_difference = (today - example_date).days
    return (day_difference // 7) % 2 == 0

def toronto_time():
    toronto_tz = pytz.timezone('America/Toronto')
    utc_now = datetime.now(pytz.utc)
    return utc_now.astimezone(toronto_tz)

def setup_notification(discord_url):
    apobj = apprise.Apprise()
    apobj.add('discord://' + discord_url)
    return apobj

