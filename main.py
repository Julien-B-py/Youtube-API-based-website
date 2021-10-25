from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    with open("video_ids.txt", "r") as f:
        video_ids = f.readlines()

    clean_list = [video_id.strip('\n') for video_id in video_ids]

    return render_template("videos.html", clean_list=clean_list)


if __name__ == "__main__":
    app.run(debug=True)
