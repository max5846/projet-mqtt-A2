# certs/gen_certs.py
# Génère les certificats TLS pour Mosquitto (cross-platform Windows/Linux/Mac)
import os
import subprocess
import sys


def run(cmd):
    print(">", cmd)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Échec de la commande : {cmd}")
        sys.exit(1)


def main():
    # Se placer dans le dossier certs/
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("=== Génération des certificats TLS — Smart House E203 ===\n")

    # 1. Autorité de certification (CA)
    run("openssl genrsa -out ca.key 2048")
    run('openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=SmartHouse-CA"')

    # 2. Certificat serveur
    run("openssl genrsa -out server.key 2048")
    run('openssl req -new -key server.key -out server.csr -subj "/CN=localhost"')
    run("openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650")

    # 3. Certificat client
    run("openssl genrsa -out client.key 2048")
    run('openssl req -new -key client.key -out client.csr -subj "/CN=client-E203"')
    run("openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 3650")

    # 4. Nettoyage des fichiers intermédiaires
    for f in os.listdir("."):
        if f.endswith((".csr", ".srl")):
            os.remove(f)
            print(f"🗑️  Supprimé : {f}")

    print("\n✅ Certificats générés dans ./certs")
    print("Fichiers attendus : ca.crt, ca.key, server.crt, server.key, client.crt, client.key")


if __name__ == "__main__":
    main()