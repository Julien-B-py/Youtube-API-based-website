import datetime
import os

from flask import Flask, render_template, flash, url_for
from flask_bootstrap import Bootstrap
from werkzeug.utils import redirect

from forms import AddChannelForm
from utils import enough_time_since_last_request, request_latest_video

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

Bootstrap(app)


@app.route("/")
def home():
    updated = False

    # Limit to 1 per 24 hours to not exceed quota
    # If True: call API
    if enough_time_since_last_request():

        print('Collecting updated data')

        with open("channels_ids.txt", "r") as f:
            channels_ids = f.readlines()

        channels_list = [channel_id.strip('\n') for channel_id in channels_ids]

        # YOUTUBE API CALL
        video_ids = [request_latest_video(channel) for channel in channels_list]

        # # FOR TESTING
        # video_ids = ['NSWr6dkc_Xw', 'bRV7dQW9ZWE', "tX06aPu1aIg"]

        # Save current videos id
        with open('videos_ids.txt', 'w') as f:
            for video_id in video_ids:
                f.write(f"{video_id}\n")

        # Save current date
        with open("last_checked_time.txt", "w") as f:
            f.write(datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"))
        print('Saving current date')

        updated = True

    else:
        # LOAD SAVED DATA
        print('Loading data from database')

        try:
            with open("videos_ids.txt", "r") as f:
                video_ids = f.readlines()
        except FileNotFoundError:
            video_ids = []
        else:
            video_ids = [video_id.strip('\n') for video_id in video_ids]

    return render_template("videos.html", video_ids=video_ids, updated=updated)


@app.route("/add", methods=['POST', 'GET'])
def add_channel():
    form = AddChannelForm()

    if form.validate_on_submit():

        channel_id = form.channel_id.data

        with open("channels_ids.txt", "r") as f:
            channels_ids = f.readlines()

        channels_list = [channel_id.strip('\n') for channel_id in channels_ids]

        if channel_id in channels_list:
            flash('already exists')

        else:
            channels_list.append(channel_id)

            # Save updated channels list
            with open("channels_ids.txt", "w") as f:
                for channel_id in channels_list:
                    f.write(f'{channel_id}\n')
            print('Saving current data')

            return redirect(url_for('home'))

    return render_template("add.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
