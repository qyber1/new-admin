import os
import json
import logging


def get_regions() -> dict[str, str]:
    """

    Returns:
        берет данные по регионам из JSON-файла

    """
    current_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_path, 'conf/full_info.json')

    try:
        with open(file_path) as file:
            data = json.load(file)
        return data
    except Exception as e:
        logging.error(f'Ошибка - {e}')


