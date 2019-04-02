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
        players = pd.read_csv(env['DOWNLOAD_PATH'], encoding="ISO-8859-1")
        final_df = scrape_pages(driver, env, players)
        final_df.to_csv('players.csv', Index=False)
    except CSVDownloadError as e:
        print(e)
        print('Unable to Download the CSV')
    except UnicodeDecodeError as e:
        print(e)
        print('UnicodeDecodeError')
    except Exception as e:
        print(e)
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
    max_attempt = 60
    while not csv_file.is_file():
        if attempt > max_attempt:
            raise CSVDownloadError()
        time.sleep(1)
        attempt += 1


def scrape_pages(driver, env, players):
    final_list = []
    player_template = {
        'name': '',
        'position': '',
        'mlb_team': '',
        'throws': '',
        'bats': '',
        'espn_id': '',
        'bref_id': '',
        'fg_id': '',
        'last_seven_ba': '',
        'last_seven_obp': '',
        'last_seven_slg': '',
        'last_seven_ops': '',
        'last_seven_era': '',
        'last_seven_ip': '',
        'last_seven_so': '',
        'last_seven_bb': '',
    }
    for i, player in players.iterrows():
        if player['espn_id'] != '':
            current_player = player_template.copy()
            current_player['name'] = player['espn_name']
            current_player['position'] = player['espn_pos']
            current_player['mlb_team'] = player['mlb_team']
            current_player['throws'] = player['throws']
            current_player['bats'] = player['bats']
            current_player['espn_id'] = str(int(player['espn_id']))
            current_player['bref_id'] = player['bref_id']

            espn_url = env['ESPN_URL'] + current_player['espn_id']
            br_url = env['BR_URL'] + current_player['bref_id']
            driver.get(espn_url)
            tr_xpath_start = '//*[@id="content"]/div[6]/div[1]/div/div[2]/div[2]/div/table/tbody/tr'
            table_rows = driver.find_elements_by_xpath(tr_xpath_start)

            for row in table_rows:
                row_title = row.find_element_by_xpath('.//td[1]').text
                if row_title == 'Last 7 Days':
                    if current_player['position'] != 'RP' and current_player['position'] != 'SP':
                        current_player['last_seven_ba'] = row.find_element_by_xpath('.//td[14]').text
                        current_player['last_seven_obp'] = row.find_element_by_xpath('.//td[15]').text
                        current_player['last_seven_slg'] = row.find_element_by_xpath('.//td[16]').text
                        current_player['last_seven_ops'] = row.find_element_by_xpath('.//td[17]').text
                    else:
                        current_player['last_seven_era'] = row.find_element_by_xpath('.//td[2]').text
                        current_player['last_seven_ip'] = row.find_element_by_xpath('.//td[10]').text
                        current_player['last_seven_so'] = row.find_element_by_xpath('.//td[16]').text
                        current_player['last_seven_bb'] = row.find_element_by_xpath('.//td[15]').text

            final_list.append(current_player)
            

    final_df = pd.DataFrame(final_list)
    return final_df


if __name__ == "__main__":
    main(sys.argv[1:])