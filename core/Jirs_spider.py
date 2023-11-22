from jira import JIRA

from tqdm import tqdm
import pandas as pd
import re

import const
from Tool.week_tool import TimeTool
from Tool.count_tool import CountTool
from Tool.group_tool import GroupTool


class JiraTest:

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
            project_list += JiraTest.get_worklog_info(
                worklogs=worklogs,
                this_week=this_week,
                groups=groups,
                issue=issue
            )
        person = JiraTest.get_project_by_person(project_list=project_list, groups=groups)
        group = JiraTest.get_project_by_group(project_list=project_list)
        JiraTest.excel(info1=project_list, info2=person, info3=group)
        return True

    @classmethod
    def get_project_by_person(cls, project_list, groups):
        for time in project_list:
            if time is None:
                continue
            else:
                name = time['name']
                time = float(time['spend_time'])
                for g in groups:
                    if g['name'] == name:
                        g['time'] += float(time)
        return groups

    @classmethod
    def get_project_by_group(cls, project_list):
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
        return result

    @classmethod
    def excel(cls, info1, info2, info3):
        writer = pd.ExcelWriter(r'/Users/user/Desktop/vicky_report.xlsx')
        df1 = pd.DataFrame(info1)
        df2 = pd.DataFrame(info2)
        df3 = pd.DataFrame(info3)
        df1.to_excel(writer, sheet_name='By_name')
        df2.to_excel(writer, sheet_name='By_project')
        df3.to_excel(writer, sheet_name='By_group')
        writer.close()

        # df1 = pd.DataFrame(result)
        # df.to_excel(f'Byperson.xlsx', 'counter1', index=False)

    @classmethod
    def get_worklog_info(cls, worklogs, this_week, issue, groups):
        """
            取得 all_worklog 資料
        """
        week = TimeTool.parse_week_(this_week=this_week, rule=True)
        project_list, group_list, time_list, apple, issue_list, name_list = [[] for _ in range(6)]

        for work in worklogs:
            parse = work.started[:10]
            if parse in week:
                issue_list.append(issue.fields.summary)
                time_list.append(round(eval(CountTool.compute_cost(sp_time=work.timeSpent))))
                name_list.append(str(re.sub(r'[^a-zA-Z,]', '', work.author.name)))
                a = [g['group'] for g in groups if g['name'] == str(re.sub(r'[^a-zA-Z,]', '', work.author.name))]
                group_list.append(re.sub(r'[^a-zA-Z,]', '', str(a)))
                if issue.fields.project.name == 'Design Team':
                    prog = re.compile('【.*?】')
                    re_content = prog.match(issue.fields.summary)
                    if re_content:
                        project_list.append(re_content.group())
                    else:
                        project_list.append('Design Team')
                else:
                    project_list.append(issue.fields.project.name)

        for project in range(len(project_list)):
            result = {
                'project': project_list[project],
                'group': group_list[project],
                'name': name_list[project],
                'summary': issue_list[project],
                'spend_time': time_list[project],
            }
            apple.append(result)
        return apple
