import asyncio

from lib.logger import DiscordLoguruHandler, logger
from lib.settings import SETTINGS
from models.bot import Tavernier


def main():
    intents = Tavernier.get_needed_intents()
    tavernier = Tavernier(
        SETTINGS.PREFIX,
        description="description test",
        application_id=SETTINGS.CLIENT_ID,
        intents=intents,
    )
    asyncio.run(tavernier.up_and_running())
    try:
        tavernier.run(
            token=SETTINGS.TOKEN, log_handler=DiscordLoguruHandler(), log_level=1
        )
    except Exception:
        logger.exception("Client encountered an unexpected exception:")
    else:
        logger.success("Client have gracefully shut down.")


if __name__ == "__main__":
    main()
