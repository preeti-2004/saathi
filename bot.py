import logging
import random
import threading
from telegram import Update, Poll, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, PollAnswerHandler, CallbackQueryHandler
from telegram.constants import ParseMode
import json
import os
from daily_scheduler import run_scheduler, subscribe_chat, unsubscribe_chat

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "7657408408:AAExecDjPENZ9d3kRhKCd3dbgaPBWCYbOSo"

# Store user votes to prevent multiple voting
user_votes = {}

# Store questions data
questions_file = "questions.json"

# Sample questions data structure
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
    },
    {
        "type": "spot_error",
        "question": "Spot the error: 'Neither the principal nor the teachers was present at the meeting.'",
        "options": ["Neither", "nor", "was", "No error"],
        "correct_option": 2
    },
    {
        "type": "synonym",
        "question": "Choose the synonym of 'DILIGENT'",
        "options": ["Lazy", "Careless", "Hardworking", "Negligent"],
        "correct_option": 2
    },
    {
        "type": "antonym",
        "question": "Choose the antonym of 'FRUGAL'",
        "options": ["Economical", "Thrifty", "Extravagant", "Careful"],
        "correct_option": 2
    },
    {
        "type": "spot_error",
        "question": "Spot the error: 'The committee have decided to postpone the meeting.'",
        "options": ["The", "committee", "have", "No error"],
        "correct_option": 2
    },
    {
        "type": "synonym",
        "question": "Choose the synonym of 'AUDACIOUS'",
        "options": ["Timid", "Bold", "Cautious", "Fearful"],
        "correct_option": 1
    },
    {
        "type": "antonym",
        "question": "Choose the antonym of 'VERBOSE'",
        "options": ["Concise", "Wordy", "Lengthy", "Detailed"],
        "correct_option": 0
    },
    {
        "type": "spot_error",
        "question": "Spot the error: 'One of my friend are coming to the party.'",
        "options": ["One", "of my friend", "are", "No error"],
        "correct_option": 2
    },
    {
        "type": "synonym",
        "question": "Choose the synonym of 'PERNICIOUS'",
        "options": ["Beneficial", "Harmful", "Helpful", "Advantageous"],
        "correct_option": 1
    }
]

# Initialize questions data
def init_questions():
    if not os.path.exists(questions_file):
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(sample_questions, f, indent=4)

# Get a random question
def get_random_question():
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            return random.choice(questions)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is corrupted, use sample questions
        return random.choice(sample_questions)

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if the command is from a group admin
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type in ["group", "supergroup"]:
        # Get chat administrators
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = [admin.user.id for admin in admins]
        
        # Check if the user is an admin
        if user.id in admin_ids:
            await send_question(update, context)
        else:
            await update.message.reply_text("Only group admins can start a new question.")
    else:
        await update.message.reply_text("This bot is designed to work in groups. Please add me to a group!")

# Send a random question as a poll
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question_data = get_random_question()
    
    # Create a poll with the question
    message = await context.bot.send_poll(
        update.effective_chat.id,
        question=question_data["question"],
        options=question_data["options"],
        type=Poll.QUIZ,
        correct_option_id=question_data["correct_option"],
        explanation=f"This is a {question_data['type']} question from SSC CGL previous year papers.",
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    
    # Save poll data in context.bot_data
    poll_id = message.poll.id
    context.bot_data[poll_id] = {
        "chat_id": update.effective_chat.id,
        "message_id": message.message_id,
        "correct_option": question_data["correct_option"],
        "voters": set(),
    }

# Handle poll answers
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    poll_id = update.poll_answer.poll_id
    user_id = update.poll_answer.user.id
    
    # Check if this poll is being tracked
    if poll_id not in context.bot_data:
        return
    
    # Check if user has already voted
    if user_id in context.bot_data[poll_id]["voters"]:
        # User already voted, try to remove their vote (though this might not be possible with Telegram's API)
        return
    
    # Add user to voters
    context.bot_data[poll_id]["voters"].add(user_id)

# Command handler for /subscribe
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if the command is from a group admin
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type in ["group", "supergroup"]:
        # Get chat administrators
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = [admin.user.id for admin in admins]
        
        # Check if the user is an admin
        if user.id in admin_ids:
            subscribe_chat(chat.id)
            await update.message.reply_text("This group has been subscribed to daily SSC CGL questions!")
        else:
            await update.message.reply_text("Only group admins can subscribe to daily questions.")
    else:
        await update.message.reply_text("This bot is designed to work in groups. Please add me to a group!")

# Command handler for /unsubscribe
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if the command is from a group admin
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type in ["group", "supergroup"]:
        # Get chat administrators
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = [admin.user.id for admin in admins]
        
        # Check if the user is an admin
        if user.id in admin_ids:
            if unsubscribe_chat(chat.id):
                await update.message.reply_text("This group has been unsubscribed from daily SSC CGL questions.")
            else:
                await update.message.reply_text("This group was not subscribed to daily questions.")
        else:
            await update.message.reply_text("Only group admins can unsubscribe from daily questions.")
    else:
        await update.message.reply_text("This bot is designed to work in groups. Please add me to a group!")

# Command handler for /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🎓 *SSC CGL English Questions Bot* 🎓\n\n"
        "This bot provides SSC CGL English questions for your group.\n\n"
        "*Commands:*\n"
        "/start - Generate a new question (admin only)\n"
        "/subscribe - Subscribe to daily questions (admin only)\n"
        "/unsubscribe - Unsubscribe from daily questions (admin only)\n"
        "/help - Show this help message\n\n"
        "Questions include synonyms, antonyms, and spot the error types from previous year SSC CGL papers."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# Main function to run the bot
def main() -> None:
    # Initialize questions
    init_questions()
    
    # Load subscribed chats
    from daily_scheduler import load_subscribed_chats
    load_subscribed_chats()
    
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add poll answer handler
    application.add_handler(PollAnswerHandler(handle_poll_answer))
    
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()