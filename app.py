from core.vicky_report import JiraByPeople
from core.weekly_report import JiraByAll
from core.pocky_dog import JiraByProject
from core.Jirs_spider import JiraTest

if __name__ == '__main__':
    # JiraByAll.export_excel_test(this_week=False)
    # JiraByProject.get_person_info(this_week=False)
    # JiraByPeople.get_person_info(this_week=False)
    JiraTest.get_person_info(this_week=False)
