FROM acidrain/python-poetry:3.9-slim
USER root
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/haphan/vertex-ai-cs.git .

RUN poetry install -vvv

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["poetry", "run", "streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]
