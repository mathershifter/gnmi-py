#!/bin/sh
#
# Lab / Testing CA
#
# generates:
# - a local authority
# - signs a server cert with a CN matching the hostname
# - client server for auth
#
# config:
# - creates an ssl profile
# - enables eapi with ssl/tls (for testing)
#
# Note: this script will invalidate any previously generated client and server certs 
#
# usage: 
#   sh ./ca.sh <server-name>

if [ -z "$1" ]; then
  echo "error, no servername"
  exit 1
fi

#: "${HOSTNAME:=$(hostname)}"
SERVERNAME="$1"

PASSPHRASE="democa"

# add custom alt names i.e. "DNS:${HOSTNAME}.sub.arista.io,DNS:blah.region.arista.io"
EXTRA_SAN=

# DN
C="US"
ST="CA"
L="Santa Clara"
O="Arista"
OU="CE"
CA_CN="${OU} CA Root"
CLIENT_CN="admin"

OPENSSL_CNF="openssl.cnf"


TESTS_DIR=$(CDPATH="" cd -- "$(dirname -- "$0")" && pwd)
CA_DIR="$TESTS_DIR/assets/ca"

PRIVATE_DIR="$CA_DIR/private"
CSR_DIR="$CA_DIR/csr"
CERTS_DIR="$CA_DIR/certs"
OPENSSL_CNF="$TESTS_DIR/openssl.cnf"
mkdir -p "$PRIVATE_DIR" "$CSR_DIR" "$CERTS_DIR" "$CA_DIR/newcerts"


SAN="DNS:localhost,DNS:$SERVERNAME"

if [ "$EXTRA_SAN" != "" ]; then
    SAN="$SAN,$EXTRA_SAN"
fi

bash <<EOF
find $CA_DIR -type f | xargs rm
touch $CA_DIR/index.txt
echo 1000 > "$CA_DIR/serial"
EOF


# enable copy extensions in openssl config
#sudo sed -i 's/^#\? *copy_extensions.*/copy_extensions = copy/' /etc/ssl/openssl.cnf

#
# CA
#
openssl genrsa -out "$PRIVATE_DIR/ca.key.pem" 2048

openssl req \
    -batch -new -x509 -sha256 -days 3750 \
    -passout "pass:$PASSPHRASE" \
    -config "$OPENSSL_CNF" \
    -key "$PRIVATE_DIR/ca.key.pem" \
    -out "$CERTS_DIR/ca.cert.pem" \
    -subj "/C=$C/ST=$ST/L=$L/O=$O/OU=$OU/CN=$CA_CN" \
    -extensions v3_ca


#
# Server
#

openssl genrsa -out "$PRIVATE_DIR/$SERVERNAME.key.pem" 2048

openssl req -new -sha256 \
    -config "$OPENSSL_CNF" \
    -key "$PRIVATE_DIR/$SERVERNAME.key.pem" \
    -out "$CSR_DIR/$SERVERNAME.csr.pem" \
    -subj "/C=$C/ST=$ST/L=$L/O=$O/OU=$OU/CN=$SERVERNAME" \
    -addext "subjectAltName = $SAN"


openssl ca -batch -config "$OPENSSL_CNF" \
    -days 375 -md sha256 -notext \
    -in "$CSR_DIR/$SERVERNAME.csr.pem" \
    -out "$CERTS_DIR/$SERVERNAME.cert.pem" \

#
# Client
#
openssl genrsa -out "$PRIVATE_DIR/$CLIENT_CN.key.pem" 2048

openssl req -new -sha256 \
    -config "$OPENSSL_CNF" \
    -key "$PRIVATE_DIR/$CLIENT_CN.key.pem" \
    -out "$CSR_DIR/$CLIENT_CN.csr.pem" \
    -subj "/C=$C/ST=$ST/L=$L/O=$O/OU=$OU/CN=$CLIENT_CN"

openssl ca -batch -config "$OPENSSL_CNF" \
    -days 375 -md sha256 -notext \
    -in "$CSR_DIR/$CLIENT_CN.csr.pem" \
    -out "$CERTS_DIR/$CLIENT_CN.cert.pem" \
    -extensions usr_cert


cat << EOF
## SETTINGS ##
SUBJ: "/C=$C/ST=$ST/L=$L/O=$O/OU=$OU"
SERVER_NAME: $SERVERNAME
SAN: $SAN

CLIENT_CN: $CLIENT_CN
EOF

