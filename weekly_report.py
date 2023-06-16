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
    def get_member_list(cls, jira):
        """
        取得所有 Trevi 員工資訊, 並移除'目標範圍外'的員工 --->'block_list'
        """
        members = jira.group_members('TREVI')
        members_list = [member.lower() for member in members if member not in Jira.block_list]

        return members_list

    @classmethod
    def parse_week(cls):
        """
        取得本週的起始日期
        """
        today = datetime.datetime.today()
        weekday = today.weekday()
        days_to_monday = datetime.timedelta(days=weekday)
        monday = today - days_to_monday
        start = monday.strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
        return start, end

    @classmethod
    def get_person_info(cls):
        """
        Main content
        取得相關所需資料
        """
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        members_list = Jira.get_member_list(jira=jira)
        summary = list()
        str_creatd = list()
        link = list()
        priority = list()
        project = list()
        status_list = list()
        user_list = list()
        worklog_ = list()
        worklog_list = None
        start, end = Jira.parse_week()

        for user in tqdm(members_list):
            # 下條件式, 利用JQL
            issues = jira.search_issues(
                f'updated >= {start} '
                f'AND updated <= now()'
                f'AND (assignee was {user} OR reporter = {user})'
            )
            # 取得資料 解析
            for issue in issues:
                worklogs = jira.worklogs(issue)
                worklog_list += [Jira.get_worklog_info(worklogs=worklogs, user=user)]
                # worklog_list = Jira.count_timespant(timespent=worklog_)
                status = issue.fields.status.name
                if status not in Jira.skip_:
                    status_list.append(status)
                else:
                    continue
                user_list += [user.lower()]
                summary += [issue.fields.summary]
                project += [issue.fields.project.name]
                created = issue.fields.created
                created = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", created)
                str_creatd += ["".join(created)]
                link += [issue.permalink()]
                priority += [issue.fields.priority.name]
        print(len(summary))
        return summary, user_list, project, priority, str_creatd, status_list, worklog_list, link

    @classmethod
    def get_worklog_info(cls, worklogs, user):
        """
        取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        worklog_list = list()
        week = Jira.parse_week_()

        for work in worklogs:
            started = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", work.started)
            str_started = "".join(started)
            if str_started in week:
                # 須將登記時數人員名稱 與 員工列表 資料媒合 且回傳
                parse = str(work.author).lower().replace(' ', '')
                parse_a = str(work.author.name).lower().replace(' ', '')
                if parse == user.lower() or parse_a == user.lower():
                    info = [f'{work.timeSpent}']
                    worklog_list.extend(info)
        return worklog_list

    @classmethod
    def parse_week_(cls):
        """
        取得 一週 的 所有時間
        """
        today = datetime.datetime.today()
        week_day = 5
        week = ['20' + datetime.datetime.strftime(today - datetime.timedelta(today.weekday() - i), '%y-%m-%d') for i in
                range(week_day)]
        return week

    @classmethod
    def export_excel(cls):
        """
        匯出 且 存入 excel
        """
        summary, user_list, project, priority, str_creatd, status_list, worklog_list, link = Jira.get_person_info()
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'jira_', cell_overwrite_ok=True)
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'user_name')
        sheet.write(0, 2, 'project')
        sheet.write(0, 3, 'summary')
        sheet.write(0, 4, 'priority')
        sheet.write(0, 5, 'created')
        sheet.write(0, 6, 'status')
        sheet.write(0, 7, 'worklog')
        sheet.write(0, 8, 'link')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, user_list[i])
            sheet.write(i + 1, 2, project[i])
            sheet.write(i + 1, 3, summary[i])
            sheet.write(i + 1, 4, priority[i])
            sheet.write(i + 1, 5, str_creatd[i])
            sheet.write(i + 1, 6, status_list[i])
            sheet.write(i + 1, 7, worklog_list[i])
            sheet.write(i + 1, 8, link[i])
        # excel 檔案名稱
        start, end = Jira.parse_week()
        file.save(f'JIRA_{end}.xls')

    @classmethod
    def test_for_worklog(cls):
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        issues = jira.search_issues(f'updated >= 2023-06-12 '
                                    f'AND updated <= now()'
                                    'AND project = FT ')
        # AND resolution = Unresolved ORDER BY priority DESC, updated DESC
        for i in issues:
            summary = [i.fields.summary]
            worklogs = jira.worklogs(i)
            for work in worklogs:
                started = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", work.started)
                info = [f'000{summary}00花費時間：{work.timeSpent}, /  內容：{work.author.name.lower()} / 時間：{work.started}, '
                        f'{work.started}']
                print(info)
                # 負責人：{work.author}, Time:{str_started}

    @classmethod
    def compute_cost(cls, sp_time):
        cost = sp_time.replace('d', '*8').replace('h', '*1').replace('m', '/60').replace(' ', '+')
        return cost

    @classmethod
    def count_timespant(cls, timespent):
        temp = list()
        a_list = list()
        time_list = list()
        for time in timespent:
            time_list = list()
            for t in time:
                cost = eval(cls.compute_cost(sp_time=t))
                time_list.append(cost)
            temp.append(time_list)
        for i in temp:
            a_list.append(sum(i))
        return a_list
            # print(timespent)
            # temp = list()
        #     for sp_time in time:
        #
        #         result = sp_time.replace('d', '*8').replace('h', '*1').replace('m', '/60').replace(' ', '+')
        #         result = eval(result)
        #         print(result)
        #     time_list.append(result)
        # print(time_list)
        #         temp.append(result)
        #     time_list.append(temp)
        # a_list = [sum(i) for i in time_list]
        # print(a_list)


        # return a_list





# 執行檔
if __name__ == '__main__':
    # Jira.count_timespant()
    Jira.export_excel()
    # jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
    # print(Jira.get_member_list(jira=jira))
