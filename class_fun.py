from typing import Tuple, List

import requests
from bs4 import BeautifulSoup

import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class StageResults:
    """
    Класс результатов этапа, содержит счета и команды каждого этапа плей-офф
    """

    def __init__(self, link: str, stage: str) -> None:

        self.__link = link
        self.__stage = stage

    def get_result(self) -> List[List[str]]:
        """
        Получаем команды и голы с сайта уефа

        :return: список с командами и их голами на этапе
        """

        stage_link = self.__link + self.__stage

        match_page = BeautifulSoup(requests.get(stage_link).text, features='lxml')
        teams = match_page.find_all('span', {'class': 'js-fitty'})
        home_score_page = match_page.find_all('span', {'class': 'js-team--home-score home-score'})
        away_score_page = match_page.find_all('span', {'class': 'js-team--away-score away-score'})

        penalties = [match.find('span', {'class': 'js-penalty-score penalty-score'})
                     for match in match_page.find_all('a', {'class': 'match-row_link'})]

        pen_winners = ['' if penalty.contents == [] else str(1) if penalty.contents[0][1:-1].split('-')[0] >
                                                                   penalty.contents[0][1:-1].split('-')[0]
                                                                   else str(2) for penalty in penalties]

        home_team = []
        home_score = []
        away_team = []
        away_score = []

        for i in range(len(teams)):
            home_team.append(teams[i].contents[0].strip()) if i % 2 == 0 else away_team.append(
                teams[i].contents[0].strip())
            if i < len(teams) / 2 and len(home_score_page[i].contents) > 0:
                home_score.append(home_score_page[i].contents[0])
                away_score.append(away_score_page[i].contents[0])
            elif i < len(teams) / 2:
                home_score.append('')
                away_score.append('')

        return [home_team, home_score, away_score, away_team, pen_winners]


class GoogleSheet:
    """
    Класс позволяет получить данные с листа и записать данные на лист
    """

    def __init__(self, spreadsheet_id) -> None:

        self.__spreadsheet_id = spreadsheet_id

    def get_creds(self) -> Credentials:

        """
        Проверяет правильные ли данные для авторизации и схораняет на будущее

        :return: параметры авторизации для подключения к гугл доку
        """
        creds = None

        scopes = ['https://www.googleapis.com/auth/spreadsheets']

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds

    def get_values(self, table_range: str) -> list:
        """
        Функция позволяет получить данные из гугл дока

        :param table_range: диапазон получаемых значений
        :return: сами значения
        """
        service = build('sheets', 'v4', credentials=self.get_creds())

        sheet = service.spreadsheets().values()
        result = sheet.get(spreadsheetId=self.__spreadsheet_id, range=table_range).execute()
        values = result.get('values', [])

        return values

    def set_values(self, table_range: str, values: List[List[str]]) -> None:
        """
        Функция записывает данные в табличку

        :param table_range: диапазон, в который записываются значения
        :param values: значения, записываемые в диапазон
        :return: ничего не возвращает, просто записывает в табличку
        """

        service = build('sheets', 'v4', credentials=self.get_creds())

        service.spreadsheets().values().batchUpdate(spreadsheetId=self.__spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",  # Данные воспринимаются, как вводимые пользователем
            "data": [
                {"range": table_range,
                 "majorDimension": "COLUMNS",  # Сначала заполнять столбцы, затем строки
                 "values": values  # Заполняем столбцы
                 }
            ]
        }).execute()


def blank_insert(list_example: List[List[str]]) -> None:
    """
    Функция получает список и возвращает его же, только с лишними пустыми элементами (для упрощения заполнения)

    :param list_example: любой список из 4 списков
    :return: ничего не возвращает, меняет исходный список
    """

    for i in range((len(list_example[0]) - 1) * 4 - 1):
        if i % 4 == 0:
            for j in range(4):
                list_example[j].insert(i + 1, '')
                list_example[j].insert(i + 2, '')
                list_example[j].insert(i + 3, '')
