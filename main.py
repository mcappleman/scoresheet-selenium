import pandas as pd
import json
import sys
import time
import os

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from classes.exceptions import CSVDownloadError


def main(argv):
    """
    Write the Projected best lineup
    """

    driver = webdriver.Chrome()
    env = load_env('environment.json')

    # Do Stuff Here
    try:
        download_csv(driver, env)
    except CSVDownloadError:
        print('Unable to Download the CSV')
    except:
        print('Another error happened somewhere')

    driver.close()


def load_env(json_env_path):
    env = {}
    with open(json_env_path) as json_file:
        env = json.load(json_file)

    csv_file = Path(env['DOWNLOAD_PATH'])
    if csv_file.is_file():
        os.remove(env['DOWNLOAD_PATH'])
    
    return env


def download_csv(driver, env):
    driver.get(env['CSV_URL'])
    csv_elem = driver.find_element_by_xpath('/html/body/div/font/big/b/a[1]')
    csv_elem.click()
    
    csv_file = Path(env['DOWNLOAD_PATH'])
    attempt = 0
    max_attempt = 15
    while not csv_file.is_file():
        if attempt > max_attempt:
            raise CSVDownloadError()
        time.sleep(10)
        attempt += 1


if __name__ == "__main__":
    main(sys.argv[1:])