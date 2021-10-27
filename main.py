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


class Time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_checked_time = db.Column(db.String(100), unique=True, nullable=False)


db.create_all()

Bootstrap(app)


def manual_update():
    print('Collecting updated data')

    all_channels = db.session.query(Channel).all()
    channels_list = [channel.channel_id for channel in all_channels]

    # YOUTUBE API CALL
    video_ids = [request_latest_video(channel) for channel in channels_list if
                 request_latest_video(channel) != '']

    if video_ids:

        # UPDATE DATABASE WITH LATEST VIDEO IDS
        for channel, video_id in zip(all_channels, video_ids):
            channel.latest_video_id = video_id

        db.session.commit()

        # UPDATE DATABASE WITH LATEST CHECK TIME
        update_last_checked_time()

        return video_ids

    # UPDATE DATABASE WITH LATEST CHECK TIME
    update_last_checked_time()

    return []


def update_last_checked_time():
    # UPDATE DATABASE WITH LATEST CHECK TIME
    time_update = Time.query.filter_by(id=1).first()
    time_update.last_checked_time = datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
    db.session.commit()


@app.route("/")
def home():
    last_checked = db.session.query(Time).first()

    if not last_checked:
        last_checked_time_str = "1900/01/01, 00:00:00"
        new_time = Time(id=1, last_checked_time=last_checked_time_str)
        db.session.add(new_time)
        db.session.commit()
    else:
        last_checked_time_str = last_checked.last_checked_time

    # Limit to 1 per 12 hours to not exceed daily quota
    if enough_time_since_last_request(last_checked_time_str):

        video_ids = manual_update()
        flash("Listing successfully updated")

    else:

        # LOAD SAVED DATA
        flash('Loaded data from our database')

        all_channels = db.session.query(Channel).all()

        video_ids = [channel.latest_video_id for channel in all_channels if channel.latest_video_id is not None]

    return render_template("videos.html", video_ids=video_ids)


@app.route("/add", methods=['POST', 'GET'])
def add_channel():
    form = AddChannelForm()

    if form.validate_on_submit():

        channel_id = form.channel_id.data

        channel = Channel.query.filter_by(channel_id=channel_id).first()

        if channel:
            flash('This channel is already registered')
            return render_template("add.html", form=form)

        # DB
        new_channel = Channel(channel_id=channel_id)
        db.session.add(new_channel)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("add.html", form=form)


@app.route("/update")
def force_update():
    manual_update()
    flash('Manual update successful')
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
