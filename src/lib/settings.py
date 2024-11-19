from pathlib import Path
from tomllib import TOMLDecodeError, load

from .logger import logger


class Settings(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        try:
            config_file = Path("config", "config.toml")
            with open(config_file, "rb") as f:
                config = load(f)
                self.PREFIX: str = config["DISCORD"]["prefix"]
                self.CLIENT_ID: str = config["DISCORD"]["client_id"]
                self.TOKEN: str = config["DISCORD"]["token"]
                self.LOGGER_LVL: str = config["LOGGER"]["lvl"]
                self.LOGGER_MAX_LVL: str = config["LOGGER"]["max_lvl"]
                self.ENV: str = config["LOGGER"]["environnement"]
        except FileNotFoundError:
            logger.critical("The toml config file was not found.")
        except TOMLDecodeError:
            logger.critical("The toml config file is malformed.")
        except KeyError as e:
            logger.critical(f"A required key in config file was not found: {e}")


SETTINGS = Settings()
