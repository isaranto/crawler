import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import dbconfig
from peewee import *


def make_soup(url):
    resp = requests.get(url)
    html = resp.text
    return BeautifulSoup(html, "html5lib")


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

    def get_comments(self, soup):
        comments = []
        for page in range(2):
            page_soup = make_soup(self.url[:-1]+str(page))
            comments_html = page_soup.findAll("div", class_="message")
            for c in comments_html:
                comment = Comment(c, self.id)
                comments.append(comment)
            # here we delay for 1 second (or the appropriate # of seconds) to avoid being banned by the server
            time.sleep(1)
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


if __name__=="__main__":
    # we can either use the requests package or urllib2
    url = 'http://www.capital.gr/forum/thread/5491339?page=1'
    article = Article(url)
    try:
        dbconfig.articles.create(title=article.title, id = article.id, user_id=article.user_id, text=article.text)
    except IntegrityError:
        dbconfig.users.create(username = article.username, id=article.user_id)
        dbconfig.articles.create(title=article.title, id=article.id, user_id=article.user_id, text=article.text)
    for c in article.comments:
        try:
            dbconfig.comments.create(id=c.id, user_id=c.user_id , article_id= c.article_id, text =c.text , time=c.time,
                          votes=c.votes)
        except IntegrityError:
            dbconfig.users.create(username= c.username, id=c.user_id)
            dbconfig.comments.create(id =c.id, user_id=c.user_id , article_id= c.article_id, text =c.text , time=c.time,
                          votes=c.votes)