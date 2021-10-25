import datetime
import os

import requests

from flask import Flask, render_template

app = Flask(__name__)

API_KEY = os.environ.get('API_KEY')
URL = 'https://www.googleapis.com/youtube/v3/search'


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


@app.route("/")
def home():
    with open("last_checked_time.txt", "r") as f:
        last_checked_time_str = f.read()

    with open("channels_ids.txt", "r") as f:
        channels_ids = f.readlines()

    channels_list = [channel_id.strip('\n') for channel_id in channels_ids]

    # # TODO: Limit to 1 per 24 hours to not exceed quota
    # # YOUTUBE API CALL
    # video_ids = [request_latest_video(channel) for channel in channels_list]

    print(last_checked_time_str)
    last_checked_time = datetime.datetime.strptime(last_checked_time_str, "%Y/%m/%d, %H:%M:%S")
    print(last_checked_time)

    # Add 24hours delta to the loaded data to determine when we need to call the API again
    next_check_time = last_checked_time + datetime.timedelta(hours=24)
    print(next_check_time)

    # Check if current time > saved time value
    print(datetime.datetime.now() > last_checked_time)
    # Check if current time > next time check value
    print(datetime.datetime.now() >= next_check_time)
    # If True: call API

    # with open("last_checked_time.txt","w") as f:
    #     f.write(datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"))

    return render_template("videos.html", video_ids=video_ids)


if __name__ == "__main__":
    app.run(debug=True)
