from flask import Flask
from threading import Thread
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask('')

@app.route('/')
def home():
    return "EmailBot is running"

def progress(status, remaining, total):
    print(f'Copied {total-remaining} of {total} pages...')

def backup_db():
    con = sqlite3.connect('bot.db')
    bck = sqlite3.connect('backup.db')
    with bck:
        con.backup(bck, pages=1, progress=progress)
    bck.close()
    con.close()
    print("Sqlite3 backed up")

sched = BackgroundScheduler(daemon=True)
sched.add_job(backup_db,'interval',minutes=30)
sched.start()

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()