import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import dbconfig as db
from peewee import *
import urlparse


def make_soup(url):
    resp = requests.get(url)
    html = resp.text
    return BeautifulSoup(html, "html5lib")


def get_video_id(url):
    url_data = urlparse.urlparse(url)
    query = urlparse.parse_qs(url_data.query)
    return url_data.path.split("/")[2]


def get_video_url(id):
    return "https://www.youtube.com/watch?v="+id

class Article:
    def __init__(self, url):
        self.url = url
        soup = make_soup(url)
        self.article_soup = soup.article
        self.title = soup.find("span", class_="threadTitle").contents[0].strip()
        self.id = int(self.article_soup.get("data-messageid"))
        self.text = soup.find("span", class_="fullText").contents[0].text
        self.num_pages = int(soup.find("li", class_="next arrow").find_previous_sibling().string)
        self.username = soup.find("a", class_="member-nickname").contents[1]
        self.user_id = int(soup.find("a", class_="member-nickname").contents[0].get("data-memberid"))
        self.time = datetime.strptime(soup.find("time").contents[0], '%d/%m/%Y %H:%M')
        self.comments = self.get_comments(soup)
        self.votes = soup.find("li", class_="stars").get("data-totalvotes")
        self.videos = [get_video_id(v.get("src")) for v in soup.findAll("iframe")]

    def get_comments(self, soup):
        comments = []
        for page in range(1,2):  #self.num_pages+1
            page_soup = make_soup(self.url[:-1]+str(page))
            comments_html = page_soup.findAll("div", class_="message")
            for c in comments_html:
                comment = Comment(c, self.id)
                comments.append(comment)
            # here we delay for 1 second (or the appropriate # of seconds) to avoid being banned by the server
            #time.sleep(1)
        return comments


class Comment:
    def __init__(self, soup, article_id):
        self.username = soup.find("a", class_="member-nickname").contents[1]
        self.user_id = int(soup.find("a", class_="member-nickname").contents[0].get("data-memberid"))
        self.id = int(soup.get("data-messageid"))
        self.text = soup.find("div", class_="text").find("div", class_="details").text
        self.time = datetime.strptime(soup.find("time").contents[0], '%d/%m/%Y %H:%M')
        self.votes = soup.find("li", class_="stars").get("data-totalvotes")
        self.article_id = article_id
        self.videos = [get_video_id(v.get("src")) for v in soup.findAll("iframe")]


if __name__ == "__main__":
    # we can either use the requests package or urllib2
    url = 'http://www.capital.gr/forum/thread/5491339?page=1'
    article = Article(url)
    #
    with db.database_driver().db.atomic():
        try:
            query = db.users.select().where(db.users.id == article.user_id)
            if not query.exists():
                db.users.create(username = article.username, id=article.user_id)
            db.articles.create(title=article.title, id=article.id, user_id=article.user_id, text=article.text)
            for v in article.videos:
                db.videos.create(article_id=article.id, url=get_video_url(v), token=v)
        except IntegrityError:  #article already exists
            pass
        for c in article.comments:
            try:
                query = db.users.select().where(db.users.id == c.user_id)
                if not query.exists():
                    db.users.create(username=c.username, id=c.user_id)
                db.comments.create(id=c.id, user_id=c.user_id, article_id=c.article_id,
                                   text=c.text, time=c.time, votes=c.votes)
                for v in c.videos:
                    db.videos.create(comment_id=c.id, url=get_video_url(v), token=v, article_id=article.id)
            except IntegrityError:  #comment or video already exists
                pass