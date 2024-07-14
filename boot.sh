#!/bin/bash
# Wait for the database service to be ready
export FLASK_DB_UPGRADE=1
flask db upgrade
# Unset the environment variable after the upgrade
unset FLASK_DB_UPGRADE

exec gunicorn -b :5678 --access-logfile - --error-logfile - musicservice:webapp