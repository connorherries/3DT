#!/usr/bin/env bash
set -e

docker compose up -d --build

echo
 echo "Website:   http://localhost:5000"
echo "phpMyAdmin: http://localhost:8080"
