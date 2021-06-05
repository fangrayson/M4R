"""
Title: Data Exploration

Description: Exploring the Training, US Election, and Georgia Election datasets
This includes:
    i.   Comparing features of the datasets to check if the training dataset is representative of the collected datasets
    ii.  Comparing proportions of humans and bots in the datasets
    iii. Checking statistics of the datasets to check how representative of all Twitter users the Georgia and US tweets are
"""

# 1. SETUP --------------------------------------------------------------------
import pickle, sys, datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import seaborn as sns
from imblearn.combine import SMOTEENN
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import AdaBoostClassifier
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sns.set(font="Arial") # Setting the plot style
m4r_data = "C:\\Users\\fangr\\Documents\\Year 4\\M4R\\m4r_data\\" # folder location where data is held
# Importing Account Level Detection
sys.path.insert(1, "C:\\Users\\fangr\\Documents\\Year 4\\M4R\\m4r_repository")
from account_level_detection import get_full_dataset, features
figure_path = "C:\\Users\\fangr\\Documents\\Year 4\\M4R\\Report\\Figures\\" # folder location to store files


# i. 
def comparing_to_training_set():
    """
    Comparing some features of the dataset in order to check that the training dataset
    is representative of the US and Georgia datasets
    """
    # Load the user data of each dataset:
    us = (pickle.load(open(m4r_data + "us_election_tweets.p", "rb"))).groupby("user.id").first().reset_index()
    ga = (pickle.load(open(m4r_data + "georgia_election_tweets.p", "rb"))).groupby("user.id").first().reset_index()
    trainset = pickle.load(open(m4r_data + "balanced_account_training_data.p", "rb"))
    
    # Plotting the follower counts of each of the datasets as a boxplot:
    follower_data = pd.DataFrame({
        "US" : us["user.followers_count"],
        "Georgia" : ga["user.followers_count"],
        "Training" : trainset["user.followers_count"]
        })
    plt.figure(figsize=(6, 6))
    sns.boxplot(
        data = follower_data,
        );
    plt.yscale("symlog"); plt.ylim(0, 1e9); plt.title("Comparing User Followers", fontweight = "bold")
    plt.xlabel("Account Dataset", fontweight = "bold"); plt.ylabel("User Follower Count", fontweight = "bold")
    #plt.savefig(figure_path + "compare_datasets_follower_count.pdf", bbox_inches = "tight")
    plt.show()
    
    # Plotting the lengths of the user descriptions for each of the datasets as a boxplot:
    description_data = pd.DataFrame({
        "US" : us["user.description.length"],
        "Georgia" : ga["user.description.length"],
        "Training" : trainset["user.description.length"]
        })
    plt.figure(figsize=(6, 6))
    sns.boxplot(
        data = description_data,
        );
    plt.title("Comparing User Description Lengths", fontweight = "bold")
    plt.xlabel("Account Dataset", fontweight = "bold"); plt.ylabel("User Description Length", fontweight = "bold")
    #plt.savefig(figure_path + "compare_datasets_description_length.pdf", bbox_inches = "tight")
    plt.show()

# ii.
def proportions_of_bots_and_humans():
    """
    Comparing the proportions of bots to humans for the US and Georgia datasets for:
        1. all of the (unique) users
        2. all of the tweets
        3. all of the retweets
        4. all of the replies
    """
    # Loading the US or Georgia election dataset: (change file name to choose)
    df = pickle.load(open(m4r_data + "us_election_tweets.p", "rb"))
    # Retrieving the unique users:
    userdf = df.groupby("user.id").first()
    # Retrieving the retweets:
    retweetdf = df[["retweeted_status.id", "predicted_class"]].dropna()
    # Retrieving the replies:
    replydf = df[["in_reply_to_status_id", "predicted_class"]].dropna()
    
    # Setting colours and fonts
    c = ["#83C9F1" , "#FED28F"]
    t = {'fontsize': 15, "fontweight" : "bold"}
    
    # Plotting 4 pie charts
    fig, axes = plt.subplots(1, 4, figsize=(8, 4))
    fig.suptitle('Proportions of Humans and Bots in the US Election Dataset', fontweight = "bold", y = 0.8)
    # PROPORTION OF USERS PIE CHART
    axes[0].set_title("Accounts", fontweight = "bold");
    h = sum(userdf["predicted_class"] == "human")
    b = sum(userdf["predicted_class"] == "bot")
    counts = [h, b]
    axes[0].pie(counts, autopct='%1.2f%%', colors = c, textprops=t)
    
    # PROPORTION OF TWEETS PIE CHART
    axes[1].set_title("Tweets", fontweight = "bold");
    h = sum(df["predicted_class"] == "human")
    b = sum(df["predicted_class"] == "bot")
    counts = [h, b]
    axes[1].pie(counts, autopct='%1.2f%%', colors = c, textprops=t)
    
    # PROPORTION OF RETWEETS PIE CHART
    axes[2].set_title("Retweets", fontweight = "bold");
    h = sum(retweetdf["predicted_class"] == "human")
    b = sum(retweetdf["predicted_class"] == "bot")
    counts = [h, b]
    axes[2].pie(counts, autopct='%1.2f%%', colors = c, textprops=t)
    
    # PROPORTION OF REPLIES PIE CHART
    axes[3].set_title("Replies", fontweight = "bold");
    h = sum(replydf["predicted_class"] == "human")
    b = sum(replydf["predicted_class"] == "bot")
    counts = [h, b]
    axes[3].pie(counts, autopct='%1.2f%%', colors = c, textprops=t)
        
    # Adding a legend
    handles, labels = axes[0].get_legend_handles_labels()
    orange_patch = mpatches.Patch(color=c[1], label='Bot')
    blue_patch = mpatches.Patch(color=c[0], label='Human')
    plt.legend(handles=[blue_patch, orange_patch], bbox_to_anchor=(1, 0.9))
    
    plt.subplots_adjust(wspace = 0.05, hspace = -0.5)
    #plt.savefig(figure_path + "proportions_pie_chart_us.pdf", bbox_inches = "tight")
    plt.show()
    
# iii.
def exploring_user_distribution():
    """
    Printing out statistics for each of the US and Georgia datasets:
        1. Number of Unique Users
        2. Number of Unique Verified Users
        3. How many tweets the top 10% of users produced
        4. The mean number of followers for an account in the dataset
    """
    # Loading US or Georgia data:
    us = (pickle.load(open(m4r_data + "georgia_election_tweets.p", "rb")))
    us["tweet_count"] = 1
    # Retrieving unique users:
    user_features = ['user.created_at', 'user.name', 'user.screen_name', 'user.description',
       'user.lang', 'user.verified', 'user.geo_enabled',
       'user.default_profile', 'user.default_profile_image',
       'user.followers_count', 'user.friends_count', 'user.listed_count',
       'user.favourites_count', 'user.statuses_count', "predicted_class"]
    us_users = us.groupby("user.id").first()[user_features]
    us_users = us_users.merge(us[["user.id", "tweet_count"]].groupby("user.id").count().reset_index(), how = "left", on = "user.id")
    
    # Printing the number of unique users:
    print("There are " + str(len(us_users)) + " unique users")
    # Printing the number of unique verified users:
    print("Out of this, there are " + str(sum(us_users["user.verified"])) + " verified users")
    # Printing the number of tweets the top 10% of users produced:
    print("The top 10% of Users Produced "
          + str( sum(us_users["tweet_count"].sort_values().tail(int(len(us_users) * 0.1))) )
          + " of the tweets in the dataset")
    # Printing the average number of followers for the dataset:
    print("The average number of followers the accounts have is " + str(np.mean(us_users["user.followers_count"])))
    
    