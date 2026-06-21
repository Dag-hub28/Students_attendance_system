#!/usr/bin/env bash
# Start script that expands $PORT safely and launches Streamlit
PORT=${PORT:-8501}
exec streamlit run app.py --server.port "$PORT" --server.headless true
