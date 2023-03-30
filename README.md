# Sorullo Machine

This is a bot that uses OpenAI and Discord to generate text.

The idea is to test OpenAI API with model "gpt-4" and see how it works, but sadly, it's not available yet.

## Installation

1. Get an OPENAI_API_KEY from [OpenAI](https://openai.com/)
1. Create an app on [Discord](https://discord.com/developers/applications) and also create a bot with its token. Put a nice image on that bot!
1. Invite the bot to your server, easy way to accomplish is to use `https://discordapp.com/oauth2/authorize?client_id=<YOUR_APP_CLIENT_ID>&scope=bot`
1. git clone the repo
1. create a `docker-compose.yml` based on the `docker-compose.sample.yml`. Fill the 3 variables: OPENAI_API_KEY, DISCORD_TOKEN and GPT4AVAILABLE
1. Run with `docker-compose.yml build && docker-compose.yml up -d`
1. You can see the logs with `docker-compose.yml logs -f`


## Usage

Depends on the name you set to your bot in Discord, you just need to mention it and then type your message. For example, if you named your bot `sorullo`, you can type `@sorullo !help` and it will reply with a list of all available commands.

Command `!analyze` is intended for use with "gpt-4" model, but it's not available yet.
