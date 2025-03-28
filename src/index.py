from asyncio import run
from signal import SIGTERM, signal

from discord.client import (
    ConnectionClosed,
    GatewayNotFound,
    HTTPException,
    LoginFailure,
)

from lib.logger import logger
from lib.settings import SETTINGS
from models.bot import Tavernier


def signal_handler(sig, frame):
    logger.success("Client have gracefully shut down (SystemExit).")
    exit(0)


async def main():
    intents = Tavernier.get_needed_intents()
    tavernier = Tavernier(
        SETTINGS.PREFIX,
        description="description test",
        application_id=SETTINGS.CLIENT_ID,
        intents=intents,
    )
    async with tavernier:
        await tavernier.up_and_running()
        try:
            await tavernier.login(token=SETTINGS.TOKEN)
        except LoginFailure:
            logger.exception("The used token is not valid.")
        except HTTPException:
            logger.exception("And unknown HTTP error has occurred.")

        try:
            await tavernier.connect(reconnect=True)
        except GatewayNotFound:
            logger.exception(
                "The connection cannot be established with discord WebSocket, gateway was not found."
            )
        except ConnectionClosed:
            logger.exception("The connection to discord WebSocket has been terminated.")


if __name__ == "__main__":
    # handle docker signals properly
    signal(SIGTERM, signal_handler)
    try:
        run(main())
    except Exception:
        logger.exception("Client encountered an unexpected exception:")
    except KeyboardInterrupt:
        logger.success("Client have gracefully shut down.")
