# ELK Monitoring & Deployment — Nagios Plugin

This repository provides tools to monitor and deploy an ELK (Elasticsearch, Logstash, Kibana) stack. It includes a Nagios-compatible Python plugin, an automated pytest test suite, and a Bash script for quick containerized deployment using Docker.

---

## Contents

- **`check_elk.py`**: Python Nagios plugin to monitor Elasticsearch, Kibana, and Logstash status.
- **`test_check_elk.py`**: Pytest suite to verify plugin functionality.
- **`docker_elk_setup.sh`**: Shell script for setting up the ELK stack in Docker containers.
- **`requirements.txt`**: Python dependencies required for the plugin and tests.

---

## 🛠 Prerequisites

- Python 3.6+
- `pip`
- Docker and Docker Compose

### Install Python Dependencies

```bash
pip install -r requirements.txt
# or
pip install requests python-dotenv pytest
```

---

## 1. Nagios Plugin (`check_elk.py`)

### Configuration

Use environment variables or CLI arguments to pass credentials and host settings.

1. Create a `.env` file in the project root:

```ini
ELK_HOST=elk.example.local
ELK_USER=username
ELK_PASS=password
```

Default ports (unless overridden via CLI):

- Elasticsearch: `9200`
- Kibana: `5601`
- Logstash: `9600`

### Usage

```bash
usage: check_elk.py [-h] -c {elasticsearch,kibana,logstash}
                    [-i HOST] [-p PORT] [-u USER] [-w PASSWORD] [-l]
```

#### Examples

- Basic Elasticsearch check:

  ```bash
  python check_elk.py --check elasticsearch
  ```

- Specify custom host for Kibana:

  ```bash
  python check_elk.py -c kibana -i kibana.example.local -p 5601
  ```

- Logstash check with SSL ignore:

  ```bash
  python check_elk.py -c logstash -i logstash.local -p 9600 -u user -w pass -l
  ```

Nagios standard exit codes:

- `0`: OK
- `1`: WARNING
- `2`: CRITICAL
- `3`: UNKNOWN

---

## 2. Test Suite (`test_check_elk.py`)

### What It Covers

- Elasticsearch health: `green`, `yellow`, `red`
- HTTP and state errors
- Auth failures (401)
- Kibana states: `available`, `degraded`, `unavailable`
- Logstash pipeline count check

### Run Tests

```bash
pytest -v
```

Or with coverage:

```bash
pytest --cov=check_elk.py --cov-report=term-missing
```

---

## 3. Docker Deployment (`docker_elk_setup.sh`)

### Start Configuration

Set environment variables in `.env`:

```ini
ES_PASS=changeme
KB_USER=kibana_system_user
KB_PASS=changekb
```

### Run Script

```bash
chmod +x docker_elk_setup.sh
./docker_elk_setup.sh
```

This will:

1. Load `.env` values.
2. Create Docker network `elk-net`.
3. Start containers:
   - `elasticsearch-test` (port 9200)
   - `kibana-test` (port 5601)
   - `logstash-test` (port 9600)
4. Wait for Elasticsearch to be ready.
5. Auto-create Kibana user.

#### Output

```text
Elasticsearch: https://localhost:9200 (user: elastic / pass: $ES_PASS)
Kibana:        http://localhost:5601 (user: $KB_USER / pass: $KB_PASS)
Logstash:      http://localhost:9600
```

---

## Contributing

1. Fork the repo
2. Create a new branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push branch: `git push origin feature/my-feature`
5. Open a Pull Request
