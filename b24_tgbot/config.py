from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    telegram_token: str
    bitrix_base: str
    responsible_id: int | None
    manager_chat_id: int | None

def get_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    base = os.getenv("BITRIX_WEBHOOK_BASE", "").rstrip("/") + "/"
    resp = os.getenv("RESPONSIBLE_ID")
    chat = os.getenv("MANAGER_CHAT_ID")
    PORTAL_TZ = os.getenv("PORTAL_TZ", "Asia/Almaty")
    return Settings(
        telegram_token=token,
        bitrix_base=base,
        responsible_id=int(resp) if resp else None,
        manager_chat_id=int(chat) if chat else None,
    )
