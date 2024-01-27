from quart_wtf import QuartForm
from wtforms.fields import TextAreaField
from wtforms import validators


class LicenseForm(QuartForm):
     license = TextAreaField(
        'License Key',
        validators=[
            validators.DataRequired('must provide a license key'),
        ]
    )
