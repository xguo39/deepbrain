import datetime

class Config(object):
    max_task_waiting_time = datetime.timedelta(minutes=10)

class Constant(object):
    FAIL_STATUS = 'Failed'
    IN_PROGRESS_STATUS = 'In progress'
    SUCCESS_STATUS = 'Succeed'