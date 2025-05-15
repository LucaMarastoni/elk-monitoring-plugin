#!/usr/bin/env python3


import os
import sys
import argparse
import requests
from dotenv import load_dotenv
import warnings
from urllib3.exceptions import InsecureRequestWarning, NotOpenSSLWarning

# Carico le variabili dal file .env
load_dotenv()

# Disabilito i warning di urllib3 su LibreSSL e verify=False
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# Codici di Nagios
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# Definizione degli argomenti
def parse_args():
    parser = argparse.ArgumentParser(
        description="ELK Monitoring Nagios Plugin"
    )
    parser.add_argument(
        "-c", "--check",
        choices=["elasticsearch", "kibana", "logstash"],
        required=True,
        help="Servizio da controllare"
    )
    parser.add_argument(
        "-i", "--host",
        default=os.getenv("ELK_HOST", "localhost"),
        help="Host o endpoint del servizio (default localhost)"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        help="Porta del servizio (default 9200/5601/9600 in base a --check)"
    )
    parser.add_argument(
        "-u", "--user",
        default=os.getenv("ELK_USER", None),
        help="Username per basic auth (default da ELK_USER env)"
    )
    parser.add_argument(
        "-w", "--password",
        default=os.getenv("ELK_PASS", None),
        help="Password per basic auth (default da ELK_PASS env)"
    )
    parser.add_argument(
        "-l", "--ssl-ignore",
        action="store_true",
        help="Ignora errori di certificato SSL (self-signed)"
    )
    return parser.parse_args()


def check_elasticsearch(host, port, user, pwd, ssl_ignore):

    #/_cluster/health e mappa green/yellow/red --> OK/WARNING/CRITICAL.

    url = f"https://{host}:{port}/_cluster/health"
    try:
        resp = requests.get(
            url, auth=(user, pwd),
            verify=not ssl_ignore, timeout=5
        )
    except requests.RequestException as e:
        return UNKNOWN, f"UNKNOWN - Connessione Elasticsearch fallita: {e}"

    if resp.status_code == 200:
        data = resp.json()
        status = data.get("status")
        nodes = data.get("number_of_nodes", "n.d.")
        if status == "green":
            return OK, f"OK - Elasticsearch cluster green ({nodes} nodi)"
        if status == "yellow":
            return WARNING, f"WARNING - Elasticsearch cluster yellow ({nodes} nodi)"
        if status == "red":
            return CRITICAL, f"CRITICAL - Elasticsearch cluster red ({nodes} nodi)"
        return UNKNOWN, f"UNKNOWN - Stato cluster inaspettato: {status}"

    elif resp.status_code == 401:
        return UNKNOWN, "UNKNOWN - Autenticazione Elasticsearch fallita (401)"
    else:
        return CRITICAL, f"CRITICAL - Elasticsearch HTTP {resp.status_code}"


def check_kibana(host, port, user, pwd, ssl_ignore):

    #available/degraded/unavailable --> OK/WARNING/CRITICAL.

    url = f"http://{host}:{port}/api/status"
    try:
        resp = requests.get(
            url, auth=(user, pwd),
            verify=not ssl_ignore, timeout=5
        )
    except requests.RequestException as e:
        return UNKNOWN, f"UNKNOWN - Connessione Kibana fallita: {e}"

    if resp.status_code == 200:
        data = resp.json()
        overall = None
        if "status" in data and "overall" in data["status"]:
            overall = data["status"]["overall"]
        elif "overall" in data:
            overall = data["overall"]

        state = None
        if overall:
            state = overall.get("state") or overall.get("level")

        if state in ("available", "green"):
            return OK, f"OK - Kibana status: {state}"
        if state in ("degraded", "yellow"):
            return WARNING, f"WARNING - Kibana status: {state}"
        if state in ("unavailable", "red"):
            return CRITICAL, f"CRITICAL - Kibana status: {state}"
        return UNKNOWN, f"UNKNOWN - Stato Kibana inaspettato: {state}"

    elif resp.status_code == 401:
        return UNKNOWN, "UNKNOWN - Autenticazione Kibana fallita (401)"
    else:
        return CRITICAL, f"CRITICAL - Kibana HTTP {resp.status_code}"


def check_logstash(host, port, user, pwd, ssl_ignore):

    #/_node/stats
    
    url = f"http://{host}:{port}/_node/stats"
    try:
        resp = requests.get(
            url, auth=(user, pwd),
            verify=not ssl_ignore, timeout=5
        )
    except requests.RequestException as e:
        return UNKNOWN, f"UNKNOWN - Connessione Logstash fallita: {e}"

    if resp.status_code == 200:
        data = resp.json()
        pipelines = data.get("pipelines")
        if isinstance(pipelines, dict):
            count = len(pipelines)
        else:
            count = "n.d."
        return OK, f"OK - Logstash attivo, pipelines: {count}"

    elif resp.status_code == 401:
        return UNKNOWN, "UNKNOWN - Autenticazione Logstash fallita (401)"
    else:
        return CRITICAL, f"CRITICAL - Logstash HTTP {resp.status_code}"


def main():
    args = parse_args()

    if not args.user or not args.password:
        args.user = args.user or os.getenv("ELK_USER", "")
        args.password = args.password or os.getenv("ELK_PASS", "")

    if args.port is None:
        args.port = {"elasticsearch": 9200,
                     "kibana": 5601,
                     "logstash": 9600}[args.check]

    if args.check == "elasticsearch":
        code, message = check_elasticsearch(
            args.host, args.port, args.user, args.password, args.ssl_ignore
        )
    elif args.check == "kibana":
        code, message = check_kibana(
            args.host, args.port, args.user, args.password, args.ssl_ignore
        )
    else:
        code, message = check_logstash(
            args.host, args.port, args.user, args.password, args.ssl_ignore
        )

    print(message)
    sys.exit(code)


if __name__ == "__main__":
    main()
