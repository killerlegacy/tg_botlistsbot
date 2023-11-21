from telegram.ext import *
from telegram import *
from dotenv import load_dotenv
import logging
import sqlite3
import os
import re
import yaml
from database import botlists_data, add_bot_to_category
############# Load Environment Variables ##############
load_dotenv()
token = os.getenv("bottoken")

with open("chat.yaml", "r", encoding="utf-8") as yaml_file:
    chat_config = yaml.safe_load(yaml_file)

welcome_message = chat_config["welcome_message"]
start_message =chat_config["start_message"]

############# Database setup  ###############
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        username TEXT
    )
''')
conn.commit()

############### logging ##############
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

channelid = os.getenv("channelid")
groupid = os.getenv("groupid")
chat_developer_id=os.getenv("creator_id")

keyboard1 = [
        [InlineKeyboardButton("Broadcast Channel", url="https://t.me/botlistschnl")],
        [InlineKeyboardButton("Discussion Group", url="https://t.me/+ANWsvewoD5swZTA8")],
    ]

reply_markup1 = InlineKeyboardMarkup(keyboard1)


###################### Start Function ###############
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_chat.id
    user = update.effective_user
    username = update.effective_user.username
    add_user_to_database(user.id, user.first_name, user.last_name, user.username)
    status = await context.bot.get_chat_member(channelid, user_id)
    status1 = await context.bot.get_chat_member(groupid, user_id)
    # status1 = await context.bot.get_chat_member(groupid, user_id)

    checkpoint = status.status
    checkpoint1 = status1.status
    # checkpoint1= status1.status
    print(checkpoint, checkpoint1)
    if (checkpoint != 'creator'): #if is not creator
        if (checkpoint != 'member' or checkpoint1 != "member" ): #if is not member
            await context.bot.send_message(user_id, text=f"To use this bot, please join our channel.", reply_markup =reply_markup1 )
        else:
            await context.bot.send_message(user_id, text=start_message)
    
    else:
    # User is a member, enable bot features
        await context.bot.send_message(user_id, text=start_message)


################ Add user to Database #####################
def add_user_to_database(user_id, first_name, last_name, username):
    # Check if the user already exists
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        # User doesn't exist, so insert into the database
        cursor.execute('INSERT INTO users (user_id, first_name, last_name, username) VALUES (?, ?, ?, ?)',
                       (user_id, first_name, last_name, username))
        conn.commit()


############## Keyboard 2 #################

categories = [
    'Productivity Bots',
    'Finance Bots',
    'Entertainment Bots',
    'News & Updates Bots',
    'Health & Fitness Bots',
    'Personal Assistant',
    # Add more categories as needed
]

###################### Botlist Function ###############
async def bot_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
 
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=f"👀Heyy how are you {update.effective_user.first_name}?")
    keyboard = [
        [InlineKeyboardButton(category, callback_data=category) for category in categories[i : i + 2]
        ]
        for i in range(0, len(categories), 2)
    ]
    
    reply_markup_cat = InlineKeyboardMarkup(keyboard)
    user_id = update.effective_chat.id
    user = update.effective_user
    status = await context.bot.get_chat_member(channelid, user_id)
    status1 = await context.bot.get_chat_member(groupid, user_id)
    checkpoint = status.status
    checkpoint1 = status1.status
    if (checkpoint != 'creator'): #if is not creator
        if (checkpoint != 'member' or checkpoint1 != "member" ): #if is not member
            await context.bot.send_message(user_id, text=f"👀To use this bot, please join our channel.", reply_markup =reply_markup1 )
        else:
            await update.message.reply_text("Choose a category:", reply_markup=reply_markup_cat)
    else:
    # User is a member, enable bot features
        await update.message.reply_text("Choose a category:", reply_markup=reply_markup_cat)
    

async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('bots_database.db')
    cursor = conn.cursor()

    # Select all rows from the table
    cursor.execute('SELECT * FROM bots')
    rows = cursor.fetchall()

    # Create a dictionary to store the retrieved data
    botlists_data = {}
    for row in rows:
        category, bots = row
        botlists_data[category] = bots.split(', ')

    conn.close()
    categories_data = botlists_data
    query = update.callback_query
    await query.answer()
    category = query.data
    # print(category)
    if category in categories_data:
        bots_list = "\n".join(categories_data[category])
        reply_text = f"Bots in the {category} category:\n{bots_list}"
    else:
        reply_text = "Invalid category selected."

    await query.edit_message_text(text=reply_text)

category_keyboard = [
    ['Productivity Bots', 'Finance Bots'],
    ['Entertainment Bots', 'News & Updates Bots'],
    ['Health & Fitness Bots', 'Personal Assistant'],
]


CATEGORY, BOT_NAME = range(2)
###################### New Bot Function ###############
async def new_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    status = await context.bot.get_chat_member(channelid, user_id)
    status1 = await context.bot.get_chat_member(groupid, user_id)
    if (status.status != 'creator'):   
        if status.status != 'member' or status1.status != 'member':
            await update.message.reply_text("To add a new bot, please join our channel and group.")
            return ConversationHandler.END

        await update.message.reply_text(
            "Great! You're eligible to add a new bot. Please choose a category:",
            reply_markup= ReplyKeyboardMarkup(category_keyboard, one_time_keyboard=True)
        )
    else:
        await update.message.reply_text( 
            "Great! You're eligible to add a new bot. Please choose a category:",
            reply_markup= ReplyKeyboardMarkup(category_keyboard, one_time_keyboard=True))

    return CATEGORY


async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('bots_database.db')
    cursor = conn.cursor()

    # Select all rows from the table
    cursor.execute('SELECT * FROM bots')
    rows = cursor.fetchall()

    # Create a dictionary to store the retrieved data
    botlists_data = {}
    for row in rows:
        category, bots = row
        botlists_data[category] = bots.split(', ')

    conn.close()
    categories_data = botlists_data
    user_id = update.effective_user.id
    context.user_data['category'] = update.message.text
    if context.user_data['category'] in categories_data:
        await update.message.reply_text(
            f"Okay! You selected the category: {context.user_data['category']}. Now, please enter the username of the bot. \nTo Cancel operation Send /cancel Command.", reply_markup=ReplyKeyboardRemove())
        
         
    else:
        await context.bot.send_message(chat_id=user_id, text="Invalid Category.Please Try again")
        return ConversationHandler.END    

    return BOT_NAME
async def enter_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user=update.effective_user.first_name
    category = context.user_data['category']
    bot_name = update.message.text
    

    check = bot_name

    # Define a regular expression to extract the word "bot"
    pattern = re.compile(r'bot', flags=re.IGNORECASE)

    # Search for the pattern in the string
    match = pattern.search(check)

    # # Extract the matched word or print a message if not found
    checkpoint = match.group() if match else "Not found"
    if  checkpoint =="bot":
    # Here, you can save the bot to the database or perform any other necessary actions.
    # For simplicity, let's print the information.
        print(f"User {user_id} wants to add a bot named {bot_name} in the category {category}.")

        await update.message.reply_text(f"Bot '{bot_name}' username has been notified to Admin and after verification Your bot will be added to botlist")
        await context.bot.send_message(chat_id=chat_developer_id, text=f"{user} wants to add {bot_name} in the category {category}.")
        return ConversationHandler.END
    else:
        await context.bot.send_message(chat_id=user_id, text="Invalid username. Please restart from /newbot.")
        return ConversationHandler.END
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END


###################### Help Function ###############
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)


###################### Subscribe Function ###############
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Heyy how are you {update.effective_user.first_name}?")

SELECTING_CATEGORY, ENTERING_BOT_NAME = range(2)

async def add_bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories_list = get_categories_from_database()
        # Convert categories_list to a list of lists
    category_keyboard = [[category] for category in categories_list]

    await update.message.reply_text("Please select a category:", reply_markup=ReplyKeyboardMarkup(category_keyboard, one_time_keyboard=True))

    return SELECTING_CATEGORY

# Function to handle the selected category
async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['selected_category'] = update.message.text
    await update.message.reply_text(f"Category selected: {update.message.text}. Now, please enter the name of the bot.",reply_markup=ReplyKeyboardRemove())
    
    return ENTERING_BOT_NAME

# Function to handle entering the bot name
async def enter_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = context.user_data['selected_category']
    bot_name = update.message.text

    add_bot_to_category(category, bot_name)
    await update.message.reply_text(f"Bot '{bot_name}' added to category '{category}'.")

    return ConversationHandler.END

# Handler to cancel the operation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END


SELECTING_CATEGORY_TO_REMOVE, ENTERING_BOT_NAME_TO_REMOVE = range(2)

def get_categories_from_database():
    conn = sqlite3.connect('bots_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT DISTINCT category FROM bots')
    categories = [row[0] for row in cursor.fetchall()]

    conn.close()
    return categories

# Function to remove a bot from a category in the database
def remove_bot_from_category(category, bot_name):
    conn = sqlite3.connect('bots_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT bots FROM bots WHERE category = ?', (category,))
    existing_bots = cursor.fetchone()

    if existing_bots:
        # Remove the bot from the list if it exists
        bot_list = existing_bots[0].split(', ')
        bot_list = [bot for bot in bot_list if bot != bot_name]
        updated_bots = ', '.join(bot_list)

        cursor.execute('UPDATE bots SET bots = ? WHERE category = ?', (updated_bots, category))

    conn.commit()
    conn.close()

# Command handler for /removebot command
async def remove_bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories_list = get_categories_from_database()

    # Convert categories_list to a list of lists
    category_keyboard = [[category] for category in categories_list]

    await update.message.reply_text("Please select a category to remove a bot from:",
                                   reply_markup=ReplyKeyboardMarkup(category_keyboard, one_time_keyboard=True))

    return SELECTING_CATEGORY_TO_REMOVE

# Function to handle selecting the category to remove the bot from
async def select_category_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['selected_category_to_remove'] = update.message.text
    await update.message.reply_text(f"Category selected: {update.message.text}. Now, please enter the name of the bot to remove.")

    return ENTERING_BOT_NAME_TO_REMOVE

# Function to handle entering the bot name to remove
async def enter_bot_name_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = context.user_data['selected_category_to_remove']
    bot_name = update.message.text

    remove_bot_from_category(category, bot_name)
    await update.message.reply_text(f"Bot '{bot_name}' removed from category '{category}'.")

    return ConversationHandler.END

# Handler to cancel the remove bot operation
async def cancel_remove_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

async def add_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


####################### Main Runner #################
def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start)) #start command
    application.add_handler(CommandHandler("botlist", bot_list)) #bot list command
    application.add_handler(CallbackQueryHandler(category_selected))
    application.add_handler(CommandHandler("help", help)) #help command
    # application.add_handler(CommandHandler("subscribe", subscribe)) #subscribe Command

    new_bot_handler = ConversationHandler(
        entry_points=[CommandHandler('newbot', new_bot)],
        states={
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_category)],
            BOT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_bot_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(new_bot_handler)
    application.add_handler(CommandHandler('cancel', cancel))
    
    application.add_handler(ConversationHandler(
    entry_points=[CommandHandler('addbot', add_bot_start)],
    states={
        SELECTING_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_category)],
        ENTERING_BOT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_bot_name)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
    )
    application.add_handler(ConversationHandler(
    entry_points=[CommandHandler('removebot', remove_bot_start)],
    states={
        SELECTING_CATEGORY_TO_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_category_to_remove)],
        ENTERING_BOT_NAME_TO_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_bot_name_to_remove)],
    },
    fallbacks=[CommandHandler('cancel', cancel_remove_bot)],
)
    )
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
