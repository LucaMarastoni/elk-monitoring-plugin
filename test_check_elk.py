import pytest
import requests
import check_elk as elk_monitor

class DummyResponse:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

@pytest.mark.parametrize("status, expected_code, expected_msg", [
    ("green", elk_monitor.OK,    "OK - Elasticsearch cluster green (3 nodi)"),
    ("yellow", elk_monitor.WARNING, "WARNING - Elasticsearch cluster yellow (2 nodi)"),
    ("red", elk_monitor.CRITICAL, "CRITICAL - Elasticsearch cluster red (1 nodi)"),
])
def test_check_elasticsearch_status(monkeypatch, status, expected_code, expected_msg):
    dummy = DummyResponse(200, {"status": status, "number_of_nodes": int(expected_msg.split("(")[1].split()[0])})
    def fake_get(url, auth, verify, timeout):
        return dummy
    monkeypatch.setattr(elk_monitor.requests, "get", fake_get)

    code, msg = elk_monitor.check_elasticsearch("h", 9, "u", "p", ssl_ignore=True)
    assert code == expected_code
    assert msg == expected_msg

def test_check_elasticsearch_unexpected(monkeypatch):
    dummy = DummyResponse(200, {"status": "blue"})
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_elasticsearch("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.UNKNOWN
    assert "UNKNOWN - Stato cluster inaspettato: blue" in msg

def test_check_elasticsearch_401(monkeypatch):
    dummy = DummyResponse(401)
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_elasticsearch("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.UNKNOWN
    assert msg == "UNKNOWN - Autenticazione Elasticsearch fallita (401)"

def test_check_elasticsearch_http_error(monkeypatch):
    dummy = DummyResponse(500)
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_elasticsearch("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.CRITICAL
    assert "CRITICAL - Elasticsearch HTTP 500" in msg

def test_check_elasticsearch_exception(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("fail")
    monkeypatch.setattr(elk_monitor.requests, "get", fake_get)

    code, msg = elk_monitor.check_elasticsearch("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.UNKNOWN
    assert "UNKNOWN - Connessione Elasticsearch fallita" in msg


@pytest.mark.parametrize("state, expected_code, expected_msg", [
    ("available", elk_monitor.OK,       "OK - Kibana status: available"),
    ("green",     elk_monitor.OK,       "OK - Kibana status: green"),
    ("degraded",  elk_monitor.WARNING,  "WARNING - Kibana status: degraded"),
    ("yellow",    elk_monitor.WARNING,  "WARNING - Kibana status: yellow"),
    ("unavailable", elk_monitor.CRITICAL, "CRITICAL - Kibana status: unavailable"),
    ("red",       elk_monitor.CRITICAL,  "CRITICAL - Kibana status: red"),
])
def test_check_kibana_states(monkeypatch, state, expected_code, expected_msg):
    dummy = DummyResponse(200, {"status": {"overall": {"state": state}}})
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_kibana("h", 5, "u", "p", ssl_ignore=False)
    assert code == expected_code
    assert msg == expected_msg

def test_check_kibana_unexpected(monkeypatch):
    dummy = DummyResponse(200, {"status": {"overall": {"state": "weird"}}})
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_kibana("h", 5, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.UNKNOWN
    assert "UNKNOWN - Stato Kibana inaspettato: weird" in msg

def test_check_kibana_401(monkeypatch):
    dummy = DummyResponse(401)
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_kibana("h", 5, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.UNKNOWN
    assert msg == "UNKNOWN - Autenticazione Kibana fallita (401)"

def test_check_kibana_exception(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("down")
    monkeypatch.setattr(elk_monitor.requests, "get", fake_get)

    code, msg = elk_monitor.check_kibana("h", 5, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.UNKNOWN
    assert "UNKNOWN - Connessione Kibana fallita" in msg


def test_check_logstash_pipelines(monkeypatch):
    dummy = DummyResponse(200, {"pipelines": {"a": {}, "b": {}}})
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_logstash("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.OK
    assert msg == "OK - Logstash attivo, pipelines: 2"

def test_check_logstash_no_dict(monkeypatch):
    dummy = DummyResponse(200, {"pipelines": ["x", "y", "z"]})
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_logstash("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.OK
    assert msg == "OK - Logstash attivo, pipelines: n.d."

def test_check_logstash_401(monkeypatch):
    dummy = DummyResponse(401)
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_logstash("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.UNKNOWN
    assert msg == "UNKNOWN - Autenticazione Logstash fallita (401)"

def test_check_logstash_http_error(monkeypatch):
    dummy = DummyResponse(502)
    monkeypatch.setattr(elk_monitor.requests, "get", lambda *args, **kwargs: dummy)

    code, msg = elk_monitor.check_logstash("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.CRITICAL
    assert "CRITICAL - Logstash HTTP 502" in msg

def test_check_logstash_exception(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("fail")
    monkeypatch.setattr(elk_monitor.requests, "get", fake_get)

    code, msg = elk_monitor.check_logstash("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk_monitor.UNKNOWN
    assert "UNKNOWN - Connessione Logstash fallita" in msg
