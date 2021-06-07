from config import *
from bs4 import BeautifulSoup
import requests
import sqlite3
import datetime


page_div = ""
date_now = datetime.datetime.now().strftime("%d.%m.%y %H.%M")
user_agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"}


def save_request_page(name):

    """save page, find url image and video, check url in db"""

    r = requests.get(url=url.format(name), headers=user_agent)
    with open("saved page/{}.html".format(name), "wb") as f:
        f.write(r.content)

    with open("saved page/{}.html".format(name), "rb") as f:
        content = f.read()
    soup = BeautifulSoup(content, "lxml")
    search = soup.find_all("div", class_=content_container)

    url_db = []
    count = 0

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

    for i in search:
        image = i.find("img", class_=image_container).get("src")
        x_image = "http:{}".format(image)
        try:
            video = i.find("video", class_=video_container).get("src")
            x_video = "http:{}".format(video)
        except Exception:
            x_video = None

        if x_image in url_db:
            continue
        else:
            save_image(x_image, x_video, name, count)
        count += 1


def save_image(image, video, name, count):

    """save image and video, save url in db"""

    s_image = "image/{} {} {}.jpg".format(name, count, date_now)
    s_video = "image/{} {} {}.mp4".format(name, count, date_now)

    r = requests.get(url=image, headers=user_agent)
    with open(s_image, "wb") as f:
        f.write(r.content)

    if video is None:
        pass
    else:
        r = requests.get(url=video, headers=user_agent, stream=True)
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
                   (date_now, name, image))
    connect_db.commit()
    cursor.close()
    connect_db.close()

    div_page(name, s_image, s_video)
    print("save new {}".format(name))


def div_page(name, image, video):

    """append content to div"""

    global page_div
    x = """
    <div class="content">
        <div class="name">{}</div>
        <div class="media">
            <div class="image"><img src="{}"></div>
            <div class="video"><video src="{}" controls></video></div>
        </div>
    </div>\n""".format(name, image, video)
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


def main():
    for i in item:
        save_request_page(i)
    create_new()
    input("---done press Enter---")


if __name__ == "__main__":
    main()
