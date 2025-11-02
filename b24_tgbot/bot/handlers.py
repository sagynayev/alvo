import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from .keyboards import lead_actions_kb
from .utils import two_hours_ago_iso_with_tz, first_phone, to_local_display
from .bitrix import BitrixClient

router = Router()
log = logging.getLogger(__name__)

def setup_handlers(dp_router: Router, b24: BitrixClient, responsible_id: int | None, manager_chat_id: int | None):
    @dp_router.message(Command("start"))
    async def start_cmd(m: Message):
        await m.answer("Hi! Use /expired — I’ll show NEW leads older than 2 hours.")

    @dp_router.message(Command("expired"))
    async def expired_cmd(m: Message):
        if manager_chat_id and m.chat.id != manager_chat_id:
            await m.answer("Access restricted. Please contact the manager.")
            return

        iso_border = two_hours_ago_iso_with_tz("Asia/Almaty")
        await m.answer(f"Searching for NEW leads created earlier than: {iso_border}")

        try:
            leads = await b24.list_new_leads_older_than(iso_border)
        except Exception as e:
            log.exception("Bitrix list leads error")
            await m.answer("Failed to fetch leads from Bitrix. Please try again later.")
            return

        if not leads:
            await m.answer("No overdue leads found.")
            return

        # check id, title, phone
        for ld in leads:
            log.info("LEAD: %s | %s | %s", ld.get("ID"), ld.get("TITLE"), first_phone(ld))

        # send to manager
        for ld in leads:
            created_local = to_local_display(ld.get("DATE_CREATE"), "Asia/Almaty")
            text = (
                f"Lead No. {ld.get('ID')}\n"
                f"Title(name of lead): {ld.get('TITLE')}\n"
                f"Phone: {first_phone(ld)}\n"
                f"Created: {created_local}"
            )
            await m.answer(text, reply_markup=lead_actions_kb(int(ld["ID"])))

    # Button handlers
    @dp_router.callback_query(F.data.startswith("call:"))
    async def mark_called(cq: CallbackQuery):
        lead_id = int(cq.data.split(":")[1])
        try:
            await b24.add_timeline_comment(lead_id, "manager called")
            await b24.update_lead_status(lead_id, "IN_PROCESS")
        except Exception:
            log.exception("add_timeline_comment failed")
            await cq.answer("Error adding comment.", show_alert=True)
            return
        await cq.message.edit_text(cq.message.text + "\n\n ✅Marked: called")
        await cq.answer("Comment added.")

    @dp_router.callback_query(F.data.startswith("write:"))
    async def mark_wrote(cq: CallbackQuery):
        lead_id = int(cq.data.split(":")[1])
        try:
            await b24.add_timeline_comment(lead_id, "manager wrote")
            await b24.update_lead_status(lead_id, "IN_PROCESS")
        except Exception:
            log.exception("add_timeline_comment failed")
            await cq.answer("Error adding comment.", show_alert=True)
            return
        await cq.message.edit_text(cq.message.text + "\n\n 💬Marked: wrote")
        await cq.answer("Comment added.")

    @dp_router.callback_query(F.data.startswith("postpone:"))
    async def postpone_2h(cq: CallbackQuery):
        lead_id = int(cq.data.split(":")[1])
        try:
            task_id = await b24.create_task_postpone_2h(lead_id, responsible_id)
            await b24.update_lead_status(lead_id, "IN_PROCESS")
        except Exception:
            log.exception("create_task_postpone_2h failed")
            await cq.answer("Failed to create a task.", show_alert=True)
            return
        await cq.message.edit_text(cq.message.text + f"\n\n ⏳Task created (ID {task_id}) with a +2h deadline")
        await cq.answer("Task created.")
