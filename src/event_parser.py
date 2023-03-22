import requests
import numpy as np
import pandas as pd
from tqdm import tqdm
from dateutil import parser
from typing import Dict, Any
from bs4 import BeautifulSoup
from src.data_class import Links


class EventsParser(Links):

    def cooking_soup(self, url: str) -> Any:
        """
        Function create an object soup and return it.
        """
        r = requests.get(url=url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def get_all_event_data(self) -> pd.DataFrame:
        """
        The main body of the parser. Collects data of events fights.
        :return: raw dataframe
        """
        soup = self.cooking_soup(self.page_events)

        # Parse all events
        event_ls, parse_list = [], []
        events = [(row.find('span').text.strip(), row.find('a')['href'])
                  for row in soup.find_all('i', class_=self.cls_statistics)]

        # Parse all fights per events
        for event in tqdm(events, desc='Events parsed'):
            soup = self.cooking_soup(event[1])
            event_fights = [row['data-link']
                            for row in soup.find_all('tr', class_=self.cls_fight_details_tb)]
            event_ls.append([event[0], event[1], event_fights])

        # Main parser loop
        for event in tqdm(event_ls, desc='Fights per event parsed'):
            for fight in event[2]:
                try:
                    event_dict = {'date': event[0], 'event_url': event[1], 'event_fight': fight}
                    event_dict = self.get_event_info(event_dict, fight)
                    parse_list.append(event_dict)
                except:
                    pass

        # Raw dataframe
        data = pd.DataFrame(parse_list)
        data = data.replace('--', np.nan, regex=True)
        data['time'] = [parser.parse(time).time() for time in data['time']]
        data['date'] = [parser.parse(date) for date in data['date'] if type(date) == str]
        print('-----ALL FIGHTS EVENTS PARSED-----')
        return data

    def get_event_info(self, event_dict: Dict[str, str], url: str) -> Dict[str, str]:
        """
        This function collects information in the event header
        :param event_dict:
        :param url: url of fight event
        :return: updated dictionary
        """
        soup = self.cooking_soup(url)

        f1_status_fg = soup.find_all('div', class_=self.cls_fg_dt)[0]
        event_dict['f1_status_fg'] = f1_status_fg.text.replace('\n', '').strip().split(' ')[0]

        f2_status_fg = soup.find_all('div', class_=self.cls_fg_dt)[1]
        event_dict['f2_status_fg'] = f2_status_fg.text.replace('\n', '').strip().split(' ')[0]

        event_dict['f1_fullname'] = soup.find_all('a', class_=self.cls_person)[0].text.strip()
        event_dict['f2_fullname'] = soup.find_all('a', class_=self.cls_person)[1].text.strip()

        first_fighter_nick = soup.find_all('p', class_=self.cls_fight_details)[0].text.strip()
        event_dict['f1_nickname'] = first_fighter_nick.replace('"', '')

        second_fighter_nick = soup.find_all('p', class_=self.cls_fight_details)[1].text.strip()
        event_dict['f2_nickname'] = second_fighter_nick.replace('"', '')

        event_dict['win_method'] = soup.find_all('i', {'style': 'font-style: normal'})[0].text.strip()

        round_ = soup.find_all('i', class_=self.cls_text)[0].text
        event_dict['round'] = round_.replace('\n', '').replace('Round:', '').strip()

        time_ = soup.find_all('i', class_=self.cls_text)[1].text
        event_dict['time'] = time_.replace('\n', '').replace('Time:', '').strip()

        time_format_ = soup.find_all('i', class_=self.cls_text)[2].text
        event_dict['time_format'] = time_format_.replace('\n', '').replace('Time format:', '').strip()

        referee_ = soup.find_all('i', class_=self.cls_text)[3].text
        event_dict['referee'] = referee_.replace('\n', '').replace('Referee:', '').strip()

        data_block = soup.find_all('tr', class_='b-fight-details__table-row')

        event_dict = self.get_fight_info_per_rounds(event_dict, 1, data_block)
        event_dict = self.get_fight_info_per_rounds(event_dict, 2, data_block)

        land_trg_head = soup.find_all('div', class_=self.cls_charts)[0].text.strip()
        event_dict['f1_land_trg_head'] = land_trg_head.replace('\n', '').replace('   ', '').split(' ')[0]
        event_dict['f2_land_trg_head'] = land_trg_head.replace('\n', '').replace('   ', '').split(' ')[2]

        land_trg_body = soup.find_all('div', class_=self.cls_charts)[1].text.strip()
        event_dict['f1_land_trg_body'] = land_trg_body.replace('\n', '').replace('   ', '').split(' ')[0]
        event_dict['f2_land_trg_body'] = land_trg_body.replace('\n', '').replace('   ', '').split(' ')[2]

        land_trg_leg = soup.find_all('div', class_=self.cls_charts)[2].text.strip()
        event_dict['f1_land_trg_leg'] = land_trg_leg.replace('\n', '').replace('   ', '').split(' ')[0]
        event_dict['f2_land_trg_leg'] = land_trg_leg.replace('\n', '').replace('   ', '').split(' ')[2]

        land_trg_dist = soup.find_all('div', class_=self.cls_charts)[3].text.strip()
        event_dict['f1_land_trg_dist'] = land_trg_dist.replace('\n', '').replace('   ', '').split(' ')[0]
        event_dict['f2_land_trg_dist'] = land_trg_dist.replace('\n', '').replace('   ', '').split(' ')[2]

        land_trg_clinch = soup.find_all('div', class_=self.cls_charts)[4].text.strip()
        event_dict['f1_land_trg_clinch'] = land_trg_clinch.replace('\n', '').replace('   ', '').split(' ')[0]
        event_dict['f2_land_trg_clinch'] = land_trg_clinch.replace('\n', '').replace('   ', '').split(' ')[2]

        land_trg_ground = soup.find_all('div', class_=self.cls_charts)[5].text.strip()
        event_dict['f1_land_trg_ground'] = land_trg_ground.replace('\n', '').replace('   ', '').split(' ')[0]
        event_dict['f2_land_trg_ground'] = land_trg_ground.replace('\n', '').replace('   ', '').split(' ')[2]

        return event_dict

    def get_fight_info_per_rounds(self, event_dict: Dict[str, str], fg_num: int, data_block: Any) -> Dict[str, str]:
        """
        This function collects information on the central unit, taking into account the tables for each round
        :param event_dict: work dictionary
        :param fg_num: number of fighter 1 or 2
        :param data_block: block of bs4 soup
        :return: updated dictionary
        """
        event_rounds = int(event_dict['round'])
        sig_num = event_rounds + 4

        i = 0 if fg_num == 1 else 1

        # Total parameters
        event_dict[f'f{fg_num}_kd'] = self.return_block(data_block, 1, 2, i)
        event_dict[f'f{fg_num}_sig_str'] = self.return_block(data_block, 1, 4, i)
        event_dict[f'f{fg_num}_sig_str%'] = self.return_block(data_block, 1, 6, i)
        event_dict[f'f{fg_num}_total_str'] = self.return_block(data_block, 1, 8, i)
        event_dict[f'f{fg_num}_td'] = self.return_block(data_block, 1, 10, i)
        event_dict[f'f{fg_num}_td%'] = self.return_block(data_block, 1, 12, i)
        event_dict[f'f{fg_num}_sub.att'] = self.return_block(data_block, 1, 14, i)
        event_dict[f'f{fg_num}_rev'] = self.return_block(data_block, 1, 16, i)
        event_dict[f'f{fg_num}_ctrl'] = self.return_block(data_block, 1, 18, i)

        for rnd in range(1, event_rounds + 1):
            step = rnd + 2
            event_dict[f'f{fg_num}_rnd{rnd}_kd'] = self.return_block(data_block, step, 2, i)
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str'] = self.return_block(data_block, step, 4, i)
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str%'] = self.return_block(data_block, step, 6, i)
            event_dict[f'f{fg_num}_rnd{rnd}_total_str'] = self.return_block(data_block, step, 8, i)
            event_dict[f'f{fg_num}_rnd{rnd}_td'] = self.return_block(data_block, step, 10, i)
            event_dict[f'f{fg_num}_rnd{rnd}_td%'] = self.return_block(data_block, step, 12, i)
            event_dict[f'f{fg_num}_rnd{rnd}_sub.att'] = self.return_block(data_block, step, 14, i)
            event_dict[f'f{fg_num}_rnd{rnd}_rev'] = self.return_block(data_block, step, 16, i)
            event_dict[f'f{fg_num}_rnd{rnd}_ctrl'] = self.return_block(data_block, step, 18, i)

        for rnd in range(int(event_dict['round']) + 1, self.num_rounds + 1):
            event_dict[f'f{fg_num}_rnd{rnd}_kd'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str%'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_total_str'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_td'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_td%'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_sub.att'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_rev'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_ctrl'] = '---'

        event_dict[f'f{fg_num}_sig_str_head'] = self.return_block(data_block, sig_num, 6, i)
        event_dict[f'f{fg_num}_sig_str_body'] = self.return_block(data_block, sig_num, 8, i)
        event_dict[f'f{fg_num}_sig_str_leg'] = self.return_block(data_block, sig_num, 10, i)
        event_dict[f'f{fg_num}_sig_str_dist'] = self.return_block(data_block, sig_num, 12, i)
        event_dict[f'f{fg_num}_sig_str_clinch'] = self.return_block(data_block, sig_num, 14, i)
        event_dict[f'f{fg_num}_sig_str_ground'] = self.return_block(data_block, sig_num, 16, i)

        for rnd in range(1, event_rounds + 1):
            step = sig_num + rnd + 1
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_head'] = self.return_block(data_block, step, 6, i)
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_body'] = self.return_block(data_block, step, 8, i)
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_leg'] = self.return_block(data_block, step, 10, i)
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_dist'] = self.return_block(data_block, step, 12, i)
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_clinch'] = self.return_block(data_block, step, 14, i)
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_ground'] = self.return_block(data_block, step, 16, i)

        for rnd in range(int(event_dict['round']) + 1, self.num_rounds + 1):
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_head'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_body'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_leg'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_dist'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_clinch'] = '---'
            event_dict[f'f{fg_num}_rnd{rnd}_sig_str_ground'] = '---'

        return event_dict

    def return_block(self, data_block: Any, num: int, ind: int, i: int) -> str:
        """
        Standard block for information output
        :param data_block: block of bs4 soup
        :param num: step parameter
        :param ind: index of information block
        :param i: number of fighter
        :return: result information
        """
        string = data_block[num].find_all('p', class_=self.cls)[ind+i].text.strip()
        return string
