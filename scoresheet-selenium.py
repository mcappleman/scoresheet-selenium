import pandas as pd
import json
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def main(argv):
    """
    Write the Projected best lineup
    """

    driver = webdriver.Chrome()
    env = load_env('environment.json')

    # Do Stuff Here
    download_csv(driver, env)

    driver.close()


def load_env(json_env_path):
    env = {}
    with open(json_env_path) as json_file:
        env = json.load(json_file)

    return env


def download_csv(driver, env):
    driver.get(env['CSV_URL'])
    csv_elem = driver.find_element_by_xpath('/html/body/div/font/big/b/a[1]')
    csv_elem.click()


if __name__ == "__main__":
    main(sys.argv[1:])