"""Add feedback action to InvestigationViewSet."""
path = '/app/apps/investigations/views.py'
content = open(path).read()

if 'def feedback' in content:
    print('Already has feedback method')
    raise SystemExit(0)

feedback_method = '''

    @action(detail=True, methods=["post", "get"], url_path="feedback", permission_classes=[permissions.IsAuthenticated])
    def feedback(self, request, pk=None):
        """POST: submit feedback. GET: list feedback."""
        from .models import Feedback
        from .serializers import FeedbackSerializer

        inv = self.get_object()
        if request.method == "GET":
            fb_list = inv.feedback_entries.all()
            return Response({"count": fb_list.count(), "results": FeedbackSerializer(fb_list, many=True).data})

        verdict = request.data.get("verdict", "").strip().lower()
        if verdict not in ("correct", "partial", "wrong", "unclear"):
            return Response({"error": "invalid verdict"}, status=400)

        fb = Feedback.objects.create(
            investigation=inv,
            user=request.user if request.user.is_authenticated else None,
            verdict=verdict,
            comment=request.data.get("comment", "").strip(),
            actual_root_cause=request.data.get("actual_root_cause", "").strip(),
        )
        return Response(FeedbackSerializer(fb).data, status=201)
'''

idx = content.find('class InvestigationStepViewSet')
if idx < 0:
    print('ERROR: InvestigationStepViewSet not found')
    raise SystemExit(1)

content = content[:idx] + feedback_method.strip() + '\n\n\n' + content[idx:]
open(path, 'w').write(content)
print('Feedback action added')
print('Has def feedback:', 'def feedback' in content)
