from datetime import datetime


class DateConverter(object):
    """
    FROM: https://stackoverflow.com/a/61134265
    """
    regex = '\d{4}/\d{2}'

    def to_python(self, value):
        year, month = value.split('/')
        return (year, month)

    def to_url(self, value):
        return value
