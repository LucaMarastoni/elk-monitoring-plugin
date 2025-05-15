#!/bin/bash

# Crea una rete Docker custom per farli comunicare
docker network create elk-net 2>/dev/null

# ELASTICSEARCH
docker rm -f elasticsearch-test 2>/dev/null
docker run -d --name elasticsearch-test \
  --net elk-net \
  -p 9200:9200 \
  -e discovery.type=single-node \
  -e ELASTIC_PASSWORD=changeme \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.0

# Attendi l'avvio di Elasticsearch (risponde su /)
echo "⏳ Aspetto che Elasticsearch sia pronto..."
until curl -sk -u elastic:changeme https://localhost:9200 > /dev/null 2>&1; do
  sleep 2
done
echo "✅ Elasticsearch è attivo!"

# Crea l'utente kibana_system_local via API
echo "🔐 Creo l'utente kibana_system_local..."
curl -sk -u elastic:changeme -X POST https://localhost:9200/_security/user/kibana_system_local \
  -H "Content-Type: application/json" \
  -d '{"password":"kibanapass","roles":["kibana_system"],"full_name":"Local Kibana"}' > /dev/null

# KIBANA
docker rm -f kibana-test 2>/dev/null
docker run -d --name kibana-test \
  --net elk-net \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=https://elasticsearch-test:9200 \
  -e ELASTICSEARCH_USERNAME=kibana_system_local \
  -e ELASTICSEARCH_PASSWORD=kibanapass \
  -e ELASTICSEARCH_SSL_VERIFICATIONMODE=none \
  -e NODE_OPTIONS="--openssl-legacy-provider" \
  docker.elastic.co/kibana/kibana:8.17.0

# LOGSTASH
docker rm -f logstash-test 2>/dev/null
docker run -d --name logstash-test \
  --net elk-net \
  -p 9600:9600 \
  docker.elastic.co/logstash/logstash:8.17.0

echo -e \"\\n🎉 Tutti i servizi sono attivi:\"
echo "  → Elasticsearch: https://localhost:9200 (user: elastic / pass: changeme)"
echo "  → Kibana:        http://localhost:5601 (user: kibana_system_local / pass: kibanapass)"
echo "  → Logstash:      http://localhost:9600"
