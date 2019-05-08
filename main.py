import pandas as pd
import json
import math
import sys
import time
import os

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from classes.exceptions import CSVDownloadError
from classes.player import Player

TRANSLATIONS = {
    "Daniel Robertson": "DanielRay Robertson(TB)",
    "Jackie Bradley Jr.": "Jackie Bradley",
    "Jose Ramirez": "Jose Ramirez(Cle)",
    "Ronald Acuna Jr.": "Ronald Acuna",
    "Vladimir Guerrero Jr.": "VladimirJr. Guerrero",
    "Carlos Martinez": "Carlos(Matias) Martinez(StL)",
    "Felipe Rivero": "Felipe Vazquez",
    "Josh Bell": "Josh Bell(Pit)",
    "Enrique Hernandez": "Kike Hernandez",
    "Ryan Braun": "Ryan Braun(Mil)",
    "Michael Fulmer": "Michael(out/2019) Fulmer",
    "Amed Rosario": "Amed(German) Rosario",
    "Will Smith": "Will Smith(SF)",
    "Lourdes Gurriel Jr.": "Lourdes Gurriel",
    "Danny Salazar": "Danny(hurt) Salazar",
    "Will Harris": "Will Harris(Hou)",
    "Matt Duffy": "Matt Duffy(TB)",
    "Steven Souza Jr.": "Steven Souza",
    "Fernando Tatis Jr.": "Fernando Tatis",
    "Christin Stewart": "Christin Stewart(Det)",
    "Daniel Ponce de Leon": "Daniel Poncedeleon",
    "Seunghwan Oh": "SeungHwan Oh",
    "Carl Edwards Jr.": "Carl Edwards",
    "Didi Gregorius": "Didi(hurt) Gregorius",
    "Michael A. Taylor": "MichaelA. Taylor",
    "JaCoby Jones": "Jacoby Jones",
    "Jung Ho Kang": "JungHo Kang",
    "Cam Gallagher": "Cameron Gallagher",
    "Phil Ervin": "Phillip Ervin",
    "Sean Manaea": "Sean(hurt) Manaea",
    "Yoenis Cespedes": "Yoenis(hurt) Cespedes",
    "Dwight Smith Jr.": "Dwight Smith",
    "Luis Garcia": "Luis Garcia(LAA)"
}

TRADES = {
    "Teoscar Hernandez": 12
}

MISSING_BREF = {
    "Oscar Mercado": {},
    "Brent Honeywell": {},
    "Dylan Cease": {},
    "Mitch Keller": {}
}

TEAM_ROSTER_NAMES_FOUND = {}

def main(argv):
    """
    Write the Projected best lineup
    """

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')
    headless_driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome()
    env = load_env('environment.json')

    team_rosters = {}
    with open('team_rosters.json') as json_file:
        team_rosters = json.load(json_file)

    # Do Stuff Here
    try:
        download_csv(driver, env)
        driver.close()

        print('CSV Download Complete')
        players = pd.read_csv(env['DOWNLOAD_PATH'], encoding="ISO-8859-1")

        print('Begin Scraping')
        final_lists = scrape_pages(headless_driver, env, team_rosters, players)

        batter_df = pd.DataFrame(final_lists['batter_list'])
        pitcher_df = pd.DataFrame(final_lists['pitcher_list'])

        column_order_start = ['name', 'position', 'team_number', 'mlb_team', 'throws', 'bats']
        key_start_columns = ['last_seven', 'last_15', 'last_30', 'vs_left', 'vs_right']
        # sites = ['ESPN', 'BR']
        sites = ['BR']
        batter_stats = ['ba', 'obp', 'slg', 'ops']
        pitcher_stats = ['era', 'ip', 'so', 'bb', 'ba', 'obp', 'slg', 'ops']
        column_batters = get_column_order(column_order_start, key_start_columns, sites, batter_stats)
        column_pitchers = get_column_order(column_order_start, key_start_columns, sites, pitcher_stats)

        batter_df.to_csv('batters.csv', index=False, columns=column_batters)
        pitcher_df.to_csv('pitchers.csv', index=False, columns=column_pitchers)
        print('\n\nCompleted Successfully!!!\n\n')

        check_all_players_found(team_rosters)
    except CSVDownloadError as e:
        print(e)
        print('Unable to Download the CSV')
    except UnicodeDecodeError as e:
        print(e)
        print('UnicodeDecodeError')
    except Exception as e:
        print(e)
        print('Another error happened somewhere')

    headless_driver.close()


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


def scrape_pages(driver, env, team_rosters, players):
    pitcher_list = []
    batter_list = []
    for i, player in players.iterrows():
        my_player = env['MY_PLAYERS'].get(player['espn_name'])
        team_id = team_rosters.get(player['bref_name'])

        if player['bref_id'] == '':
            continue

        if team_id is not None:
            player['team_id'] = team_id
            TEAM_ROSTER_NAMES_FOUND[player['bref_name']] = True
        elif TRANSLATIONS.get(player['bref_name']) is not None:
            translation = TRANSLATIONS.get(player['bref_name'])
            team_id = team_rosters.get(translation)
            player['team_id'] = team_id
            TEAM_ROSTER_NAMES_FOUND[translation] = True
        else:
            continue

        if TRADES.get(player['bref_name']) is not None:
            team_id = TRADES.get(player['bref_name'])

        #if team_id != 8:
        #    continue

        print('Scraping Player: ' + player['bref_name'] + ' index: ' + str(i) + '\n\n')

        current_player = Player(player)
        if my_player is not None:
            current_player.mine = True

        # Baseball Reference
        br_url = env['BR_URL'] + current_player.bref_id
        if not current_player.batter:
            br_url = br_url + '&t=p'

        driver.get(br_url)
        tr_xpath_start = '//*[@id="total"]/tbody/tr'
        current_player = get_stats(driver, 'BR', tr_xpath_start, './/th[1]', current_player)
        tr_xpath_start = '//*[@id="plato"]/tbody/tr'
        current_player = get_stats(driver, 'BR', tr_xpath_start, './/th[1]', current_player)
        if not current_player.batter:
            tr_xpath_start = '//*[@id="total_extra"]/tbody/tr'
            current_player = get_stats(driver, 'BR', tr_xpath_start, './/th[1]', current_player)

        if current_player.batter:
            batter_list.append(current_player.to_dict())
        else:
            pitcher_list.append(current_player.to_dict())
            
    
    return {
        'batter_list': batter_list,
        'pitcher_list': pitcher_list,
    }


def get_column_order(start, keys, sites, stats):
    column_order = start.copy()
    for key in keys:
        for site in sites:
            for stat in stats:
                column_order.append(key + '_' + site + '_' + stat)

    return column_order


def get_stats(driver, site, xpath_start, title_xpath, current_player):
    
    table_rows = driver.find_elements_by_xpath(xpath_start)

    for row in table_rows:
        row_title = row.find_element_by_xpath(title_xpath).text.lower()
        if row_title == 'Last 7 Days'.lower():
            current_player.get_stats(row, 'last_seven', site)
        elif row_title == 'Last 15 Days'.lower() or row_title == 'Last 14 days'.lower():
            current_player.get_stats(row, 'last_15', site)
        elif row_title == 'Last 30 Days'.lower() or row_title == 'Last 28 days'.lower():
            current_player.get_stats(row, 'last_30', site)
        elif row_title == 'vs. Left'.lower() or row_title == 'vs LHP'.lower() or row_title == 'vs LHB'.lower():
            current_player.get_stats(row, 'vs_left', site)
        elif row_title == 'vs. Right'.lower() or row_title == 'vs RHP'.lower() or row_title == 'vs RHB'.lower():
            current_player.get_stats(row, 'vs_right', site)

    return current_player


def check_all_players_found(team_rosters):
    print('\n\nNot Found Players')
    for key, value in team_rosters.items():
        if TEAM_ROSTER_NAMES_FOUND.get(key) is None:
            print(key + ", Team " + str(value))



if __name__ == "__main__":
    main(sys.argv[1:])