# Sentiment-Analysis-of-Tweets
A continuation of the Get Tweets project where Sentiment Analysis is applied to every tweet retrieved. A score is determined, and result is derived from the score.

# Sentiment Analysis
Sentiment Analysis is the process where a piece of text (a tweet in this case) is analyzed to determine whether it is positive, negative, or neutral.

I will be incorporating sentiment analysis into my original [Get-Tweets]( https://github.com/jsue7/Get-Tweets) project. Drawing on user [yenchenchou’s]( https://github.com/yenchenchou) [Sentiment Analysis on NBA players’ Twitter Accounts](https://github.com/yenchenchou/Sentiment-Analysis-on-NBA-players-s-Twitter-aacount#part3-sentiment-analysis) project, I will utilize his analysis method and modify his code to fit my existing [getTweets.py]( https://github.com/jsue7/Get-Tweets/blob/main/getTweets.py) code.

The result is [sentimentAnalysis.py](https://github.com/jsue7/Sentiment-Analysis-of-Tweets/blob/main/sentimentAnalysis.py) where it contains the functions used to perform sentiment analysis on the original tweet, tokenized tweet, and snowstemmed tweet.

# Output

This script will produce a .csv file containing all Tweets retrieved per topic of interest. Each record in the .csv file corresponds to single Tweet. This is largely the same except for a couple new fields. The table below describes the new fields.

| Field  | Field Description |
| :---: | --- |
| sentiment_original_compound| The sentiment compound score of the original tweet.|
| sentiment_original_result | The result based on the sentiment compound score of the original tweet.|
| sentiment_token_compound | The sentiment compound score of the tokenized tweet. |
| sentiment_token_result | The result based on the sentiment compound score of the tokenized tweet.|
| sentiment_stem_compound | The sentiment compound score of the snowballstemmed tweet.|
| sentiment_stem_result | The result based on the sentiment compound score of the snowballstemmed tweet. |

# Conclusions
Sentiment Analysis is a quick and easy way to analyze a large amount of text such as Tweets to quickly determine the “sentiment” (positive, negative, or neutral). The sentiment results can be used determine the overall result of the query and mapped out using data visualization.
