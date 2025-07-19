#!/bin/bash
echo "Iniciando servidor de detección de emociones..."
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 