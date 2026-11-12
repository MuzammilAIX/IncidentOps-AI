
from celery import shared_task


@shared_task
def poll_alerts():
    # fetch alerts -> create incidents -> trigger investigations
    return {"polled": 0}
