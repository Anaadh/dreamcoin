import discord
from discord.ext import commands
import sqlite3
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Read configuration from text file
with open('config.txt', 'r') as file:
    config = {}
    for line in file:
        key, value = line.strip().split(': ')
        if key == 'Supply':
            value = int(value)
        elif key == 'Daily Faucet Amount':
            value = int(value)
        elif key == 'Initial Wallet Amount':
            value = int(value)
        config[key] = value

# Initialize the bot with the necessary intents
intents = discord.Intents(messages=True, guilds=True, members=True, message_content=True)
bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to the SQLite database
conn = sqlite3.connect('dreamcoin.db')
c = conn.cursor()

# Create the necessary tables
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id TEXT PRIMARY KEY, balance INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id TEXT, receiver_id TEXT, amount INTEGER, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
c.execute('''CREATE TABLE IF NOT EXISTS faucet
             (user_id TEXT PRIMARY KEY, last_claim TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
c.execute('''CREATE TABLE IF NOT EXISTS treasury
             (balance INTEGER)''')
conn.commit()

# Initialize the Treasury with the configured supply
c.execute("SELECT * FROM treasury")
result = c.fetchone()
if result is None:
    c.execute("INSERT INTO treasury (balance) VALUES (?)", (config['Supply'],))
    conn.commit()


# Wallet creation and token minting
@bot.command()
async def createwallet(ctx):
    user_id = str(ctx.author.id)
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    if result is None:
        c.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, config['Initial Wallet Amount']))
        conn.commit()
        await ctx.reply(
            f"Your {config['Name']} wallet has been created with an initial balance of {config['Initial Wallet Amount']} coins.")
    else:
        await ctx.reply(f"You already have a {config['Name']} wallet.")


# Payments
@bot.command()
async def pay(ctx, recipient: discord.User, amount: int):
    sender_id = str(ctx.author.id)
    receiver_id = str(recipient.id)

    c.execute("SELECT balance FROM users WHERE user_id = ?", (sender_id,))
    sender_balance = c.fetchone()[0]

    if sender_balance >= amount:
        c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, sender_id))
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, receiver_id))
        c.execute("INSERT INTO transactions (sender_id, receiver_id, amount) VALUES (?, ?, ?)",
                  (sender_id, receiver_id, amount))
        conn.commit()
        await ctx.reply(f"You have sent {amount} {config['Name']} to {recipient.mention}.")
    else:
        await ctx.reply(f"You don't have enough {config['Name']} to make this payment.")


@bot.command()
async def faucet(ctx):
    user_id = str(ctx.author.id)
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_result = c.fetchone()

    if user_result is None:
        await ctx.reply("You need to create a wallet before you can claim the faucet.")
        return

    c.execute("SELECT balance FROM treasury")
    treasury_balance = c.fetchone()[0]

    if treasury_balance >= int(config['Daily Faucet Amount']):
        c.execute("SELECT last_claim FROM faucet WHERE user_id = ?", (user_id,))
        last_claim = c.fetchone()

        if last_claim is None or last_claim[0] is None:
            c.execute("INSERT INTO faucet (user_id) VALUES (?)", (user_id,))
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (int(config['Daily Faucet Amount']), user_id))
            c.execute("UPDATE treasury SET balance = balance - ?", (int(config['Daily Faucet Amount']),))
            conn.commit()
            await ctx.reply(f"You have claimed your daily {config['Daily Faucet Amount']} {config['Name']} from the faucet.")
        else:
            now = datetime.datetime.now()
            last_claim_datetime = datetime.datetime.strptime(last_claim[0], '%Y-%m-%d %H:%M:%S')
            if (now - last_claim_datetime).days >= 1:
                c.execute("UPDATE faucet SET last_claim = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
                c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (int(config['Daily Faucet Amount']), user_id))
                c.execute("UPDATE treasury SET balance = balance - ?", (int(config['Daily Faucet Amount']),))
                conn.commit()
                await ctx.reply(f"You have claimed your daily {config['Daily Faucet Amount']} {config['Name']} from the faucet.")
            else:
                await ctx.reply(f"You can only claim your daily faucet once per day.")
    else:
        await ctx.reply(
            f"The {config['Name']} faucet has run out of coins. Please wait until more are minted.")


@bot.command()
async def forbes(ctx):
    c.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 3")
    results = c.fetchall()

    if not results:
        await ctx.reply(f"The {config['Name']} Forbes list is currently empty.")
    else:
        message = f"{config['Name']} Forbes List:\n"
        for i, (user_id, balance) in enumerate(results, 1):
            user = await bot.fetch_user(user_id)
            message += f"{i}. {user.name}: {balance} {config['Name']}\n"
        await ctx.reply(message)


@bot.command()
async def treasury(ctx):
    c.execute("SELECT balance FROM treasury")
    treasury_balance = c.fetchone()[0]
    await ctx.reply(f"The {config['Name']} treasury currently has {treasury_balance} coins.")


# Run the bot
bot.run(BOT_TOKEN)