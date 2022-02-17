from datetime import datetime
from enum import Enum


class VisitInfo:
    user_id = 0
    user_display_name = "default_username"
    visit_type = ""
    channel_name = ""
    visit_datetime = ""

    def __init__(self, user_id: int, user_display_name: str,
                 visit_type: str, channel_name: str, visit_datetime: datetime):
        self.user_id = user_id
        self.user_display_name = user_display_name
        self.visit_type = visit_type
        self.channel_name = channel_name
        self.visit_datetime = visit_datetime.replace(microsecond=0)


def find_left(visits: list, join: VisitInfo):
    for v in visits:
        if v.visit_type == "left" and v.user_id == join.user_id:
            return v
    return None


class VisitPairs:
    visit_pairs: list

    def __init__(self, sorted_visits_list: list):
        """Convert sorted_visits_list to visit_pairs (sorted_visits_list will become empty)

        :param sorted_visits_list: list visits sorted by name and time
        """
        self.visit_pairs = list()
        while len(sorted_visits_list) > 0:
            visit = sorted_visits_list[0]
            if visit.visit_type == 'left':
                self.visit_pairs.append([None, visit])
                sorted_visits_list.remove(visit)
            elif visit.visit_type == 'joined':
                left = find_left(sorted_visits_list, visit)
                self.visit_pairs.append([visit, left])
                sorted_visits_list.remove(visit)
                if left is not None:
                    sorted_visits_list.remove(left)

    def get_all_visits_string(self):
        string = ''

        for joined, left in self.visit_pairs:
            if joined is None:
                string += f'{left.user_display_name}\t'
                string += f'\t'
                string += f'{left.visit_datetime}\t'
                string += f''
                string += '\n'
            elif left is None:
                string += f'{joined.user_display_name}\t'
                string += f'{joined.visit_datetime}\t'
                string += f'\t'
                string += f''
                string += f'\n'
            else:
                string += f'{joined.user_display_name}\t'
                string += f'{joined.visit_datetime}\t'
                string += f'{left.visit_datetime}\t'
                string += f'{left.visit_datetime - joined.visit_datetime}'
                string += '\n'

        return string


class WriteMode(Enum):
    write = 'w'
    write_byte = 'wb'
    append = 'a'
    append_byte = 'ab'


def write_visits_to_file(text: str, filename="visits.tsv", encoding="utf-8", write_mode=WriteMode.write):
    with open(filename, mode=write_mode.value, encoding=encoding) as file:
        file.write(text)
    return filename
