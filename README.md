# ELK Monitoring Plugin & Docker Setup

This repository provides a set of Python and Bash tools to monitor an ELK (Elasticsearch, Logstash, Kibana) stack using Nagios-compatible checks, along with Docker-based setup for local testing and development.

---

## 📁 Project Structure

``` markdown
elk-monitoring-plugin/
├── README.md
├── check_elk.py                  # Main Nagios-compatible monitoring plugin
├── coverage_report.txt           # Code coverage report after testing
├── pytest.ini                    # Pytest configuration file
├── requirements.txt              # Python dependencies
├── start_elk.sh                  # Bash script to launch ELK in Docker
└── test/
    ├── test_check_elk.py         # Unit tests for core functionality
    └── test_check_elk_extra.py   # Additional test cases
```

---

## Features

- **Nagios plugin** to monitor the health of Elasticsearch, Kibana, and Logstash.
- **pytest test suite** with coverage reporting.
- **Docker setup** script for spinning up ELK stack locally.

---

## 🔧 Requirements

- Python 3.6+
- pip
- Docker & Docker Compose

### Install Python Dependencies

```bash
pip install -r requirements.txt
# or
pip install requests python-dotenv pytest
```

---

## 1. Monitoring Script (`check_elk.py`)

This script checks the availability and health of Elasticsearch, Kibana, and Logstash.

### Environment Configuration

Create a `.env` file in the root:

```ini
ELK_HOST=localhost
ELK_USER=your_user
ELK_PASS=your_pass
```

You can override these via CLI options.

Default ports:

- Elasticsearch: `9200`
- Kibana: `5601`
- Logstash: `9600`

### Usage

```bash
python check_elk.py --check {elasticsearch|kibana|logstash} [options]
```

#### Options

```text
  -i, --host         Hostname or IP (default from ELK_HOST env)
  -p, --port         Port (default per service)
  -u, --user         Username (default from ELK_USER env)
  -w, --password     Password (default from ELK_PASS env)
  -l, --ssl-ignore   Ignore self-signed SSL certs
```

#### Examples

```bash
python check_elk.py -c elasticsearch
python check_elk.py -c kibana -i kibana.local -p 5601
python check_elk.py -c logstash -i logstash.local -l -u user -w pass
```

Nagios Exit Codes:

- `0`: OK
- `1`: WARNING
- `2`: CRITICAL
- `3`: UNKNOWN

---

## 2. Tests (`test/`)

### Coverage

- Elasticsearch: green, yellow, red
- Kibana: available, degraded, unavailable
- Logstash: pipeline metrics
- Error handling: timeouts, 401s, unreachable hosts

### Run Tests

```bash
pytest -v
```

With coverage:

```bash
pytest --cov=check_elk.py --cov-report=term-missing
```

---

## 3. Docker Setup (`start_elk.sh`)

Spin up a simple ELK stack for development.

### Configure `.env`

```ini
ES_PASS=changeme
KB_USER=kibana_system_user
KB_PASS=changekb
```

### Start Stack

```bash
chmod +x start_elk.sh
./start_elk.sh
```

Creates:

- Network `elk-net`
- `elasticsearch-test` (9200)
- `kibana-test` (5601)
- `logstash-test` (9600)

Waits for readiness, creates Kibana user via API, prints endpoints.
