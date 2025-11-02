from datetime import datetime, timedelta, timezone
import pytz
ISO_FMT = "%Y-%m-%dT%H:%M:%S"

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def first_phone(lead: dict) -> str:
    phones = lead.get("PHONE") or []
    if isinstance(phones, list) and phones:
        val = phones[0].get("VALUE") or ""
        return val or "none"
    val = lead.get("PHONE") or ""
    return val or "none"

def to_local_display(dt_iso: str, tz_name: str = "Asia/Almaty") -> str:
    dt = datetime.fromisoformat(dt_iso.replace("Z", "+00:00"))
    tz = pytz.timezone(tz_name)
    return dt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %z")

# for +5 UTC
def _iso_with_colon_tz(dt: datetime) -> str:
    base = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    return base[:-2] + ":" + base[-2:]

def two_hours_ago_iso_with_tz(tz_name: str) -> str:
    tz = pytz.timezone(tz_name)
    local = datetime.now(tz) - timedelta(hours=2)
    return _iso_with_colon_tz(local)

def deadline_plus_hours_iso_with_tz(hours: int, tz_name: str) -> str:
    tz = pytz.timezone(tz_name)
    local = datetime.now(tz) + timedelta(hours=hours)
    return _iso_with_colon_tz(local)