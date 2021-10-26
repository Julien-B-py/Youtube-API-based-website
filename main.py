import datetime
import os

from flask import Flask, render_template, flash, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect

from forms import AddChannelForm
from utils import enough_time_since_last_request, request_latest_video

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yt_channels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(80), unique=True, nullable=False)
    latest_video_id = db.Column(db.String(120), nullable=True)
    last_check_time = db.Column(db.String(80), nullable=True)


db.create_all()

Bootstrap(app)


@app.route("/")
def home():
    updated = False

    # Limit to 1 per 24 hours to not exceed quota
    # If True: call API
    if enough_time_since_last_request():

        print('Collecting updated data')

        all_channels = db.session.query(Channel).all()
        channels_list = [channel.channel_id for channel in all_channels]

        # channels_list = [channel_id.strip('\n') for channel_id in channels_ids]

        # YOUTUBE API CALL
        video_ids = [request_latest_video(channel) for channel in channels_list]

        # TEST
        for channel, video_id in zip(all_channels, video_ids):
            channel.latest_video_id = video_id

        db.session.commit()

        # Save current date
        with open("last_checked_time.txt", "w") as f:
            f.write(datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"))
        print('Saving current date')

        updated = True

    else:

        # LOAD SAVED DATA
        print('Loading data from database')

        all_channels = db.session.query(Channel).all()

        video_ids = [channel.latest_video_id for channel in all_channels if channel.latest_video_id is not None]

    return render_template("videos.html", video_ids=video_ids, updated=updated)


@app.route("/add", methods=['POST', 'GET'])
def add_channel():
    form = AddChannelForm()

    if form.validate_on_submit():

        channel_id = form.channel_id.data

        channel = Channel.query.filter_by(channel_id=channel_id).first()

        if channel:
            flash('already exists')
            return render_template("add.html", form=form)

        # DB
        new_channel = Channel(channel_id=channel_id)
        db.session.add(new_channel)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("add.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
