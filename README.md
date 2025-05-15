# ELK Monitoring Plugin 🛠️

Plugin in stile **Nagios** per monitorare lo stato dei principali servizi della ELK stack:
- [x] Elasticsearch
- [x] Kibana
- [x] Logstash

Restituisce **codici di uscita standard** (`0=OK`, `1=WARNING`, `2=CRITICAL`, `3=UNKNOWN`) e messaggi leggibili per l'integrazione con sistemi di monitoraggio automatico.

---

## 🚀 Requisiti

- Python 3.7+
- Docker (per test locali)
- Virtualenv consigliato

---

## 📦 Installazione

```bash
git clone https://github.com/lucamarastoni/elk-monitoring-plugin.git
cd elk-monitoring-plugin
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
