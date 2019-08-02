import argparse
from bs4 import BeautifulSoup
import requests
import time
import logging
from MarketwatchNewsScraper import MarketwatchNewsScraper
from SentimentAnalyzer import SentimentAnalyzer
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, './src')


class NewsScraper:
    def __init__(self, url=None, frequency=120):
        self.url = url
        self.headlines = []
        self.followedlinks = []
        self.frequency = frequency

    def scrape_site(self):

        marketwatchScraper = MarketwatchNewsScraper()
        newsHeadlines = []

        sentimentAnalyzer = SentimentAnalyzer()

        while True:
            headlines = marketwatchScraper.scrape()

            for headline in headlines:
                if headline not in newsHeadlines:
                    print('headline:', headline)
                    newsHeadlines.append(headline)
                    sentimentAnalyzer.google_analyze(headline)

            # for headline in newsHeadlines:
            #         #print('headline: ', headline)
            #     sentimentAnalyzer.google_analyze(headline)
            # # print('headline: ', newsHeadlines[0])
            # # sentimentAnalyzer.google_analyze(newsHeadlines[0])
            logger.info("Will get news headlines again in %s sec..." %
                        self.frequency)
            print()
            print()
            print()
            print()
            time.sleep(self.frequency)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--frequency", metavar="FREQUENCY", default=120, type=int,
                        help="How often in seconds to retrieve news headlines (default: 120 sec)")

    args = parser.parse_args()

    logformatter = '%(asctime)s [%(levelname)s][%(name)s] %(message)s'
    loglevel = logging.DEBUG
    logging.basicConfig(format=logformatter, level=loglevel)

    logger = logging.getLogger('news_scraper')

    try:
        url = "https://www.marketwatch.com/latest-news"
        logger.info("Scraping news from %s" % (url))

        # create instance of NewsHeadlineListener
        newslistener = NewsScraper(url, args.frequency)
        newslistener.scrape_site()
    except KeyboardInterrupt:
        print("Ctrl-c keyboard interrupt, exiting...")
        sys.exit(0)
