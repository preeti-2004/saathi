# SSC CGL English Questions Telegram Bot

This Telegram bot sends SSC CGL English questions (synonyms, antonyms, spot the error, etc.) to groups where it's added as an admin. The bot generates questions with 4 options when a group admin types /start, allows members to vote once on options, and displays poll percentages.

## Features

- Sends SSC CGL English questions with 4 options
- Only group admins can start a new question
- Members can vote only once
- Shows poll percentages to everyone
- Supports different question types: synonyms, antonyms, spot the error

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the bot:
   ```
   python bot.py
   ```

3. Add the bot to your Telegram group as an admin

4. Type `/start` in the group to generate a new question (only works if you're a group admin)

## Customizing Questions

You can add more questions by editing the `questions.json` file. Each question should follow this format:

```json
{
    "type": "synonym",  // or "antonym", "spot_error"
    "question": "Choose the synonym of 'WORD'",
    "options": ["Option1", "Option2", "Option3", "Option4"],
    "correct_option": 1  // Index of the correct option (0-based)
}
```