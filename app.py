from core.vicky_report import Jira
from core.weekly_report import Jira
from core.pocky_report import JiraByOrder

if __name__ == '__main__':
    Jira.export_excel_test(this_week=False)
    # Jira.get_person_info(this_week=False)
    # JiraByOrder.get_person_info(this_week=False)
