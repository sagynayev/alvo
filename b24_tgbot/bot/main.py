import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import get_settings
from .bitrix import BitrixClient
from .handlers import router, setup_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
log = logging.getLogger("main")

async def main():
    cfg = get_settings()
    if not cfg.telegram_token or not cfg.bitrix_base:
        raise RuntimeError("check TELEGRAM API and BITRIX URL")

    bot = Bot(token=cfg.telegram_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # init BITRIX client
    b24 = BitrixClient(cfg.bitrix_base)

    # attach handlers
    setup_handlers(dp, b24, cfg.responsible_id, cfg.manager_chat_id)

    log.info("bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
