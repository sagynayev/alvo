import aiohttp
import asyncio
from typing import Any, Dict, List, Optional
from .utils import deadline_plus_hours_iso_with_tz

class BitrixClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def _post(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{method}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if "error" in data:
                    raise RuntimeError(f"Bitrix error: {data.get('error_description', data['error'])}")
                return data

    async def list_new_leads_older_than(self, iso_datetime: str) -> List[Dict[str, Any]]:
        """
        Returns all leads with status <NEW> and a creation date earlier than iso_datetime (older than 2 hours).
        """
        method = "crm.lead.list"
        start = 0
        items: List[Dict[str, Any]] = []
        while True:
            payload = {
                "filter": {
                    "STATUS_ID": "NEW",
                    "<DATE_CREATE": iso_datetime
                },
                "select": ["ID", "TITLE", "PHONE", "DATE_CREATE"],
                "start": start
            }
            data = await self._post(method, payload)
            batch = data.get("result", [])
            items.extend(batch)
            next_start = data.get("next")
            if next_start is None:
                break
            start = next_start
        return items

    async def add_timeline_comment(self, lead_id: int, comment: str) -> int:
        method = "crm.timeline.comment.add"
        payload = {
            "fields": {
                "ENTITY_TYPE": "lead",
                "ENTITY_ID": lead_id,
                "COMMENT": comment
            }
        }
        data = await self._post(method, payload)
        return int(data["result"])

    async def create_task_postpone_2h(self, lead_id: int, responsible_id: Optional[int]) -> int:
        method = "tasks.task.add"
        from datetime import datetime, timedelta, timezone
        deadline = deadline_plus_hours_iso_with_tz(2, "Asia/Almaty")
        fields = {
            "TITLE": f"Follow-up for lead No. {lead_id}",
            "DESCRIPTION": "Postponed for 2 hours via Telegram bot",
            "DEADLINE": deadline,
        }
        if responsible_id:
            fields["RESPONSIBLE_ID"] = responsible_id
        payload = {"fields": fields}
        data = await self._post(method, payload)
        return int(data["result"]["task"]["id"])
    
    async def update_lead_status(self, lead_id: int, status_id: str) -> bool:
        data = await self._post("crm.lead.update", {
            "id": lead_id,
            "fields": {"STATUS_ID": status_id}
        })
        return bool(data.get("result"))
