import datetime as dt
from data.__all_models import Jobs, User
from data.db_session import global_init, create_session

global_init('db/blogs.db')
db_sess = create_session()

job = Jobs()
job.team_leader = 1
job.job = 'deployment of residential modules 1 and 2'
job.work_size = 15
job.collaborators = '2, 3'
job.is_finished = False

