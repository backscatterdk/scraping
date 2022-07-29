from pathlib import Path
import instaloader

hashtag = ""
INSTAGRAM_ACCOUNT = ""

L = instaloader.Instaloader(
    download_pictures=True, download_videos=False, download_video_thumbnails=False,
    fatal_status_codes=[400, 429], post_metadata_txt_pattern="")
L.load_session_from_file(INSTAGRAM_ACCOUNT)

post_iterator = instaloader.NodeIterator(
    L.context, "9b498c08113f1e09617a1703c22b2f32",
    lambda d: d['data']['hashtag']['edge_hashtag_to_media'],
    lambda n: instaloader.Post(L.context, n),
    {'tag_name': hashtag},
    f"https://www.instagram.com/explore/tags/{hashtag}/")

with instaloader.resumable_iteration(context=L.context,iterator=post_iterator,load=instaloader.load_structure_from_file,save=instaloader.save_structure_to_file,format_path=lambda magic: f"resume_info_{magic}.json.xz",) as (is_resuming, start_index):
    if is_resuming:
        next(post_iterator)
    for post in post_iterator:
        L.download_post(post)  