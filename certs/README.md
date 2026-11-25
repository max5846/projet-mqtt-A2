\# Certificats TLS



Les certificats ne sont \*\*pas\*\* versionnés (sécurité). Pour les regénérer :



```bash

\# Depuis la racine du projet

mkdir -p certs \&\& cd certs

openssl genrsa -out ca.key 2048

openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=SmartHouse-CA"

openssl genrsa -out server.key 2048

openssl req -new -key server.key -out server.csr -subj "/CN=localhost"

openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650

openssl genrsa -out client.key 2048

openssl req -new -key client.key -out client.csr -subj "/CN=client-E203"

openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 3650

rm -f \*.csr \*.srl

