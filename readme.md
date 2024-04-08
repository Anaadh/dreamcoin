## DreamCoin Discord Bot


The DreamCoin Discord Bot is a simple currency management system built on the Discord platform. It allows users to create wallets, send and receive the DreamCoins currency, and claim daily rewards from a central treasury.

### Features

    Wallet Creation: Users can create a new DreamCoin wallet with an initial balance of 100 coins.
    Payments: Users can send DreamCoins to other users on the server.
    Faucet: Users can claim a daily reward of 100 DreamCoins from the central treasury, as long as the treasury has enough funds.
    Forbes List: The bot displays the top 3 DreamCoin holders by balance.
    Treasury Balance: The bot displays the current balance of the DreamCoin treasury.

### Commands

    !createwallet: Creates a new DreamCoin wallet for the user.
    !pay @user amount: Sends the specified amount of DreamCoins to the mentioned user.
    !faucet: Claims the daily 100 DreamCoin faucet reward.
    !forbes: Displays the top 3 DreamCoin holders.
    !treasury: Displays the current balance of the DreamCoin treasury.

### Configuration

The bot's behavior is controlled by a few configuration values stored in a config.txt file:

    Name: The name of the cryptocurrency (default: "Dreamcoin")
    Supply: The total supply of DreamCoins (default: 1,000,000)
    Daily Faucet Amount: The amount of coins awarded from the daily faucet (default: 100)
    Initial Wallet Amount: The initial balance of a newly created wallet (default: 100)

    rename te .env.example to .env and replace BOT_TOKEN with your own

### Running the Bot

To run the bot, follow these steps:

    Install the required dependencies by running pip install -r requirements.txt.
    Create a Discord bot and obtain the bot token.
    Create a .env file in the project directory and add the bot token: BOT_TOKEN=your_bot_token_here.
    Create a config.txt file in the project directory and add the desired configuration values.
    Run the main.py script to start the bot.

