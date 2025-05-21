# ELK Monitoring e Deployment Nagios Plugin

Questo repository contiene script Python per monitorare i servizi di un cluster ELK (Elasticsearch, Kibana e Logstash), i relativi test automatici con pytest e uno script Bash per il deployment rapido dei container Docker per ambiente di sviluppo o test.

## Contenuti

* **check\_elk.py**: plugin Nagios per verificare lo stato di Elasticsearch, Kibana e Logstash.
* **test\_check\_elk.py**: suite di test basata su pytest per validare i comportamenti del plugin.
* **start\_elk.sh**: script Bash per avviare container Docker di Elasticsearch, Kibana e Logstash in una rete dedicata.
* **requirements.txt**: elenco delle dipendenze Python necessarie per eseguire gli script.

---

## Prerequisiti

* Python 3.6 o superiore
* `pip` per la gestione dei pacchetti Python
* Docker e Docker Compose installati

### Dipendenze Python

Installare tutte le dipendenze con:

```bash
pip install -r requirements.txt
```

Oppure manualmente:

```bash
pip install requests python-dotenv pytest
```

---

# 1. Plugin Nagios Python (check\_elk.py)

## Configurazione

Le credenziali e l'host del cluster ELK possono essere passati via variabili d'ambiente o come argomenti a linea di comando.

1. Creare un file `.env` nella radice del progetto:

   ```ini
   ELK_HOST=elk.miodominio.local
   ELK_USER=utente
   ELK_PASS=password
   ```

2. (Opzionale) Definire le porte di default:

   * Elasticsearch: `9200`
   * Kibana: `5601`
   * Logstash: `9600`

Oppure passare il parametro `--port` alla CLI.

## Utilizzo

```text
usage: check_elk.py [-h] -c {elasticsearch,kibana,logstash}
                    [-i HOST] [-p PORT] [-u USER] [-w PASSWORD]
                    [-l]

ELK Monitoring Nagios Plugin

optional arguments:
  -h, --help            show this help message and exit
  -c, --check {elasticsearch,kibana,logstash}
                        Servizio da controllare
  -i, --host HOST       Host o endpoint del servizio (default: localhost o
                        ELK_HOST env)
  -p, --port PORT       Porta del servizio (default: 9200/5601/9600)
  -u, --user USER       Username per basic auth (default: ELK_USER env)
  -w, --password PASSWORD
                        Password per basic auth (default: ELK_PASS env)
  -l, --ssl-ignore      Ignora errori di certificato SSL (self-signed)
```

### Esempi

* Elasticsearch:

  ```bash
  python check_elk.py --check elasticsearch
  ```
* Kibana personalizzato:

  ```bash
  python check_elk.py -c kibana -i kibana.myhost.local -p 5601
  ```
* Logstash con SSL ignore:

  ```bash
  python check_elk.py -c logstash -i logstash.local -p 9600 \
      -u user -w pass -l
  ```

Il plugin restituisce i codici standard:

* `0` (OK)
* `1` (WARNING)
* `2` (CRITICAL)
* `3` (UNKNOWN)

---

# 2. Suite di test pytest (test\_check\_elk.py)

La suite di test copre:

* Stati `green`, `yellow`, `red` di Elasticsearch
* Stato inatteso e errori HTTP
* Gestione eccezioni di connessione e autenticazione (401)
* Stati `available`, `degraded`, `unavailable` di Kibana
* Conteggio pipelines di Logstash

## Esecuzione

```bash
pytest -v
```

Con report di copertura (se installato `pytest-cov`):

```bash
pytest --cov=check_elk.py --cov-report=term-missing
```

---

# 3. Deployment Docker (docker\_elk\_setup.sh)

Script Bash per avviare rapidamente un ambiente ELK completo in Docker.

## Configurazione

Creare il file `.env` con queste variabili:

```ini
# Credenziali e password
ES_PASS=changeme
KB_USER=kibana_system_user
KB_PASS=changekb
```

## Utilizzo

Rendere eseguibile lo script e lanciarlo:

```bash
chmod +x start_elk.sh
./start_elk.sh
```

Lo script esegue le seguenti operazioni:

1. Carica ed esporta le variabili da `.env`.
2. Crea la rete Docker `elk-net`.
3. Avvia container:

   * `elasticsearch-test` (porta 9200, modalità single-node, password da ES\_PASS)
   * `kibana-test` (porta 5601, connesso ad Elasticsearch, SSL ignore)
   * `logstash-test` (porta 9600)
4. Attende che Elasticsearch sia operativo e crea un utente Kibana via API.
5. Stampa gli endpoint e le credenziali per l'accesso:

   ```text
   Elasticsearch: https://localhost:9200 (user: elastic / pass: $ES_PASS)
   Kibana:        http://localhost:5601 (user: $KB_USER / pass: $KB_PASS)
   Logstash:      http://localhost:9600
   ```

