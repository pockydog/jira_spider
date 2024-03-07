import datetime

today = datetime.date(2024, 2, 1)
week_day = 32

week = [today - datetime.timedelta(today.weekday() - i) for i in range(week_day)]
week = ['20'+ datetime.datetime.strftime(date, '%y-%m-%d') for date in week]

print(week)
