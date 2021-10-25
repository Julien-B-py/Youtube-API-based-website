import datetime
import os

import requests

API_KEY = os.environ.get('API_KEY')
URL = 'https://www.googleapis.com/youtube/v3/search'


def enough_time_since_last_request() -> bool:
    try:
        with open("last_checked_time.txt", "r") as f:
            last_checked_time_str = f.read()
    except FileNotFoundError:
        last_checked_time_str = "1900/01/01, 00:00:00"

    # print(last_checked_time_str)
    last_checked_time = datetime.datetime.strptime(last_checked_time_str, "%Y/%m/%d, %H:%M:%S")
    # print(last_checked_time)

    # Add 12 hours delta to the loaded data to determine when we need to call the API again
    next_check_time = last_checked_time + datetime.timedelta(hours=12)

    # # FOR TESTING
    # next_check_time = last_checked_time + datetime.timedelta(minutes=5)

    # print(next_check_time)

    # Check if current time > next check time value
    return datetime.datetime.now() >= next_check_time


def request_latest_video(channel_id) -> str:
    params = {
        'key': API_KEY,
        'channelId': channel_id,
        'part': 'snippet,id',
        'order': 'date',
        'maxResults': 20,
    }

    channel_data = requests.get(url=URL, params=params).json()

    return channel_data.get('items')[0].get('id').get('videoId')
