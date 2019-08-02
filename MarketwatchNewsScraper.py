import logging

import requests
from bs4 import BeautifulSoup

class MarketwatchNewsScraper: 
  def __init__(self, url='https://www.marketwatch.com/latest-news'):
    self.url = url

  def scrape(self):
    req = requests.get(self.url)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    summaries = soup.findAll("p", {"class": "article__summary"})
    headlines = []
    
    if summaries:
      for summary in summaries:
        headlines.append(summary.getText())
        
    return headlines


