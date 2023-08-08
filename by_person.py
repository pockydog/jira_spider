from jira import JIRA
import xlwt
import re
from tqdm import tqdm
import datetime
from collections import Counter


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'VickyChen'
    password = '1Q2W3E4R!!!'
    is_this_week = False

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
    def get_person_info(cls):
        """
        Main content
        取得相關所需資料
        """
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        result = {}
        # summary = list()
        # str_creatd = list()
        # link = list()
        # priority = list()
        # project = list()
        # status_list = list()
        # user_list = list()
        # timespent = list()
        # name = list()
        # t_worklog_ = None
        info_list = list()
        start, end = Jira.parse_week(this_week=this_week)

        # 下條件式, 利用JQL
        issues = jira.search_issues(f'updated >= {start} AND updated <= now()', maxResults=0)
        # 取得資料 解析
        for issue in tqdm(issues):
            status = issue.fields.status.name
            if status in Jira.skip_:
                continue
            summary = issue.fields.summary
            link = issue.permalink()
            project = issue.fields.project.name
            created = issue.fields.created
            created = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", created)
            str_creatd = "".join(created)
            priority = issue.fields.priority.name
            worklogs = jira.worklogs(issue)
            # timespent = Jira.get_worklog_info(worklogs=worklogs, this_week=this_week)
            user_list = Jira.get_worklog_info(worklogs=worklogs, this_week=this_week, time=False)
            t_worklog_ = Jira.count_timespant(timespent=timespent, is_count=True)
            result += {
                'project': project,
                'str_creatd': str_creatd,
                'user_list': user_list,
            }
        return result
        # worklog_ = Jira.test_pocky(name_list=user_list, timespent=timespent)

        # return summary, project, priority, str_creatd, status_list, timespent, t_worklog_, link, worklog_


    @classmethod
    def get_worklog_info(cls, worklogs, this_week, time=True):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = Jira.parse_week_(this_week=this_week, rule=True)
        info_ = list()
        name_list = list()
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
        week_day = 7
        week = ['20' + datetime.datetime.strftime(today - datetime.timedelta(today.weekday() - i), '%y-%m-%d') for i in
                range(week_day)]
        week += ['2023-07-17']
        return week

    @classmethod
    def export_excel(cls, this_week):
        """
        匯出 且 存入 excel
        """
        summary, project, priority, str_creatd, status_list, timespent, t_worklog_, link, worklog_ =Jira.get_person_info(this_week=this_week)
        file = xlwt.Workbook('encoding = utf-8')
        format_info = set(project)
        for info in format_info:
            sheet = file.add_sheet(f'{info}', cell_overwrite_ok=True)
            sheet.write(0, 0, '')
            sheet.write(0, 1, 'project')
            sheet.write(0, 2, 'summary')
            sheet.write(0, 3, 'priority')
            sheet.write(0, 4, 'created')
            sheet.write(0, 5, 'status')
            sheet.write(0, 6, 'worklog')
            sheet.write(0, 7, 'total_worklog')
            sheet.write(0, 8, 'link')
            round = 0
            for i in range(len(project)):
                if info != project[i]:
                    continue
                else:
                    round += 1
                    sheet.write(round + 1, 0, i)
                    sheet.write(round + 1, 1, project[i])
                    sheet.write(round + 1, 2, summary[i])
                    sheet.write(round + 1, 3, priority[i])
                    sheet.write(round + 1, 4, str_creatd[i])
                    sheet.write(round + 1, 5, status_list[i])
                    sheet.write(round + 1, 6, worklog_[i])
                    sheet.write(round + 1, 7, t_worklog_[i])
                    sheet.write(round + 1, 8, link[i])
        # excel 檔案名稱
        start, end = Jira.parse_week(this_week=this_week)
        file.save(f'JIRA_{end}{Jira.is_this_week}.xls')

    @classmethod
    def compute_cost(cls, sp_time):
        cost = sp_time.replace('d', '*8').replace('h', '*1').replace('m', '/60').replace(' ', '+').\
            replace('w', '*40').replace('s', '/3600')
        return cost

    @classmethod
    def count_timespant(cls, timespent, is_count=None):
        temp = list()
        a_list = list()
        for time in timespent:
            time_list = list()
            for t in time:
                cost = t.replace('d', '*8').replace('h', '*1').replace('m', '/60').replace(' ', '+').replace('w', '*40')
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
    def test_pocky(cls, timespent, name_list):
        temp = cls.count_timespant(timespent=timespent)
        B = list()
        ans_list = list()
        for a, b in zip(name_list, temp):
            name_value_pairs = [f'{x}:{y}' for x, y in zip(a, b)]
            name_sum = Counter()
            # Counter 統計可迭代序列中，每個元素出現的次數
            names = list()
            for item in name_value_pairs:
                name, value = item.split(":")
                names.append(name)
                name_sum[name] += float(value)

            combined = [f"{name}:{name_sum[name]}" for name in names]
            B.append(combined)
        ans = [str(set(i)).replace('set()', '') for i in B]
        for i in ans:
            print(i)
        #     if i != '':
        #         continue
        #     else:
        #         ans_list.append(i)
        # print(ans_list)
        return ans


if __name__ == '__main__':
    print(Jira.get_person_info())
