import smtplib
from email.message import EmailMessage
import sqlite3
import copy
import feedparser

###
#
# Get news feed from a website, email them to recipient's inbox
# and add them to database of sent news.
#
###

# constants
server_name = "smtp.gmail.com"  # google your email's provider smtp information
port = 587
username = "yourmail@gmail.com"  # this is the address you're gonna use to all_news your mails
password = "yourpassword"
recipient = "yourothermail@gmail.com"  # if recipients are more than one, use a list here

# get news feed
news_feed = feedparser.parse("http://website/rss/news")

# connect to sqlite database  --- creating a database is optional ---
conn = sqlite3.connect("example.db")  # for this example we already have a news table created with id, title, date, link
c = conn.cursor()

# list of news
all_news = [entry for entry in news_feed["entries"]]

# before connecting to the server, we check if the news to send are already in our database
# since we are modifying our list as it iterates, we are gonna need to make a deep copy
all_news_copy = copy.deepcopy(all_news)
for e in all_news_copy:
    news_id = int(e["id"])  # this step can be different for every website's feed
    if len(c.execute("SELECT id FROM news WHERE id=?", (news_id,)).fetchall()) == 0:
        continue
    else:
        all_news.remove(e)

# connect to smtp server only if there's anything to send
if all_news:
    server = smtplib.SMTP(server_name, port)
    server.ehlo()
    server.starttls()
    server.login(username, password)

    # build  email
    for e in all_news:
        msg = EmailMessage()
        msg["Subject"] = e["title"]
        msg["From"] = username
        msg["To"] = recipient
        msg_text = e["summary"]
        msg.add_alternative(msg_text, subtype="html")
        # add news to database
        news_id = int(e["id"])
        c.execute("INSERT INTO news(id, title, date, link) VALUES(?, ?, ?, ?)", (news_id, e["title"], e["published"],
                                                                                 e["link"]))
        conn.commit()
        server.send_message(msg)

    server.quit()

conn.close()
