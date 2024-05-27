#!/bin/bash
flask db upgrade
exec gunicorn -b :5678 --access-logfile - --error-logfile - musicservice:webapp