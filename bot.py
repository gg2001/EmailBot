import discord
from discord.ext import commands
import sqlite3
import re
import os
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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

def get_users_codes(userid, code):
    return c.execute("SELECT * FROM users WHERE userid=? AND code=?", (userid, code)).fetchall()

def verify_msg(guildname):
    return "To verify yourself on {}, **reply here with your @student.monash.edu email address**.".format(guildname)

def new_user(userid, guildid, email="", code=0, verified=0):
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (userid, guildid, email, code, verified))
    conn.commit()

def verify_user(userid, guildid):
    c.execute("UPDATE users SET verified=1 WHERE userid=? AND guildid=?", (userid, guildid))
    conn.commit()

def get_domains(guildid):
    return get_guild(guildid)[1]

def add_domain(domain, guildid):
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

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_member_join(member):
    check_on_join = get_guild(member.guild.id)
    if check_on_join == None:
        new_guild(member.guild.id)
    elif check_on_join[2] == 1:
        user_prev_verify = get_user_guild(member.guild.id, member.id)
        if user_prev_verify == None:
            await member.send(verify_msg(member.guild))
            new_user(member.id, member.guild.id)
        elif user_prev_verify[4] == 0:
            await member.send(verify_msg(member.guild))

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
                guild_domains = get_domains(i)
                if len(guild_domains) == 0:
                    continue
                guild_domains = guild_domains.split('|')
                if message_content.split("@")[1] in guild_domains:
                    verif_list.append(i)
            if len(verif_list) >= 1:
                random_code = random.randint(100000, 999999)
                for i in verif_list:
                    insert_code(random_code, message.author.id, i)
                    insert_email(message_content, message.author.id, i)
                emailmessage = Mail(
                    from_email='from_email@mail.gcubed.io',
                    to_emails=message_content,
                    subject='Verify your server email',
                    html_content=str(random_code))
                try:
                    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                    response = sg.send(emailmessage)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                    await message.channel.send("Email sent.")
                except Exception as e:
                    await message.channel.send("Email failed to send.")
            else:
                await message.channel.send("Invalid email.")
        else:
            await message.channel.send("You have not joined a server.")
    elif (len(message_content) == 6) and message_content.isdigit():
        verif_code = int(message_content)
        prev_codes = get_users_codes(message.author.id, verif_code)
        if len(prev_codes) >= 1:
            verif_servers = []
            for i in prev_codes:
                verify_user(message.author.id, i[1])
                verif_servers.append(client.get_guild(i[1]).name)
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
                verif_servers = ', '.join(verif_servers)
                await message.channel.send("You have been verified on these servers: " + verif_servers + ".")
        else:
            await message.channel.send("Incorrect code")
    elif message.guild == None:
        await message.channel.send("Invalid email")
    await client.process_commands(message)

@client.event
async def on_guild_join(guild):
    check_on_join = get_guild(guild.id)
    if check_on_join == None:
        new_guild(guild.id)

@client.command()
async def domainadd(ctx, domain=None):
    if domain and ctx.guild and ctx.author.guild_permissions.administrator:
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        add_domain(domain.strip(), ctx.guild.id)
        await ctx.send("Current domains: " + get_domains(ctx.guild.id))

@client.command()
async def domainremove(ctx, domain=None):
    if domain and ctx.guild and ctx.author.guild_permissions.administrator:
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        remove_domain(domain.strip(), ctx.guild.id)
        await ctx.send("Current domains: " + get_domains(ctx.guild.id))

@client.command()
async def enableonjoin(ctx):
    if ctx.guild and ctx.author.guild_permissions.administrator:
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        enable_onjoin(ctx.guild.id)
        await ctx.send("Users **will** now be sent a DM to verify when they join the server")

@client.command()
async def disableonjoin(ctx):
    if ctx.guild and ctx.author.guild_permissions.administrator:
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        disable_onjoin(ctx.guild.id)
        await ctx.send("Users **will not** be sent a DM to verify when they join the server")

@client.command()
async def verify(ctx):
    if ctx.guild:
        check_on_join = get_guild(ctx.guild.id)
        if check_on_join == None:
            new_guild(ctx.guild.id)
        user_prev_verify = get_user_guild(ctx.guild.id, ctx.author.id)
        if user_prev_verify == None:
            new_user(ctx.author.id, ctx.guild.id)
            await ctx.author.send(verify_msg(ctx.guild))
        elif user_prev_verify[4] == 0:
            await ctx.author.send(verify_msg(ctx.guild))

client.run('')

