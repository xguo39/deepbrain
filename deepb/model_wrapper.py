from deepb.models import Raw_input_table

class Raw_input_table_with_status_and_id(object):
    raw_input_table = None
    status = None
    id = None

    def __init__(self, raw_input_table, status, id=None):
        self.raw_input_table = raw_input_table
        self.status = status
        self.id = id