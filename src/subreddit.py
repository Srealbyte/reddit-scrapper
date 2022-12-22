import praw
import math
import pandas as pd
from datetime import datetime
import re
import time
from tqdm import tqdm
tqdm.pandas()
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

user_agent="agent01"
reddit = praw.Reddit(username="No-Professional-8030",
                     password="Tutorial01",
                     client_id="2MS-Ef8sTpSYzdbqEpIxAg",
                     client_secret="Cnht4sjg8xG0EZTaPI8Yk0Kn3zGKqw",
                     user_agent=user_agent
)
subreddit_name="buildapcsales"
subreddit = reddit.subreddit(subreddit_name)

hot_subreddit=subreddit.hot()

df = pd.DataFrame()
post=[]
type = ''
price = 0.00
item = ''
regex= r"\[([^\]]+)\](.+?)(\$\d+)"
for submission in subreddit.hot():
    if(submission.id in ('yvocv1','z2atkk')):
        continue
    result = re.search(r'\[([^\]]+)\](.+?)(\$\d+\.?\d+)', submission.title)
    type=result.group(1)
    item=result.group(2).lstrip()
    price=result.group(3)
    post.append([submission.id,type,item,price,submission.score,submission.url,submission.created])

post = pd.DataFrame(post,columns=['id','Type','Item','Price','score','url','Time Created'])

def get_comments(submission_id):
    submission = reddit.submission(submission_id)
    comments = []
    for top_level_comment in submission.comments:
        comments.append(top_level_comment.body)
        
    comment = ' '.join(comments)
    comment = comment.replace("\n",' ')
    return comment


def sentiment_scores(sentence):

    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    
    if sentiment_dict['compound'] >= 0.05 :
        return "Positive"
    elif sentiment_dict['compound'] <= - 0.05 :
        return "Negative"
    else :
        return "Neutral"
    
    
def get_date_time(x):
    return datetime.fromtimestamp(x)

def get_post_hours(x):
    return (time.time() - x)/3600

def search_item(x):
    return any([True if i.lower() in x.lower() else False for i in item.split()])


post['Comment'] = post['id'].progress_apply(lambda x: get_comments(x))


post['Sentiment'] = post['Comment'].progress_apply(lambda x: sentiment_scores(x))


post['Time Created1'] = post['Time Created'].progress_apply(lambda x: get_date_time(x))


post['LikesPerHour'] = post.progress_apply(lambda x: math.ceil(x['score']/get_post_hours(x['Time Created'])),axis=1)

post.rename(columns={'score':'Overall Likes'},inplace=True)

post.drop(['Time Created'],axis=1,inplace=True)

post.rename(columns={'Time Created1':'Post Datetime'},inplace=True)

n = int(input("How many likes per hour ratio does the post have: "))
item = input("What type of sale item are they looking for: ")

post_filtered = post[post['LikesPerHour']>=n]

post_filtered = post_filtered[post_filtered['Type'].apply(lambda name: search_item(name))]
#print(post)
print(post_filtered)

post_filtered.to_csv('post.csv',index=False)


