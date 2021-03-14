#import packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tweepy
import json


df=pd.read_csv('twitter-archive-enhanced-2.csv',parse_dates=['timestamp'])

#remove unwanted columns
df.drop(columns=['in_reply_to_status_id','in_reply_to_user_id','retweeted_status_id','retweeted_status_user_id','retweeted_status_timestamp','expanded_urls'],inplace=True)

#combining the four stage columns in one column
df['stage']=df['doggo']+df['floofer']+df['pupper']+df['puppo']
df['stage'].value_counts()

#Ref.: https://www.amazon.com/WeRateDogs-Most-Hilarious-Adorable-Youve/dp/1510717145
stageMap={'NoneNoneNoneNone':'puppo','doggoNonepupperNone':'puppo','doggoflooferNoneNone':'doggo',
         'doggoNoneNonepuppo':'doggo','NoneflooferNoneNone':'doggo','NoneNonepupperNone':'pupper',
         'doggoNoneNoneNone':'doggo','NoneNoneNonepuppo':'puppo'}
df['stage']=df['stage'].map(stageMap)

#clipping  rating_numerator values to make sense
df['rating_numerator']=np.clip(df['rating_numerator'],a_min=10,a_max=20)
df['rating_denominator']=np.clip(df['rating_denominator'],a_min=10,a_max=10)

# download tweets from  api 
""" consumer_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
consumer_secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
tweets=[]
failedIds=[]
for id in df['tweet_id']:
    try:
        tweets.append(api.get_status(id))
        print('appending id: '+str(id)+"\n")
    except:
        failedIds.append(id)
        print('id: '+str(id)+" not found\n")
with open('failed_ids.txt', 'a+') as outfile:
    for failed_id in failedIds:
        outfile.write(str(failed_id)+'\n')
with open('tweet_json.txt', 'a+') as outfile:
    for tweet in tweets:
        json.dump(tweet._json, outfile)
        outfile.write('\n') """

#load failed api ids
file = open('failed_ids.txt', 'r')
lines=file.readlines()
failedIds=[]
for line in lines:
    failedIds.append(int(line.strip()))

#load tweets
file = open('tweet_json.txt', 'r')
lines=file.readlines()
retweet_count=[]
failed_retweet_count=[]
favorite_count=[]
failed_favorite_count=[]
for line in lines:
    try:
        retweet_count.append(json.loads(line.strip())['retweet_count'])
    except:
        failed_retweet_count.append(json.loads(line.strip())['tweet_id'])
    try:
        favorite_count.append(json.loads(line.strip())['favorite_count'])
    except:
        failed_favorite_count.append(json.loads(line.strip())['tweet_id'])

df=df[~df.tweet_id.isin(failedIds)]
df['retweet_count']=retweet_count
df['favorite_count']=favorite_count

df_image_prediction=pd.read_csv('image-predictions.tsv', sep='\t')
df_image_prediction['total_sucsess']=df_image_prediction['p1_dog'] | df_image_prediction['p2_dog'] | df_image_prediction['p3_dog']
df_image_prediction['total_sucsess'].value_counts()


#calc total p for df_image_prediction
"""def best_p(confs,ps):
    return ps[confs.index(max(confs))]
    
failedPredectionIds=[]
total_p=[]
for index,row in df_image_prediction.iterrows():
    if(row.total_sucsess):
        total_p.append(best_p([row.p1_conf,row.p2_conf,row.p3_conf],[row.p1,row.p2,row.p3]))
    else:
        total_p.append('None')
        failedPredectionIds.append(row.tweet_id)

with open('failed_prediction_ids.txt', 'a+') as outfile:
    for id in failedPredectionIds:
        outfile.write(str(id)+'\n')
with open('total_p_prediction.txt', 'a+') as outfile:
    for p in total_p:
        outfile.write(str(p)+'\n')"""

#load toptal_p
total_p=[]
file = open('total_p_prediction.txt', 'r')
lines=file.readlines()
for line in lines:
    total_p.append(line)
df_image_prediction['total_p']=total_p
#load failed_prediction_ids
file = open('failed_prediction_ids.txt', 'r')
lines=file.readlines()
failedPredictionIds=[]
for line in lines:
    failedPredictionIds.append(int(line.strip()))
df=df[~df.tweet_id.isin(failedPredictionIds)]


#calc total_p for df
"""df_p=[]
missingPredectionIds=[]
for index,row in df.iterrows():
    try:
        x=df_image_prediction[df_image_prediction['tweet_id']==int(row.tweet_id)].reset_index()['total_p'].iloc[0]
        df_p.append(str(x).strip().lower())
        print('id '+str(row.tweet_id)+' done')
    except Exception as e:
        print(str(e))
        print('id '+str(row.tweet_id)+' missing')
        missingPredectionIds.append(str(row.tweet_id))
        
with open('missing_prediction_ids.txt', 'a+') as outfile:
    for id in missingPredectionIds:
        outfile.write(str(id)+'\n')
with open('df_p.txt', 'a+') as outfile:
    for p in df_p:
        outfile.write(str(p)+'\n')"""

#load total_p for df
file = open('missing_prediction_ids.txt', 'r')
lines=file.readlines()
missingPredectionIds=[]
for line in lines:
    missingPredectionIds.append(int(line.strip()))

file = open('df_p.txt', 'r')
lines=file.readlines()
df_p=[]
for line in lines:
    df_p.append(line.strip())

df=df[~df.tweet_id.isin(missingPredectionIds)]
df['total_p']=df_p

df.to_csv('df_final.csv') 


