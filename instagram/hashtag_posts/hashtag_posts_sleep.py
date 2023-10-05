from datetime import datetime
from itertools import dropwhile, takewhile
import instaloader # 4.9.5
from pathlib import Path
import time
import random
import os


def main():
    L = instaloader.Instaloader(fatal_status_codes=[400, 429],
                                download_pictures=False,
                                download_comments=False, 
                                download_videos=False, 
                                download_geotags=False,
                                save_metadata=True) 

    USER = "" 
    HASHTAG =""  

    L.load_session_from_file(USER)

    CHUNK_SIZE = 2000  # Number of posts to process before sleeping.  
    SLEEP_TIME = 3 * 60 * 60   # Sleep time in seconds
    iterations = 0

    # use jitter to vary the chunksize
    jitter = lambda x: x + x * 0.1 * random.random() * random.choice([1, -1])
    next_chunk_size = jitter(CHUNK_SIZE)

    # create NodeIterator for hashtag
    post_iterator = instaloader.NodeIterator(
    L.context, "9b498c08113f1e09617a1703c22b2f32",
    lambda d: d['data']['hashtag']['edge_hashtag_to_media'],
    lambda n: instaloader.Post(L.context, n),
    {'tag_name': HASHTAG},
    f"https://www.instagram.com/explore/tags/{HASHTAG}/")

    # Create a resumable iteration context for the NodeIterator
    with instaloader.resumable_iteration(
        context=L.context,
        iterator=post_iterator,
        load=instaloader.load_structure_from_file,
        save=instaloader.save_structure_to_file,
        format_path=lambda magic: f"resume_info_{magic}.json.xz",
    ) as (is_resuming, start_index):
        if is_resuming:
            next(post_iterator)

        for post in post_iterator:
            L.download_post(post, target='#'+HASHTAG)
            iterations += 1

            if iterations >= next_chunk_size:
                print("I'm going to sleep now...")
                time.sleep(SLEEP_TIME)
                next_chunk_size = next_chunk_size
                iterations = 0
                print("I just woke up!")

if __name__:
    main()
