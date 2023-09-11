import datetime


class TimeTool:
    this_week = False

    @classmethod
    def parse_week(cls, this_week, rule=None):
        """
        取得本週 / 上週 的起始日期
        """
        if this_week is True:
            end_day = datetime.datetime.today()
            weekday = end_day.weekday()
            days_to_monday = datetime.timedelta(days=weekday)
            monday = end_day - days_to_monday

        else:
            today = datetime.datetime.now() - datetime.timedelta(days=7)
            monday = today - datetime.timedelta(days=today.weekday())
            end_day = monday + datetime.timedelta(days=6 - today.weekday())

        if rule is True:
            return monday

        yesterday = monday - datetime.timedelta(days=1)
        start = yesterday.strftime('%Y-%m-%d')
        end = end_day.strftime('%Y-%m-%d')

        return start, end

    @classmethod
    def new_parse_week(cls, this_week):
        """
        取得本週 / 上週 的起始日期
        """
        today = datetime.datetime.today()

        if this_week is True:
            days_difference = today.weekday() + 1
            sunday = today - datetime.timedelta(days=days_difference)
            days_difference = (5 - today.weekday())
            saturday = today + datetime.timedelta(days=days_difference)
            return sunday.strftime("%Y-%m-%d"), saturday.strftime("%Y-%m-%d")
        else:
            days_difference = (today.weekday() + 1) + 7
            sunday = today - datetime.timedelta(days=days_difference)
            days_difference = (today.weekday() + 2)
            saturday = today - datetime.timedelta(days=days_difference)
            return sunday.strftime("%Y-%m-%d"), saturday.strftime("%Y-%m-%d")

    @classmethod
    def parse_week_(cls, this_week, rule=True):
        """
        取得 一週 的 所有日期
        """
        today = cls.parse_week(this_week=this_week, rule=rule)
        yesterday = today - datetime.timedelta(days=1)
        week_day = 7
        week = ['20' + datetime.datetime.strftime(today - datetime.timedelta(today.weekday() - i), '%y-%m-%d') for i in
                range(week_day)]
        yesterday = yesterday.strftime('%Y-%m-%d')
        week.append(yesterday)
        return week

    @classmethod
    def test_week(cls, this_week):
        return f'WEEK😀：{TimeTool.new_parse_week(this_week=this_week)},' \
               f'ALL_DAY_CHECK😀：{TimeTool.parse_week_(this_week=this_week)}'


if __name__ == '__main__':
    print(TimeTool.test_week(this_week=TimeTool.this_week))
