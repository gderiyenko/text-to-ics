# Telegam bot
# that accepts text message
# sends it to openAI API
# with {System perscription to "Answer only valid .ics"} + {User's message}
# and returns the .ics file

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import logging
from openai import OpenAI
from datetime import datetime
import uuid


# Environment variables
load_dotenv()
TOKEN = os.getenv('TOKEN') # Telegram bot token
openai_key = os.getenv('OPENAI_API_KEY') # OpenAI API key
storage_path = os.getenv('STORAGE_PATH') # Path to store .ics files
domain = os.getenv('DOMAIN') # Domain to serve .ics files
whitelisted_user = os.getenv('WHITELISTED_USER') # mention here your telegram username, to allow only you to use the bot

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set openai api
openai_client = OpenAI()

# [Start] command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Send me a what's your plan, and I'll make a .ics file for you")

# [Help] command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('All you need is to describe your plan:\n ⏱️Time\n ✍️ Naming\n ⚙️Optional: Duration, When to notify and mention people.\n\n👨‍🔬The request will be processed with OpenAI API and valid iCalendar event results returned.')

# Validation on .ics
def ics_validation(ics_content: str) -> bool:
    """Validate the .ics file."""
    try:
        # check if text is a valid .ics file
        if ics_content.find("BEGIN:VCALENDAR") == -1:
            return False

        # remove everything before BEGIN
        ics_content = ics_content[ics_content.find("BEGIN:VCALENDAR"):]

        # remove everything after END
        ics_content = ics_content[:ics_content.find("END:VCALENDAR") + len("END:VCALENDAR")]

        # Check that content is not empty
        if len(ics_content) < 20:
            return False

        return True
    except Exception as e:
        print(e)
        return False


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    try:
        # Decline everyone exept youself
        if update.message.from_user.username != whitelisted_user:
            return "Sorry, I couldn't generate the .ics file for you"

        # Get response from openai
        response = get_openai_response(update.message.text)
        ics_content = response.choices[0].message.content

        # Validate the .ics file
        if not ics_validation(ics_content):
            await update.message.reply_text("Sorry, I couldn't generate the .ics file for this request. Please try again.")
            return

        # Generate uuid
        uid = str(uuid.uuid4())

        # Put .ics into storage
        ics_file = open(storage_path + "/" + uid + ".ics", "w")
        ics_file.write(ics_content)
        ics_file.close()

        # Send the file
        ics_file = open(storage_path + "/" + uid + ".ics", "rb")
        await update.message.reply_document(ics_file)
        ics_file.close()

        # remove the file
        #os.remove("event.ics")

        await update.message.reply_text(ics_content)

        await update.message.reply_text(domain + "/" + uid + ".ics")
    except Exception as e:
        print(e)

# Get the response from OpenAI
def get_openai_response(message: str) -> str:
    """Get the response from OpenAI."""
    try:
        today = datetime.today().strftime('%Y-%m-%d')
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "Answer only valid .ics Today is " + today
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        # log response
        print(response)
        return response
    except Exception as e:
        print(e)
        return "Sorry, I couldn't generate the .ics file for you"

def main() -> None:

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()