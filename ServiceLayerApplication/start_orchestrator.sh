#!/bin/bash
pkill gunicorn
echo "" > FrogOrchestrator.log
python gunicorn.py
