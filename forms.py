from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddChannelForm(FlaskForm):
    channel_name = StringField("Channel name", validators=[DataRequired()])
    channel_id = StringField("Channel id", validators=[DataRequired()])

    # submit = SubmitField("Submit")