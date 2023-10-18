from apscheduler.schedulers.background import BackgroundScheduler

def some_job():
    print("Every 10 seconds")


scheduler = BackgroundScheduler()

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler.configure(job_defaults=job_defaults)
scheduler.add_job(some_job, 'interval', seconds=3)
scheduler.start()





scheduler.shutdown()


##try:
##        # This is here to simulate application activity (which keeps the main thread alive).
##        while True:
##            time.sleep(2)
##    except (KeyboardInterrupt, SystemExit):
##        # Not strictly necessary if daemonic mode is enabled but should be done if possible
##        scheduler.shutdown()
