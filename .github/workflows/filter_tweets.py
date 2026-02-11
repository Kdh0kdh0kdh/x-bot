def filter_image_tweets(tweets):
    image_tweets = []

    for t in tweets:
        if not t["attachments"]:
            continue

        for m in t["media"]:
            if m and m.type == "photo":
                image_tweets.append(t)
                break

    return image_tweets
