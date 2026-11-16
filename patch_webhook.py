"""Patch generic_webhook to create Incident + trigger investigation."""
path = '/app/apps/monitoring/views.py'
content = open(path).read()

if 'ingest_as_incident' in content:
    print('Already patched')
    raise SystemExit(0)

# Find and replace the generic_webhook function
old_func = '''@api_view(["POST"])
@permission_classes([AllowAny])
def generic_webhook(request):
    from apps.monitoring.watchers.webhook_ingester import WebhookIngester
    count = WebhookIngester.ingest_generic(request.data)
    return Response({"ingested": count}, status=status.HTTP_201_CREATED)'''

new_func = '''@api_view(["POST"])
@permission_classes([AllowAny])
def generic_webhook(request):
    """Generic webhook: creates an Incident + auto-triggers AI investigation."""
    from apps.monitoring.watchers.webhook_ingester import WebhookIngester
    from apps.incidents.services import trigger_investigation
    from apps.incidents.models import Incident

    try:
        result = WebhookIngester.ingest_as_incident(request.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    triggered = False
    task_id = None
    try:
        incident = Incident.objects.get(id=result["incident_id"])
        queue_result = trigger_investigation(incident)
        triggered = queue_result.get("queued", False)
        task_id = queue_result.get("task_id")
    except Exception:
        pass

    return Response({
        "incident_id": result["incident_id"],
        "service": result["service"],
        "investigation_triggered": triggered,
        "task_id": task_id,
    }, status=status.HTTP_201_CREATED)'''

if old_func in content:
    content = content.replace(old_func, new_func, 1)
    open(path, 'w').write(content)
    print('Patched generic_webhook')
    print('Has ingest_as_incident:', 'ingest_as_incident' in content)
else:
    print('ERROR: Could not find old function - showing current generic_webhook:')
    idx = content.find('def generic_webhook')
    if idx >= 0:
        print(content[idx:idx+400])
    else:
        print('generic_webhook not found in file')
