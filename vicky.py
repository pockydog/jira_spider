from jira import JIRA
import const


class JiraAutoCreateOrder:
    PROJECT_NAME = 'PC'

    @classmethod
    def jira(cls):
        jira = JIRA(server=const.domain, basic_auth=(const.account, const.password))
        # project_id = jira.project(JiraAutoCreateOrder.PROJECT_NAME).id
        # issue = {
        #     'project': {'id': project_id},
        #     'issuetype': {'name': 'PM Story'},
        #     'summary': '',
        #     'description': 'pocky',
        # }
        # jira.create_issue(issue)


        data = {
            'project': 'PC',
            'issuetype': 'Epic',
            'customfield_10103': 'vickys',
            'summary': '[LT v1] Epic',
            'description': 'test',
            'assignee': {'name': 'Vicky.C'}
        }
        a = jira.create_issue(data)
        print(a)

if __name__ == '__main__':
    JiraAutoCreateOrder.jira()
