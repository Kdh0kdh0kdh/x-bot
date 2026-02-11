import os
import sqlite3
import requests
import tweepy
import random
import re

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

    if not response or response.data is None:
        print("ツイートが見つかりませんでした。")
        return

    # メディア情報のマッピング
    media_map = {}
    if response.includes and "media" in response.includes:
        media_map = {m.media_key: m for m in response.includes["media"]}

    # 2. 画像付き かつ 未投稿 のツイートを抽出
    candidates = []
    for t in response.data:
        # すでに投稿済みならスキップ
        if is_already_posted(str(t.id)):
            continue
        
        # 添付ファイルのチェック
        attachments = getattr(t, 'attachments', None)
        if attachments and "media_keys" in attachments:
            m_key = attachments["media_keys"][0]
            media = media_map.get(m_key)
            
            # 画像(photo)であり、URLが存在する場合のみ対象
            if media and media.type == "photo" and hasattr(media, 'url') and media.url:
                # 本文のクリーニング
                clean_text = t.text
                
                # 冒頭の「RT @username: 」を削除
                clean_text = re.sub(r'^RT @\w+: ', '', clean_text)
                
                # 文末のリンクURLを削除（画像添付時に自動で付くもの）
                clean_text = re.sub(r'https://t\.co/\w+$', '', clean_text).strip()
                
                candidates.append({
                    "id": t.id, 
                    "text": clean_text, 
                    "url": media.url
                })

    if not candidates:
        print("投稿可能な新しい画像付きツイートがありません。")
        return

    # 3. ランダムに1つ選択
    target = random.choice(candidates)
    print(f"投稿対象ツイートID: {target['id']}")

    # 4. 画像を一時ダウンロード
    img_res = requests.get(target['url'])
    temp_file = "temp_image.jpg"
    with open(temp_file, "wb") as f:
        f.write(img_res.content)
    
    try:
        # 5. 画像をアップロード(v1.1)
        media_upload_res = api_v1.media_upload(filename=temp_file)

        # 6. 新規ツイートとして投稿(v2)
        client_v2.create_tweet(
            text=target['text'], 
            media_ids=[media_upload_res.media_id]
        )
        
        # 7. DBに記録
        mark_as_posted(str(target['id']))
        print("新規投稿が完了しました。")
        
    except Exception as e:
        print(f"投稿エラー: {e}")
    finally:
        # 一時ファイルの削除
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    main()
