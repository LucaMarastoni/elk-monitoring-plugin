import os
import sys
import pytest
import check_elk as elk
from types import SimpleNamespace

class DummyResponse:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}
    def json(self):
        return self._json_data

# 1. parse_args
def test_parse_args_defaults(monkeypatch):
    monkeypatch.setenv("ELK_USER", "env_user")
    monkeypatch.setenv("ELK_PASS", "env_pass")
    monkeypatch.setattr(sys, "argv", ["prog", "--check", "elasticsearch"])
    args = elk.parse_args()
    assert args.check == "elasticsearch"
    assert args.host == "localhost"
    assert args.port is None  # viene assegnata in main()
    assert args.user == "env_user"
    assert args.password == "env_pass"    
    assert not args.ssl_ignore

def test_parse_args_all_flags(monkeypatch):
    monkeypatch.setattr(sys, "argv", [
        "prog", "-c", "kibana",
        "-i", "myhost", "-p", "1234",
        "-u", "user1", "-w", "pass1", "-l"
    ])
    args = elk.parse_args()
    assert args.check == "kibana"
    assert args.host == "myhost"
    assert args.port == 1234
    assert args.user == "user1"
    assert args.password == "pass1"
    assert args.ssl_ignore

# 2. Kibana top-level overall + level
@pytest.mark.parametrize("level, expected_code, expected_msg", [
    ("yellow", elk.WARNING,  "WARNING - Kibana status: yellow"),
    ("red",    elk.CRITICAL, "CRITICAL - Kibana status: red"),
])
def test_check_kibana_top_level_and_level(monkeypatch, level, expected_code, expected_msg):
    dummy = DummyResponse(200, {"overall": {"level": level}})
    def fake_get(url, auth, verify, timeout):
        return dummy
    monkeypatch.setattr(elk.requests, "get", fake_get)
    code, msg = elk.check_kibana("h", 5, "u", "p", ssl_ignore=False)
    assert code == expected_code
    assert msg == expected_msg

# 3. HTTP error branch per Kibana e Logstash
def test_check_kibana_http_error(monkeypatch):
    dummy = DummyResponse(503)
    monkeypatch.setattr(elk.requests, "get", lambda *a, **k: dummy)
    code, msg = elk.check_kibana("h", 5, "u", "p", ssl_ignore=False)
    assert code == elk.CRITICAL
    assert "Kibana HTTP 503" in msg

def test_check_logstash_http_error_non401(monkeypatch):
    dummy = DummyResponse(502)
    monkeypatch.setattr(elk.requests, "get", lambda *a, **k: dummy)
    code, msg = elk.check_logstash("h", 9, "u", "p", ssl_ignore=False)
    assert code == elk.CRITICAL
    assert "Logstash HTTP 502" in msg

# 4. main() flow + default porta + env fallback
def run_main_and_capture(monkeypatch, capsys, check_name, resp_code, resp_msg, env_user=None, env_pass=None):
    # monkeypatch ENV
    if env_user: monkeypatch.setenv("ELK_USER", env_user)
    if env_pass: monkeypatch.setenv("ELK_PASS", env_pass)
    # monkeypatch args
    monkeypatch.setattr(sys, "argv", ["prog", "-c", check_name])
    # sostituisco le funzioni di check_<service>
    fake = lambda *a, **k: (resp_code, resp_msg)
    monkeypatch.setattr(elk, f"check_{check_name}", fake)
    # catturo SystemExit
    with pytest.raises(SystemExit) as e:
        elk.main()
    captured = capsys.readouterr()
    return e.value.code, captured.out.strip()

@pytest.mark.parametrize("service,port", [
    ("elasticsearch", 9200),
    ("kibana",        5601),
    ("logstash",      9600),
])
def test_main_defaults_and_exit(monkeypatch, capsys, service, port):
    code, out = run_main_and_capture(
        monkeypatch, capsys,
        check_name=service,
        resp_code=elk.OK,
        resp_msg=f"OK - dummy {service}"
    )
    assert code == elk.OK
    assert out == f"OK - dummy {service}"

def test_main_uses_env_creds(monkeypatch, capsys):
    # imposto env e verifico che non crashi (fake ritorna OK)
    code, out = run_main_and_capture(
        monkeypatch, capsys,
        check_name="elasticsearch",
        resp_code=elk.OK,
        resp_msg="OK - dummy es",
        env_user="eu",
        env_pass="ep"
    )
    assert code == elk.OK
    assert out == "OK - dummy es"
