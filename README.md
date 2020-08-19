# EmailBot

Discord Email verification bot written in Python 3.

Invite link: https://discord.com/api/oauth2/authorize?client_id=731027450607435846&permissions=268503040&scope=bot

Discord server: https://discord.gg/MfFMxu9

## How to use

A domain must be added using `.dominadd domain` for this bot to work. `.vstatus` is the help command.

```
User commands: 
   .verify -> Sends a DM to the user to verify their email

Admin commands: 
   .vstatus -> This help message
   .enableonjoin -> Enables verifying users on join
   .disableonjoin -> Disables verifying users on join
   .domainadd domain -> Adds an email domain
   .domainremove domain -> Removes an email domain
   .rolechange role -> Changes the name of the verified role
 - A domain must be added before users can be verified.
 - Use .rolechange instead of server settings to change the name of the verified role.

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
