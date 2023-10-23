#!/bin/bash
which poetry 

APP_PORT="${PORT:=default}"

poetry run streamlit run main.py --server.port=$APP_PORT --server.address=0.0.0.0
