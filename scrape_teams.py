import json
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

LEAGUES = [
    'wBL600'
    ]

my_league = 'wBL600'

player_dict = {}
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(options=options)

for league in LEAGUES:
    url = 'http://www.scoresheet.com/htm-lib/picks.htm?dir_lgw=/FOR_WWW1/' + league + ';all'
    driver.get(url)
    elem = driver.find_element_by_id('msgs')
    
    regex = r"^Team\s*(?P<team_id>[0-9]*)\s*\((?P<team_name>.*)\).*drafted\s(?P<player_id>[0-9]*)\s*(?P<player_team>[A-Za-z-]*)\s*(?P<player_position>[A-Za-z0-9]*)\s*(?P<player_name>[A-Za-z\S]*\s[A-Za-z\S]*)"
    matches = re.finditer(regex, elem.text, re.MULTILINE)
    
    for match_num, match in enumerate(matches, start=1):
        current_player = {
            'name': match.group('player_name'),
            'position': match.group('player_position'),
            'team': match.group('player_team')
            }
        player_id = match.group('player_id')
        team_id = match.group('team_id')

        if player_dict.get(current_player['name']) is None:
            player_dict[current_player['name']] = int(team_id)
        else:
            print(current_player['name'] + ", " + player_id)

driver.close()

with open('team_rosters.json', 'w') as fp:
    json.dump(player_dict, fp)