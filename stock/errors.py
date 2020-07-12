class DateError(Exception):

    def __init__(self, date):
        super().__init__()
        self.date = date

    def __str__(self):
        return f'{self.date} not support date'
