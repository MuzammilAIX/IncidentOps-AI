def inject(service_id: str, percent: int = 99):
    return {"service_id": service_id, "failure": "cpu_spike", "percent": percent}
