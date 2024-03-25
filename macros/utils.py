import datetime
import os
import json
import logging
import httplib2
from typing import Optional
from dataclasses import dataclass
from pyzabbix import ZabbixAPI
from calendar import monthrange
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel
from redis import Redis

from .get_region_data import get_regions


def rearrange_dicts(original_list):
    rearranged_list = []
    for item in original_list:
        rearranged_item = {
            "name": item["name"],
            "start": item.get("{$BILLING.START.DATE}", '-'),
            "end": item.get("{$BILLING.END.DATE}", "-"),
            "proc": item.get("{$BILLING.PROC.PERIOD}", "-"),
            "speed": item.get("{$BILLING.SPEED.PERIOD}", '-'),
            "error": item.get("{$BILLING.ERROR.CALC.PERIOD}", '-')
        }
        rearranged_list.append(rearranged_item)
    return rearranged_list


def serialize(hosts: list[str | dict[str, str]]) -> list:
    result: list[dict[str, str]] = []
    example = [
        '{$BILLING.END.DATE}', '{$BILLING.START.DATE}', '{$BILLING.ERROR.CALC.PERIOD}',
        '{$BILLING.PROC.PERIOD}', '{$BILLING.SPEED.PERIOD}', ]

    for host in hosts:
        inner = {}
        inner["name"] = host["name"]
        for macro in host['macros']:
            if macro['macro'] in example:
                inner.setdefault(macro["macro"], macro["value"])
            else:
                continue
        result.append(inner)


    return rearrange_dicts(result)


class Cache:
    '''Выполняется подключение к хранилищу Redis'''

    def __init__(self):
        self.redis = Redis(host='redis', db=1)


@dataclass
class ZabbixConfig:
    login = os.environ.get("ZABBIX_LOGIN")
    password = os.environ.get("ZABBIX_PASS")



def validate_date(start: datetime, end: datetime) -> bool:
    if start < end:
        return True
    else:
        return False


def validate_month(start: str, end: str) -> bool:
    """

    ----
    Args:
        start: дата начала
        end: дата окончания
    ----

    Returns:
        True - если время валидное, в противном случае вернет False

    """
    if start < end or (start == '12' and end == '01'):
        return True
    return False


class Region(BaseModel):
    """

    Класс для сериализации данных

    ----
    Атрибуты:
        hostid: строка или список с id хостов (в случае с регионами типо Татарстан)
        data: префиксы и часы снятия реестров для каждого региона
    ----

    """
    hostid: str | list[str, ]
    data: Optional[dict]


def get_date(start: str, end: str) -> (datetime, datetime):
    """
    ----
    Args:
        start: дата начала в виде строки
        end: дата конца в виде строки
    ----

    Returns:
        Возращает обьект даты для последующего форматирования и работы
    """
    _start = datetime.datetime.strptime(start.replace(',', '.'), "%d.%m.%Y")
    _end = datetime.datetime.strptime(end.replace(',', '.'), "%d.%m.%Y")
    return _start, _end


def formatted_string(start: datetime, end: datetime) -> str:
    """

    ----
    Args:
        start: дата начала в виде объекта класса datetime
        end: дата конца в виде объекта класса datetime
    ----

    Returns:
        Возращает шаблон строки для макроса $BILLING.SPEED.PERIOD
        Пример:
            start - 09.12.2023
            end - 11.12.2023
        Вернет:
            md9,11

    """
    delta = end - start
    str_ = 'md'
    if delta.days == 1:
        return str_ + f'{int(start.strftime("%d"))}'
    if delta.days < 7:
        return str_ + f'{int(start.strftime("%d"))},{int(end.strftime("%d")) - 1}'
    elif delta.days == 7:
        return str_ + f'{int(start.strftime("%d"))},{int(end.strftime("%d"))}'
    else:
        _current = start
        _result = []
        while _current <= end:
            _result.append(str(_current.day))
            _current += datetime.timedelta(days=7)
        if delta.days % 7 == 0:
            return str_ + f'{",".join(_result)}'
        else:
            last = (end - datetime.timedelta(days=1)).day
            if int(_result[-1]) != last:
                _result.append(str((end - datetime.timedelta(days=1)).day))
            return str_ + f'{",".join(_result)}'


class GoogleManager:
    """

    Класс для подключения к таблице Google под сервисным аккаунтом, это нужно для доступа к возможностям GoogleAPI
    В классе реализована логика получения данных, но напрямую он не используется

    ----
    Атрибуты:
        CREDENTIALS_FILE - путь до файла с данными для авторизации
        ID - id самого документа
        sheet - номер/название листа
        regions - список регионов с датами из Google-таблицы
    ----

    """

    CREDENTIALS_FILE = os.path.join(os.path.dirname(
        __file__), 'conf/google.json')
    ID = '1bH7qC8clHeWqkThHlf5DcDUv6g_XkCHkW-WKOxE8r6A'

    def __init__(self, sheet) -> None:
        self.sheet = sheet
        self.regions = self.g_connect(self.CREDENTIALS_FILE,
                                      self.ID,
                                      self.sheet)

    @staticmethod
    def g_connect(credentials: str, id: str, sheet: str) -> list:
        """

        ----
        Args:
            credentials: атрибут класса CREDENTIALS_FILE
            id: атрибут класса ID
            sheet: номер/название листа
        ----

        Returns:
            Возращает список регионов с датами начала и конца снятия реестров

        """
        try:
            __credentials = ServiceAccountCredentials.from_json_keyfile_name(
                credentials,
                [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ])
            __httpAuth = __credentials.authorize(
                httplib2.Http())  # Авторизуемся
            __service = discovery.build('sheets', 'v4', http=__httpAuth)
            spreadsheet: dict = __service.spreadsheets().values().get(
                spreadsheetId=id,
                range=f'{sheet}!A:C').execute()
            logging.info('Информация из Google получена')
            return spreadsheet.get('values')[2:]
        except Exception as e:
            logging.error('Ошибка при запросе данных от Google', e)


def google_data(sheet: str):
    """
        Функция, которая обращается к классу и получает значение

    ----
    Args:
        sheet: номер/название листа
    ----

    Returns:
        Возврщает список с регионами и датами

    """
    regions = GoogleManager(sheet)
    return regions.regions






class ZabbixManager:
    """

    Класс для реализации функционала смены макросов

    ----
    Атрибуты:
        URL - Zabbix url
        LOGIN - логин учетной запись интеграционного пользователя
        PASS - пароль учетной запись интеграционного пользователя
    ----

    Методы:
        zabbix_connect - выполняет подключение к ZabbixAPI
        get_hostmacro_period - получает макросы текущего региона
        update_macro - выполняет обновление макросов

    """
    URL = 'https://zabbix-med.bars.group/'

    @staticmethod
    def zabbix_connect(url=URL):
        zapi = ZabbixAPI(server=url)
        zapi.login(ZabbixConfig.login, ZabbixConfig.password)
        return zapi

    def __init__(self):
        self.instance = self.zabbix_connect()

    def get_hostmacro_period(self, id: str) -> list[dict[str, str]]:
        """

        ----
        Args:
            id: id хоста в строковом виде
        ----

        Returns:
            Возвращает список со словарем, которые содержат в себе текущие значения макросов

        """
        return self.instance.usermacro.get(filter={"hostid": id, 'macro': [
            '{$BILLING.END.DATE}', '{$BILLING.START.DATE}', '{$BILLING.ERROR.CALC.PERIOD}',
            '{$BILLING.ERROR.PERIOD}',
            '{$BILLING.PROC.PERIOD}', '{$BILLING.SPEED.PERIOD}', ]})

    def update_macro(self, macros: list[dict], end: datetime, start: datetime, data: dict[str, str]):
        """

        ----
        Args:
            macros: список со словарем необходимых макросов для замены
            end: дата окончания
            start: дата начала
            data: необходимые префиксы и т.д для каждого региона, которые лежат в файле full_info
        ----

        Returns:
            В переменную result добавляются макросы котоорые нужно обновить и далее обновляет макросы хоста

        """
        if validate_date(start, end):
            result = []
            for macro in macros:
                if macro['macro'] == '{$BILLING.END.DATE}':
                    params = {
                        'hostmacroid': macro['hostmacroid'],
                        'value': end.strftime("%d.%m.%Y")
                    }
                    result.append(params)
                elif macro['macro'] == '{$BILLING.START.DATE}':
                    params = {
                        'hostmacroid': macro['hostmacroid'],
                        'value': start.strftime("%d.%m.%Y")
                    }
                    result.append(params)
                elif macro['macro'] in ['{$BILLING.ERROR.CALC.PERIOD}', '{$BILLING.ERROR.PERIOD}',
                                        '{$BILLING.PROC.PERIOD}']:
                    postfix = data[macro['macro']]
                    if validate_month(start.strftime('%m'), end.strftime('%m')):
                        current = monthrange(
                            int(start.strftime('%Y')), int(start.strftime('%m')))
                        params = {
                            'hostmacroid': macro['hostmacroid'],
                            'value': f'md{int(start.strftime("%d"))}-{current[-1]},1-{int(end.strftime("%d"))}{postfix}'
                        }
                        result.append(params)
                    else:
                        params = {
                            'hostmacroid': macro['hostmacroid'],
                            'value': f'md{int(start.strftime("%d"))}-{int(end.strftime("%d"))}{postfix}'
                        }
                        result.append(params)
                elif macro['macro'] == '{$BILLING.SPEED.PERIOD}':
                    postfix = data[macro['macro']]
                    value = formatted_string(start, end)
                    params = {
                        'hostmacroid': macro['hostmacroid'],
                        'value': f"{value}{postfix}"
                    }
                    result.append(params)

            return self.instance.usermacro.update(*result)
        else:
            return False


def zabbix_data() -> ZabbixManager:
    """

    Returns:
        Возвращает экземпляр класса ZabbixManager для дальнейше работы с ZabbixAPI

    """
    zapi = ZabbixManager()
    return zapi


def full_change_macros(sheet: str):
    """
    Функция проводит сравнение дат из таблицы и Zabbix и если есть отличия, то обновляет макросы в Zabbix

    ----
    Args:
        sheet: строка с номером листа Google
    ----

    """

    logging.info('Начинаем работу')
    regions: list[str] = google_data(sheet)
    zabbix = zabbix_data()
    full_info: dict = get_regions()
    print(full_info)

    if full_info:
        logging.info(f'Информация получена из json\n')
    else:
        logging.info(f'Произошла ошибка при получении информации ')

    for region in regions:
        logging.info(f'Обрабатываю регион - {region[0]}')

        if len(region) in [1, 2] or region[1] == '':
            logging.info(f'В регионе - {region[0]} отсутсвует дата')
            continue

        if region[1].isalpha() or region[2].isalpha():
            continue

        elif region[0] in ['Самара', 'Санкт-Петербург (НИИ Отта)']:

            name, start_date, end_date = region
            start, end = get_date(start_date, end_date)
            reg = Region(**full_info[name])
            macros = zabbix.get_hostmacro_period(reg.hostid)
            if macros[0]["value"] == end.strftime("%Y%m%d") and macros[1]["value"] == start.strftime("%Y%m%d"):
                logging.info(f'Изменений в датах у региона {name} нет')
                continue

            else:
                result = []

                for macro in macros:

                    if macro['macro'] == '{$BILLING.END.DATE}':
                        params = {
                            'hostmacroid': macro['hostmacroid'],
                            'value': end.strftime("%Y%m%d")
                        }
                        result.append(params)
                    elif macro['macro'] == '{$BILLING.START.DATE}':
                        params = {
                            'hostmacroid': macro['hostmacroid'],
                            'value': start.strftime("%Y%m%d")
                        }
                        result.append(params)
                try:
                    zabbix.instance.usermacro.update(*result)
                    logging.info(f'Данные по {name} изменены')
                except Exception as e:
                    logging.error(f'Данные не изменены по {name}', e)

        else:

            name, start_date, end_date = region
            start, end = get_date(start_date, end_date)
            reg = Region(**full_info[name])

            if start == end:
                end += datetime.timedelta(days=1)

            if isinstance(reg.hostid, list):
                for id in reg.hostid:
                    macros = zabbix.get_hostmacro_period(id)
                    if end_date.replace(',', '.') == macros[0]["value"] and start_date.replace(',', '.') == macros[-1]["value"]:
                        logging.info(f'Изменений в датах у региона {name} нет')
                        break
                    else:
                        try:
                            zabbix.update_macro(macros=macros, end=end,
                                                start=start, data=reg.data)
                            logging.info(f'Данные по {name} изменены')
                        except Exception as e:
                            logging.error(f'Данные не изменены по {name}', e)

            elif isinstance(reg.hostid, str):
                macros = zabbix.get_hostmacro_period(reg.hostid)

                if end_date.replace(',', '.') == macros[0]["value"] and start_date.replace(',', '.') == macros[-1]["value"]:
                    logging.info(f'Изменений в датах у региона {name} нет')
                    continue
                else:
                    try:
                        zabbix.update_macro(macros=macros, end=end,
                                            start=start, data=reg.data)
                        logging.info(f'Данные по {name} изменены')
                    except Exception as e:
                        logging.error(f'Данные не изменены по {name}', e)


class VersionManager:
    """
    Класс для сериализации данных для обновления версии в Zabbix.
    Реализован ввиде контекстного менеджера. Более подробно в Google

    ----
    Атрибуты:
        version: номер версии который передается с помощью POST запроса
        file_path: путь до файла где лежит список актуальных версии
        zabbix: получение экземпляра класса ZabbixAPI для использования методов API
        prefix: код js который идет до версий
        postfix: код js который идет после версий
    ----

    """
    current_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_path, 'conf/version.json')
    zabbix = zabbix_data()
    prefix = 'var vers = ['
    postfix = '''];
    var order = {};
    var j = 0;
    for (var i = 0; i <vers.length; i++){
         order[vers[i]] = i;
    }
    if(order[value]==null)
     return "Вышла новая версия"
    return order[value];
    '''

    def __init__(self, version):
        self.version = version

    def __enter__(self):
        self.file = open(file=self.file_path, mode="r")
        self.result = json.load(fp=self.file)
        self.result["version"].insert(0, f"\n            '{self.version}'")
        self.file.close()
        return self.prefix + ','.join(self.result['version']) + self.postfix

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file = open(file=self.file_path, mode="w")
        vers = {
            "version": self.result["version"]
        }
        json.dump(vers, fp=self.file, indent=4)
        self.file.close()
