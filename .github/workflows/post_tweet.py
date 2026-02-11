from fetch_tweets import get_client

def post(text: str):
    client = get_client()
    client.create_tweet(text=text)
