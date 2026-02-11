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
    """
    自分のツイートを取得し、
    『本文＋画像URL』の形で返す
    """
    client = get_client()
    user_id = os.environ["X_USER_ID"]

    tweets = client.get_users_tweets(
        id=user_id,
        max_results=max_results,
        tweet_fields=["attachments", "created_at"],
        expansions=["attachments.media_keys"],
        media_fields=["url", "type"]   # ★ url を取得するのがポイント
    )

    if not tweets.data:
        return []

    # media_key -> mediaオブジェクト のマッピング
    media_dict = {}
    if tweets.includes and "media" in tweets.includes:
        for m in tweets.includes["media"]:
            media_dict[m.media_key] = m

    results = []
    for t in tweets.data:
        image_url = None

        # 画像がある場合、最初の画像URLを取得
        if t.attachments and "media_keys" in t.attachments:
            media = media_dict.get(t.attachments["media_keys"][0])
            if media and media.type == "photo":
                image_url = media.url

        results.append({
            "id": t.id,
            "text": t.text,
            "image_url": image_url,   # ★ ここが重要
            "created_at": t.created_at,
        })

    return results
