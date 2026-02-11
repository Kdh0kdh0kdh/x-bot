def filter_image_tweets(tweets):
    image_tweets = []

    if not tweets:
        return image_tweets

    for t in tweets:
        # attachmentsキーが存在し、かつ中にmedia_keysが含まれているか確認
        attachments = t.get("attachments")
        if not attachments or "media_keys" not in attachments:
            continue

        # mediaキーが存在するか確認
        # ※tweepyの辞書型アクセスの場合、t.get("media") を使用
        media_list = t.get("media")
        if not media_list:
            continue

        for m in media_list:
            # mが辞書の場合は m.get("type")、オブジェクトの場合は m.type を使用
            # ここではAPIの一般的なレスポンス形式（辞書型）を想定
            media_type = m.get("type") if isinstance(m, dict) else getattr(m, 'type', None)
            
            if media_type == "photo":
                image_tweets.append(t)
                break

    return image_tweets
