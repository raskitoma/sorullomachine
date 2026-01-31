#!/bin/bash
# This script will restart sorullo and update to its latest version. It assumes you have a valid docker-compose.yml and you're using docker compose as a docker plugin.
docker compose down && git pull && docker compose build && docker compose up -d

