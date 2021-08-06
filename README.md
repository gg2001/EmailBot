**Purdue Email Bot** allows you to verify that your Discord server members have a `purdue` email address.

[![Discord](https://img.shields.io/discord/868977679590883420)](https://discord.gg/xPJfDaztvS) [![License](https://img.shields.io/badge/license-GPL-brightgreen)](LICENSE)

> Invite: https://discord.com/api/oauth2/authorize?client_id=873244750868783144&permissions=268503040&scope=bot

## Usage

After [inviting](https://discord.com/api/oauth2/authorize?client_id=873244750868783144&permissions=268503040&scope=bot) the bot to your server. `.vstatus` is the help command:

```
User commands:
   .verify -> Sends a DM to the user to verify their email
   .vstatus -> This help message

Domains: purdue.edu
Verified role: Verified
```

## Installation

Install the dependencies:

```
pip install -r requirements.txt
```

Before running it make sure these environment variables are set. You will need a [Sendgrid](https://sendgrid.com/docs/for-developers/sending-email/api-getting-started/) and [Discord](https://discordpy.readthedocs.io/en/latest/discord.html#discord-intro) account (both are free). Optionally consider making a [Mailgun](https://documentation.mailgun.com/en/latest/quickstart-sending.html#how-to-start-sending-email) account, since this bot uses Mailgun when Sendgrid fails to send an email:

```
export SENDGRID_API_KEY='YOUR_SENDGRID_API_KEY'
export SENDGRID_EMAIL='YOUR_SENDGRID_EMAIL'
export DISCORD_TOKEN='YOUR_DISCORD_TOKEN'
export MAILGUN_API_KEY='YOUR_MAILGUN_API_KEY'
export MAILGUN_DOMAIN='YOUR_MAILGUN_DOMAIN'
```

Run the bot with:

```
python bot.py
```

## License

Purdue Email Bot is licensed under [GNU GPL v3](LICENSE).
