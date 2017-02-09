# pineapple
A modular, extendible, discord bot framework based on discord.py.

Check out our Trello page for our progress and plans:
https://trello.com/b/tj0OqFwR/pineapple-feature-timeline

# Installation
This guide will be for installing the bot on Ubuntu.

## Creating a bot account

1. Go to [the discord developers page](https://discordapp.com/developers/applications/me)
2. Click New Application
3. Give your bot a name and an icon, then press Create Application
4. On the next page, click Create a Bot User
5. Next to Token, click Click to reveal to see your token
6. Enter your token inside the configuration file for the bot.

## running the bot

1. Clone the repo locally using `git clone https://github.com/peter765/pineapple.git`.
2. Edit the config.ini.default with the necessary information.
3. Rename config.ini.default to config.ini.
4. Update pip with `python3.5 -m pip install --upgrade pip` for Ubuntu 14.04 or `python3 -m pip install --upgrade pip` for 16.04 and later.
5. Use `pip install -r requirements.txt` to install dependencies.
6. Install py-trello using `pip install -r py-trello`.
7. Run the bot using `python3.5 bot.py` for Ubuntu 14.04 or `python3 bot.py` for 16.04 and later.

## Adding the bot to your server

1. Make sure you have Manage Server permissions.
2. go to [the discord developers page](https://discordapp.com/developers/applications/me) and click on your application. At the top, you will find the bot account's Client ID.
3. Replace "CLIENT_ID" in the following link the Client ID from your application page, and then open that URL in a browser.
https://discordapp.com/oauth2/authorize?&client_id=CLIENT_ID&scope=bot&permissions=0
4. Select your server and add the bot to that server
# Common issues

###ImportError: cannot import name 'quote_plus'
This error happens when you install trello instead of py-trello. You can use
`pip install py-trello` to fix this this issue.

