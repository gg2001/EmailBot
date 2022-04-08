<p align="center">
  <img src="docs/emailbot.png" />
</p>

**EmailBot** allows you to verify that your Discord server members have an email address with a specific domain.

[![Discord](https://img.shields.io/discord/731028346569228288)](https://discord.gg/MfFMxu9) [![License](https://img.shields.io/badge/license-GPL-brightgreen)](LICENSE)

> Invite: https://discord.com/api/oauth2/authorize?client_id=731027450607435846&permissions=268503040&scope=bot

> Discord server: https://discord.gg/MfFMxu9

## P.S. 

I just fixed this as their a user bypass vulnerability available in the orginal and they won't fix even though I PR'd :/

## Usage

After [inviting](https://discord.com/api/oauth2/authorize?client_id=731027450607435846&permissions=268503040&scope=bot) the bot to your server, a domain must be added using `.dominadd domain`. `.vstatus` is the help command:

```
User commands: 
   .verify -> Sends a DM to the user to verify their email
   .vstatus -> This help message

Admin commands: 
 - A domain must be added before users can be verified.
 - Use .rolechange instead of server settings to change the name of the verified role.
   .enableonjoin -> Enables verifying users on join
   .disableonjoin -> Disables verifying users on join
   .domainadd domain -> Adds an email domain
   .domainremove domain -> Removes an email domain
   .rolechange role -> Changes the name of the verified role

Domains: 
Verify when a user joins? (default=False): False
Verified role (default=Verified): Verified
```

## Example

Let's say you want a Discord server just for people who have a @randomuniversity.edu email address. Add this bot to your server and when someone joins, they will get a DM asking for their @randomuniversity.edu email address. The bot then emails them a verification code. If they reply with the correct code, they get the "Verified" role.

<p align="center">
  <img src="docs/screenshot.png" />
</p>

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

## Task list

- [ ] Separate bot commands/events into cogs and put sqlite commands in a separate file
- [ ] Make the flask server and scheduled sqlite backups optional
- [ ] Allow roles with spaces to be added
- [ ] Make the feature that allows users who leave to retain their Verified role when they join back, optional for the server admin
- [ ] Add a `.unverify member` command
- [ ] Use Role.id instead of Role.name

## License

EmailBot is licensed under [GNU GPL v3](LICENSE).
