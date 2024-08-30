from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import apprise
import json


with open('config.json', 'r') as f:
    config = json.load(f)

discord, interval, url = config['discord'], config['interval'] * 60, config['url_base'] + str(config['round'])


apobj = apprise.Apprise()
apobj.add('discord://' + discord)

driver = webdriver.Chrome()

while True:
    driver.get(url)
    time.sleep(3)
    element = driver.find_element(By.XPATH, "//*[@id='wb-auto-5']")
    if element.text == '':
        now = datetime.now()
        if now.hour < 16:
            time.sleep(interval)
            continue
        else:
            body = 'no draw today'
            break
    draw = driver.find_element(By.CLASS_NAME, 'well')

    try:
        pop = driver.find_element(By.ID, 'gc-im-popup')
        driver.execute_script("arguments[0].style.display = 'none';", pop) 
    except:
        pass


    draw.screenshot('result.png')
    body = url
    config['round'] += 1
    break

with open('config.json', 'w') as f:
    json.dump(config, f, indent=4)


apobj.notify(
    body = body,
    attach='result.png'
)

import os
if os.path.exists("result.png"):
  os.remove("result.png")


driver.quit()