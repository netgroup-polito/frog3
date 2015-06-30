#!/bin/bash
pkill gunicorn
echo "" > FrogServiceLayer.log
python gunicorn.py
