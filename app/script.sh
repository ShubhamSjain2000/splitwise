#!/bin/sh
sleep 2
alembic upgrade head
python run.py