"""Unit tests for choice enums."""
import pytest
from apps.incidents.models import Incident
from apps.approvals.models import ApprovalRequest
from apps.investigations.models import Investigation


class TestSeverityChoices:
    def test_all_severities_unique(self):
        severities = [c[0] for c in Incident.SEVERITY]
        assert len(severities) == len(set(severities))

    def test_expected_severities_present(self):
        severities = [c[0] for c in Incident.SEVERITY]
        for expected in ["low", "medium", "high", "critical"]:
            assert expected in severities

    def test_severity_choices_are_tuples(self):
        for choice in Incident.SEVERITY:
            assert isinstance(choice, tuple)
            assert len(choice) == 2


class TestStatusChoices:
    def test_all_statuses_unique(self):
        statuses = [c[0] for c in Incident.STATUS]
        assert len(statuses) == len(set(statuses))

    def test_expected_statuses_present(self):
        statuses = [c[0] for c in Incident.STATUS]
        for expected in ["open", "investigating", "resolved"]:
            assert expected in statuses


class TestApprovalStatuses:
    def test_all_approval_statuses_unique(self):
        statuses = [c[0] for c in ApprovalRequest.STATUS]
        assert len(statuses) == len(set(statuses))

    def test_expected_approval_statuses_present(self):
        statuses = [c[0] for c in ApprovalRequest.STATUS]
        for expected in ["pending", "approved", "rejected"]:
            assert expected in statuses


class TestInvestigationStatuses:
    def test_expected_investigation_statuses(self):
        statuses = [c[0] for c in Investigation.STATUS]
        for expected in ["running", "done", "failed"]:
            assert expected in statuses
