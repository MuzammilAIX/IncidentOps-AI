"""Seed realistic runbooks matching the demo incidents."""
from apps.monitoring.models import Runbook


RUNBOOKS = [
    {
        "code": "RB-101",
        "title": "Payment service returning HTTP 500 after deploy",
        "category": "deployment",
        "service_hint": "payment-service",
        "keywords": ["payment", "500", "migration", "deploy", "insert", "null"],
        "content": "SYMPTOM: payment-service returns HTTP 500 to all requests; logs show 'null value in column payment_id violates not-null constraint'.\n\nLIKELY CAUSE: A recent deployment introduced a schema change without applying the corresponding data migration.\n\nIMMEDIATE MITIGATION:\n1. Check the most recent deployment.\n2. Compare against last known good deployment tag.\n3. Roll back to the previous SHA.\n4. Verify with /health.\n\nFOLLOW-UP:\n- File a postmortem for the missing migration.\n- Add a pre-deploy migration check to CI.",
    },
    {
        "code": "RB-102",
        "title": "Container OOM-killed - memory exhaustion",
        "category": "resource",
        "keywords": ["oom", "memory", "killed", "restart", "exhausted"],
        "content": "SYMPTOM: Container state=exited, oom_killed=true, exit_code=137. Frequent restarts.\n\nLIKELY CAUSE: Memory limit exceeded - either a leak or a traffic spike.\n\nIMMEDIATE MITIGATION:\n1. Confirm oom_killed with docker inspect.\n2. Check memory limit.\n3. Increase limit: docker update --memory 2g.\n4. Restart the container.\n\nLONG-TERM:\n- Profile heap usage with py-spy or memray.\n- Add memory alerts at 80 percent of limit.",
    },
    {
        "code": "RB-103",
        "title": "API gateway 502 Bad Gateway from upstream",
        "category": "network",
        "service_hint": "api-gateway",
        "keywords": ["502", "gateway", "upstream", "bad gateway", "proxy"],
        "content": "SYMPTOM: api-gateway returns 502 Bad Gateway to clients. Upstream requests fail.\n\nLIKELY CAUSE: Upstream service (e.g., payment-service) is down or returning 5xx.\n\nIMMEDIATE MITIGATION:\n1. Identify affected upstream in gateway logs.\n2. Check upstream health.\n3. If upstream is down, restart it.\n4. If upstream is returning errors, apply its own runbook.\n\nDO NOT:\n- Restart the gateway - this won't fix the upstream.",
    },
    {
        "code": "RB-104",
        "title": "Auth service latency above SLO",
        "category": "resource",
        "service_hint": "auth-service",
        "keywords": ["auth", "latency", "slow", "slo", "p99", "cpu"],
        "content": "SYMPTOM: p99 latency on auth-service exceeds SLO. CPU utilization high.\n\nLIKELY CAUSE: Increased load, CPU throttling, or downstream dependency slow.\n\nIMMEDIATE MITIGATION:\n1. Check CPU with docker stats.\n2. Check cgroup throttling.\n3. Scale up replicas.\n4. If downstream (Redis, DB) is slow, escalate.\n\nDO NOT:\n- Blame auth-service before checking downstream.",
    },
    {
        "code": "RB-105",
        "title": "Database connection pool exhausted",
        "category": "database",
        "keywords": ["database", "connection", "pool", "exhausted", "timeout", "postgres"],
        "content": "SYMPTOM: Requests fail with 'connection pool exhausted' or 'too many clients'.\n\nLIKELY CAUSE: Connection leak or unusual traffic spike.\n\nIMMEDIATE MITIGATION:\n1. Check active connections in pg_stat_activity.\n2. Check connections by application_name.\n3. Kill idle connections older than 5 minutes.\n4. If a specific app is leaking, restart it and file a bug.\n\nLONG-TERM:\n- Add connection pool monitoring.\n- Set CONN_MAX_AGE appropriately.",
    },
]


def main():
    print("Seeding runbooks...")
    created = 0
    updated = 0
    for rb in RUNBOOKS:
        obj, was_created = Runbook.objects.update_or_create(
            code=rb["code"],
            defaults={
                "title": rb["title"],
                "category": rb["category"],
                "content": rb["content"],
                "keywords": rb.get("keywords", []),
                "service_hint": rb.get("service_hint", ""),
            },
        )
        if was_created:
            created += 1
            print(f"  + Created {obj.code}: {obj.title}")
        else:
            updated += 1
            print(f"  ~ Updated {obj.code}: {obj.title}")

    print(f"\nDone. Created: {created}, Updated: {updated}, Total: {Runbook.objects.count()}")


if __name__ == "__main__":
    main()
