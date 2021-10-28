import datetime
import os

import requests
from flask import flash

API_KEY = os.environ.get('API_KEY')
URL = 'https://www.googleapis.com/youtube/v3/search'


def enough_time_since_last_request(last_checked_time_str) -> bool:
    # print(last_checked_time_str)
    last_checked_time = datetime.datetime.strptime(last_checked_time_str, "%Y/%m/%d, %H:%M:%S")
    # print(last_checked_time)

    # Add 12 hours delta to the loaded data to determine when we need to call the API again
    next_check_time = last_checked_time + datetime.timedelta(hours=12)

    # # FOR TESTING
    # next_check_time = last_checked_time + datetime.timedelta(minutes=1)

    # print(next_check_time)

    # Check if current time > next check time value
    return datetime.datetime.now() >= next_check_time


def request_latest_video(channel_id) -> str:
    params = {
        'key': API_KEY,
        'channelId': channel_id,
        'part': 'snippet,id',
        'order': 'date',
        'maxResults': 1,
    }

    try:
        response = requests.get(url=URL, params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return ''
    else:
        channel_data = response.json()
        # print(channel_data)
        return channel_data.get('items')[0].get('id').get('videoId')
