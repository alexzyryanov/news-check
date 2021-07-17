from config import *


div = ""


class Application:

    """check news, append new in html page"""

    def __init__(self, name):
        self.name = name

    def save_page(self):

        """save page, find url image and video, check url in db"""

        r = requests.get(url=url.format(self.name), headers=user_agent)
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
            param = """SELECT url FROM sp"""
            for i in cursor.execute(param):
                url_db.append(i[0])
            cursor.close()
            connect_db.close()
        except:
            pass

        for i in search:
            image = i.find("img", class_=image_container).get("src")
            x_image = "http:{}".format(image)
            if ".png" in x_image:
                x_image = None

            try:
                video = i.find("video", class_=video_container).get("src")
                x_video = "http:{}".format(video)
            except:
                x_video = None

            url_p = i.find("div", class_=url_container).find("a").get("href")
            x_url = url_1.format(url_p, self.name)

            if x_image not in url_db:
                self.download_image(x_image, x_video, x_url)

        print(f"-- {self.name} --")

    def download_image(self, image, video, x_url):

        """save url in db"""

        connect_db = sqlite3.connect("image_url.db")
        cursor = connect_db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS sp (name TEXT, url TEXT)""")
        connect_db.commit()
        cursor.execute("""INSERT INTO sp VALUES (?, ?)""", (self.name, image))
        connect_db.commit()
        cursor.close()
        connect_db.close()

        self.div_page(image, video, x_url)

    def div_page(self, image, video, x_url):

        """append content in div"""

        x = """
        <div class="content">
            <div class="name"><a href="{}" target="_blank">{}</a></div>
            <div class="media">
                <div class="image"><img src="{}"></div>
                <div class="video"><video src="{}" controls></video></div>
            </div>
        </div>\n""".format(x_url, self.name, image, video)
        global div
        div += x


def create_new():

    """create html page"""

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
    </html>""".format(div)

    with open("new.html", "w", encoding="utf-8") as f:
        f.write(page)


def start_application():
    if os.path.exists("saved page") is not True:
        os.mkdir("saved page")
    try:
        for i in item:
            app = Application(i)
            app.save_page()
        create_new()
        os.startfile("new.html")
    except:
        create_new()
        os.startfile("new.html")
