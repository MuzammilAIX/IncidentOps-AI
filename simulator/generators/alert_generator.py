def generate_alert(service_id: str, severity: str = "high"):
    return {"service_id": service_id, "severity": severity}
