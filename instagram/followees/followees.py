"""Also works for followers, just change the function"""

from pathlib import Path
from time import sleep
import random
from datetime import datetime
import instaloader

INSTAGRAM_ACCOUNT = ""
CHUNK_SIZE = 3000
SLEEP_TIME = 3 * 60 * 60
MAX_FOLLOWERS = 1000000

L = instaloader.Instaloader(fatal_status_codes=[400, 429])
L.load_session_from_file(INSTAGRAM_ACCOUNT)

# Get targets
with open("targets_to_download.txt", "r") as f:
    targets = f.read().splitlines()
with open("completed_targets.txt", "r") as f:
    completed = f.read().splitlines()
targets = [target for target in targets if not target in completed]

Path("targets").mkdir(exist_ok=True)

iterations = 0
jitter = lambda x: x + x * 0.1 * random.random() * random.choice([1, -1])
next_chunk_size = jitter(CHUNK_SIZE)

for target in targets:
    print(f"Retrieving followees of {target}...")
    profile = instaloader.Profile.from_id(L.context, target)

    if profile.followers > MAX_FOLLOWERS:
        with open("too_big.txt", "a") as f:
            f.write(f"{target}\n")
        continue

    with open(f"targets/{target}.txt", "a") as f:
        followee_iterator = profile.get_followees()
        with instaloader.resumable_iteration(
            context=L.context,
            iterator=followee_iterator,
            load=instaloader.load_structure_from_file,
            save=instaloader.save_structure_to_file,
            format_path=lambda magic: f"resume_info_{magic}.json.xz",
        ) as (is_resuming, start_index):
            if is_resuming:
                next(followee_iterator)
            for followee in followee_iterator:
                f.write(f"{followee.userid}\n")
                iterations += 1
                if iterations > next_chunk_size:
                    sleep(SLEEP_TIME)
                    next_chunk_size = jitter(CHUNK_SIZE)
                    iterations = 0

    with open("completed_targets.txt", "a") as f:
        f.write(f"{target}\n")
