from collections import defaultdict

from jira import JIRA

from tqdm import tqdm
import pandas as pd
import re

import const
from Tool.week_tool import TimeTool
from Tool.count_tool import CountTool
from Tool.group_tool import GroupTool


class JiraByOrder:
    parse_info = {
        'project': '',
        'QA': 0,
        'FE-RD': 0,
        'BE-RD': 0,
        'PM': 0,
        'Server': 0,
        'Design': 0
    }

    @classmethod
    def get_person_info(cls, this_week):
        jira = JIRA(server=const.domain, basic_auth=(const.account, const.password))
        info_, user_list, timespent, project, link, summary = [list() for _ in range(6)]
        start, end = TimeTool.new_parse_week(this_week=this_week)
        groups = GroupTool.get_group(jira=jira, group_list=True)
        # 下條件式, 利用JQL
        issues = jira.search_issues(f'updated >= {start} AND updated <= now()', maxResults=0)
        # 取得資料 解析
        for issue in tqdm(issues):
            worklogs = jira.worklogs(issue)
            project = issue.fields.project.name
            timespent += [JiraByOrder.get_worklog_info(
                worklogs=worklogs,
                this_week=this_week,
                project=project,
                groups=groups
            )]
        vicky = JiraByOrder.get(timespent=timespent)

        # worklog_ = CountTool.sum_info(name_list=user_list, timespent=timespent)
        # JiraByOrder.get_spendtime(jira=jira, worklog_=worklog_)

    @classmethod
    def get(cls, timespent):
        result = list()
        for time in timespent:
            if time is None:
                continue
            else:
                project = time['project']
                group = time['group']
                time = float(time['time'])
                project_dict = next((d for d in result if d['project'] == project), None)
            if project_dict is None:
                project_dict = {'project': project, 'QA': 0, 'FE-RD': 0, 'BE-RD': 0, 'PM': 0, 'Server': 0, 'Design': 0}
                result.append(project_dict)
            project_dict[group] += time
            df = pd.DataFrame(result)
            df.to_excel(f'vp.xlsx', 'counter1', index=False)

        return result

    @classmethod
    def get_worklog_info(cls, worklogs, this_week, project, groups):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = TimeTool.parse_week_(this_week=this_week, rule=True)
        # groups = GroupTool.get_group(jira=jira, group_list=True)
        # for i in str(worklog_).split(','):
        #     name = str(re.sub(r'[^a-zA-Z,]', '', i))
        #     time = str(re.sub(r'[^0-9/.]', '', i)).lstrip('.')
        #     for g in groups:

        for work in worklogs:
            parse = work.started[:10]
            if parse in week:
                name = str(re.sub(r'[^a-zA-Z,]', '', work.author.name))
                time = f'{round(eval(CountTool.compute_cost(sp_time=work.timeSpent)), 2)}'
                for g in groups:
                    if g['name'] == name:
                        role = g['group']
                        info = {
                            'project': project,
                            'time': time,
                            'group': role
                        }
                        return info

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


if __name__ == '__main__':
    JiraByOrder.get_person_info(this_week=True)
