import os
import logging
import pandas as pd
from typing import Any


def save_data(filename: str, data: pd.DataFrame) -> None:
    """
    This function saved parsed data.
    :param filename: Filename
    :param data: Saved DataFrame
    :return: No return
    """
    file_path = os.path.join(os.getcwd(), 'data')

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    save_path = os.path.join(file_path, filename)
    data.to_excel(save_path, engine='xlsxwriter', index=False)


def logger(log_name: str) -> Any:
    """
    This function create logger for debugging program.
    Not used in production version.
    :return: logging
    """
    logging.basicConfig(
        format='%(levelname)s: %(asctime)s - %(message)s',
        datefmt='%d-%b-%y %H:%M:%S',
        level=logging.INFO,
        filename=f'{log_name}.log',
        filemode='w'
    )

    return logging
