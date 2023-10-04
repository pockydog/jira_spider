from jira import JIRA
import re
from tqdm import tqdm
import pandas as pd
from Tool.week_tool import TimeTool
from Tool.count_tool import CountTool
from Tool.group_tool import GroupTool
from report import Jira_
import const


class Jira:
    # 基本設定
    # group = [{'QA': 0}, {'PM': 0}, {'Server': 0}, {'FE-RD': 0}, {'BE-RD': 0}, {'Design': 0}]
    is_this_week = False

    @classmethod
    def get_person_info(cls, this_week):
        """
        Main content
        取得相關所需資料
        """
        jira = JIRA(server=const.domain, basic_auth=(const.account, const.password))
        user_list = list()
        timespent = list()
        start, end = TimeTool.new_parse_week(this_week=this_week)

        # 下條件式, 利用JQL
        issues = jira.search_issues(f'updated >= {start} AND updated <= now()', maxResults=0)
        # 取得資料 解析
        for issue in tqdm(issues):
            worklogs = jira.worklogs(issue)
            timespent += [Jira.get_worklog_info(worklogs=worklogs, this_week=this_week)]
            user_list += [Jira.get_worklog_info(worklogs=worklogs, this_week=this_week, time=False)]
        worklog_ = CountTool.sum_info(name_list=user_list, timespent=timespent)
        result = Jira.get_spendtime(jira=jira, worklog_=worklog_)

        return result

    @classmethod
    def get_worklog_info(cls, worklogs, this_week, time=True):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = TimeTool.parse_week_(this_week=this_week, rule=True)
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
    def get_spendtime(cls, jira, worklog_):
        groups = GroupTool.get_group(jira=jira, group_list=True)
        for i in str(worklog_).split(','):
            name = str(re.sub(r'[^a-zA-Z,]', '', i))
            time = str(re.sub(r'[^0-9/.]', '', i)).lstrip('.')
            for g in groups:
                if g['name'] == name:
                    g['time'] += float(time)
        df = pd.DataFrame(groups)
        df.to_excel(f'vicky.xlsx', 'counter1', index=False)

