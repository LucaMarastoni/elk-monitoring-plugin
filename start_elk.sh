#!/bin/bash

# Carica le variabili da .env e le esporta
set -a
source .env
set +a

# Crea una rete Docker per collegare i container
docker network create elk-net 2>/dev/null

# ELASTICSEARCH
docker rm -f elasticsearch-test 2>/dev/null
docker run -d --name elasticsearch-test \
  --net elk-net \
  -p 9200:9200 \
  -e discovery.type=single-node \
  -e ELASTIC_PASSWORD="$ES_PASS" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.0

# Attendi che Elasticsearch sia pronto
echo "⏳ Aspetto che Elasticsearch sia pronto..."
until curl -sk -u elastic:"$ES_PASS" https://localhost:9200 > /dev/null 2>&1; do
  sleep 2
done
echo "✅ Elasticsearch è attivo!"

# Crea l'utente Kibana via API
echo "🔐 Creo l'utente $KB_USER..."
curl -sk -u elastic:"$ES_PASS" -X POST https://localhost:9200/_security/user/"$KB_USER" \
  -H "Content-Type: application/json" \
  -d "{\"password\":\"$KB_PASS\",\"roles\":[\"kibana_system\"],\"full_name\":\"Local Kibana\"}" > /dev/null

# KIBANA
docker rm -f kibana-test 2>/dev/null
docker run -d --name kibana-test \
  --net elk-net \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=https://elasticsearch-test:9200 \
  -e ELASTICSEARCH_USERNAME="$KB_USER" \
  -e ELASTICSEARCH_PASSWORD="$KB_PASS" \
  -e ELASTICSEARCH_SSL_VERIFICATIONMODE=none \
  -e NODE_OPTIONS="--openssl-legacy-provider" \
  docker.elastic.co/kibana/kibana:8.17.0

# LOGSTASH
docker rm -f logstash-test 2>/dev/null
docker run -d --name logstash-test \
  --net elk-net \
  -p 9600:9600 \
  docker.elastic.co/logstash/logstash:8.17.0

# Output finale
echo -e "\n🎉 Tutti i servizi sono attivi:"
echo "  → Elasticsearch: https://localhost:9200 (user: elastic / pass: $ES_PASS)"
echo "  → Kibana:        http://localhost:5601 (user: $KB_USER / pass: $KB_PASS)"
echo "  → Logstash:      http://localhost:9600"
