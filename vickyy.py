from jira import JIRA
import pygsheets
import re
import Const


class ExcelParser:
    def __init__(self, project_name, is_open):
        self.project_name = project_name
        self.is_open = is_open

    def get_excel_info(self, project_name):
        get_json = pygsheets.authorize(service_file=Const.SETTING_FILE)
        open_by_url = get_json.open_by_url(Const.SURVEY_URL)
        worksheet = open_by_url.worksheet_by_title(project_name)
        data = worksheet.get_all_records()
        return data

    def parse_info(self):
        excel_data = self.get_excel_info(project_name=self.project_name)
        feature_story_list, department_story_list, pdm, title = list(), list(), None, None
        for data in excel_data:
            if data['reporter'] or data['Epic_name']:
                pdm = data['reporter']
                title = data['summary']
            feature_story_list += [self.get_story_info(excel=data, title=title, pdm=pdm)]
            for key, value in data.items():
                if key in data and value == 'TRUE':
                    department_story_list += [self.get_story_info(excel=data, key=key, pdm=pdm, title=title)]
        if self.is_open is True:
            template_list, id_list = self.template(title=title, is_open=self.is_open)
            return template_list, feature_story_list, department_story_list, id_list
        else:
            return feature_story_list, department_story_list

    def input_jira_issue(self):
    #     id_list_ = list()
        template_list, story_list, smell_story_list, id_list = self.parse_info()
        issue_id_list = self.input_jira(datas=story_list, mapping=True, Epic=True)
    #     smell_issue_id_list = self.input_jira(datas=smell_story_list, mapping=True, Epic=False)
    #     template_id_list = self.input_jira(datas=template_list, mapping=True, Epic=False)
    #
    #     for template in template_id_list:
    #         id_list_.extend([template['id'] for id_ in id_list if id_ == template['name'].split(']')[1]])
    #
    #     return issue_id_list, smell_issue_id_list, template_id_list, template_list, id_list_
    #
    # def mapping_order(self):
    #     issue_id = None
    #     issue_id_list, smell_issue_id_list, template_id_list, template_list, id_list = self.input_jira_issue()
    #     jira = JIRA(server=Const.domain, basic_auth=(Const.account, Const.password))
    #
    #     for data in smell_issue_id_list:
    #         match = re.match(r'(.*)【', data['name'])
    #         match = match.group(1)
    #         mapping_id = data['id']
    #
    #         for issue in issue_id_list:
    #             if match == issue['name']:
    #                 issue_id = issue['id']
    #
    #         for id_ in id_list:
    #             jira.create_issue_link('relates to', issue_id, id_)
    #
    #         jira.create_issue_link('relates to', issue_id, mapping_id)
    #
    def template(self, title, is_open):
        template_list = list()
        id_list = list()
        if is_open is True:
            datas = self.get_excel_info(project_name='Template')
            for data in datas:
                match = data['summary'].split(' ')
                result = match[0]
                if result in Const.lead_list_:
                    data['assignee'] = Const.lead_list_[result]
                if data['is_link'] == 'TRUE':
                    id_list.append(data['summary'])
                template_list += [self.get_story_info(excel=data, title=title, pdm=data['assignee'], key=None)]
            return template_list, id_list
    #
    def input_jira(self, datas, mapping, Epic):
        jira = JIRA(server=Const.domain, basic_auth=(Const.account, Const.password))
        id_list = list()
        mapping_id = None
        test = None

        for data in datas:
            data['project'] = self.project_name
            issue_id = str(jira.create_issue(data))

            if mapping is True or data['issuetype'] == Const.EPIC_CODE:
                id_list.append(issue_id)
                mapping_id = self.get_mapping_id_list(issue_id_list=id_list, datas=datas)
                test = issue_id

        if Epic is True:
            for mapping in mapping_id:
                if test == mapping['id']:
                    continue
                jira.create_issue_link('relates to', mapping['id'], test)

        return mapping_id
    #
    # def get_mapping_id_list(self, issue_id_list, datas):
    #     mapping_list = list()
    #
    #     for i in range(len(issue_id_list)):
    #         data = {
    #             'name': datas[i]['summary'],
    #             'id': issue_id_list[i],
    #         }
    #         mapping_list.append(data)
    #
    #     return mapping_list

    def get_story_info(self, excel, title, pdm, key=None):
        data = {
            'issuetype': excel['issuetype'],
            'summary': title + excel['summary'],
            'description': excel['description'] or '自行填入',
            'assignee': {'name': pdm},
            'reporter': {'name': pdm}
        }
        if excel['Epic_name'] != '':
            data['customfield_10103'] = str(excel['Epic_name'])
            data['summary'] = title

        if key is not None:
            group_list = Const.lead_list
            data['summary'] += key
            data['assignee']['name'] = f'{group_list[key]}'

        return data


if __name__ == '__main__':
    parser = ExcelParser(project_name='PC', is_open=False)
    print(parser.input_jira_issue())
