#!/bin/bash
which poetry 

APP_PORT="${PORT:=8080}"

poetry run streamlit run main.py --server.port=$APP_PORT --server.address=0.0.0.0
