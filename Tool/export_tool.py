import xlwt


class Export:

    @classmethod
    def export_excel(cls, this_week):
        """
        匯出 且 存入 excel
        """
        # user_list, summary, project, priority, str_creatd, status_list, timespent, t_worklog_, link, worklog_ =Jira.get_person_info(this_week=this_week)
        # file = xlwt.Workbook('encoding = utf-8')
        # format_info = set(project)
        # for info in format_info:
        #     sheet = file.add_sheet(f'{info}', cell_overwrite_ok=True)
        #     sheet.write(0, 0, '')
        #     sheet.write(0, 1, 'user_list')
        #     sheet.write(0, 2, 'project')
        #     sheet.write(0, 3, 'summary')
        #     sheet.write(0, 4, 'priority')
        #     sheet.write(0, 5, 'created')
        #     sheet.write(0, 6, 'status')
        #     sheet.write(0, 7, 'worklog')
        #     sheet.write(0, 8, 'total_worklog')
        #     sheet.write(0, 9, 'link')
        #     round = 0
        #     for i in range(len(project)):
        #         if info != project[i]:
        #             continue
        #         else:
        #             round += 1
        #             sheet.write(round + 1, 1, user_list[i])
        #             sheet.write(round + 1, 2, project[i])
        #             sheet.write(round + 1, 3, summary[i])
        #             sheet.write(round + 1, 4, priority[i])
        #             sheet.write(round + 1, 5, str_creatd[i])
        #             sheet.write(round + 1, 6, status_list[i])
        #             sheet.write(round + 1, 7, worklog_[i])
        #             sheet.write(round + 1, 8, t_worklog_[i])
        #             sheet.write(round + 1, 9, link[i])




