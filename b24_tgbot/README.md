# Telegram Bitrix24 Reminder Bot
The bot is built with **aiogram 3**.
It works exactly according to the task requirements.

**Features:**
* Command `/expired` shows leads with status `NEW` created more than 2 hours ago.
* Each lead message has buttons: ✅ Called, 💬 Wrote, ⏳ Postpone for 2 hours.

**Button actions:**
* Adds a comment to the lead timeline in Bitrix24
* Creates a follow-up task with a +2h deadline
* Updates the lead status to `IN_PROCESS` (In progress)


## Requirements
* Python 3.10+
* Bitrix24 incoming webhook with CRM and Tasks access
* Telegram bot token


## Installation
```
git clone https://github.com/sagynayev/alvo
cd b24_tgbot

python -m venv .venv
# for Windows:
.venv\Scripts\activate
# for Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
python -m bot.main

## Structure
bot/handlers.py - commands and button handlers
bot/keyboards.py - inline buttons
bot/bitrix.py - Bitrix24 API logic (via webhook)
bot/utils.py - time formatting and phone parsing
config.py - tokens and settings
main.py - initialization and launch

## /expired command logic
1. Calculates local time minus 2 hours (+5 UTC).
2. Calls `crm.lead.list` with filters `STATUS_ID=NEW` and `<DATE_CREATE`.
3. Sends each lead with buttons.

**Buttons:**
* Called/Wrote - adds a comment and updates status to `IN_PROCESS`
* Postpone - creates a Bitrix task with deadline +2h and updates the lead status


## Check
Telegram API = @alvobt_bot
In Telegram, send the bot:
* `/start` - short help message
* `/expired` - shows overdue leads (if none, says so)

If you want to restrict `/expired` to yourself only, set your Telegram ID in `MANAGER_CHAT_ID`.