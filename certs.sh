#!/bin/bash
# certs.sh — génère CA + certificats serveur/client pour Mosquitto TLS

mkdir -p certs
cd certs

# 1. Autorité de certification (CA)
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "//CN=SmartHouse-CA"

# 2. Certificat serveur
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "//CN=localhost"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -days 3650

# 3. Certificat client
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr \
  -subj "//CN=client-E203"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out client.crt -days 3650

# Nettoyage des fichiers intermédiaires
rm -f *.csr *.srl

echo "✅ Certificats générés dans ./certs"