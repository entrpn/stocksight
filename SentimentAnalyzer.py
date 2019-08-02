from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

import sys
import six


class SentimentAnalyzer:

    def __init__(self):
        self.client = language.LanguageServiceClient()

    def classify_content(self, text):
        if len(text.split()) <= 20:
            return

        if isinstance(text, six.binary_type):
            text = text.decode('utf-8')

        document = types.Document(
            content=text.encode('utf-8'),
            type=enums.Document.Type.PLAIN_TEXT)

        categories = self.client.classify_text(document).categories

        for category in categories:
            print(u'=' * 20)
            print(u'{:<16}: {}'.format('name', category.name))
            print(u'{:<16}: {}'.format('confidence', category.confidence))

    def google_analyze(self, text):
            # Instantiates a client
        self.classify_content(text)
        # client = language.LanguageServiceClient()
        # document = types.Document(
        #     content=text,
        #     type=enums.Document.Type.PLAIN_TEXT)

        # # Detect and send native Python encoding to receive correct word offsets.
        # encoding = enums.EncodingType.UTF32
        # if sys.maxunicode == 65535:
        #     encoding = enums.EncodingType.UTF16

        # # Detects the sentiment of the text
        # print('getting sentiment')
        # sentiment = client.analyze_sentiment(
        #     document=document).document_sentiment

        # print('Text: {}'.format(text))
        # print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))

        # result = client.analyze_entity_sentiment(document, encoding)

        # for entity in result.entities:
        #     print('Mentions: ')
        #     print(u'Name: "{}"'.format(entity.name))
        #     for mention in entity.mentions:
        #         print(u'  Begin Offset : {}'.format(mention.text.begin_offset))
        #         print(u'  Content : {}'.format(mention.text.content))
        #         print(u'  Magnitude : {}'.format(mention.sentiment.magnitude))
        #         print(u'  Sentiment : {}'.format(mention.sentiment.score))
        #         print(u'  Type : {}'.format(mention.type))
        #     print(u'Salience: {}'.format(entity.salience))
        #     print(u'Sentiment: {}\n'.format(entity.sentiment))

    def analyze(self, text):
        """Determine if sentiment is positive, negative, or neutral
        algorithm to figure out if sentiment is positive, negative or neutral
        uses sentiment polarity from TextBlob, VADER Sentiment and
        sentiment from text-processing URL
        could be made better :)
        """
        # pass text into TextBlob
        text_tb = TextBlob(text)

        # pass text into VADER Sentiment
        analyzer = SentimentIntensityAnalyzer()
        text_vs = analyzer.polarity_scores(text)

        if text_tb.sentiment.polarity <= 0 and text_vs['compound'] <= -0.5:
            sentiment = "negative"  # very negative
        elif text_tb.sentiment.polarity <= 0 and text_vs['compound'] <= -0.1:
            sentiment = "negative"  # somewhat negative
        elif text_tb.sentiment.polarity == 0 and text_vs['compound'] > -0.1 and text_vs['compound'] < 0.1:
            sentiment = "neutral"
        elif text_tb.sentiment.polarity >= 0 and text_vs['compound'] >= 0.1:
            sentiment = "positive"  # somewhat positive
        elif text_tb.sentiment.polarity > 0 and text_vs['compound'] >= 0.1:
            sentiment = "positive"  # very positive
        else:
            sentiment = "neutral"

        print(text)
        # calculate average polarity from TextBlob and VADER
        polarity = (text_tb.sentiment.polarity + text_vs['compound']) / 2
        # output sentiment polarity
        print("Sentiment Polarity: " + str(polarity))

        # output sentiment subjectivity (TextBlob)
        print("Sentiment Subjectivity: " + str(text_tb.sentiment.subjectivity))

        print("Sentiment (algorithm): " + str(sentiment))
        print()

        return polarity, text_tb.sentiment.subjectivity, sentiment
