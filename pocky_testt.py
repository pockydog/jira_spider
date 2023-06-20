from jira import JIRA
import xlwt
import re
from tqdm import tqdm
import datetime


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'VickyChen'
    password = '1Q2W3E4R!!!'

    # 排除 Trevi group 不需要登記的人員列表
    block_list = [
        'DebbyChen', 'SashaLin', 'gitlab', 'hanklin',
        'cedric', 'billji', 'PeggyHuang', 'ahrizhou', 'MarsLi'
    ]

    # 排除不需要顯示的狀態列表
    skip_ = ['Planning', 'Pending']

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

        start = monday.strftime('%Y-%m-%d')
        end = end_day.strftime('%Y-%m-%d')
        return start, end

    @classmethod
    def get_person_info(cls, this_week):
        """
        Main content
        取得相關所需資料
        """
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        summary = list()
        str_creatd = list()
        link = list()
        assignee = list()
        priority = list()
        project = list()
        status_list = list()
        user_list = list()
        worklogA = list()
        start, end = Jira.parse_week(this_week=this_week)

        # 下條件式, 利用JQL
        issues = jira.search_issues(f'updated >= {start} AND updated <= now()', maxResults=0)
        # 取得資料 解析
        for issue in tqdm(issues):
            status = issue.fields.status.name
            if status not in Jira.skip_:
                status_list.append(status)
            else:
                continue
            summary += [issue.fields.summary]
            project += [issue.fields.project.name]
            created = issue.fields.created
            created = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", created)
            str_creatd += ["".join(created)]
            link += [issue.permalink()]
            priority += [issue.fields.priority.name]
            worklogs = jira.worklogs(issue)
            worklogA += [Jira.get_worklog_info(worklogs=worklogs, this_week=this_week)]
            user_list += [Jira.get_worklog_info(worklogs=worklogs, this_week=this_week, time=False)]
            t_worklog_ = Jira.count_timespant(timespent=worklogA)
            assignee += [issue.fields.creator.name]
        worklog_ = Jira.test_pocky(name_list=user_list, time_list=worklogA)

        return user_list, assignee, summary, project, priority, str_creatd, status_list, worklog_, t_worklog_, link

    @classmethod
    def get_worklog_info(cls, worklogs, this_week, time=True):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = Jira.parse_week_(this_week=this_week, rule=True)
        info_ = list()
        for work in worklogs:
            parse = work.started[:10]
            if parse in week:
                if time is True:
                    info_ += [f'{work.timeSpent}']
                else:
                    info_ += [f'{work.author.name}']

        return info_

    @classmethod
    def parse_week_(cls, this_week, rule=True):
        """
        取得 一週 的 所有時間
        """
        today = cls.parse_week(this_week=this_week, rule=rule)
        week_day = 5
        week = ['20' + datetime.datetime.strftime(today - datetime.timedelta(today.weekday() - i), '%y-%m-%d') for i in
                range(week_day)]
        return week

    @classmethod
    def export_excel(cls, this_week):
        """
        匯出 且 存入 excel
        """
        user_list, assignee,  summary, project, priority, str_creatd, status_list, worklog_, t_worklog_, link = \
            Jira.get_person_info(this_week=this_week)
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'jira_', cell_overwrite_ok=True)
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'assignee')
        sheet.write(0, 2, 'user_name')
        sheet.write(0, 3, 'project')
        sheet.write(0, 4, 'summary')
        sheet.write(0, 5, 'priority')
        sheet.write(0, 6, 'created')
        sheet.write(0, 7, 'status')
        sheet.write(0, 8, 'worklog')
        sheet.write(0, 9, 'total_worklog')
        sheet.write(0, 10, 'link')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, assignee[i])
            sheet.write(i + 1, 2, user_list[i])
            sheet.write(i + 1, 3, project[i])
            sheet.write(i + 1, 4, summary[i])
            sheet.write(i + 1, 5, priority[i])
            sheet.write(i + 1, 6, str_creatd[i])
            sheet.write(i + 1, 7, status_list[i])
            sheet.write(i + 1, 8, worklog_[i])
            sheet.write(i + 1, 9, t_worklog_[i])
            sheet.write(i + 1, 10, link[i])
        # excel 檔案名稱
        start, end = Jira.parse_week(this_week=this_week)
        file.save(f'JIRA_{end}!.xls')

    @classmethod
    def compute_cost(cls, sp_time):
        cost = sp_time.replace('d', '*8').replace('h', '*1').replace('m', '/60').replace(' ', '+').replace('w', '*40')
        return cost

    @classmethod
    def count_timespant(cls, timespent, is_count=None):
        temp = list()
        a_list = list()
        for time in timespent:
            time_list = list()
            for t in time:
                cost = eval(cls.compute_cost(sp_time=t))
                cost = (round(cost, 2))
                time_list.append(cost)
            temp.append(time_list)

        if is_count is None:
            return temp

        if is_count is True:
            for i in temp:
                a_list.append(str(sum(i)))
        return a_list


    @classmethod
    def test_pocky(cls, name_list, time_list):
        c = list()
        B = list()
        temp = list()
        for t in time_list:
            time_list = list()
            for i in t:
                a = eval(cls.compute_cost(sp_time=i))
                cost = (round(a, 2))
                time_list.append(cost)
            temp.append(time_list)

        for a, b in zip(name_list, temp):
            temp = []
            for x, y in zip(a, b):
                temp.append(f'{x}:{y}')
            c.append(temp)
        names = []
        for sublist in c:
            sublist_names = []
            for item in sublist:
                name = item.split(":")[0]
                sublist_names.append(name)
            names.append(sublist_names)
        sums = []
        for sublist in c:
            name_sum = {}
            for item in sublist:
                name, value = item.split(":")
                if name in name_sum:
                    name_sum[name] += float(value)
                else:
                    name_sum[name] = float(value)
            sums.append(name_sum)
        for sublist_names, sublist_sums in zip(names, sums):
            combined = []
            for name in sublist_names:
                value = sublist_sums[name]
                combined.append(f"{name}:{value}")
            B.append(combined)
        a = [(str(set(i)).replace('set()', '')) for i in B]
        return a


if __name__ == '__main__':
    Jira.export_excel(this_week=True)

