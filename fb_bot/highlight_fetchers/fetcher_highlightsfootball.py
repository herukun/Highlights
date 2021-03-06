import json
from datetime import datetime

import requests
import dateparser
import time

from bs4 import BeautifulSoup

from fb_bot.highlight_fetchers import fetcher_footyroom
from fb_bot.highlight_fetchers.Highlight import Highlight

ROOT_URL = 'https://highlightsfootball.com/wp-admin/admin-ajax.php'


class HighlightsFootballHighlight(Highlight):

    def __init__(self, link, match_name, img_link, view_count, category, time_since_added):
        super().__init__(link, match_name, img_link, view_count, category, time_since_added, [])

    def get_match_info(self, match):
        match = match.replace('Highlights', '').strip()

        match_split = match.split()
        middle_index = match_split.index('vs')

        def join(l):
            return " ".join(l)

        team1 = join(match_split[:middle_index])
        score1 = -1
        team2 = join(match_split[middle_index + 1:])
        score2 = -1

        return team1, score1, team2, score2

    def get_source(self):
        return 'highlightsfootball'


def fetch_highlights(num_pagelet=4, max_days_ago=7):
    """
    Fetch all the possible highlights available on highlightsfootball given a number of pagelet to look at
    (15 highlights per pagelet)

    :param num_pagelet: number of pagelet to consider
    :param max_days_ago: max age of a highlight (after this age, we don't consider the highlight)
    :return: the latests highlights available on highlightsfootball
    """

    highlights = []

    for pagelet_num in range(num_pagelet):
        highlights += _fetch_pagelet_highlights(pagelet_num, max_days_ago)

    return highlights


def _fetch_pagelet_highlights(pagelet_num, max_days_ago):
    highlights = []

    page = requests.post(ROOT_URL, data={
        'action': 'td_ajax_block',
        'block_type': 'td_block_3',
        'td_current_page': pagelet_num + 1
    })

    html = json.loads(page.text)['td_data'] \
        .replace("\n", "") \
        .replace("\t", "") \
        .replace("\\", "")

    soup = BeautifulSoup(html, 'html.parser')

    # Extract videos
    for vid in soup.find_all(class_='td_module_1'):

        # Extract match name
        match_name = str(vid.find('img').get('title'))

        if not 'vs' in match_name:
            # Check that the highlight is for a match
            continue

        # Extract view count - NOT AVAILABLE for this website
        view_count = 0

        # Extract category
        info = vid.find(class_='td-post-category')

        if not info:
            continue

        category = str(info.get_text())

        # Extract time since video added
        date = vid.find(class_='td-module-date')

        if not date:
            continue

        now = datetime.now()

        time_since_added = str(date.get_text())
        time_since_added_date = dateparser.parse(time_since_added).replace(hour=now.hour, minute=now.minute)
        time_since_added = str(time_since_added_date)

        # If error occur while parsing date, skip
        # TODO: handle case where date malformed (special string field)
        if not time_since_added_date:
            continue

        if not fetcher_footyroom.is_recent(time_since_added_date, max_days_ago):
            continue

        # Extract image link
        image = vid.find('img')

        if not image:
            continue

        img_link = str(image.get("src"))

        # Extract link
        link_tag = vid.find("a")

        link = str(link_tag.get("href"))

        if not _is_valid_link(link):
            continue

        video_link = _get_video_link(link)

        if not video_link:
            continue

        highlights.append(HighlightsFootballHighlight(video_link, match_name, img_link, view_count, category, time_since_added))

    return highlights


def _is_valid_link(link):
    if not isinstance(link, str):
        return False

    # clean the URLS
    link = link.strip()

    # check if it is a football Match highlight video
    return link.startswith("https://highlightsfootball.com/video/")


def _get_video_link(full_link):
    page = requests.get(full_link)
    soup = BeautifulSoup(page.content, 'html.parser')

    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")

        # Only pick video urls coming from the following websites
        if src:
            if 'dailymotion.com' in src:
                return 'https://' + src.replace('//', '')

            if 'streamable.com' in src:
                resource_id = src.split('/s/')[1].split('/')[0]

                # Return streamable link in the format 'https://streamable.com/e/ioz1l'
                return 'https://streamable.com/e/' + resource_id

            if 'ok.ru' in src:
                return 'https://' + src.replace('//', '')

    return None


if __name__ == "__main__":

    print("\nFetch highlights ------------------------------ \n")

    start_time = time.time()
    highlights = fetch_highlights()

    for highlight in highlights:
        print(highlight)

    print("Number of highlights: " + str(len(highlights)))
    print("Time taken: " + str(round(time.time() - start_time, 2)) + "s")