import praw
import re
from datetime import datetime, timedelta
from collections import defaultdict

# Initialize Reddit API
def initialize_reddit():
    return praw.Reddit(
        client_id="rIAs8ccsw-b7WTS5iWYJrg",
        client_secret="LOqxTB2SqPxGHNQy0c15NNOv60O-yw",
        user_agent="Reddit Word Tracker v1"
    )

# Fetch data from Reddit
def fetch_reddit_data(reddit, subreddits, days_to_scan):
    word_occurrences = defaultdict(list)
    pattern = r'\b[A-Z]{3,5}\b'  # Match all-cap words (3-5 characters)
    start_time = datetime.utcnow() - timedelta(days=days_to_scan)
    
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        
        for post in subreddit.new(limit=100):  # Reduce limit for faster fetching
            post_time = datetime.utcfromtimestamp(post.created_utc)
            if post_time > start_time:
                # Find matches in the post title
                words_in_title = re.findall(pattern, post.title)
                for word in words_in_title:
                    word_occurrences[word].append(post_time)
                
                # Check all comments for matches, but only for recent posts
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    words_in_comment = re.findall(pattern, comment.body)
                    for word in words_in_comment:
                        word_occurrences[word].append(datetime.utcfromtimestamp(comment.created_utc))
    
    return word_occurrences

