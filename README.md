## ELK Monitoring and Deployment Nagios Plugin

This repository contains Python scripts to monitor the services of an ELK cluster (Elasticsearch, Kibana, and Logstash), their automated tests with pytest, and a Bash script for quick deployment of Docker containers in a development or test environment.

---

## Contents

* **check\_elk.py**: A Nagios plugin to verify the status of Elasticsearch, Kibana, and Logstash.
* **test\_check\_elk.py**: A pytest-based test suite to validate the plugin's behavior.
* **docker\_elk\_setup.sh**: A Bash script to start Elasticsearch, Kibana, and Logstash Docker containers on a dedicated network.
* **requirements.txt**: A list of Python dependencies required to run the scripts.

---

## Prerequisites

* Python 3.6 or higher
* `pip` for Python package management
* Docker and Docker Compose installed

### Python Dependencies

Install all dependencies with:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install requests python-dotenv pytest
```

---

# 1. Nagios Plugin in Python (`check_elk.py`)

## Configuration

Credentials and the ELK host can be provided via environment variables or command-line arguments.

1. Create a `.env` file in the project root:

   ```ini
   ELK_HOST=elk.example.local
   ELK_USER=username
   ELK_PASS=password
   ```

2. (Optional) Default ports:

   * Elasticsearch: `9200`
   * Kibana: `5601`
   * Logstash: `9600`

   Alternatively, pass the `--port` parameter to the CLI.

## Usage

```text
usage: check_elk.py [-h] -c {elasticsearch,kibana,logstash}
                    [-i HOST] [-p PORT] [-u USER] [-w PASSWORD]
                    [-l]

ELK Monitoring Nagios Plugin

optional arguments:
  -h, --help            show this help message and exit
  -c, --check {elasticsearch,kibana,logstash}
                        Service to check
  -i, --host HOST       Service host or endpoint (default: localhost or
                        ELK_HOST env)
  -p, --port PORT       Service port (default: 9200/5601/9600)
  -u, --user USER       Username for basic auth (default: ELK_USER env)
  -w, --password PASSWORD
                        Password for basic auth (default: ELK_PASS env)
  -l, --ssl-ignore      Ignore SSL certificate errors (self-signed)
```

### Examples

* Check Elasticsearch:

  ```bash
  python check_elk.py --check elasticsearch
  ```

* Custom Kibana host:

  ```bash
  python check_elk.py -c kibana -i kibana.example.local -p 5601
  ```

* Logstash with SSL ignore:

  ```bash
  python check_elk.py -c logstash -i logstash.local -p 9600 \
      -u user -w pass -l
  ```

The plugin returns standard Nagios exit codes:

* `0` (OK)
* `1` (WARNING)
* `2` (CRITICAL)
* `3` (UNKNOWN)

---

# 2. pytest Test Suite (`test_check_elk.py`)

The test suite covers:

* Elasticsearch health states: `green`, `yellow`, `red`
* Unexpected states and HTTP errors
* Connection and authentication exceptions (401)
* Kibana states: `available`, `degraded`, `unavailable`
* Logstash pipeline count verification

## Running the Tests

```bash
pytest -v
```

With coverage report (if `pytest-cov` is installed):

```bash
pytest --cov=check_elk.py --cov-report=term-missing
```

---

# 3. Docker Deployment Script (`docker_elk_setup.sh`)

A Bash script to quickly spin up a full ELK stack in Docker.

## Configuration

Create a `.env` file with these variables:

```ini
# Credentials and passwords
ES_PASS=changeme
KB_USER=kibana_system_user
KB_PASS=changekb
```

## Usage

Make the script executable and run it:

```bash
chmod +x docker_elk_setup.sh
./docker_elk_setup.sh
```

The script will:

1. Load and export variables from `.env`.
2. Create the `elk-net` Docker network.
3. Start containers:

   * `elasticsearch-test` (port 9200, single-node mode, password from `ES_PASS`)
   * `kibana-test` (port 5601, connected to Elasticsearch, SSL ignore)
   * `logstash-test` (port 9600)
4. Wait for Elasticsearch to be ready and create a Kibana user via API.
5. Print endpoints and credentials:

   ```text
   Elasticsearch: https://localhost:9200 (user: elastic / pass: $ES_PASS)
   Kibana:        http://localhost:5601 (user: $KB_USER / pass: $KB_PASS)
   Logstash:      http://localhost:9600
   ```

---

## Contributing

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/x`
3. Commit changes: `git commit -m "Description of change"`
4. Push to your branch: `git push origin feature/x`
5. Open a Pull Request
