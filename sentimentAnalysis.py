import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from nltk.sentiment.util import *
from nltk import tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
snowballstemmer = SnowballStemmer("english")
stopwords = stopwords.words('english')
analyzer = SentimentIntensityAnalyzer()

def tweet_cleaner(tweet):
    """
    This function removes any unnecessary characters from the tweet before
    any further processing (tokenization and stopword).

    Parameter tweet: must be a string.
    """
    tweet = re.sub(r'@[A-Za-z0-9_]+','', tweet)
    tweet = re.sub(r"http\S+", "", tweet)
    tweet = re.sub(r"[0-9]*", "", tweet)
    tweet = re.sub(r"(”|“|-|\+|`|#|,|;|\|)*", "", tweet)
    tweet = re.sub(r"&amp", "", tweet)
    tweet = tweet.lower().strip()
        
    return tweet

def tweet_stopword_stem(tweet):
    """
    This function tokenizes the tweet (string) and removes all stopwords.
    It will create two results: token tweet where stopwords are removed and
    snowball stem token tweet where in addition to stopwords, the words are
    snowball stemmed. The two tweets are put back together (detokenized) and
    returned.

    Parameter tweet: must be a string.
    """
    # initialize token and snowball stem token tweet lists
    token_tweet = []
    snowballstemmer_token_tweet = []

    # tokenize the tweet
    tokens = nltk.word_tokenize(tweet)

    # append only non-stopwords to lists
    for token in tokens:
        if token not in stopwords:
            token_tweet.append(token)
            snowballstemmer_token_tweet.append(snowballstemmer.stem(token))

    # return detokenized tweets
    return TreebankWordDetokenizer().detokenize(token_tweet), TreebankWordDetokenizer().detokenize(snowballstemmer_token_tweet)

def sentiment_score(tweet):
    """
    This function will create sentiment scores based on the given tweet.
    An additional key will be added to the sentiment dictionary with the
    results: Positive, Negative or Neutral.

    Parameter tweet: must be a string.
    """
    # create a SentimentIntensityAnalyzer object.
    sentiment_analyzer = SentimentIntensityAnalyzer()

    # generate sentiment analysis scores
    tweet_score = sentiment_analyzer.polarity_scores(tweet)

    # add new key into score dictionary with result
    if tweet_score['compound'] >= 0.05:
        tweet_score['result'] = "Positive"
    elif tweet_score['compound'] <= -0.05:
        tweet_score['result'] = "Negative"
    else:
        tweet_score['result'] = "Neutral"

    return tweet_score

def generate_sentiment_scores(tweet):
    """
    This function will process a tweet and produce three separate sentiment
    dictionaries based on the original tweet, tokenized tweet and the tokenized
    and snowball stemmed tweet.

    Parameter tweet: must be a string.
    """
    # generate sentiment analysis scores for original tweet
    original_tweet_score = sentiment_score(tweet)

    # clean, tokenize and remove stopwords for tweet
    # generate sentiment analysis scores for tokenized tweet
    token_tweet, snowballstemmer_token_tweet = tweet_stopword_stem(tweet_cleaner(tweet))
    token_tweet_score = sentiment_score(token_tweet)
    snowballstemmer_token_tweet_score = sentiment_score(snowballstemmer_token_tweet)

    return original_tweet_score, token_tweet_score, snowballstemmer_token_tweet_score
