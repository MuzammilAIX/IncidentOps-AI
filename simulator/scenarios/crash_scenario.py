
"""Simulate a container crash for AI testing."""
from ai_engine.tools.docker_tools import _get_docker


def run_crash_scenario(service_id: str = "web-api") -> dict:
    """Simulate a container exiting with OOMKilled using the shared simulator instance."""
    docker = _get_docker()

    # Ensure container exists
    if hasattr(docker, "create_container"):
        docker.create_container(service_id, state="running")
        docker.containers[service_id]["logs"] = [
            "Starting web-api...",
            "FATAL: Out of memory",
            "OOMKilled",
        ]
        docker.containers[service_id]["state"] = "exited"
        docker.containers[service_id]["oom_killed"] = True
        docker.containers[service_id]["exit_code"] = 137
    elif hasattr(docker, "containers"):
        # Fallback: set state directly if create_container not available
        if service_id not in docker.containers:
            docker.containers[service_id] = {}
        docker.containers[service_id].update({
            "state": "exited",
            "oom_killed": True,
            "exit_code": 137,
            "logs": ["FATAL: Out of memory", "OOMKilled"],
        })

    return docker.get_status(service_id)
