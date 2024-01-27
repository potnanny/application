from quart_wtf import QuartForm
from quart_auth import current_user
from wtforms.fields import (StringField, PasswordField, HiddenField)
from wtforms import validators
from wtforms.widgets import PasswordInput


class LoginForm(QuartForm):
    username = StringField(
        'Username',
        validators=[
            validators.DataRequired('please enter username'),
        ]
    )

    password = PasswordField(
        'Password',
        widget=PasswordInput(hide_value=False),
        validators=[
            validators.DataRequired('please enter password'),
        ]
    )


class PasswordResetForm(QuartForm):
    username = HiddenField(
        validators=[validators.optional()]
    )
    current = PasswordField(
        'Current Password',
        widget=PasswordInput(hide_value=False),
        validators=[
            validators.DataRequired('please enter current password'),
        ]
    )
    password = PasswordField(
        'New Password',
        widget=PasswordInput(hide_value=False),
        validators=[
            validators.DataRequired('please enter a new password'),
        ]
    )
    again = PasswordField(
        'New Password again',
        widget=PasswordInput(hide_value=False),
        validators=[
            validators.DataRequired('passwords must match'),
        ]
    )
