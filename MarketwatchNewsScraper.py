import logging

import requests
from article import Article
from bs4 import BeautifulSoup


class MarketwatchNewsScraper:
    def __init__(self, url='https://www.marketwatch.com/latest-news'):
        self.url = url

    def scrape(self):
        req = requests.get(self.url)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        for div in soup.findAll("div", {"class": "article__content"}):
            linkClass = div.find('a', {"class": "link"})
            if linkClass:
                article = Article(linkClass.getText(), linkClass['href'])
                articles.append(article)

        return articles
