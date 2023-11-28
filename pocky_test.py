from jira import JIRA
import pygsheets
import re
import const


class ExcelParser:
    setting_file = 'google_info.json'
    survey_url = 'https://docs.google.com/spreadsheets/d/1fqCf63GdcCOAkUMCeFj3MS9r9IBHVhY4ZaoX3Zr3PsM/' \
                 'edit#gid=1029704456https://docs.google.com/spreadsheets/d/1fqCf63GdcCOAkUMCeFj3MS9r9IBHVhY4' \
                 'ZaoX3Zr3PsM/edit#gid=1029704456'

    @classmethod
    def get_excel_info(cls, project_name):
        get_json = pygsheets.authorize(service_file=ExcelParser.setting_file)
        open_by_url = get_json.open_by_url(ExcelParser.survey_url)
        worksheet = open_by_url.worksheet_by_title(project_name)
        data = worksheet.get_all_records()
        return data

    @classmethod
    def exec(cls, project_name):
        excel_data = cls.get_excel_info(project_name=project_name)
        cls.parse_info(excel_data=excel_data, project_name=project_name, is_open=True)
        return 'POCKYYYYYYY'

    @classmethod
    def parse_info(cls, excel_data, project_name, is_open):
        group_list = const.lead_list
        story_list = list()
        smell_story_list = list()

        for excel in excel_data:
            if excel['reporter']:
                PDM = excel['reporter']
            if excel['Epic_name']:
                title = excel['summary']
            data = {
                'issuetype': excel['issuetype'],
                'summary': title + excel['summary'],
                'description': excel['description'] or '-',
                'assignee': {'name': PDM},
                'reporter': {'name': PDM}
            }
            for key, value in excel.items():
                if key in excel and value == 'TRUE':
                    new_data = {
                        'issuetype': excel['issuetype'],
                        'summary': title + excel['summary'] + key,
                        'description': excel['description'] or '-',
                        'assignee': {'name': f'{group_list[key]}'},
                        'reporter': {'name': PDM}
                    }
                    smell_story_list.append(new_data)

            if excel['Epic_name'] != '':
                data['customfield_10103'] = excel['Epic_name']
            story_list.append(data)
        issue_id_list = cls.input_jira(datas=story_list, project_name=project_name, mapping=True)
        smell_issue_id_list = cls.input_jira(datas=smell_story_list, project_name=project_name, mapping=True)
        cls.mapping_order(smell_issue_id_list=smell_issue_id_list, issue_id_list=issue_id_list)
        cls.template(title=title, is_open=is_open)

    @classmethod
    def template(cls, title, is_open):
        if is_open is True:
            datas = cls.get_excel_info(project_name='Template')
            for data in datas:
                match = data['summary'].split(' ')
                result = match[0]
                if result in const.lead_list_:
                    data['assignee'] = {'name': f'{const.lead_list_[result]}'}
                    data['summary'] = title + data['summary']
            cls.input_jira(datas, project_name='PC', mapping=False)
        return 'OK'

    @classmethod
    def input_jira(cls, datas, project_name, mapping):
        jira = JIRA(server=const.domain, basic_auth=(const.account, const.password))
        id_list = list()
        mapping_id = None
        for data in datas:
            data['project'] = project_name
            issue_id = str(jira.create_issue(data))
            if mapping is True:
                id_list.append(issue_id)
                mapping_id = cls.mapping_id(issue_id_list=id_list, datas=datas)
        return mapping_id

    @classmethod
    def mapping_order(cls, smell_issue_id_list, issue_id_list):
        jira = JIRA(server=const.domain, basic_auth=(const.account, const.password))
        issue_id = None
        for data in smell_issue_id_list:
            match = re.match(r'(.*)【', data['name'])
            match = match.group(1)
            mapping_id = data['id']
            # 小單id
            for issue in issue_id_list:
                if match == issue['name']:
                    issue_id = issue['id']
            # 大單id
            jira.create_issue_link('relates to', issue_id, mapping_id)

    @classmethod
    def mapping_id(cls, issue_id_list, datas):
        mapping_list = list()
        for i in range(len(issue_id_list)):
            data = {
                'name': datas[i]['summary'],
                'id': issue_id_list[i],
            }
            mapping_list.append(data)
        return mapping_list


if __name__ == '__main__':
    ExcelParser.exec(project_name='PC')
