
import os
import logging

from telethon import TelegramClient, events
from pymongo import MongoClient

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up database connection
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    raise ValueError('No MongoDB URL found in environment variables')
client = MongoClient(MONGO_URL)
db = client.get_default_database()

# Set up Telegram client
API_ID = os.environ.get('TELEGRAM_API_ID')
API_HASH = os.environ.get('TELEGRAM_API_HASH')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError('Missing Telegram API credentials or bot token')
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Define message handler
@bot.on(events.NewMessage(pattern='(?i)@my_bot'))
async def handle_mention(event):
    user_id = event.message.from_id.user_id
    chat_id = event.message.chat_id
    message_id = event.message.id
    message_text = event.message.text

    # Check if user has already been mentioned
    if db.mentions.find_one({'user_id': user_id, 'chat_id': chat_id}):
        await bot.send_message(chat_id, f'You already mentioned @{event.message.from_id.username} in this chat!')
    else:
        # Save mention to database
        db.mentions.insert_one({'user_id': user_id, 'chat_id': chat_id, 'message_id': message_id, 'message_text': message_text})

        # Respond to user mention
        response = f'Thanks for mentioning me, @{event.message.from_id.username}!'
        await bot.send_message(chat_id, response)

# Start bot
bot.run_until_disconnected()
