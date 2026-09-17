from processor import health


def test_heartbeat_age_seconds_none_before_first_record(monkeypatch):
    monkeypatch.setattr(health, "_last_heartbeat", None)

    assert health.heartbeat_age_seconds() is None


def test_heartbeat_age_seconds_reports_recent_record(monkeypatch):
    monkeypatch.setattr(health, "_last_heartbeat", None)
    health.record_heartbeat()

    age = health.heartbeat_age_seconds()

    assert age is not None
    assert age < 5
