from datetime import datetime


class HolidayWarning(Exception):
    def __init__(self, date):
        super().__init__()
        self.date = date

    def __str__(self):
        if datetime.now().strftime('%Y%m%d') == self.date:
            return f'{self.date} data has not been captured, may not have been released, or be a holiday'
        else:
            return f'{self.date} is holiday'


class DateFormatError(Exception):
    pass
