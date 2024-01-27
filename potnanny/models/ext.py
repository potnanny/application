import json
from peewee import Field

class JSONField(Field):
    field_type = 'text'

    def db_value(self, value):
        try:
            result = json.dumps(value)
        except:
            result = None
        return result

    def python_value(self, value):
        try:
            result = json.loads(value)
        except:
            result = None
        return result
