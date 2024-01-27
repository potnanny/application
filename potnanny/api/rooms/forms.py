from quart_wtf import QuartForm
from wtforms.fields import (StringField, TextAreaField, HiddenField)
from wtforms import validators


class RoomForm(QuartForm):
    id = HiddenField('id', validators=[validators.optional()])
    remove = HiddenField('remove', validators=[validators.optional()])
    name = StringField('name', validators=[validators.DataRequired()])
    notes = TextAreaField('notes', validators=[validators.optional()])
