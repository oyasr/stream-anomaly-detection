import logging

from app.models import Environment


class Logger:
    def __init__(self, file_path: str = None):
        self._formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        self._stream_handler = logging.StreamHandler()
        self._stream_handler.setFormatter(self._formatter)

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(self._stream_handler)

        if file_path:
            self._file_handler = logging.FileHandler(file_path)
            self._file_handler.setFormatter(self._formatter)
            self.logger.addHandler(self._file_handler)

    def init_app(self, env: Environment):
        if env == Environment.PRODUCTION:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.DEBUG)

    def exception(self, msg: str):
        self.logger.exception(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)
