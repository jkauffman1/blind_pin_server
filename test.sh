#!/bin/bash
echo Doing handshake...
SKE=`curl -s -X POST -H "Content-Type: application/json" localhost:8096/start_handshake | jq -r .ske`
echo "Handshake complete ske is ${SKE}"
echo Setting pin to 1234
CKE=02b924fcc0a4c44bb5c15724d13ddd2254c280439fe630520c97ad37add2964190
ENCRYPTED_DATA=12345678
HMAC_ENCRYPTED_DATA=d387bb987eae39610e504841dbd2a1d3a29b2277f1b9e9af7083ba6292028b89
#curl -X POST -H "Content-Type: application/json" -d "{\"ske\": \"${SKE}\", \"cke\": \"${CKE}\", \"encrypted_data\":\"${ENCRYPTED_DATA}\", \"hmac_encrypted_data\": \"${HMAC_ENCRYPTED_DATA}\"}" localhost:8096/set_pin
