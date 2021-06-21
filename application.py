from config import *
from bs4 import BeautifulSoup
import requests
import sqlite3
import datetime
import os


total = len(item)
add_new = []
page_div = ""


class Application:

    """download image and video, append data for html page"""

    date_now = datetime.datetime.now().strftime("%d.%m.%y %H.%M")
    user_agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                "(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"}

    def __init__(self, name):
        self.name = name

    def save_page(self):

        """save page, find url image and video, check url in db"""

        r = requests.get(url=url.format(self.name), headers=self.user_agent)
        with open("saved page/{}.html".format(self.name), "wb") as f:
            f.write(r.content)

        with open("saved page/{}.html".format(self.name), "rb") as f:
            content = f.read()
        soup = BeautifulSoup(content, "lxml")
        search = soup.find_all("div", class_=content_container)

        url_db = []
        try:
            connect_db = sqlite3.connect("image_url.db")
            cursor = connect_db.cursor()
            param = """SELECT url FROM image"""
            for i in cursor.execute(param):
                url_db.append(i[0])
            cursor.close()
            connect_db.close()
        except Exception:
            print("don't have db")
            pass

        count = 0
        for i in search:
            image = i.find("img", class_=image_container).get("src")
            x_image = "http:{}".format(image)
            if ".png" in x_image:
                x_image = None
            try:
                video = i.find("video", class_=video_container).get("src")
                x_video = "http:{}".format(video)
            except Exception:
                x_video = None
            if x_image not in url_db:
                self.download_image(x_image, x_video, count)
            count += 1
        global total
        print(f"-- {total} -- {self.name} --")
        total -= 1

    def download_image(self, image, video, count):

        """save image and video, save url in db"""

        s_image = "image/{} {} {}.jpg".format(self.name, count, self.date_now)
        s_video = "image/{} {} {}.mp4".format(self.name, count, self.date_now)

        if image is None:
            pass
        else:
            r = requests.get(url=image, headers=self.user_agent)
            with open(s_image, "wb") as f:
                f.write(r.content)

        if video is None:
            pass
        else:
            r = requests.get(url=video, headers=self.user_agent, stream=True)
            with open(s_video, "wb") as f:
                for chunk in r.iter_content(chunk_size=10000):
                    if chunk:
                        f.write(chunk)

        connect_db = sqlite3.connect("image_url.db")
        cursor = connect_db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS image
                            (date TEXT, name TEXT, url TEXT)""")
        connect_db.commit()
        cursor.execute("""INSERT INTO image VALUES (?, ?, ?)""",
                       (self.date_now, self.name, image))
        connect_db.commit()
        cursor.close()
        connect_db.close()

        self.div_page(s_image, s_video)
        add_new.append(self.name)

    def div_page(self, image, video):

        """append content to div"""

        x = """
        <div class="content">
            <div class="name">{}</div>
            <div class="media">
                <div class="image"><img src="{}"></div>
                <div class="video"><video src="{}" controls></video></div>
            </div>
        </div>\n""".format(self.name, image, video)
        global page_div
        page_div += x


def create_new():

    """create html page for div_page"""

    page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="style/style.css">
        <title>check</title>
    </head>
    <body>
        {}
    </body>
    </html>""".format(page_div)

    with open("new.html", "w", encoding="utf-8") as f:
        f.write(page)


def start_application():
    if os.path.exists("image") is not True:
        os.mkdir("image")
    if os.path.exists("saved page") is not True:
        os.mkdir("saved page")

    for i in item:
        app = Application(i)
        app.save_page()

    create_new()

    for i in add_new:
        print(i)

    input("---done press Enter---")

    os.startfile("new.html")
