import asyncio
import datetime
import logging
import json
import random
import os
from telegram import Bot

# Bot token - duplicated here to avoid circular import
TOKEN = "7657408408:AAExecDjPENZ9d3kRhKCd3dbgaPBWCYbOSo"

# Get a random question - duplicated here to avoid circular import
def get_random_question():
    questions_file = "questions.json"
    sample_questions = [
        {
            "type": "synonym",
            "question": "Choose the synonym of 'ENORMOUS'",
            "options": ["Tiny", "Huge", "Average", "Weak"],
            "correct_option": 1
        },
        {
            "type": "antonym",
            "question": "Choose the antonym of 'BENEVOLENT'",
            "options": ["Kind", "Generous", "Malevolent", "Charitable"],
            "correct_option": 2
        }
    ]
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            return random.choice(questions)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is corrupted, use sample questions
        return random.choice(sample_questions)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store chat IDs where the bot should send daily questions
subscribed_chats = set()

# File to store subscribed chats
SUBSCRIBED_CHATS_FILE = "subscribed_chats.json"

# Load subscribed chats from file
def load_subscribed_chats():
    global subscribed_chats
    try:
        with open(SUBSCRIBED_CHATS_FILE, 'r') as f:
            chats = json.load(f)
            subscribed_chats = set(chats)
            logger.info(f"Loaded {len(subscribed_chats)} subscribed chats from file")
    except (FileNotFoundError, json.JSONDecodeError):
        subscribed_chats = set()
        logger.info("No subscribed chats file found or file is corrupted")

# Save subscribed chats to file
def save_subscribed_chats():
    with open(SUBSCRIBED_CHATS_FILE, 'w') as f:
        json.dump(list(subscribed_chats), f)
    logger.info(f"Saved {len(subscribed_chats)} subscribed chats to file")

# Time to send daily questions (24-hour format)
DAILY_QUESTION_HOUR = 9  # 9 AM
DAILY_QUESTION_MINUTE = 0

# Subscribe a chat to daily questions
def subscribe_chat(chat_id):
    subscribed_chats.add(chat_id)
    save_subscribed_chats()
    logger.info(f"Chat {chat_id} subscribed to daily questions")

# Unsubscribe a chat from daily questions
def unsubscribe_chat(chat_id):
    if chat_id in subscribed_chats:
        subscribed_chats.remove(chat_id)
        save_subscribed_chats()
        logger.info(f"Chat {chat_id} unsubscribed from daily questions")
        return True
    return False

# Send a daily question to all subscribed chats
async def send_daily_questions(bot):
    if not subscribed_chats:
        logger.info("No chats subscribed to daily questions")
        return
    
    question_data = get_random_question()
    
    for chat_id in subscribed_chats:
        try:
            # Create a poll with the question
            await bot.send_poll(
                chat_id=chat_id,
                question=question_data["question"],
                options=question_data["options"],
                type="quiz",
                correct_option_id=question_data["correct_option"],
                explanation=f"This is a {question_data['type']} question from SSC CGL previous year papers.",
                is_anonymous=False,
                allows_multiple_answers=False,
            )
            logger.info(f"Daily question sent to chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send daily question to chat {chat_id}: {e}")

# Calculate seconds until next scheduled time
def seconds_until_next_time(hour, minute):
    now = datetime.datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If target time is in the past, schedule for tomorrow
    if target_time <= now:
        target_time += datetime.timedelta(days=1)
    
    return (target_time - now).total_seconds()

# Main scheduler loop
async def scheduler_loop():
    # Load subscribed chats when starting the scheduler
    load_subscribed_chats()
    bot = Bot(token=TOKEN)
    
    while True:
        # Calculate seconds until next scheduled time
        wait_seconds = seconds_until_next_time(DAILY_QUESTION_HOUR, DAILY_QUESTION_MINUTE)
        logger.info(f"Waiting {wait_seconds} seconds until next scheduled time")
        
        # Wait until scheduled time
        await asyncio.sleep(wait_seconds)
        
        # Send daily questions
        await send_daily_questions(bot)

# Run the scheduler
def run_scheduler():
    asyncio.run(scheduler_loop())

if __name__ == "__main__":
    run_scheduler()