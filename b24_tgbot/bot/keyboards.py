from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def lead_actions_kb(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Called", callback_data=f"call:{lead_id}"),
            InlineKeyboardButton(text="💬 Wrote", callback_data=f"write:{lead_id}"),
        ],
        [
            InlineKeyboardButton(text="⏳ Postpone for 2 hours", callback_data=f"postpone:{lead_id}")
        ]
    ])
