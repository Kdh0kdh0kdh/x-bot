import tweepy
import os

def get_client():
    return tweepy.Client(
        bearer_token=os.environ["X_BEARER_TOKEN"],
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"],
    )

def fetch_my_tweets(max_results: int = 100):
    client = get_client()
    user_id = os.environ["X_USER_ID"]

    tweets = client.get_users_tweets(
        id=user_id,
        max_results=max_results,
        tweet_fields=["attachments"],
        expansions=["attachments.media_keys"],
        media_fields=["type"]
    )

    if not tweets.data:
        return []

    media_dict = {}
    if tweets.includes and "media" in tweets.includes:
        for m in tweets.includes["media"]:
            media_dict[m.media_key] = m

    results = []
    for t in tweets.data:
        results.append({
            "id": t.id,
            "text": t.text,
            "attachments": t.attachments,
            "media": [media_dict.get(k) for k in (t.attachments["media_keys"] if t.attachments else [])]
        })

    return results
