#!/bin/bash
echo "" > FrogServiceLayer.log
python gunicorn.py
