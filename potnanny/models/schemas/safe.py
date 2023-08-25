import datetime
from markupsafe import escape
from marshmallow import Schema, EXCLUDE, pre_load

class SafeSchema(Schema):
    """
    Subclass of the marshmallow Schema base.
    Excludes unknown fields, and sanitizes all as potential markdown data
    """

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def _sanitize(self, data, **kwargs):
        """
        sanitize all input data, with markupsafe.escape()
        """

        for key, value in data.items():
            if not value:
                continue

            if isinstance(value, dict):
                value = self._sanitize(value)
                continue

            if isinstance(value, datetime.datetime):
                continue

            clean = escape(value)
            data[key] = str(clean)

        return data
