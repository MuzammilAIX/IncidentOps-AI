
from celery import shared_task


@shared_task
def execute_remediation_task(plan_id: str):
    return {"plan_id": plan_id, "status": "pending"}
