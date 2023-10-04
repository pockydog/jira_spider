import re


class GroupTool:
    group_list = ['QA', 'PM', 'Server', 'FE-RD', 'BE-RD', 'Design']
    group_dict = ['QA', 'PM', 'Server', 'FE-RD', 'BE-RD', 'Design']

    @classmethod
    def get_group(cls, jira, group_list):
        member_list = list()
        member_set = dict()
        result = None

        for group in GroupTool.group_list:
            group_members = jira.group_members(group)
            for member in group_members:
                if group_list is True:
                    result = GroupTool.get_group_info(group=group, member=member, member_list=member_list)
                else:
                    result = GroupTool.counter_for_group(group=group, member_set=member_set)
        return result

    @classmethod
    def get_group_info(cls, group, member, member_list):
        member_ = {
            'group': group,
            'name': str(re.sub(r'[^a-zA-Z,]', '', member)),
            'time': int(0)
        }
        member_list.append(member_)
        return member_list

    @classmethod
    def counter_for_group(cls, group, member_set):
        if group in member_set:
            member_set[group] += 1
        else:
            member_set[group] = 1

        return member_set
