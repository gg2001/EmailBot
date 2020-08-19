from flask import Flask
from threading import Thread
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask('')

@app.route('/')
def home():
    return "EmailBot is running"

def backup_db():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    with open('dump.sql', 'w') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
    conn.close()
    print("Sqlite3 Dumped")

sched = BackgroundScheduler(daemon=True)
sched.add_job(backup_db,'interval',minutes=30)
sched.start()

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()