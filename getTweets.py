import tweepy as tw
import pandas as pd
from iso639 import languages
from datetime import datetime, timezone
import config
import sentimentAnalysis

# retrieve keys from config
api_key = config.api_key
api_secret = config.api_secret
bearer_token = config.bearer_token
access_token = config.access_token
access_token_secret = config.access_token_secret

# initialize and authenticate
client = tw.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
auth = tw.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tw.API(auth)

# define tweet parameters
tweet_fields = ['author_id', 'lang', 'source', 'geo', 'entities', 'public_metrics','context_annotations', 'created_at']
user_fields = ['profile_image_url']
expansions = ['author_id', 'geo.place_id', 'referenced_tweets.id', 'attachments.media_keys']
place_fields = ['place_type','geo']

def search_recent_tweets(query_list):
    """
    Returns a dataframe containing all tweets retrieved based on query(ies) found in query_list.
    This function will retrieve the maximum of 100 tweets per query in query_list.
    
    Parameter query_list: must be a list.
    Precondition: query_list must be a non-empty list.
    """

    # list to store tweets
    dataFrame = []

    # iterate and retrieve tweets per query in query_list
    for query in query_list:
        print(query)
        # retrieve tweets
        tweets = client.search_recent_tweets(query = query,
                                            tweet_fields = tweet_fields,
                                            user_fields = user_fields,
                                            expansions = expansions,
                                            place_fields = place_fields,
                                            max_results = 100)

        # get users list from the includes object
        users = {u["id"]: u for u in tweets.includes["users"]}

        # iterate through retrieved tweets
        for tweet in tweets.data:

            # check if tweet has location data and store it if there are
            if tweet.geo is not None:
                location = api.geo_id(tweet.geo["place_id"]).full_name
            else:
                location = "N/A"

            # convert language from BCP47 language tag to readable format
            try:
                lang = "{} ({})".format(languages.get(alpha2 = tweet.lang).name, tweet.lang)
            except:
                lang = "Unknown ({})".format(tweet.lang)

            # build and retrieve fields to capture
            user = users[tweet.author_id]
            tweet_id = tweet.id
            user_id = tweet.author_id
            username = user.username
            tweet_text = tweet.text
            created_at = tweet.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None) # change to local time
            source = tweet.source   

            # public metrics
            reply_count = tweet.public_metrics["reply_count"]
            retweet_count = tweet.public_metrics["retweet_count"]
            like_count = tweet.public_metrics["like_count"]
            quote_count = tweet.public_metrics['quote_count']

            # user profile and url of tweet
            user_profile_url = "https://twitter.com/{}".format(username)
            tweet_url = "https://twitter.com/{}/status/{}".format(username, tweet_id)

            # retrieve tweet entities
            if tweet.entities:
                entities = tweet.entities

                # retrieve hashtags
                if "hashtags" in entities:
                    entities_hashtags = entities["hashtags"]
                    hashtags = "#{}".format(entities_hashtags[0]["tag"])

                    if len(entities_hashtags) > 1:
                        for hashtag in entities_hashtags[1:]:
                            hashtags = hashtags + "\n#{}".format(hashtag["tag"])
                else:
                    hashtags = "N/A"

                # retrieve urls
                if "urls" in entities:
                    entities_urls = entities["urls"]
                    urls = "{}".format(entities_urls[0]["expanded_url"])

                    if len(entities_urls) > 1:
                        for url in entities_urls[1:]:
                            urls = urls + "\n{}".format(url["expanded_url"])
                else:
                    urls = "N/A"
                
                # retrieve mentions
                if "mentions" in entities:
                    entities_mentions = entities["mentions"]
                    mentions = "@{} (user_id: {})".format(entities_mentions[0]["username"], entities_mentions[0]["id"])

                    if len(entities_mentions) > 1:
                        for mention in entities_mentions[1:]:
                            mentions = mentions + "\n@{} (user_id: {})".format(mention["username"], mention["id"])
                else:
                    mentions = "N/A"

            # check for referenced tweets (retweets, replies and quotes)
            if tweet.referenced_tweets:
                referenced_tweet_type = tweet.referenced_tweets[0].type
                original_tweet_id = str(tweet.referenced_tweets[0].id)

                # wrap TooManyRequests to salvage dataframe
                try:
                    original_tweet = client.get_tweet(original_tweet_id, tweet_fields = tweet_fields, expansions = expansions)
                except tw.TooManyRequests:
                    return dataFrame

                # if tweet text is truncated
                if tweet_text[-1:] == '…':
                    # retrieve full tweet text
                    tweet_text = "RT @{}: {}".format(original_tweet.includes["users"][0].username, original_tweet.data.text)

                # Wrapped to handle NoneType
                try:
                    # retrieve metrics of referenced tweet
                    reference_reply_count = original_tweet.data.public_metrics["reply_count"]
                    reference_retweet_count = original_tweet.data.public_metrics["retweet_count"]
                    reference_like_count = original_tweet.data.public_metrics["like_count"]
                    reference_quote_count = original_tweet.data.public_metrics["quote_count"]
                except:
                    reference_reply_count = reference_retweet_count = reference_like_count = reference_quote_count = "N/A"

                # retrieve original tweet link and user profile
                reference_user_profile_url = "https://twitter.com/{}".format(original_tweet.includes['users'][0].username)
                reference_tweet_url = "https://twitter.com/{}/status/{}".format(original_tweet.includes['users'][0].username, original_tweet_id)
            else:
                # set up default values for original tweets
                referenced_tweet_type = "original"
                reference_reply_count = reference_retweet_count = reference_like_count = reference_quote_count = reference_user_profile_url = reference_tweet_url = "N/A"

            # generate sentiment analysis scores
            original, token, stem = sentimentAnalysis.generate_sentiment_scores(tweet_text)

            # append tweet to dataframe
            dataFrame.append([tweet_id, user_id, username, tweet_text, created_at, location, lang, source, original['compound'], 
                                original['result'], token['compound'], token['result'], stem['compound'], stem['result'],
                                reply_count, retweet_count, like_count, quote_count, hashtags, urls, mentions, referenced_tweet_type, 
                                reference_reply_count, reference_retweet_count, reference_like_count, reference_quote_count, 
                                user_profile_url, tweet_url, reference_user_profile_url, reference_tweet_url])

    return dataFrame

# set up dataframe fields/parameters
columns = ["tweet_id",
            "user_id",
            "username",
            "tweet_text",
            "created_at",
            "location",
            "lang",
            "source",
            "sentiment_original_compound",
            "sentiment_original_result",
            "sentiment_token_compound",
            "sentiment_token_result",
            "sentiment_stem_compound",
            "sentiment_stem_result",
            "reply_count",
            "retweet_count",
            "like_count",
            "quote_count",
            "hashtags",
            "urls",
            "mentions",
            "referenced_tweet_type",
            "reference_reply_count",
            "reference_retweet_count",
            "reference_like_count",
            "reference_quote_count",
            "user_profile_url",
            "tweet_url",
            "reference_user_profile_url",
            "reference_tweet_url"]

# call function to retrieve tweets in a list
print("Retrieve tweets.")
query_list = ['Fred VanVleet', 'Scottie Barnes', 'O.G. Anunoby', 'Gary Trent Jr.']
dataFrame = search_recent_tweets(query_list)

# create dataframe and create csv
tweets = pd.DataFrame(dataFrame, columns = columns)
tweets.to_csv("getTweets_{}.csv".format(datetime.today().strftime("%Y-%m-%d")), index = False)
print("Done.")
