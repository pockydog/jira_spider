from jira import JIRA
import pygsheets
import threading
import re
import Const


class ExcelParser:

    @classmethod
    def get_excel_info(cls, project_name):
        get_json = pygsheets.authorize(service_file=Const.SETTING_FILE)
        open_by_url = get_json.open_by_url(Const.SURVEY_URL)
        worksheet = open_by_url.worksheet_by_title(project_name)
        data = worksheet.get_all_records()
        return data

    @classmethod
    def parse_info(cls, project_name, is_open):
        excel_data = cls.get_excel_info(project_name=project_name)
        story_list, smell_story_list, pdm, title = list(), list(), None, None
        for excel in excel_data:
            if excel['reporter'] or excel['Epic_name']:
                pdm = excel['reporter']
                title = excel['summary']
            data = cls.get_story_info(excel=excel, title=title, pdm=pdm)
            for key, value in excel.items():
                if key in excel and value == 'TRUE':
                    smell_story_list += [cls.get_story_info(excel=excel, key=key, pdm=pdm, title=title)]
            if excel['Epic_name'] != '':
                data['customfield_10103'] = excel['Epic_name']
                data['summary'] = title
            story_list.append(data)
        template_list, id_list = cls.template(title=title, is_open=is_open)
        return template_list, story_list, smell_story_list, id_list

    @classmethod
    def input_jira_issue(cls, project_name, is_open):
        id_list_ = list()
        template_list, story_list, smell_story_list, id_list = cls.parse_info(project_name=project_name, is_open=is_open)
        issue_id_list = cls.input_jira(datas=story_list, project_name=project_name, mapping=True, Epic=True)
        smell_issue_id_list = cls.input_jira(datas=smell_story_list, project_name=project_name, mapping=True,
                                             Epic=False)
        template_id_list = cls.input_jira(datas=template_list, project_name=project_name, mapping=True, Epic=False)
        for template in template_id_list:
            id_list_.extend([template['id'] for id_ in id_list if id_ == template['name'].split(']')[1]])
        return issue_id_list, smell_issue_id_list, template_id_list, template_list, id_list_

    @classmethod
    def mapping_order(cls, project_name, is_open):
        issue_id = None
        issue_id_list, smell_issue_id_list, template_id_list, template_list, id_list = cls.input_jira_issue(
            project_name=project_name, is_open=is_open)
        jira = JIRA(server=Const.domain, basic_auth=(Const.account, Const.password))
        for data in smell_issue_id_list:
            match = re.match(r'(.*)【', data['name'])
            match = match.group(1)
            mapping_id = data['id']
            # 小單id
            for issue in issue_id_list:
                if match == issue['name']:
                    issue_id = issue['id']
            # 大單id
            for id_ in id_list:
                jira.create_issue_link('relates to', issue_id, id_)
            #     Template 單id
            jira.create_issue_link('relates to', issue_id, mapping_id)

    @classmethod
    def template(cls, title, is_open):
        template_list = list()
        id_list = list()
        if is_open is True:
            datas = cls.get_excel_info(project_name='Template')
            for data in datas:
                match = data['summary'].split(' ')
                result = match[0]
                if result in Const.lead_list_:
                    data['assignee'] = Const.lead_list_[result]
                if data['is_link'] == 'TRUE':
                    id_list.append(data['summary'])
                template_list += [cls.get_story_info(excel=data, title=title, pdm=data['assignee'], key=None)]
        return template_list, id_list

    @classmethod
    def input_jira(cls, datas, project_name, mapping, Epic):
        jira = JIRA(server=Const.domain, basic_auth=(Const.account, Const.password))
        id_list = list()
        mapping_id = None
        test = None
        for data in datas:
            data['project'] = project_name
            issue_id = str(jira.create_issue(data))
            if mapping is True or data['issuetype'] == Const.EPIC_CODE:
                id_list.append(issue_id)
                mapping_id = cls.get_mapping_id_list(issue_id_list=id_list, datas=datas)
                # if data['issuetype'] == Const.EPIC_CODE:
                test = issue_id
        if Epic is True:
            for mapping in mapping_id:
                if test == mapping['id']:
                    continue
                jira.create_issue_link('relates to', mapping['id'], test)
        return mapping_id

    @classmethod
    def get_mapping_id_list(cls, issue_id_list, datas):
        mapping_list = list()
        for i in range(len(issue_id_list)):
            data = {
                'name': datas[i]['summary'],
                'id': issue_id_list[i],
            }
            mapping_list.append(data)
        return mapping_list

    @classmethod
    def get_story_info(cls, excel, title, pdm, key=None):
        data = {
            'issuetype': excel['issuetype'],
            'summary': title + excel['summary'],
            'description': excel['description'] or '自行填入',
            'assignee': {'name': pdm},
            'reporter': {'name': pdm}
        }
        if key is not None:
            group_list = Const.lead_list
            data['summary'] += key
            data['assignee']['name'] = f'{group_list[key]}'
        return data


if __name__ == '__main__':
    ExcelParser.mapping_order(project_name='PC', is_open=True)
    # ExcelParser.mapping_order(project_name='PC')
