from jira import JIRA
import xlwt
import re
from tqdm import tqdm
import datetime


class Test:
    @classmethod
    def last_weekly(cls):
        a = cls.test_vicky(this_week=False)
        # today = datetime.datetime.now() - datetime.timedelta(days=7)
        # this_week_start = today - datetime.timedelta(days=today.weekday())
        # last_end_day = today + datetime.timedelta(days=6 - today.weekday())
        # last_first_day = this_week_start.strftime('%Y-%m-%d')
        # last_end_day = last_end_day.strftime('%Y-%m-%d')
        #
        # return last_first_day, last_end_day


    @classmethod
    def test_vicky(cls, this_week=True):
        if this_week is True:
            end_day = datetime.datetime.today()
            weekday = end_day.weekday()
            days_to_monday = datetime.timedelta(days=weekday)
            monday = end_day - days_to_monday
        else:
            today = datetime.datetime.now() - datetime.timedelta(days=7)
            monday = today - datetime.timedelta(days=today.weekday())
            end_day = monday + datetime.timedelta(days=6 - today.weekday())

        start = monday.strftime('%Y-%m-%d')
        end = end_day.strftime('%Y-%m-%d')
        return start, end


if __name__ == '__main__':
    print(Test.test_vicky())
    print(Test.last_weekly())




