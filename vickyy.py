from jira import JIRA
import pygsheets
import re
import Const


class JiraAutoCreateIssue:
    def __init__(self, project_name, is_open):
        self.project_name = project_name
        self.is_open = is_open

    def get_excel_data(self, project_name):
        """
        取得Excel 資料，回傳Json格式
        """
        get_json = pygsheets.authorize(service_file=Const.SETTING_FILE)
        open_by_url = get_json.open_by_url(Const.SURVEY_URL)
        worksheet = open_by_url.worksheet_by_title(project_name)
        data = worksheet.get_all_records()
        return data

    def parse_infos(self):
        """
        將取得資料解析為Jira 可創單格式
        """
        excel_data = self.get_excel_data(project_name=self.project_name)  # excel資料
        feature_story_list, department_story_list, pdm, title = list(), list(), None, None
        for data in excel_data:
            if data['reporter'] or data['Epic_name']:
                pdm = data['reporter']  # 定義項目PDM
                project_title = data['summary']  # 定義項目標題名稱
            feature_story_list += [self.parse_excel_data(excel=data, pdm=pdm, project_title=project_title)]
            # 創建 Feature Story 單 / Epic 單 解析為Jira 可創單格式
            for key, value in data.items():
                if key in data and value == 'TRUE':
                    department_story_list += [self.parse_excel_data(excel=data, key=key, pdm=pdm,
                                                                    project_title=project_title)]
                    # 創建 Department Story單 解析為Jira 可創單格式
        template_list, template_link_id_list = self.parse_templat_data(project_title=project_title, pdm=pdm,
                                                                       is_open=self.is_open)
        # 創建 Template Story單 解析為Jira 可創單格式
        return template_list, feature_story_list, department_story_list, template_link_id_list

    def auto_create(self):
        template_list, feature_story_list, department_story_list, template_link_id_list = self.parse_infos()
        feature_story_id_list = self.input_jira(datas=feature_story_list, is_epic=True)  # 創建 feature story 單
        self.input_jira(datas=department_story_list, info=feature_story_list)  # 創建 Department story 單
        self.mapping_template_link(template_list=template_list, mapping_id_list=feature_story_id_list,
                                   template_link_id_list=template_link_id_list)  # 創建 Template story

    def mapping_template_link(self, template_list, mapping_id_list, template_link_id_list):
        jira = JIRA(server=Const.domain, basic_auth=(Const.account, Const.password))
        for template in template_list:
            template['project'] = self.project_name
            issue_id = str(jira.create_issue(template))
            template['id'] = issue_id

            if template['summary'] in template_link_id_list:
                template_link_id = template['id']
                for issue in mapping_id_list:
                    jira.create_issue_link('relates to', issue, template_link_id)

    def parse_templat_data(self, project_title, pdm, is_open):
        template_list = list()
        id_list = list()
        if is_open is True:
            datas = self.get_excel_data(project_name=Const.Template_sheet)
            for data in datas:
                match = data['summary'].split(' ')
                result = match[0]
                if result in Const.lead_list_:
                    data['assignee'] = Const.lead_list_[result]
                if data['is_link'] == 'TRUE':  # 判斷是否該 Templat 需要Link Feature Story 單
                    id_list.append(project_title + data['summary'])
                template_list += [self.parse_excel_data(excel=data, project_title=project_title, pdm=pdm, key=None,
                                                        Template={'name': data['assignee']})]
        return template_list, id_list

    def input_jira(self, datas, info=None, is_epic=None):
        jira = JIRA(server=Const.domain, basic_auth=(Const.account, Const.password))
        Epic_id = None
        issue_id_list = list()
        for data in datas:
            data['project'] = self.project_name
            issue_id = str(jira.create_issue(data))
            data['id'] = issue_id
            if info:
                id_ = self.input_test(data=data, info=info)
                jira.create_issue_link('relates to', issue_id, id_)
            if is_epic:
                if data['issuetype'] == Const.EPIC_CODE:
                    Epic_id = data['id']
                if Epic_id != data['id']:
                    jira.create_issue_link('relates to', issue_id, Epic_id)
                    issue_id_list.append(issue_id)
        return issue_id_list

    def input_test(self, data, info):
        match = re.match(r'(.*)【', data['summary'])
        match = match.group(1)
        for _ in info:
            if match == _['summary']:
                return _['id']

    def parse_excel_data(self, excel, project_title, pdm, key=None, Template=None):
        data = {
            'issuetype': excel['issuetype'],
            'summary': project_title + excel['summary'],
            'description': excel['description'] or '自行填入',
            'assignee': {'name': pdm},
            'reporter': {'name': pdm}
        }
        if data['issuetype'] == 'Epic':
            data['customfield_10103'] = str(excel['summary'])
            data['summary'] = project_title
        if Template:
            data['assignee'] = Template

        if key is not None:
            group_list = Const.lead_list
            data['summary'] += key
            data['assignee']['name'] = f'{group_list[key]}'
        return data


if __name__ == '__main__':
    parser = JiraAutoCreateIssue(project_name='PTRR', is_open=True)
    parser.auto_create()
# 創單模式要改，若只要Template 的單，需要爬下所有單來找單號，然後再來 Mapping 且涵蓋 link 功能
# V2 a爬蟲 順便夾帶功能
