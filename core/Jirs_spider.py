from jira import JIRA

from tqdm import tqdm
import pandas as pd
import re

import Const
from Tool.week_tool import TimeTool
from Tool.count_tool import CountTool
from Tool.group_tool import GroupTool


class JiraTest:
    PM = 'PM Team'
    Design = 'Design Team'

    @classmethod
    def exec(cls, this_week):

        jira = JIRA(server=Const.domain, basic_auth=(Const.account, Const.password))
        start_day, end_day = TimeTool.new_parse_week(this_week=this_week)
        groups = GroupTool.get_group(jira=jira, group_list=True)
        project_list = list()

        # 利用JQL, 下條件式
        issues = jira.search_issues(f'updated >= {start_day} AND updated <= now()', maxResults=0)
        # 取得資料並且解析
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
        groups_dict = {group['name']: group for group in groups}
        for project in project_list:
            if project is None:
                continue
            name = project['name']
            project_time = float(project['spend_time'])  # 一次轉換，避免重複
            if name in groups_dict:
                groups_dict[name]['time'] += project_time
        updated_groups = list(groups_dict.values())
        return updated_groups

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
                project_dict = {'project': project, 'QA': 0, 'FERD': 0, 'BERD': 0, 'PM': 0, 'ServerRD': 0, 'Design': 0}
                result.append(project_dict)
            project_dict[group] += time
        return result

    @classmethod
    def excel(cls, info1, info2, info3):
        writer = pd.ExcelWriter(r'/Users/user/Desktop/vicky_report 2024.02.xlsx')
        df1 = pd.DataFrame(info1)
        df2 = pd.DataFrame(info2)
        df3 = pd.DataFrame(info3)
        df1.to_excel(writer, sheet_name='By_name')
        df2.to_excel(writer, sheet_name='By_project')
        df3.to_excel(writer, sheet_name='By_group')
        writer.close()

    @classmethod
    def get_worklog_info(cls, worklogs, this_week, issue, groups):
        """
        取得 all_worklog 資料
        """
        week = TimeTool.parse_week_(this_week=this_week, rule=True)
        results = list()

        project_name = issue.fields.project.name
        summary = issue.fields.summary
        link = issue.permalink()

        # 預先處理專案名稱
        if project_name in [JiraTest.Design, JiraTest.PM]:
            prog = re.compile('【.*?】')
            re_content = prog.match(summary)
            project_name = re_content.group() if re_content else project_name
        else:
            project_name = 'Design Team' if project_name == 'Design Team' else 'PM Team' if project_name == 'PM Team' else project_name

        for work in worklogs:
            parse = work.started[:10]
            if parse not in week:
                continue

            author_name = re.sub(r'[^a-zA-Z,]', '', work.author.name)
            group_name = next((g['group'] for g in groups if g['name'] == author_name), '')

            results.append({
                'project': project_name,
                'group': re.sub(r'[^a-zA-Z,]', '', str(group_name)),
                'name': author_name,
                'summary': summary,
                'spend_time': round(eval(CountTool.compute_cost(sp_time=work.timeSpent))),
                'link': link,
                'log': work.comment or ''
            })

        return results
