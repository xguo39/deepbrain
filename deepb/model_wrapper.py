from deepb.models import Raw_input_table

class Raw_input_table_with_status_and_id(object):
    raw_input_table = None
    status = None
    main_table_id = None

    def __init__(self, raw_input_table, status, main_table_id=None):
        self.raw_input_table = raw_input_table
        self.status = status
        self.main_table_id = main_table_id