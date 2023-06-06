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

    # 排除目前沒有使用的 project 列表, 暫未開啟使用
    block_project_list = [
        'CCUattele', 'CKDT', 'Core', 'Block Chain', 'Lucky Hash',
        'QA-Automation-Group', 'Online Casino Management System', 'release',
        'WT', 'WT-NIU', 'WT_role_integration', 'WT_好路推薦', 'WT_後台顯示各項占成交收',
        'WT_百家樂']

    @classmethod
    def get_member_list(cls, jira):
        """
        取得所有 Trevi 員工資訊, 並移除'目標範圍外'的員工 --->'block_list'
        """
        members = jira.group_members('TREVI')
        members_list = [member for member in members if member not in Jira.block_list]
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
    def parse_last_week(cls, form='%Y-%m-%d'):
        today = datetime.date.today()
        begin_of_last_week = (today - datetime.timedelta(days=today.isoweekday() + 7)).strftime(form)
        end_of_last_week = (today - datetime.timedelta(days=today.isoweekday() + 1)).strftime(form)
        return begin_of_last_week, end_of_last_week


    @classmethod
    def get_person_info(cls):
        """
        Main content
        取得相關所需資料
        """
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        members_list = Jira.get_member_list(jira=jira)
        worklog_list = list()
        start, end = Jira.parse_week()
        summary = list()
        project = list()

        for user in tqdm(members_list):
            # 下條件式, 利用JQL
            issues = jira.search_issues(
                f'updated > {start} '
                f'AND updated < now()'
                f'AND (assignee was {user} OR reporter = {user})'
            )
            # 取得資料 解析
            for issue in issues:
                worklogs = jira.worklogs(issue)
                summary += [issue.fields.summary]
                project += [issue.fields.project.name]
                worklog_list += [Jira.get_worklog_info(worklogs=worklogs, user=user)]

        return worklog_list

    @classmethod
    def get_worklog_info(cls, worklogs, user):
        """
        取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        worklog_list = list()
        week = Jira.parse_week()
        for work in worklogs:
            started = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", work.started)
            str_started = "".join(started)
            if str_started in week:
                info = [f'Time：{work.timeSpent}, 人:{work.author}, 內容：{work.comment}']
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


if __name__ == '__main__':
    print(Jira.get_person_info())
    # print(Jira.get_person_info())
