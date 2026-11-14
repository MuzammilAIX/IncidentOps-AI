
"""Fake Docker client for local testing — singleton-based."""


class FakeDocker:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.containers = {}
        return cls._instance

    def create_container(self, service_id: str, state: str = "running"):
        self.containers[service_id] = {
            "state": state,
            "logs": [],
            "exit_code": None,
            "oom_killed": False,
            "restart_count": 0,
        }
        return self.containers[service_id]

    def get_status(self, service_id: str) -> dict:
        c = self.containers.get(service_id)
        if not c:
            return {"service_id": service_id, "state": "not_found"}
        return {
            "service_id": service_id,
            "state": c["state"],
            "exit_code": c.get("exit_code"),
            "oom_killed": c.get("oom_killed", False),
            "restart_count": c.get("restart_count", 0),
        }

    def get_logs(self, service_id: str, lines: int = 100) -> list:
        c = self.containers.get(service_id, {})
        logs = c.get("logs", [])
        return [{"line": line} for line in logs[-lines:]]

    def restart_container(self, service_id: str) -> dict:
        c = self.containers.get(service_id)
        if not c:
            return {"success": False, "error": "not found"}
        c["state"] = "running"
        c["oom_killed"] = False
        return {"success": True, "service_id": service_id, "new_state": "running"}
