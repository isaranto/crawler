import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time


def make_soup(url):
    resp = requests.get(url)
    html = resp.text
    return BeautifulSoup(html, "html5lib")


class Article:
    def __init__(self, url):
        self.url = url
        soup = make_soup(url)
        self.article_soup = soup.article
        self.num_pages = int(soup.find("li", class_="next arrow").find_previous_sibling().string)
        self.username = soup.find("a", class_="member-nickname").contents[1]
        self.user_id = soup.find("a", class_="member-nickname").contents[0].get("data-memberid")
        self.time = datetime.strptime(soup.find("time").contents[0], '%d/%m/%Y %H:%M')
        self.comments = self.get_comments(soup)
        self.votes = soup.find("li", class_="stars").get("data-totalvotes")

    def get_comments(self, soup):
        comments = []
        for page in range(10):
            page_soup = make_soup(self.url[:-1]+str(page))
            comments_html = page_soup.findAll("div", class_="message")
            for c in comments_html:
                comment = Comment(c)
                comments.append(comment)
            # here we delay for 1 second (or the appropriate # of seconds) to avoid being banned by the server
            time.sleep(1)
        return comments


class Comment:
    def __init__(self, soup):
        self.username = soup.find("a", class_="member-nickname").contents[1]
        self.user_id = soup.find("a", class_="member-nickname").contents[0].get("data-memberid")
        self.text = soup.find("div", class_="text").find("div", class_="details").text
        self.time = datetime.strptime(soup.find("time").contents[0], '%d/%m/%Y %H:%M')
        self.votes = soup.find("li", class_="stars").get("data-totalvotes")
        print self.username


# we can either use the requests package or urllib2
url = 'http://www.capital.gr/forum/thread/5491339?page=1'
article = Article(url)
