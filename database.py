import sqlite3

# categories_data = {
#     'Productivity Bots': ['1. @googledriveit_bot', '2. @skeddybot', '3. @BotFather', '4. @newfileconverterbot', '5. @DropMailBot'],
#     'Finance Bots': ['1. @unibotsniper_bot', '2. @Paal_aiBOT', '3. @finestelbot', '4. @tokenfibuybot', '5. @ChainGPTBot', '6. @Ccpricingbot'],
#     'Entertainment Bots': ['1. @kinonetbot', '2. @stickers', '3. @MemMachineBot', "4. @RoshamboGameBot", "5. @EzStickerBot", "6. @randtalkbot"],
#     'News & Updates Bots': ['1. @googlnews_bot', '2. @journalistbot', '3. @cryptonews_ericabot', '4. @advancedpollbot', '5. @metalarchives_bot'],
#     'Health & Fitness Bots': ['1. @peprecipebot', '2.@sd_health_bot', '3. @YourDomainHealthCheckBot', '4. @dailyhealthbot','5. @dailyfitbot'],
#     'Personal Assistant': ['1.@MisRose_bot', '2. @shobybot', '3. @FassonBot','4. @hotelhuntbot', '5. @choochoobot'],
#     # Add more categories and bots as needed
# }


conn = sqlite3.connect('bots_database.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create a table to store the categories and bots
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bots (
        category TEXT PRIMARY KEY,
        bots TEXT
    )
''')

# # Insert data into the database
# for category, bots in categories_data.items():
#     cursor.execute('''
#         INSERT OR REPLACE INTO bots (category, bots) VALUES (?, ?)
#     ''', (category, ', '.join(bots)))

# Commit the changes and close the connection
conn.commit()
conn.close()

def get_data_from_database():
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
    return botlists_data

# Accessing data from the database
botlists_data = get_data_from_database()

def add_bot_to_category(category, new_bot):
    conn = sqlite3.connect('bots_database.db')
    cursor = conn.cursor()

    # Retrieve existing bots for the specified category
    cursor.execute('SELECT bots FROM bots WHERE category = ?', (category,))
    existing_bots = cursor.fetchone()

    if existing_bots:
        # Append the new bot to the existing list
        updated_bots = existing_bots[0] + ', ' + new_bot
        cursor.execute('UPDATE bots SET bots = ? WHERE category = ?', (updated_bots, category))
    else:
        # If the category does not exist, create a new entry
        raise ValueError("Incorrect bot catrgory")

    conn.commit()
    conn.close()