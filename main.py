from fetch_tweets import fetch_my_tweets
from filter_tweets import filter_image_tweets
from select_tweet import select_random
from post_tweet import post
from db import init_db, already_posted, mark_posted

def main():
    # DB 初期化（重複投稿防止）
    init_db()

    # 自分の最近のツイートを取得
    tweets = fetch_my_tweets(max_results=100)

    # 画像付きのみ抽出
    image_tweets = filter_image_tweets(tweets)

    candidate = select_random(image_tweets)

    if not candidate:
        print("対象ツイートなし")
        return

    tweet_id = candidate["id"]

    # すでに投稿済みならスキップ
    if already_posted(tweet_id):
        print("すでに投稿済み:", tweet_id)
        return

    # ★ 修正ポイント：本文＋画像URLを渡す
    post(
        text=candidate["text"],
        image_url=candidate["image_url"]
    )

    # 投稿済みとして記録
    mark_posted(tweet_id)
    print("投稿完了:", tweet_id)

if __name__ == "__main__":
    main()
