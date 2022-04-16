import discord
from discord.ext import commands
import sqlite3
import re
import os
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests
from keep_alive import keep_alive

conn = sqlite3.connect('bot.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users(
   userid INT,
   guildid INT,
   email TEXT,
   code INT,
   verified INT);
""")
c.execute("""CREATE TABLE IF NOT EXISTS guilds(
   guildid INT PRIMARY KEY,
   domains TEXT,
   onjoin INT,
   role TEXT);
""")
conn.commit()

def get_guild(guildid):
    return c.execute("SELECT * FROM guilds WHERE guildid=?", (guildid,)).fetchone()

def new_guild(guildid, domains="", onjoin=0, role="Verified"):
    c.execute("INSERT INTO guilds VALUES (?, ?, ?, ?)", (guildid, domains, onjoin, role))
    conn.commit()

def get_user_guild(guildid, userid):
    return c.execute("SELECT * FROM users WHERE guildid=? AND userid=?", (guildid, userid)).fetchone()

def get_users_guilds(userid):
    return c.execute("SELECT * FROM users WHERE userid=?", (userid,)).fetchall()

def get_emails_guilds(guildid, email):
    return c.execute("SELECT * FROM users WHERE guildid=? AND email=? AND verified=1", (guildid, email)).fetchall()

def get_users_codes(userid, code):
    return c.execute("SELECT * FROM users WHERE userid=? AND code=?", (userid, code)).fetchall()

def verify_msg(guildname, domains):
    if domains == "":
        return "{} hasn't setup this bot yet.".format(guildname)
    else: 
        return "To verify yourself on {}, **reply here with your @{} email address**.".format(guildname, domains)

def new_user(userid, guildid, email="", code=0, verified=0):
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (userid, guildid, email, code, verified))
    conn.commit()

def verify_user(userid, guildid):
    c.execute("UPDATE users SET verified=1 WHERE userid=? AND guildid=?", (userid, guildid))
    conn.commit()

def get_domains(guildid):
    return get_guild(guildid)[1]

def add_domain(domain, guildid):
    d_get = get_domains(guildid)
    prevdomains = []
    if d_get != "":
        prevdomains = get_domains(guildid).split('|')
    if domain not in prevdomains:
        prevdomains.append(domain)
        c.execute("UPDATE guilds SET domains=? WHERE guildid=?", ('|'.join(prevdomains), guildid))
        conn.commit()

def remove_domain(domain, guildid):
    prevdomains = get_domains(guildid).split('|')
    if domain in prevdomains:
        prevdomains.remove(domain)
        c.execute("UPDATE guilds SET domains=? WHERE guildid=?", ('|'.join(prevdomains), guildid))
        conn.commit()

def change_role(role, guildid):
    c.execute("UPDATE guilds SET role=? WHERE guildid=?", (role, guildid))
    conn.commit()

def enable_onjoin(guildid):
    c.execute("UPDATE guilds SET onjoin=? WHERE guildid=?", (1, guildid))
    conn.commit()

def disable_onjoin(guildid):
    c.execute("UPDATE guilds SET onjoin=? WHERE guildid=?", (0, guildid))
    conn.commit()

def insert_code(code, userid, guildid):
    c.execute("UPDATE users SET code=? WHERE userid=? AND guildid=?", (code, userid, guildid))
    conn.commit()

def insert_email(email, userid, guildid):
    c.execute("UPDATE users SET email=? WHERE userid=? AND guildid=?", (email, userid, guildid))
    conn.commit()

def email_check(email):
    regex = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    if re.search(regex, email):
        return True
    else:
        return False

def mailgun_send(email_address, verification_code):
	return requests.post(
		"https://api.mailgun.net/v3/{}/messages".format(os.environ.get('MAILGUN_DOMAIN')),
		auth=("api", os.environ.get('MAILGUN_API_KEY')),
		data={"from": "EmailBot <mailgun@{}>".format(os.environ.get('MAILGUN_DOMAIN')),
			"to": email_address,
			"subject": "Verify your server email",
			"text": str(verification_code)})

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '.', intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name='.vstatus | github.com/gg2001/EmailBot'))

@client.event
async def on_member_join(member):
    check_on_join = get_guild(member.guild.id)
    if check_on_join == None:
        new_guild(member.guild.id)
    elif check_on_join[2] == 1:
        user_prev_verify = get_user_guild(member.guild.id, member.id)
        if user_prev_verify == None:
            await member.send(verify_msg(member.guild, check_on_join[1]))
            new_user(member.id, member.guild.id)
        elif user_prev_verify[4] == 0:
            await member.send(verify_msg(member.guild, check_on_join[1]))
        elif user_prev_verify[4] == 1:
            role = discord.utils.get(member.guild.roles, name=check_on_join[3])
            if role:
                if role not in member.roles:
                    await member.add_roles(role)
            else:
                await member.guild.create_role(name=check_on_join[3])
                role = discord.utils.get(member.guild.roles, name=check_on_join[3])
                await member.add_roles(role)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    message_content = message.content.strip()
    if (message.guild == None) and email_check(message_content):
        users_guilds = get_users_guilds(message.author.id)
        if len(users_guilds) >= 1:
            guild_list = [i[1] for i in users_guilds if i[4] == 0]
            verif_list = []
            for i in guild_list:
                email_guild = get_emails_guilds(i, message_content)
                if len(email_guild) > 0:
                    continue
                guild_domains = get_domains(i)
                if len(guild_domains) == 0:
                    continue
                guild_domains = guild_domains.split('|')
                if message_content.split("@")[-1] in guild_domains:
                    verif_list.append(i)
            if len(verif_list) >= 1:
                random_code = random.randint(100000, 999999)
                for i in verif_list:
                    insert_code(random_code, message.author.id, i)
                    insert_email(message_content, message.author.id, i)
                emailmessage = Mail(
                    from_email=os.environ.get('SENDGRID_EMAIL'),
                    to_emails=message_content,
                    subject='Verify your server email',
                    html_content=str(random_code))
                try:
                    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                    response = sg.send(emailmessage)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                    await message.channel.send("Email sent. **Reply here with your verification code**. If you haven't received it, check your spam folder.")
                except Exception as e:
                    mailgun_email = mailgun_send(message_content, random_code)
                    if mailgun_email.status_code == 200:
                        await message.channel.send("Email sent. **Reply here with your verification code**. If you haven't received it, check your spam folder.")
                    else:
                        await message.channel.send("Email failed to send.")
            else:
                await message.channel.send("Invalid email.")
        else:
            await message.channel.send("You have not joined a server.")
    elif (len(message_content) == 6) and message_content.isdigit():
        verif_code = int(message_content)
        prev_codes_f = get_users_codes(message.author.id, verif_code)
        prev_codes_g = [i for i in prev_codes_f if i[4] == 0]
        prev_codes = []
        for i in prev_codes_g:
            user_emails = get_emails_guilds(i[1], i[2])
            if len(user_emails) >= 1:
                continue
            else:
                prev_codes.append(i)
        if len(prev_codes) >= 1:
            for i in prev_codes:
                verify_user(message.author.id, i[1])
                curr_guild = client.get_guild(i[1])
                guild_db = get_guild(i[1])
                role = discord.utils.get(curr_guild.roles, name=guild_db[3])
                if role:
                    member = curr_guild.get_member(message.author.id)
                    if role not in member.roles:
                        await member.add_roles(role)
                else:
                    await curr_guild.create_role(name=guild_db[3])
                    role = discord.utils.get(curr_guild.roles, name=guild_db[3])
                    member = curr_guild.get_member(message.author.id)
                    await member.add_roles(role)
                await message.channel.send("You have been verified on " + client.get_guild(i[1]).name + ".")
        else:
            await message.channel.send("Incorrect code.")
    elif message.guild == None:
        await message.channel.send("Invalid email.")
    await client.process_commands(message)

@client.event
async def on_guild_join(guild):
    check_on_join = get_guild(guild.id)
    if check_on_join == None:
        new_guild(guild.id)

@client.command()
async def rolechange(ctx, role=None):
    if role and ctx.guild and ctx.author.guild_permissions.administrator:
        role = role.strip()
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        check_on_join = get_guild(ctx.guild.id)
        role_d = discord.utils.get(ctx.guild.roles, name=check_on_join[3])
        if role_d:
            await role_d.edit(name=role)
            change_role(role, ctx.guild.id)
            await ctx.send("```Verified role: " + get_guild(ctx.guild.id)[3] + "```")
        else:
            role_d2 = discord.utils.get(ctx.guild.roles, name=role)
            if role_d2:
                change_role(role, ctx.guild.id)
                await ctx.send("```Verified role: " + get_guild(ctx.guild.id)[3] + ".```")
            else:
                await ctx.guild.create_role(name=role)
                change_role(role, ctx.guild.id)
                await ctx.send("```Verified role: " + get_guild(ctx.guild.id)[3] + ".```")

@client.command()
async def domainadd(ctx, domain=None):
    if domain and ctx.guild and ctx.author.guild_permissions.administrator:
        domain = domain.strip()
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        add_domain(domain, ctx.guild.id)
        await ctx.send("```Current email domains: " + get_domains(ctx.guild.id) + "```")

@client.command()
async def domainremove(ctx, domain=None):
    if domain and ctx.guild and ctx.author.guild_permissions.administrator:
        domain = domain.strip()
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        remove_domain(domain, ctx.guild.id)
        await ctx.send("```Current email domains: " + get_domains(ctx.guild.id) + "```")

@client.command()
async def enableonjoin(ctx):
    if ctx.guild and ctx.author.guild_permissions.administrator:
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        enable_onjoin(ctx.guild.id)
        await ctx.send("```Verify when a user joins? True```")

@client.command()
async def disableonjoin(ctx):
    if ctx.guild and ctx.author.guild_permissions.administrator:
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        disable_onjoin(ctx.guild.id)
        await ctx.send("```Verify when a user joins? False```")

@client.command()
async def vstatus(ctx):
    if ctx.guild:
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        check_on_join = get_guild(ctx.guild.id)
        on_join = bool(check_on_join[2])
        await ctx.send("```" +
            "Ping: " + "{0}ms".format(round(client.latency * 1000)) + "\n" +
            "User commands: " + "\n" +
            "   .verify -> Sends a DM to the user to verify their email" + "\n" +
            "   .vstatus -> This help message" + "\n\n" +
            "Admin commands: " + "\n" +
            " - A domain must be added before users can be verified." + "\n" +
            " - Use .rolechange instead of server settings to change the name of the verified role." + "\n" +
            "   .enableonjoin -> Enables verifying users on join" + "\n" +
            "   .disableonjoin -> Disables verifying users on join" + "\n" +
            "   .domainadd domain -> Adds an email domain" + "\n" +
            "   .domainremove domain -> Removes an email domain" + "\n" +
            "   .rolechange role -> Changes the name of the verified role" + "\n\n" +
            "Domains: " + check_on_join[1] + "\n" + 
            "Verify when a user joins? (default=False): " + str(on_join) + "\n" + 
            "Verified role (default=Verified): " + check_on_join[3] + "```")

@client.command()
async def vping(ctx):
    await ctx.send("{0}ms".format(round(client.latency * 1000)))

@client.command()
async def verify(ctx):
    if ctx.guild:
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        check_on_join = get_guild(ctx.guild.id)
        user_prev_verify = get_user_guild(ctx.guild.id, ctx.author.id)
        if user_prev_verify == None:
            new_user(ctx.author.id, ctx.guild.id)
            await ctx.author.send(verify_msg(ctx.guild, check_on_join[1]))
        elif user_prev_verify[4] == 0:
            await ctx.author.send(verify_msg(ctx.guild, check_on_join[1]))

keep_alive()
client.run(os.environ.get('DISCORD_TOKEN'))
