import time
import requests
import re
import argparse
import logging
import sys
import json
from elasticsearch import Elasticsearch
from random import randint

from config import elasticsearch_host, elasticsearch_port, elasticsearch_user, elasticsearch_password, alphavantage_apikey

STOCKSIGHT_VERSION = '0.1-b.5'
__version__ = STOCKSIGHT_VERSION

url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=SYMBOL&apikey=alphavantage_apikey"

# create instance of elasticsearch
es = Elasticsearch(hosts=[{'host': elasticsearch_host, 'port': elasticsearch_port}],
                   http_auth=(elasticsearch_user, elasticsearch_password))


symbols = ['VIX', 'SPY', 'DOW']


class GetStock:

    def get_price(self, url, input_symbol):
        import re
        url = re.sub("alphavantage_apikey", alphavantage_apikey, url)
        symbols.append(input_symbol)
        while True:

            # try:
            for symbol in symbols:
                print(symbol)
                logger.info(
                    "Grabbing stock data for symbol %s..." % symbol)
                stock_url = re.sub("SYMBOL", symbol, url)
                try:
                    r = requests.get(stock_url)
                    data = r.json()
                    print(data)
                    for series in data['Time Series (Daily)']:
                        print(data['Time Series (Daily)'][series]['4. close'])
                        open = float(
                            data['Time Series (Daily)'][series]['1. open'])
                        high = float(
                            data['Time Series (Daily)'][series]['2. high'])
                        low = float(data['Time Series (Daily)']
                                    [series]['3. low'])
                        close = float(
                            data['Time Series (Daily)'][series]['4. close'])
                        volume = int(data['Time Series (Daily)']
                                     [series]['5. volume'])
                        change = close - open
                        es.index(index=args.index,
                                 doc_type="stock",
                                 id={symbol + series},
                                 body={"symbol": symbol,
                                       "price_last": close,
                                       "price_open": open,
                                       "date": series,
                                       "price_change": change,
                                       "price_high": high,
                                       "price_low": low,
                                       "vol": volume
                                       })
                except (requests.HTTPError, requests.ConnectionError, requests.ConnectTimeout) as re:
                    logger.error(
                        "Exception: exception getting stock data from url caused by %s" % re)
                    raise
                logger.debug(data)

            # except Exception as e:
            #     logger.error(
            #         "Exception: can't get stock data, trying again later, reason is %s" % e)

            logger.info("Will get stock data again in %s sec..." %
                        args.frequency)
            time.sleep(args.frequency)


if __name__ == '__main__':

    # parse cli args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--index", metavar="INDEX", default="stocksight_stockprice",
                        help="Index name for Elasticsearch (default: stocksight)")
    parser.add_argument("-d", "--delindex", action="store_true",
                        help="Delete existing Elasticsearch index first")
    parser.add_argument("-s", "--symbol", metavar="SYMBOL",
                        help="Stock symbol to use, example: TSLA")
    parser.add_argument("-f", "--frequency", metavar="FREQUENCY", default=120, type=int,
                        help="How often in seconds to retrieve stock data (default: 120 sec)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Increase output verbosity")
    parser.add_argument("--debug", action="store_true",
                        help="Debug message output")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Run quiet with no message output")
    parser.add_argument("-V", "--version", action="version",
                        version="stocksight v%s" % STOCKSIGHT_VERSION,
                        help="Prints version and exits")
    args = parser.parse_args()

    # set up logging
    logger = logging.getLogger('stocksight')
    logger.setLevel(logging.INFO)
    eslogger = logging.getLogger('elasticsearch')
    eslogger.setLevel(logging.WARNING)
    requestslogger = logging.getLogger('requests')
    requestslogger.setLevel(logging.WARNING)
    logging.addLevelName(
        logging.INFO, "\033[1;32m%s\033[1;0m"
                      % logging.getLevelName(logging.INFO))
    logging.addLevelName(
        logging.WARNING, "\033[1;31m%s\033[1;0m"
                         % logging.getLevelName(logging.WARNING))
    logging.addLevelName(
        logging.ERROR, "\033[1;41m%s\033[1;0m"
                       % logging.getLevelName(logging.ERROR))
    logging.addLevelName(
        logging.DEBUG, "\033[1;33m%s\033[1;0m"
                       % logging.getLevelName(logging.DEBUG))
    logformatter = '%(asctime)s [%(levelname)s][%(name)s] %(message)s'
    loglevel = logging.INFO
    logging.basicConfig(format=logformatter, level=loglevel)
    if args.verbose:
        logger.setLevel(logging.INFO)
        eslogger.setLevel(logging.INFO)
        requestslogger.setLevel(logging.INFO)
    if args.debug:
        logger.setLevel(logging.DEBUG)
        eslogger.setLevel(logging.DEBUG)
        requestslogger.setLevel(logging.DEBUG)
    if args.quiet:
        logger.disabled = True
        eslogger.disabled = True
        requestslogger.disabled = True

    # print banner
    if not args.quiet:
        c = randint(1, 4)
        if c == 1:
            color = '31m'
        elif c == 2:
            color = '32m'
        elif c == 3:
            color = '33m'
        elif c == 4:
            color = '35m'

        banner = """\033[%s

                 /$$                         /$$                 /$$           /$$         /$$
                | $$                        | $$                |__/          | $$        | $$
      /$$$$$$$ /$$$$$$    /$$$$$$   /$$$$$$$| $$   /$$  /$$$$$$$ /$$  /$$$$$$ | $$$$$$$  /$$$$$$
     /$$_____/|_  $$_/   /$$__  $$ /$$_____/| $$  /$$/ /$$_____/| $$ /$$__  $$| $$__  $$|_  $$_/
    |  $$$$$$   | $$    | $$  \ $$| $$      | $$$$$$/ |  $$$$$$ | $$| $$  \ $$| $$  \ $$  | $$
     \____  $$  | $$ /$$| $$  | $$| $$      | $$_  $$  \____  $$| $$| $$  | $$| $$  | $$  | $$ /$$
     /$$$$$$$/  |  $$$$/|  $$$$$$/|  $$$$$$$| $$ \  $$ /$$$$$$$/| $$|  $$$$$$$| $$  | $$  |  $$$$/
    |_______/    \___/   \______/  \_______/|__/  \__/|_______/ |__/ \____  $$|__/  |__/   \___/
                                                                     /$$  \ $$
                           :) = +$   :( = -$                        |  $$$$$$/
                                                                     \______/  v%s
            \033[0m""" % (color, STOCKSIGHT_VERSION)
        print(banner + '\n')

    # set up elasticsearch mappings and create index
    mappings = {
        "mappings": {
            "stock": {
                "properties": {
                    "symbol": {
                        "type": "keyword"
                    },
                    "price_last": {
                        "type": "float"
                    },
                    "price_open": {
                        "type": "float"
                    },
                    "date": {
                        "type": "date"
                    },
                    "price_change": {
                        "type": "float"
                    },
                    "price_high": {
                        "type": "float"
                    },
                    "price_low": {
                        "type": "float"
                    },
                    "vol": {
                        "type": "integer"
                    }
                }
            }
        }
    }

    if args.symbol is None:
        print("No stock symbol, see -h for help.")
        sys.exit(1)

    if args.delindex:
        logger.info('Deleting existing Elasticsearch index ' + args.index)
        es.indices.delete(index=args.index, ignore=[400, 404])

    logger.info(
        'Creating new Elasticsearch index or using existing ' + args.index)
    es.indices.create(index=args.index, body=mappings, ignore=[400, 404])

    # create instance of GetStock
    stockprice = GetStock()

    try:
        # get stock price
        print(args.symbol)
        stockprice.get_price(input_symbol=args.symbol, url=url)
    # except Exception as e:
    #     logger.warning("Exception: Failed to get stock data caused by: %s" % e)
    except KeyboardInterrupt:
        print("Ctrl-c keyboard interrupt, exiting...")
        sys.exit(0)


if __name__ == '__main__':

    # parse cli args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--index", metavar="INDEX", default="stocksight_stockprice",
                        help="Index name for Elasticsearch (default: stocksight)")
    parser.add_argument("-d", "--delindex", action="store_true",
                        help="Delete existing Elasticsearch index first")
    parser.add_argument("-s", "--symbol", metavar="SYMBOL",
                        help="Stock symbol to use, example: TSLA")
    parser.add_argument("-f", "--frequency", metavar="FREQUENCY", default=120, type=int,
                        help="How often in seconds to retrieve stock data (default: 120 sec)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Increase output verbosity")
    parser.add_argument("--debug", action="store_true",
                        help="Debug message output")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Run quiet with no message output")
    parser.add_argument("-V", "--version", action="version",
                        version="stocksight v%s" % STOCKSIGHT_VERSION,
                        help="Prints version and exits")
    args = parser.parse_args()

    # set up logging
    logger = logging.getLogger('stocksight')
    logger.setLevel(logging.INFO)
    eslogger = logging.getLogger('elasticsearch')
    eslogger.setLevel(logging.WARNING)
    requestslogger = logging.getLogger('requests')
    requestslogger.setLevel(logging.WARNING)
    logging.addLevelName(
        logging.INFO, "\033[1;32m%s\033[1;0m"
                      % logging.getLevelName(logging.INFO))
    logging.addLevelName(
        logging.WARNING, "\033[1;31m%s\033[1;0m"
        % logging.getLevelName(logging.WARNING))
    logging.addLevelName(
        logging.ERROR, "\033[1;41m%s\033[1;0m"
        % logging.getLevelName(logging.ERROR))
    logging.addLevelName(
        logging.DEBUG, "\033[1;33m%s\033[1;0m"
        % logging.getLevelName(logging.DEBUG))
    logformatter = '%(asctime)s [%(levelname)s][%(name)s] %(message)s'
    loglevel = logging.INFO
    logging.basicConfig(format=logformatter, level=loglevel)
    if args.verbose:
        logger.setLevel(logging.INFO)
        eslogger.setLevel(logging.INFO)
        requestslogger.setLevel(logging.INFO)
    if args.debug:
        logger.setLevel(logging.DEBUG)
        eslogger.setLevel(logging.DEBUG)
        requestslogger.setLevel(logging.DEBUG)
    if args.quiet:
        logger.disabled = True
        eslogger.disabled = True
        requestslogger.disabled = True

    # print banner
    if not args.quiet:
        c = randint(1, 4)
        if c == 1:
            color = '31m'
        elif c == 2:
            color = '32m'
        elif c == 3:
            color = '33m'
        elif c == 4:
            color = '35m'

        banner = """\033[%s

                /$$                         /$$                 /$$           /$$         /$$
              | $$                        | $$                |__/          | $$        | $$
    /$$$$$$$ /$$$$$$    /$$$$$$   /$$$$$$$| $$   /$$  /$$$$$$$ /$$  /$$$$$$ | $$$$$$$  /$$$$$$
    /$$_____/|_  $$_/   /$$__  $$ /$$_____/| $$  /$$/ /$$_____/| $$ /$$__  $$| $$__  $$|_  $$_/
  |  $$$$$$   | $$    | $$  \ $$| $$      | $$$$$$/ |  $$$$$$ | $$| $$  \ $$| $$  \ $$  | $$
    \____  $$  | $$ /$$| $$  | $$| $$      | $$_  $$  \____  $$| $$| $$  | $$| $$  | $$  | $$ /$$
    /$$$$$$$/  |  $$$$/|  $$$$$$/|  $$$$$$$| $$ \  $$ /$$$$$$$/| $$|  $$$$$$$| $$  | $$  |  $$$$/
  |_______/    \___/   \______/  \_______/|__/  \__/|_______/ |__/ \____  $$|__/  |__/   \___/
                                                                    /$$  \ $$
                          :) = +$   :( = -$                        |  $$$$$$/
                                                                    \______/  v%s
          \033[0m""" % (color, STOCKSIGHT_VERSION)
        print(banner + '\n')

    # set up elasticsearch mappings and create index
    mappings = {
        "mappings": {
            "stock": {
                "properties": {
                    "symbol": {
                        "type": "keyword"
                    },
                    "price_last": {
                        "type": "float"
                    },
                    "date": {
                        "type": "date"
                    },
                    "change": {
                        "type": "float"
                    },
                    "price_high": {
                        "type": "float"
                    },
                    "price_low": {
                        "type": "float"
                    },
                    "vol": {
                        "type": "integer"
                    }
                }
            }
        }
    }

    if args.symbol is None:
        print("No stock symbol, see -h for help.")
        sys.exit(1)

    if args.delindex:
        logger.info('Deleting existing Elasticsearch index ' + args.index)
        es.indices.delete(index=args.index, ignore=[400, 404])

    logger.info(
        'Creating new Elasticsearch index or using existing ' + args.index)
    es.indices.create(index=args.index, body=mappings, ignore=[400, 404])

    # create instance of GetStock
    stockprice = GetStock()

    try:
        # get stock price
        stockprice.get_price(symbol=args.symbol, url=url)
    except Exception as e:
        logger.warning("Exception: Failed to get stock data caused by: %s" % e)
    except KeyboardInterrupt:
        print("Ctrl-c keyboard interrupt, exiting...")
        sys.exit(0)
