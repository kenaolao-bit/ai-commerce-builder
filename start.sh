#!/bin/sh
# Lance le backend FastAPI (port interne 8000) puis le frontend Streamlit
# (port 7860, expose par Hugging Face Spaces). Les deux processus partagent
# le meme conteneur : c'est le frontend qui est expose publiquement, le
# backend n'est joignable qu'en interne via API_BASE_URL.
set -e

uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

exec streamlit run frontend/app.py --server.port 7860 --server.address 0.0.0.0 --server.headless true
