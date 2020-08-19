<p align="center">
  <img src="docs/emailbot.png" />
</p>

![Discord](https://img.shields.io/discord/731028346569228288)

> EmailBot allows you to verify that your Discord server members have an email address with a specific domain.

> Invite: https://discord.com/api/oauth2/authorize?client_id=731027450607435846&permissions=268503040&scope=bot

> Discord server: https://discord.gg/MfFMxu9

Let's say you want  a Discord server just for people who have a @randomuniversity.edu email address. Add this bot to your server and whenever someone joins, they will get a DM asking for their @randomuniversity.edu email address. Then, the bot emails them a verification code. If they reply with the correct code, they get the "Verified" role. You can have channels that only allow verified users to ensure that non verified users can't participate.

<p align="center">
  <img src="docs/screenshot.png" />
</p>

## How to use

After inviting the bot to your server, a domain must be added using `.dominadd domain`. `.vstatus` is the help command:

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

## Install

Before running it make sure these environment variables are set:

```
export SENDGRID_API_KEY=
export SENDGRID_EMAIL=
export DISCORD_TOKEN=
```

Make sure the dependencies such as `discord`, `sendgrid`, `apscheduler` and `flask` are installed. Run the bot with:

```
python bot.py
```
