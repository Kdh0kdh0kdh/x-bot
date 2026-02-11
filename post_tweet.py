import os
import requests
import tweepy

def get_client():
    return tweepy.Client(
        bearer_token=os.environ["X_BEARER_TOKEN"],
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"],
    )

def post(text: str, image_url: str | None = None):
    client = get_client()

    media_ids = None

    if image_url:
        # 画像を一時ダウンロード
        img_data = requests.get(image_url).content
        with open("temp.jpg", "wb") as f:
            f.write(img_data)

        # X にアップロード
        media = client.media_upload(filename="temp.jpg")
        media_ids = [media.media_id]

    # ★ RTではなく「新規投稿」
    client.create_tweet(
        text=text,
        media_ids=media_ids
    )
