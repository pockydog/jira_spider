
from jira import JIRA

from tqdm import tqdm
import pandas as pd
import re

import const
from Tool.week_tool import TimeTool
from Tool.count_tool import CountTool
from Tool.group_tool import GroupTool


class JiraByProject:

    @classmethod
    def get_person_info(cls, this_week):

        jira = JIRA(server=const.domain, basic_auth=(const.account, const.password))
        start, end = TimeTool.new_parse_week(this_week=this_week)
        groups = GroupTool.get_group(jira=jira, group_list=True)
        result_list, spendtime_list, project_list, group_list = [[] for _ in range(4)]

        # 下條件式, 利用JQL
        issues = jira.search_issues(f'updated >= {start} AND updated <= now()', maxResults=0)
        # 取得資料 解析
        for issue in tqdm(issues):
            worklogs = jira.worklogs(issue)
            project_list += JiraByProject.get_worklog_info(
                worklogs=worklogs,
                this_week=this_week,
                groups=groups,
                issue=issue
            )

        JiraByProject.get(project_list=project_list)

    @classmethod
    def get(cls, project_list):
        result = list()
        for time in project_list:
            if time is None:
                continue
            else:
                project = time['project']
                group = time['group']
                time = float(time['spend_time'])
                project_dict = next((d for d in result if d['project'] == project), None)
            if project_dict is None:
                project_dict = {'project': project, 'QA': 0, 'FERD': 0, 'BERD': 0, 'PM': 0, 'Server': 0, 'Design': 0}
                result.append(project_dict)
            project_dict[group] += time
            df = pd.DataFrame(result)
            df.to_excel(f'Byperson.xlsx', 'counter1', index=False)

    @classmethod
    def get_worklog_info(cls, worklogs, this_week, issue, groups):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = TimeTool.parse_week_(this_week=this_week, rule=True)
        project_list, group_list, time_list, apple = [[] for _ in range(4)]

        for work in worklogs:
            parse = work.started[:10]
            if parse in week:
                project_list.append(issue.fields.project.name)
                time_list.append(round(eval(CountTool.compute_cost(sp_time=work.timeSpent))))
                a = [g['group'] for g in groups if g['name'] == str(re.sub(r'[^a-zA-Z,]', '', work.author.name))]
                group_list.append(re.sub(r'[^a-zA-Z,]', '', str(a)))
        for project in range(len(project_list)):
            result = {
                'project': project_list[project],
                'spend_time': time_list[project],
                'group': group_list[project]
            }
            apple.append(result)
        return apple


