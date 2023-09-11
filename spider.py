from jira import JIRA
import xlwt
import re
from tqdm import tqdm
import datetime
from collections import Counter
import pandas as pd


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'VickyChen'
    password = '1Q2W3E4R!!!'
    is_this_week = False
    file = '/Users/user/Desktop/jira_spider/JIRA_'
    mapping_file_name = '.xlsx'

    # 排除不需要顯示的狀態列表
    skip_ = ['Planning', 'Pending']

    # @classmethod
    # def get_member(cls, jira):
    #     a = jira.group_members('Trevi')
    #     member_list = [i for i in a]
    #     return member_list

    @classmethod
    def get_my_info(cls, this_week):
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
    def get_person_info(cls, this_week):
        """
        Main content
        取得相關所需資料
        """
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        start, end = Jira.get_my_info(this_week=this_week)
        # 下條件式, 利用JQL
        issues = jira.search_issues(f'updated >= {start} AND updated <= now()', maxResults=0)
        # 取得資料 解析
        for issue in tqdm(issues):
            status = issue.fields.status.name
            worklogs = jira.worklogs(issue)
            link = issue.permalink()
            a = Jira.test_by_vicky(worklogs=worklogs, this_week=this_week, jira=jira)
            timespent = Jira.get_worklog_info(worklogs=worklogs, this_week=this_week)
            timespents = Jira.get_worklog_info(time=False, worklogs=worklogs, this_week=this_week)
            t_worklog_ = Jira.count_timespant(timespent=timespent, is_count=True)
            summary = issue.fields.summary
            project = issue.fields.project.name
            created = issue.fields.created
            created = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", created)
            created = "".join(created)
            priority = issue.fields.priority.name
            user_list = Jira.get_worklog_info(worklogs=worklogs, this_week=this_week, time=False)
            print(user_list, priority, created, project, summary, t_worklog_, timespents, a)

        # worklog_ = Jira.test_pocky(name_list=user_list, timespent=timespent)



    @classmethod
    def parse_estimated_time(cls, time_type):
        if type(time_type) is int:
            estimated_time = float(time_type / 60 / 60)
            estimated_time = (round(estimated_time, 2))

        else:
            estimated_time = '-'

        return estimated_time

    @classmethod
    def get_worklog_info(cls, worklogs, this_week, time=True, workId=None):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = Jira.parse_week_(this_week=this_week, rule=True)
        info_ = list()

        for work in worklogs:
            parse = work.started[:10]
            if parse in week:
                # test_list += {f'{work.author.name}:{work.timeSpent}'}
                if time is True:
                    info_ += [f'{work.timeSpent}']
                else:
                    info_ += [f'{work.author.name}']
                if workId is True:
                    info_ += [work.issueId]
        return info_

    @classmethod
    def test_by_vicky(cls, worklogs, this_week, jira):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = Jira.parse_week(this_week=this_week, rule=True)
        name = list()
        time = list()
        for work in worklogs:
            parse = work.started[:10]
            if parse in week:
                name += [work.author.name]
                my_count = Jira.compute_cost(sp_time=work.timeSpent)
                print(my_count)
                my_count = eval(my_count)
                count = "{:.2f}".format(my_count)
                time += [count]
                dict_ = dict(zip(name, time))
                return dict_

    @classmethod
    def export_excel_test(cls, this_week):
        """
        匯出 且 存入 excel
        """
        _, summary, project, priority, str_creatd, status_list, t_worklog_, link, worklog_, due_date, estimated_time, \
            test_time = Jira.get_person_info(this_week=this_week)
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'jira_', cell_overwrite_ok=True)
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'project')
        sheet.write(0, 2, 'summary')
        sheet.write(0, 3, 'priority')
        sheet.write(0, 4, 'created')
        # sheet.write(0, 5, 'due_date')
        sheet.write(0, 5, 'worklog')
        sheet.write(0, 6, 'total_worklog')
        sheet.write(0, 7, 'status')
        sheet.write(0, 8, 'estimated_time')
        # sheet.write(0, 10, '預估時間')
        sheet.write(0, 9, 'link')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, project[i])
            sheet.write(i + 1, 2, summary[i])
            sheet.write(i + 1, 3, priority[i])
            sheet.write(i + 1, 4, str_creatd[i])
            # sheet.write(i + 1, 5, due_date[i])
            sheet.write(i + 1, 5, worklog_[i])
            sheet.write(i + 1, 6, t_worklog_[i])
            sheet.write(i + 1, 7, status_list[i])
            sheet.write(i + 1, 8, estimated_time[i])
            # sheet.write(i + 1, 10, test_time[i])
            sheet.write(i + 1, 9, link[i])
        # excel 檔案名稱
        start, end = Jira.get_my_info(this_week=this_week)
        file.save(f'JIRA_{end}{Jira.is_this_week}.xlsx')
        Jira.to_excel(this_week=this_week)

    @classmethod
    def compute_cost(cls, sp_time):
        cost = sp_time.replace('d', '*8').replace('h', '*1').replace('m', '/60').replace(' ', '+'). \
            replace('w', '*40').replace('s', '/3600')
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
    def test_pocky(cls, timespent, name_list):
        temp = cls.count_timespant(timespent=timespent)
        B = list()
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
        return ans

    @classmethod
    def to_excel(cls, this_week):
        start, end = Jira.get_my_info(this_week=this_week)
        file_name = f'{Jira.file}{end}{Jira.is_this_week}{Jira.mapping_file_name}'
        df = pd.read_excel(f'{file_name}')
        df.dropna(axis=0, how='any', inplace=True)
        df.to_excel(f'{file_name}', index=False)

    @classmethod
    def vicky_parse_info(cls, worklog_, workId, code=None):
        name = list()
        time = list()
        log_list = list()
        # pri 6

        for worklog in str(worklog_).split(','):
            name += [str(re.sub(r'[^a-zA-Z,]', '', worklog))]
            time += [str(re.sub(r'[^0-9/.]', '', worklog)).lstrip('.')]
            return name, time

        if code is True:
            for i in str(workId).split(','):
                log_list += [str(re.sub(r'[^0-9/.]', '', i))]
                return log_list


if __name__ == '__main__':
    Jira.get_person_info(this_week=Jira.is_this_week)


# 優化現在工時一個多人的狀況
# 匯出檔案 依人名分sheet 參考 (sort_info.py )
