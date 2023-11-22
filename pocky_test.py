from jira import JIRA
import pygsheets

import const


class ExcelParser:
    setting_file = 'google_info.json'
    survey_url = 'https://docs.google.com/spreadsheets/d/1fqCf63GdcCOAkUMCeFj3MS9r9IBHVhY4ZaoX3Zr3PsM/' \
                 'edit#gid=1029704456https://docs.google.com/spreadsheets/d/1fqCf63GdcCOAkUMCeFj3MS9r9IBHVhY4' \
                 'ZaoX3Zr3PsM/edit#gid=1029704456'

    @classmethod
    def get_excel_info(cls, project_name, PDM):
        get_json = pygsheets.authorize(service_file=ExcelParser.setting_file)
        open_by_url = get_json.open_by_url(ExcelParser.survey_url)
        worksheet = open_by_url.worksheet_by_title(project_name)
        datas = worksheet.get_all_records()
        data = cls.parse_info(target_info=datas, project_name=project_name, PDM=PDM)
        # for i in data:
        #     print(i)

        return data

    @classmethod
    def parse_info(cls, target_info, project_name, PDM):
        group_list = const.lead_list
        my_list = list()
        print(PDM)

        for target in target_info:
            data = {
                'issuetype': target['issuetype'],
                'summary': target['summary'],
                'description': target['description'],
                'assignee': {'name': 'Ian.W'},
                'reporter': {'name': 'Ian.W'}
            }
            if target['Epic_name'] != '':
                data['customfield_10103'] = target['Epic_name']
            my_list.append(data)
            cls.input_jira(datas=my_list, project_name=project_name)
        print(my_list)
        #     for key, value in target.items():
        #         if key in group_list and value == 'TRUE':
        #             new_data = {
        #                 'issuetype': target['issuetype'],
        #                 'summary': target['summary'] + key,
        #                 'description': target['description'],
        #                 'assignee': {'name': f'{group_list[key]}'},
        #                 'reporter': {'name': PDM}
        #
        #             }
        #             my_list.append(new_data)
        # return my_list

    @classmethod
    def input_jira(cls, datas, project_name):
        jira = JIRA(server=const.domain, basic_auth=(const.account, const.password))
        for info in datas:
            info['project'] = project_name
            issue_id = jira.create_issue(info)
            # info['project_id'] = str(issue_id)
            # print(info)

    @classmethod
    def test_by_vicky(cls):
        jira = JIRA(server=const.domain, basic_auth=(const.account, const.password))
        data = {
            'project': 'PC',
            'issuetype': 'Epic',
            'customfield_10103': 'vickys',
            'summary': '[LT v1] Epic',
            'description': 'test',
            'assignee': {'name': 'Alan.Y'},
            'reporter': {'name': 'Ian.W'}

        }
        issue = jira.create_issue(data)
        print(issue)

    # new_issue = 'PC-10'
    # parnet_issue = 'PC-20'
    # jira.create_issue_link(
    #     type='relates to',
    #     inwardIssue=new_issue,
    #     outwardIssue=parnet_issue,
    # )


if __name__ == '__main__':
    # print(ExcelParser.input_jira(project_name='PC', PDM='Ian.W'))
    # print(ExcelParser.test_by_vicky())
    print(ExcelParser.get_excel_info(project_name='PC', PDM='Ian.W'))
