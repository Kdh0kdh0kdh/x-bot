import random

def select_random(tweets):
    if not tweets:
        return None
    return random.choice(tweets)
