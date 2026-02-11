import os
import sqlite3
import requests
import tweepy
import random

# 設定
DB_PATH = "posted.db"

def get_clients():
    """API v1.1(画像用)とv2(投稿用)の両方のクライアントを返す"""
    auth = tweepy.OAuth1UserHandler(
        os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_SECRET"]
    )
    api_v1 = tweepy.API(auth)
    
    client_v2 = tweepy.Client(
        bearer_token=os.environ["X_BEARER_TOKEN"],
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"]
    )
    return api_v1, client_v2

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS posted_tweets (tweet_id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

def is_already_posted(tweet_id):
    conn = sqlite3.connect(DB_PATH)
    res = conn.execute("SELECT 1 FROM posted_tweets WHERE tweet_id = ?", (tweet_id,)).fetchone()
    conn.close()
    return res is not None

def mark_as_posted(tweet_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO posted_tweets (tweet_id) VALUES (?)", (tweet_id,))
    conn.commit()
    conn.close()

def main():
    api_v1, client_v2 = get_clients()
    user_id = os.environ["X_USER_ID"]
    init_db()

    # 1. 過去のツイートを取得
    response = client_v2.get_users_tweets(
        id=user_id,
        max_results=50,
        expansions=["attachments.media_keys"],
        media_fields=["url", "type"],
        tweet_fields=["text", "created_at"]
    )

    if not response.data:
        print("ツイートが見つかりませんでした。")
        return

    # メディア情報のマッピング
    media_map = {m.media_key: m for m in response.includes.get("media", [])} if response.includes else {}

    # 2. 画像付き かつ 未投稿 のツイートを抽出
    candidates = []
    for t in response.data:
        if is_already_posted(str(t.id)):
            continue
        
        attachments = getattr(t, 'attachments', None)
        if attachments and "media_keys" in attachments:
            m_key = attachments["media_keys"][0]
            media = media_map.get(m_key)
            if media and media.type == "photo" and hasattr(media, 'url'):
                candidates.append({"id": t.id, "text": t.text, "url": media.url})

    if not candidates:
        print("投稿可能な新しい画像ツイートがありません。")
        return

    # 3. ランダムに1つ選択
    target = random.choice(candidates)
    print(f"投稿対象: {target['id']}")

    # 4. 画像をダウンロードしてアップロード(v1.1)
    img_res = requests.get(target['url'])
    with open("temp.jpg", "wb") as f:
        f.write(img_res.content)
    
    media = api_v1.media_upload(filename="temp.jpg")

    # 5. 新規ツイートとして投稿(v2)
    client_v2.create_tweet(text=target['text'], media_ids=[media.media_id])
    
    # 6. DBに記録
    mark_as_posted(str(target['id']))
    print("投稿が完了しました。")

if __name__ == "__main__":
    main()
