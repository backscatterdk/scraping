import json
from pathlib import Path
from datetime import datetime
from itertools import dropwhile, takewhile
from instaloader import Instaloader, Profile, resumable_iteration, FrozenNodeIterator
from tqdm import tqdm

INSTAGRAM_ACCOUNT = ""
SINCE = datetime.max
UNTIL = datetime.min

L = Instaloader(download_pictures=False, download_videos=False)
L.load_session_from_file(INSTAGRAM_ACCOUNT)

# Get targets
with open("targets_to_download.txt", "r") as f:
    targets = f.read().splitlines()
with open("completed_targets.txt", "r") as f:
    completed = f.read().splitlines()
targets = [target for target in targets if not target in completed]

for target in targets:
    like_path = Path("likes") / target
    like_path.mkdir(exist_ok=True, parents=True)
    profile = Profile.from_username(L.context, target)
    post_iterator = profile.get_posts()
    with resumable_iteration(
        context=L.context,
        iterator=post_iterator,
        load=lambda _, path: FrozenNodeIterator(**json.load(open(path))),
        save=lambda fni, path: json.dump(fni._asdict(), open(path, "w")),
        format_path=lambda magic: "resume_info_{}.json".format(magic),
    ) as (is_resuming, start_index):
        for post in takewhile(
            lambda p: p.date > UNTIL, dropwhile(lambda p: p.date > SINCE, post_iterator)
        ):
            if L.download_post(post, target=target):
                with open(like_path / f"{post.shortcode}.txt", "a") as f:
                    for like in tqdm(post.get_likes(), total=post.likes, desc=post.shortcode):
                        f.write(f"{str(like.userid)}\n")
    with open("completed_targets.txt", "a") as f:
        f.write(f"{target}\n")