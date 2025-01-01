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
    """
    Fetch Reddit data for specified subreddits and days.
    Finds words matching the pattern (all-caps, 3-5 characters) in titles and comments.

    Args:
        reddit: Initialized Reddit instance.
        subreddits: List of subreddit names to fetch data from.
        days_to_scan: Number of days to look back.

    Returns:
        A dictionary where keys are words and values are lists of timestamps.
    """
    word_occurrences = defaultdict(set)  # Use a set to ensure unique timestamps
    pattern = r'\b[A-Z]{3,5}\b'  # Match all-cap words (3-5 characters)
    start_time = datetime.utcnow() - timedelta(days=days_to_scan)

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.new(limit=100):  # Adjust limit for performance
            post_time = datetime.utcfromtimestamp(post.created_utc)
            if post_time > start_time:
                # Extract words from the post title
                words_in_title = re.findall(pattern, post.title)
                for word in words_in_title:
                    word_occurrences[word].add(post_time)

                # Extract words from the comments
                try:
                    post.comments.replace_more(limit=0)
                    for comment in post.comments.list():
                        comment_time = datetime.utcfromtimestamp(comment.created_utc)
                        if comment_time > start_time:
                            words_in_comment = re.findall(pattern, comment.body)
                            for word in words_in_comment:
                                word_occurrences[word].add(comment_time)
                except Exception as e:
                    print(f"Error processing comments for post '{post.title}': {e}")

    # Convert sets back to lists for saving to the database
    return {word: list(timestamps) for word, timestamps in word_occurrences.items()}
