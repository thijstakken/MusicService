#!/bin/bash
# retry database connection until it is ready
while true; do
    # Wait for the database service to be ready
    export FLASK_DB_UPGRADE=1
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        unset FLASK_DB_UPGRADE
        break
    fi
    # Unset the environment variable after the upgrade
    echo Upgrade command failed, retrying in 5 secs...
    sleep 5
done

exec gunicorn -b :5678 --access-logfile - --error-logfile - musicservice:webapp