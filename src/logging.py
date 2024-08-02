import logging

from src.utils import Singleton


class Logger(Singleton):
    def __init__(self, filepath: str):
        self.filepath = filepath

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=(
                logging.FileHandler(filepath),
                logging.StreamHandler()
            )
        )

        self.log = logging.getLogger('global')
