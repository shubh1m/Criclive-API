from apscheduler.schedulers.background import BackgroundScheduler
from app import cron

sched = BackgroundScheduler()
sched.start()

@sched.scheduled_job('interval', id='rand', seconds=30)
def task():
	cron()
