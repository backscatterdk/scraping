from pathlib import Path
from time import sleep
from random import randint
import json
from tqdm import tqdm
from facebook_scraper import FacebookScraper, utils, get_group_info, set_cookies
from facebook_scraper.constants import FB_MOBILE_BASE_URL


EMAIL = ''
PWD = ''

class MyFacebookScraper(FacebookScraper):
    def get_groups_by_search(self, word: str, **kwargs):
        """Searches Facebook groups and yields ids for each result
        on the first page"""
        group_search_url = utils.urljoin(FB_MOBILE_BASE_URL, f"search/groups/?q={word}")
        r = self.get(group_search_url)
        for group_element in r.html.find('div[role="button"]'):
            button_id = group_element.attrs["id"]
            group_id = find_group_id(button_id, r.text)
            try:
                yield get_group_info(group_id)
            except AttributeError:
                print(f"AttributeError, skipping {group_id}")
                continue


def find_group_id(button_id, raw_html):
    """Each group button has an id, which appears later in the script
    tag followed by the group id."""
    s = raw_html[raw_html.rfind(button_id) :]
    group_id = s[s.find("result_id:") :].split(",")[0].split(":")[1]
    return int(group_id)


scraper = MyFacebookScraper()
scraper.login(email=EMAIL, password=PWD)
set_cookies('cookies.json')

with open("queries.txt", "r") as f:
    queries = f.read().splitlines()

for query in tqdm(queries):
    Path(query).mkdir(exist_ok=True)
    for group_info in scraper.get_groups_by_search(query):
        with open(f"{query}/{group_info['id']}.json", 'w') as f:
            json.dump(group_info, f)
        sleep(randint(1, 6))
    sleep(randint(30, 90))