class Player():

    def __init__(self, player):
        self.name = player['espn_name']
        self.position = player['espn_pos']
        self.mlb_team = player['mlb_team']
        self.throws = player['throws']
        self.bats = player['bats']
        self.espn_id = str(int(player['espn_id']))
        self.bref_id = player['bref_id']
        self.fg_id = ''
        self.mine = False
        self.batter = self.position != 'RP' and self.position != 'SP'
        self.stats = {}


    def to_dict(self):
        mine = ''
        if self.mine:
            mine = 'x'
        player_dict = {
            'name': self.name,
            'position': self.position,
            'mlb_team': self.mlb_team,
            'throws': self.throws,
            'bats': self.bats,
            'espn_id': self.espn_id,
            'bref_id': self.bref_id,
            'fg_id': self.fg_id,
            'mine': mine
        }

        for key, value in self.stats.items():
            player_dict[key] = value

        return player_dict


    def get_stats(self, row, key_start, site):
        key = key_start + "_" + site
        if site == 'ESPN':
            self.get_espn_stats(row, key)
        elif site == 'BR':
            self.get_br_stats(row, key)


    def get_br_stats(self, row, key_start):
        try:
            self.stats[key_start + '_ba'] = row.find_element_by_xpath('.//td[@data-stat="batting_avg"]').text
            self.stats[key_start + '_obp'] = row.find_element_by_xpath('.//td[@data-stat="onbase_perc"]').text
            self.stats[key_start + '_slg'] = row.find_element_by_xpath('.//td[@data-stat="slugging_perc"]').text
            self.stats[key_start + '_ops'] = row.find_element_by_xpath('.//td[@data-stat="onbase_plus_slugging"]').text
        except Exception:
            self.stats[key_start + '_era'] = row.find_element_by_xpath('.//td[@data-stat="earned_run_avg"]').text
            self.stats[key_start + '_ip'] = row.find_element_by_xpath('.//td[@data-stat="IP"]').text
            self.stats[key_start + '_so'] = row.find_element_by_xpath('.//td[@data-stat="SO"]').text
            self.stats[key_start + '_bb'] = row.find_element_by_xpath('.//td[@data-stat="BB"]').text


    def get_espn_stats(self, row, key_start):
        if self.batter:
            self.get_espn_batter_stats(row, key_start)
        else:
            self.get_espn_pitcher_stats(row, key_start)


    def get_espn_batter_stats(self, row, key_start):
        self.stats[key_start + '_ba'] = row.find_element_by_xpath('.//td[14]').text
        self.stats[key_start + '_obp'] = row.find_element_by_xpath('.//td[15]').text
        self.stats[key_start + '_slg'] = row.find_element_by_xpath('.//td[16]').text
        self.stats[key_start + '_ops'] = row.find_element_by_xpath('.//td[17]').text


    def get_espn_pitcher_stats(self, row, key_start):
        self.stats[key_start + '_era'] = row.find_element_by_xpath('.//td[2]').text
        self.stats[key_start + '_ip'] = row.find_element_by_xpath('.//td[10]').text
        self.stats[key_start + '_so'] = row.find_element_by_xpath('.//td[16]').text
        self.stats[key_start + '_bb'] = row.find_element_by_xpath('.//td[15]').text