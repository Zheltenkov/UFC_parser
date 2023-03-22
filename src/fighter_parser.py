import requests
import datetime
import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from collections import Counter
from src.data_class import Links
from typing import Any, List, Dict


class FighterParser(Links):

    def cooking_soup(self, url: str) -> Any:
        """
        Function create an object soup and return it.
        """
        r = requests.get(url=url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def get_events_links(self) -> List[str]:
        """
        This method gets a list of fighters and parses the list. In its body it uses the get_fighter_params method
        to collect more detailed data on the fighter. Result DataFrame automatically saved in directory data.
        """
        soup = self.cooking_soup(self.page_events)
        events_list = [row.find('a')['href'] for row in soup.find_all('i', class_=self.cls_statistics)]

        return events_list

    def get_fighters_links(self) -> Dict[str, str]:
        """
        This function creates a dictionary with the value of the fighter's name and a link to his statistics
        :return: dictionary
        """
        fighters_dict = {self.data_check(block)[0]: self.data_check(block)[1] for event_link in self.get_events_links()
                         for block in self.cooking_soup(event_link).find_all('a', class_=self.cls_style)}

        return fighters_dict

    def get_fighters_params(self) -> pd.DataFrame:
        """
        The main body of the parser. Collects data on the fighter's stats.
        :return: raw dataframe
        """
        values_list, params_name = [], []
        links = self.get_fighters_links()

        for fighter_url in tqdm(links.items(), desc='Fighters parsed'):
            if type(fighter_url[1]) == str:
                soup = self.cooking_soup(fighter_url[1])

                fighter_params = soup.find_all('li', class_=self.cls_box_list_item)
                fighter_status = soup.find_all('i', class_=self.cls_flag)

                # Don't consider upcoming fights
                dict_status = Counter([fight.text for fight in fighter_status])
                del dict_status['next']

                if not params_name:
                    params_name = [param.text.strip().replace(' ', '').replace('\n', '').split(':')[0]
                                   for param in fighter_params
                                   if len(param.text.strip().replace(' ', '').replace('\n', '').split(':')) > 1]

                    params_name = ['Fullname', 'Win', 'Loss', 'Draw'] + params_name

                # Get main fighter parameters
                values = [param.text.strip().replace(' ', '').replace('\n', '').split(':')[1]
                          for param in fighter_params
                          if len(param.text.strip().replace(' ', '').replace('\n', '').split(':')) > 1]

                # Assemble the resulting parameter sheet
                values = [fighter_url[0], dict_status['win'], dict_status['loss'], dict_status['draw']] + values
                values_list.append(values)

        # Raw dataframe
        data = pd.DataFrame(values_list, columns=params_name)
        print('-----ALL FIGHTERS PARSED-----')
        return data

    def get_fighter_data(self) -> pd.DataFrame:
        """
        This function converts the raw dataset to a convenient form for analysis
        :return: prepared fighter dataset
        """
        fighters = self.get_fighters_params()

        fighters = fighters.replace('--', np.nan, regex=True)

        fighters['Height'] = [round(int(str(height).replace("'", " ").replace('"', '').split(' ')[0]) * 30.48 +
                                    int(str(height).replace("'", " ").replace('"', '').split(' ')[1]) * 2.54, 1)
                              if type(height) != float else np.nan for height in fighters['Height']]

        fighters['Weight'] = [round(int(str(weight).replace('lbs.', '').strip()) * 0.453592, 1)
                              if type(weight) == str else np.nan for weight in fighters['Weight']]

        fighters['Reach'] = [round(int(str(reach).replace('"', '').strip()) * 2.54, 1)
                             if type(reach) == str else np.nan for reach in fighters['Reach']]

        fighters['Age'] = [datetime.date.today().year - int(dob.split(',')[1])
                           if type(dob) == str else np.nan for dob in fighters['DOB']]

        fighters['Str.Acc.'] = [int(str(val).replace('%', '').strip())
                                if type(val) == str else np.nan for val in fighters['Str.Acc.']]

        fighters['Str.Def'] = [int(str(val).replace('%', '').strip())
                               if type(val) == str else np.nan for val in fighters['Str.Def']]

        fighters['TDAcc.'] = [int(str(val).replace('%', '').strip())
                              if type(val) == str else np.nan for val in fighters['TDAcc.']]

        fighters['TDDef.'] = [int(str(val).replace('%', '').strip())
                              if type(val) == str else np.nan for val in fighters['TDDef.']]

        fighters = fighters.drop(columns=['DOB'], axis=1)

        fighters = fighters[['Fullname', 'Win', 'Loss', 'Draw', 'Age', 'Height', 'Weight', 'Reach', 'STANCE', 'SLpM',
                             'Str.Acc.', 'SApM', 'Str.Def', 'TDAvg.', 'TDAcc.', 'TDDef.', 'Sub.Avg.']]

        fighters.columns = ['Fullname', 'Win', 'Loss', 'Draw', 'Age', 'Height', 'Weight', 'Reach', 'Stance', 'SLpM',
                            'Str.Acc.%', 'SApM', 'Str.Def%', 'TDAvg.', 'TDAcc.%', 'TDDef.%', 'Sub.Avg.']

        return fighters

    @staticmethod
    def data_check(block: Any) -> List[str]:
        """
        :param block:
        :return: list consist with fighter name and actual link
        """
        fighter_name, fighter_link = None, None
        try:
            fighter_name, fighter_link = block.text.strip(), block['href']
        except KeyError:
            pass

        return [fighter_name, fighter_link]

